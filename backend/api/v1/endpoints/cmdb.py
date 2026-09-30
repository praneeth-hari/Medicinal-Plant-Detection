"""
CMDB Endpoints — ServiceNow Integration
========================================
Developer-only routes for syncing and viewing CI status in ServiceNow.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from api.deps import get_current_user
from schemas.user import TokenData
from services.servicenow_service import servicenow_service

router = APIRouter()


@router.get("/status")
async def get_cmdb_status(current_user: TokenData = Depends(get_current_user)):
    """Check ServiceNow connection and return CI status."""
    connection = await servicenow_service.test_connection()
    if not connection["connected"]:
        return {"connected": False, "error": connection.get("error"), "cis": []}
    ci_data = await servicenow_service.get_ci_status()
    return {**connection, **ci_data}


@router.post("/sync")
async def sync_cmdb(current_user: TokenData = Depends(get_current_user)):
    """Push all MediPlant CIs to ServiceNow — creates or updates."""
    return await servicenow_service.sync_all()


@router.get("/connection")
async def test_connection(current_user: TokenData = Depends(get_current_user)):
    """Test connectivity to the ServiceNow instance."""
    return await servicenow_service.test_connection()
