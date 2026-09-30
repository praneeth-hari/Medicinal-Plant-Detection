"""
ServiceNow CMDB Service
=======================
Registers and syncs MediPlant AI components as Configuration Items (CIs)
in a ServiceNow instance using the Table REST API.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)

# Local file to persist sys_id mappings so we don't duplicate CIs
_SYS_ID_FILE = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")),
    "servicenow_sys_ids.json",
)

# CIs that represent MediPlant AI components
MEDIPLANT_CIS = [
    {
        "key": "mediplant_app",
        "name": "MediPlant AI",
        "short_description": "Medicinal Plant Detection & RAG Assistant — main application",
        "version": settings.APP_VERSION,
        "operational_status": "1",  # 1 = Operational
    },
    {
        "key": "fastapi_backend",
        "name": "MediPlant FastAPI Backend",
        "short_description": "FastAPI REST backend service for MediPlant AI",
        "version": "1.0.0",
        "operational_status": "1",
    },
    {
        "key": "ml_classifier",
        "name": "MediPlant ML Classifier",
        "short_description": "MobileNetV3-Small plant image classification model",
        "version": "1.0.0",
        "operational_status": "1",
    },
    {
        "key": "sqlite_db",
        "name": "MediPlant SQLite Database",
        "short_description": "SQLite database storing users, plants, detections and chats",
        "version": "1.0.0",
        "operational_status": "1",
    },
    {
        "key": "chromadb",  # key kept stable: existing sys_id mappings and the UI use it
        "name": "MediPlant FAISS Vector Store",
        "short_description": "FAISS vector store for RAG embeddings (all-MiniLM-L6-v2)",
        "version": "1.0.0",
        "operational_status": "1",
    },
    {
        "key": "groq_api",
        "name": "MediPlant Ollama LLM Integration",
        "short_description": f"Local Ollama LLM integration using {settings.OLLAMA_MODEL}",
        "version": "1.0.0",
        "operational_status": "1",
    },
]

# ServiceNow table for application CIs
_TABLE = "cmdb_ci_appl"


class ServiceNowService:
    """Client for ServiceNow Table API — CMDB CI management."""

    def __init__(self) -> None:
        self.instance  = settings.SERVICENOW_INSTANCE.rstrip("/")
        self.username  = settings.SERVICENOW_USERNAME
        self.password  = settings.SERVICENOW_PASSWORD
        self._base_url = f"{self.instance}/api/now/table/{_TABLE}"
        self._sys_ids: dict = self._load_sys_ids()

    # ── Persistence helpers ───────────────────────────────────────

    def _load_sys_ids(self) -> dict:
        os.makedirs(os.path.dirname(_SYS_ID_FILE), exist_ok=True)
        if os.path.exists(_SYS_ID_FILE):
            try:
                with open(_SYS_ID_FILE) as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_sys_ids(self) -> None:
        with open(_SYS_ID_FILE, "w") as f:
            json.dump(self._sys_ids, f, indent=2)

    # ── Connectivity ──────────────────────────────────────────────

    def is_configured(self) -> bool:
        return bool(self.instance and self.username and self.password)

    async def test_connection(self) -> dict:
        """Ping the ServiceNow instance and return status."""
        if not self.is_configured():
            return {"connected": False, "error": "ServiceNow credentials not configured"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{self.instance}/api/now/table/cmdb_ci_appl?sysparm_limit=1",
                    auth=(self.username, self.password),
                    headers={"Accept": "application/json"},
                )
                if resp.status_code == 200:
                    return {"connected": True, "instance": self.instance}
                return {"connected": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    # ── CI Operations ─────────────────────────────────────────────

    async def _get_existing_ci(self, client: httpx.AsyncClient, name: str) -> Optional[str]:
        """Return sys_id of existing CI by name, or None."""
        resp = await client.get(
            self._base_url,
            params={"sysparm_query": f"name={name}", "sysparm_fields": "sys_id", "sysparm_limit": 1},
            auth=(self.username, self.password),
            headers={"Accept": "application/json"},
        )
        if resp.status_code == 200:
            records = resp.json().get("result", [])
            if records:
                return records[0]["sys_id"]
        return None

    async def _create_ci(self, client: httpx.AsyncClient, ci: dict) -> Optional[str]:
        """Create a new CI, return sys_id."""
        payload = {
            "name": ci["name"],
            "short_description": ci["short_description"],
            "version": ci["version"],
            "operational_status": ci["operational_status"],
            "install_status": "1",
            "manufacturer": "MediPlant AI Project",
        }
        resp = await client.post(
            self._base_url,
            json=payload,
            auth=(self.username, self.password),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        if resp.status_code == 201:
            return resp.json()["result"]["sys_id"]
        logger.error("Failed to create CI %s: %s", ci["name"], resp.text)
        return None

    async def _update_ci(self, client: httpx.AsyncClient, sys_id: str, ci: dict) -> bool:
        """Update an existing CI."""
        payload = {
            "name": ci["name"],
            "short_description": ci["short_description"],
            "version": ci["version"],
            "operational_status": ci["operational_status"],
        }
        resp = await client.patch(
            f"{self._base_url}/{sys_id}",
            json=payload,
            auth=(self.username, self.password),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        return resp.status_code == 200

    # ── Public API ────────────────────────────────────────────────

    async def sync_all(self) -> dict:
        """
        Sync all MediPlant CIs to ServiceNow.
        Creates CIs that don't exist, updates ones that do.
        Returns a summary of actions taken.
        """
        if not self.is_configured():
            return {"success": False, "error": "ServiceNow credentials not configured"}

        results = []
        async with httpx.AsyncClient(timeout=15) as client:
            for ci in MEDIPLANT_CIS:
                key = ci["key"]
                sys_id = self._sys_ids.get(key)

                if not sys_id:
                    sys_id = await self._get_existing_ci(client, ci["name"])

                if sys_id:
                    updated = await self._update_ci(client, sys_id, ci)
                    self._sys_ids[key] = sys_id
                    results.append({"name": ci["name"], "action": "updated", "sys_id": sys_id, "success": updated})
                else:
                    sys_id = await self._create_ci(client, ci)
                    if sys_id:
                        self._sys_ids[key] = sys_id
                        results.append({"name": ci["name"], "action": "created", "sys_id": sys_id, "success": True})
                    else:
                        results.append({"name": ci["name"], "action": "failed", "sys_id": None, "success": False})

        self._save_sys_ids()
        synced = sum(1 for r in results if r["success"])
        return {
            "success": True,
            "synced": synced,
            "total": len(results),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results,
        }

    async def get_ci_status(self) -> dict:
        """Fetch current status of all registered CIs from ServiceNow."""
        if not self.is_configured():
            return {"success": False, "error": "ServiceNow credentials not configured", "cis": []}

        if not self._sys_ids:
            return {"success": True, "cis": [], "message": "No CIs registered yet. Run sync first."}

        cis = []
        async with httpx.AsyncClient(timeout=15) as client:
            for key, sys_id in self._sys_ids.items():
                resp = await client.get(
                    f"{self._base_url}/{sys_id}",
                    params={"sysparm_fields": "name,version,operational_status,short_description,sys_updated_on"},
                    auth=(self.username, self.password),
                    headers={"Accept": "application/json"},
                )
                if resp.status_code == 200:
                    r = resp.json()["result"]
                    status_map = {"1": "Operational", "2": "Non-Operational", "3": "Repair in Progress", "6": "End of Life"}
                    cis.append({
                        "key": key,
                        "name": r.get("name", ""),
                        "version": r.get("version", ""),
                        "status": status_map.get(r.get("operational_status", "1"), "Unknown"),
                        "description": r.get("short_description", ""),
                        "last_updated": r.get("sys_updated_on", ""),
                        "sys_id": sys_id,
                        "url": f"{self.instance}/nav_to.do?uri={_TABLE}.do?sys_id={sys_id}",
                    })

        return {"success": True, "cis": cis, "instance": self.instance}


# Singleton
servicenow_service = ServiceNowService()
