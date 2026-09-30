"""
Chat Metrics
============
Tiny file-backed store recording per-exchange latency and token counts so the
Control Tower can show real telemetry instead of placeholders.

Stored in ``backend/data/control_tower_metrics.json`` as a list of the most
recent entries (newest last) plus running totals.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone

_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
METRICS_FILE = os.path.join(_DATA_DIR, "control_tower_metrics.json")
_MAX_ENTRIES = 50
_lock = threading.Lock()


def _load() -> dict:
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("recent"), list):
                return data
        except Exception:
            pass
    return {"recent": [], "total_exchanges": 0, "total_tokens": 0}


def record(latency_ms: float, tokens: int) -> None:
    """Append one chat exchange (latency in ms, approximate token count)."""
    with _lock:
        data = _load()
        data["recent"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latency_ms": int(latency_ms),
            "tokens": int(tokens),
        })
        data["recent"] = data["recent"][-_MAX_ENTRIES:]
        data["total_exchanges"] = int(data.get("total_exchanges", 0)) + 1
        data["total_tokens"] = int(data.get("total_tokens", 0)) + int(tokens)
        os.makedirs(_DATA_DIR, exist_ok=True)
        with open(METRICS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)


def snapshot(window: int = 10) -> dict:
    """Return recent latency/token series (last ``window``) and totals."""
    with _lock:
        data = _load()
    recent = data["recent"][-window:]
    latencies = [e["latency_ms"] for e in recent]
    tokens = [e["tokens"] for e in recent]
    return {
        "latency_history": latencies,
        "token_history": tokens,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else 0.0,
        "total_tokens": int(data.get("total_tokens", 0)),
        "peak_tokens": max(tokens) if tokens else 0,
    }
