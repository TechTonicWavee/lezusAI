"""
DRISHTI AI - Keep Integration Adapter
Provides integration with Keep (cloned in incident-management/) if an active instance is running,
and handles fallback to DRISHTI's local alert manager when Keep is not deployed.
"""

import os
import requests
from typing import Dict, Any, Optional

KEEP_API_URL = os.getenv("KEEP_API_URL", "http://localhost:8080")
KEEP_API_KEY = os.getenv("KEEP_API_KEY", "")


def is_keep_available(timeout_seconds: float = 1.0) -> bool:
    """Check whether Keep backend API is reachable."""
    try:
        response = requests.get(f"{KEEP_API_URL}/healthcheck", timeout=timeout_seconds)
        return response.status_code == 200
    except Exception:
        return False


def get_keep_status() -> Dict[str, Any]:
    """Return live status of Keep integration."""
    available = is_keep_available()
    return {
        "configured_url": KEEP_API_URL,
        "is_connected": available,
        "mode": "CONNECTED" if available else "LOCAL_FALLBACK",
        "description": "Active Keep API connected" if available else "Local alert manager fallback active (Keep server not running)"
    }


def forward_to_keep(alert_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Forward alert to Keep if available; otherwise return fallback status."""
    if not is_keep_available():
        return {
            "forwarded": False,
            "status": "LOCAL_FALLBACK",
            "message": "Keep endpoint unreachable, processed locally."
        }

    try:
        headers = {"Content-Type": "application/json"}
        if KEEP_API_KEY:
            headers["X-API-KEY"] = KEEP_API_KEY

        resp = requests.post(f"{KEEP_API_URL}/alerts/event", json=alert_payload, headers=headers, timeout=3.0)
        return {
            "forwarded": resp.status_code in [200, 201, 202],
            "status_code": resp.status_code,
            "response": resp.json() if resp.headers.get("content-type") == "application/json" else resp.text
        }
    except Exception as e:
        return {
            "forwarded": False,
            "error": str(e),
            "status": "LOCAL_FALLBACK"
        }

