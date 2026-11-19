"""
DRISHTI AI - Safe Automated Incident Response Engine
Executes targeted, safe, simulated remediation actions for detected operational anomalies.
Maintains project-aware execution logs and links actions directly to incident records.
"""

import json
import random
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from integration.alert_manager import (
    load_alerts,
    save_alerts,
    record_history_event,
)

ROOT = Path(__file__).resolve().parent.parent
ALERTS_DIR = ROOT / "alerts"
ACTIONS_FILE = ALERTS_DIR / "remediation_actions.json"


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_remediation_actions() -> List[Dict[str, Any]]:
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    if not ACTIONS_FILE.exists():
        ACTIONS_FILE.write_text("[]", encoding="utf-8")
        return []
    try:
        content = ACTIONS_FILE.read_text(encoding="utf-8").strip()
        return json.loads(content) if content else []
    except Exception:
        return []


def save_remediation_actions(actions: List[Dict[str, Any]]) -> None:
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    ACTIONS_FILE.write_text(json.dumps(actions, indent=4), encoding="utf-8")


def get_playbook_action(category: str, message: str) -> Dict[str, Any]:
    cat = category.lower()
    msg_upper = message.upper()

    if "DATABASE" in msg_upper or cat == "database":
        return {
            "action_type": "DATABASE_POOL_RECYCLE",
            "name": "Database Connection Pool Recovery",
            "description": "Recycled idle database connections, pinged DB primary, and refreshed connection pool.",
            "output": {
                "pool_size": 25,
                "idle_connections_reaped": 8,
                "db_ping_ms": round(random.uniform(0.8, 2.2), 2),
                "connection_status": "HEALTHY",
            },
        }
    elif "MEMORY" in msg_upper or cat == "memory":
        freed = random.randint(400, 1100)
        return {
            "action_type": "MEMORY_RECLAMATION",
            "name": "Process Memory Garbage Collection",
            "description": "Triggered memory compaction, released cached dataframe buffers, and recorded heap profile.",
            "output": {
                "memory_freed_mb": freed,
                "gc_objects_collected": random.randint(2500, 7800),
                "heap_status": "NORMALIZED",
            },
        }
    elif "API" in msg_upper or cat == "api":
        return {
            "action_type": "API_CIRCUIT_BREAKER_RESET",
            "name": "API Gateway Circuit Breaker Reset",
            "description": "Reset upstream circuit breaker state, flushed edge cache, and verified health probe.",
            "output": {
                "circuit_breaker": "CLOSED",
                "cache_flushed_keys": random.randint(40, 200),
                "health_probe_status": 200,
            },
        }
    elif "LATENCY" in msg_upper or cat == "latency":
        return {
            "action_type": "LATENCY_PROFILE_AND_OPTIMIZE",
            "name": "Query Profiling & Worker Optimization",
            "description": "Profiled slow request execution trace, adjusted keep-alive pool, and queued worker autoscaling.",
            "output": {
                "p99_before_ms": round(random.uniform(1200, 2400), 1),
                "p99_projected_ms": 120.0,
                "autoscaling_event": "TRIGGERED_+2_WORKERS",
            },
        }
    elif "INFERENCE" in msg_upper or "MODEL" in msg_upper or cat in ["inference", "model"]:
        return {
            "action_type": "MODEL_INFERENCE_FALLBACK_RELOAD",
            "name": "Model Inference Baseline Fallback & Reload",
            "description": "Engaged heuristic fallback scoring and re-initialized trained model artifact from disk.",
            "output": {
                "fallback_mode": "TRANSIENT_ACTIVE",
                "model_reloaded": True,
                "artifact_integrity": "SHA256_VERIFIED",
            },
        }
    else:
        return {
            "action_type": "AUTOMATED_DIAGNOSTIC_HEALTHCHECK",
            "name": "Subsystem Diagnostic Health Probe",
            "description": "Collected thread stack dumps, verified resource limits, and alerted observability channels.",
            "output": {
                "diagnostic_result": "PASSED",
                "threads_monitored": 18,
                "pagerduty_alert_dispatched": False,
            },
        }


def execute_remediation(
    incident_id: str,
    message: str,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    project_id: str = "default",
    triggered_by: str = "Automated_AIOps_Engine",
) -> Dict[str, Any]:
    """
    Execute a safe, non-destructive simulated remediation action for an incident.
    Records output to alerts/remediation_actions.json and updates incident status.
    """
    start_time = time.perf_counter()
    time.sleep(random.uniform(0.015, 0.045))  # Simulate realistic execution latency
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    cat = category or "general"
    playbook = get_playbook_action(cat, message)

    action_id = str(uuid.uuid4())[:8]
    now = _now_iso()

    action_record = {
        "action_id": action_id,
        "incident_id": incident_id,
        "project_id": project_id,
        "action_type": playbook["action_type"],
        "action_name": playbook["name"],
        "trigger_event": message,
        "category": cat,
        "status": "SUCCESS",
        "execution_duration_ms": elapsed_ms,
        "description": playbook["description"],
        "remediation_output": playbook["output"],
        "is_simulated": True,
        "triggered_by": triggered_by,
        "timestamp": now,
    }

    actions = load_remediation_actions()
    actions.append(action_record)
    save_remediation_actions(actions)

    # Update incident state to reflect remediation
    alerts = load_alerts()
    for alert in alerts:
        if alert["id"] == incident_id:
            alert["automated_response_triggered"] = True
            alert["last_remediation_action"] = playbook["action_type"]
            if alert.get("status") == "OPEN":
                alert["status"] = "MITIGATING"
            save_alerts(alerts)
            break

    record_history_event(
        incident_id=incident_id,
        action="AUTOMATED_RESPONSE_EXECUTED",
        previous_state="OPEN",
        new_state="MITIGATING",
        details=f"Executed {playbook['name']} in {elapsed_ms}ms with status SUCCESS (project: {project_id}).",
        actor="Response_Engine",
        project_id=project_id,
    )

    return action_record


def get_remediation_history(
    incident_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    actions = load_remediation_actions()
    if incident_id:
        actions = [a for a in actions if a.get("incident_id") == incident_id]
    if project_id and project_id != "all":
        actions = [a for a in actions if a.get("project_id", "default") == project_id]
    return actions


def get_response_stats(project_id: Optional[str] = None) -> Dict[str, Any]:
    actions = load_remediation_actions()
    if project_id and project_id != "all":
        actions = [a for a in actions if a.get("project_id", "default") == project_id]

    total = len(actions)
    success_count = sum(1 for a in actions if a.get("status") == "SUCCESS")
    by_type = {}
    for a in actions:
        t = a.get("action_type", "OTHER")
        by_type[t] = by_type.get(t, 0) + 1

    return {
        "project_id": project_id or "all",
        "total_actions": total,
        "success_count": success_count,
        "success_rate_percent": 100.0 if total == 0 else round((success_count / total) * 100, 1),
        "by_action_type": by_type,
    }
