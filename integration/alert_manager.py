"""
DRISHTI AI - Advanced Multi-Project Incident Management & Correlation Engine
Supports:
- Project-scoped alerts & incident isolation
- Alert severity & classification
- Alert timestamps (ISO 8601)
- Incident lifecycle (OPEN, INVESTIGATING, MITIGATING, RESOLVED, CLOSED)
- Deduplication via alert fingerprinting & occurrence tracking
- Multi-alert correlation and root-cause grouping
- Comprehensive audit trail & incident history
- Seamless Keep integration with local fallback
"""

import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from integration.keep_client import forward_to_keep, get_keep_status
from integration.metrics import record_incident_created, record_incident_resolved

ROOT = Path(__file__).resolve().parent.parent
ALERTS_DIR = ROOT / "alerts"
ALERTS_FILE = ALERTS_DIR / "incidents.json"
HISTORY_FILE = ALERTS_DIR / "incident_history.json"

SEVERITIES = ["INFO", "WARNING", "ERROR", "CRITICAL"]
VALID_STATUSES = ["OPEN", "INVESTIGATING", "MITIGATING", "RESOLVED", "CLOSED"]


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_alerts() -> List[Dict[str, Any]]:
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    if not ALERTS_FILE.exists():
        ALERTS_FILE.write_text("[]", encoding="utf-8")
        return []
    try:
        content = ALERTS_FILE.read_text(encoding="utf-8").strip()
        return json.loads(content) if content else []
    except Exception:
        return []


def save_alerts(alerts: List[Dict[str, Any]]) -> None:
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    ALERTS_FILE.write_text(json.dumps(alerts, indent=4), encoding="utf-8")


def load_history() -> List[Dict[str, Any]]:
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")
        return []
    try:
        content = HISTORY_FILE.read_text(encoding="utf-8").strip()
        return json.loads(content) if content else []
    except Exception:
        return []


def save_history(history: List[Dict[str, Any]]) -> None:
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(history, indent=4), encoding="utf-8")


def record_history_event(
    incident_id: str,
    action: str,
    previous_state: Optional[str] = None,
    new_state: Optional[str] = None,
    details: Optional[str] = None,
    actor: str = "AIOps_System",
    project_id: str = "default",
) -> Dict[str, Any]:
    history = load_history()
    event = {
        "event_id": str(uuid.uuid4())[:8],
        "incident_id": incident_id,
        "project_id": project_id,
        "action": action,
        "previous_state": previous_state,
        "new_state": new_state,
        "details": details or "",
        "actor": actor,
        "timestamp": _now_iso(),
    }
    history.append(event)
    save_history(history)
    return event


def compute_fingerprint(category: str, severity: str, message: str, project_id: str = "default") -> str:
    """Generate a stable fingerprint scoped to the project to detect duplicate alerts."""
    clean_msg = "".join(filter(str.isalpha, message.lower()))[:40]
    raw = f"{project_id.lower()}:{category.lower()}:{severity.upper()}:{clean_msg}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]


def detect_severity(message: str) -> str:
    msg_upper = message.upper()
    if "CRITICAL" in msg_upper:
        return "CRITICAL"
    if "ERROR" in msg_upper:
        return "ERROR"
    if "WARNING" in msg_upper or "LATENCY" in msg_upper:
        return "WARNING"
    return "INFO"


def detect_category(message: str) -> str:
    msg_upper = message.upper()
    for cat in ["DATABASE", "PREDICTION", "MEMORY", "INFERENCE", "LATENCY", "AUTHENTICATION", "MODEL", "API"]:
        if cat in msg_upper:
            return cat.lower()
    return "general"


def correlate_with_open_incidents(alerts: List[Dict[str, Any]], category: str, project_id: str = "default") -> Optional[str]:
    """Find related open incidents in the same project and category."""
    for alert in reversed(alerts):
        if alert.get("project_id", "default") == project_id and alert.get("status") in ["OPEN", "INVESTIGATING", "MITIGATING"]:
            if alert.get("category") == category:
                return alert["id"]
    return None


def create_alert(
    message: str,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    source: str = "Log_Anomaly_Detector",
    project_id: str = "default",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a new incident or deduplicate against existing active incidents in this project.
    """
    alerts = load_alerts()

    sev = (severity or detect_severity(message)).upper()
    if sev not in SEVERITIES:
        sev = "ERROR"

    cat = (category or detect_category(message)).lower()
    fingerprint = compute_fingerprint(cat, sev, message, project_id=project_id)
    now = _now_iso()

    # Duplicate Alert Detection: Check if active incident with same fingerprint exists in project
    for existing in alerts:
        if (
            existing.get("project_id", "default") == project_id
            and existing.get("fingerprint") == fingerprint
            and existing.get("status") in ["OPEN", "INVESTIGATING", "MITIGATING"]
        ):
            existing["occurrence_count"] = existing.get("occurrence_count", 1) + 1
            existing["last_seen_at"] = now
            if "recent_occurrences" not in existing:
                existing["recent_occurrences"] = []
            existing["recent_occurrences"].append({
                "timestamp": now,
                "message": message,
            })
            existing["recent_occurrences"] = existing["recent_occurrences"][-20:]
            save_alerts(alerts)

            record_history_event(
                incident_id=existing["id"],
                action="DEDUPLICATED_OCCURRENCE",
                previous_state=existing["status"],
                new_state=existing["status"],
                details=f"Suppressed duplicate alert in '{project_id}'. Occurrences: {existing['occurrence_count']}.",
                actor="Deduplication_Engine",
                project_id=project_id,
            )
            return existing

    # Incident Correlation: Check for related open incidents in same category & project
    correlated_id = correlate_with_open_incidents(alerts, cat, project_id=project_id)
    correlation_group = f"group_{project_id}_{cat}_{now[:10]}"

    incident_id = str(uuid.uuid4())[:8]
    new_alert = {
        "id": incident_id,
        "project_id": project_id,
        "fingerprint": fingerprint,
        "title": f"[{sev}] {cat.capitalize()} Anomaly Detected ({project_id})",
        "message": message,
        "severity": sev,
        "category": cat,
        "source": source,
        "status": "OPEN",
        "occurrence_count": 1,
        "created_at": now,
        "first_seen_at": now,
        "last_seen_at": now,
        "correlated_incident_id": correlated_id,
        "correlation_group": correlation_group,
        "resolved_at": None,
        "resolution_notes": None,
        "resolved_by": None,
        "automated_response_triggered": False,
        "metadata": metadata or {},
    }

    alerts.append(new_alert)
    save_alerts(alerts)

    record_incident_created(project_id)

    record_history_event(
        incident_id=incident_id,
        action="INCIDENT_CREATED",
        previous_state=None,
        new_state="OPEN",
        details=f"New incident created with severity {sev} in category {cat} (project: {project_id}).",
        actor="Alert_Manager",
        project_id=project_id,
    )

    # Optional forwarding to Keep (if available)
    forward_to_keep(new_alert)

    return new_alert


def get_alerts(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
) -> List[Dict[str, Any]]:
    alerts = load_alerts()
    if project_id and project_id != "all":
        alerts = [a for a in alerts if a.get("project_id", "default") == project_id]
    if status:
        alerts = [a for a in alerts if a.get("status", "").upper() == status.upper()]
    if severity:
        alerts = [a for a in alerts if a.get("severity", "").upper() == severity.upper()]
    return alerts


def update_alert_status(
    alert_id: str,
    new_status: str,
    notes: Optional[str] = None,
    actor: str = "AIOps_Operator",
) -> Optional[Dict[str, Any]]:
    """Transition an incident through its lifecycle."""
    new_status = new_status.upper()
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Allowed: {VALID_STATUSES}")

    alerts = load_alerts()
    for alert in alerts:
        if alert["id"] == alert_id:
            old_status = alert["status"]
            alert["status"] = new_status
            pid = alert.get("project_id", "default")
            if new_status == "RESOLVED":
                alert["resolved_at"] = _now_iso()
                alert["resolution_notes"] = notes or "Resolved by operator"
                alert["resolved_by"] = actor
                record_incident_resolved(pid)
            save_alerts(alerts)

            record_history_event(
                incident_id=alert_id,
                action=f"STATUS_TRANSITION_TO_{new_status}",
                previous_state=old_status,
                new_state=new_status,
                details=notes or f"Status changed from {old_status} to {new_status}",
                actor=actor,
                project_id=pid,
            )
            return alert
    return None


def resolve_alert(
    alert_id: str,
    resolution_notes: Optional[str] = "Incident resolved successfully",
    resolved_by: str = "AIOps_Operator",
) -> Optional[Dict[str, Any]]:
    """Resolve an incident and record resolution metadata."""
    return update_alert_status(
        alert_id=alert_id,
        new_status="RESOLVED",
        notes=resolution_notes,
        actor=resolved_by,
    )


def get_incident_history(
    incident_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    history = load_history()
    if incident_id:
        history = [h for h in history if h.get("incident_id") == incident_id]
    if project_id and project_id != "all":
        history = [h for h in history if h.get("project_id", "default") == project_id]
    return history


def get_incident_stats(project_id: Optional[str] = None) -> Dict[str, Any]:
    alerts = load_alerts()
    if project_id and project_id != "all":
        alerts = [a for a in alerts if a.get("project_id", "default") == project_id]

    total = len(alerts)
    open_count = sum(1 for a in alerts if a.get("status") == "OPEN")
    investigating_count = sum(1 for a in alerts if a.get("status") == "INVESTIGATING")
    mitigating_count = sum(1 for a in alerts if a.get("status") == "MITIGATING")
    resolved_count = sum(1 for a in alerts if a.get("status") == "RESOLVED")
    closed_count = sum(1 for a in alerts if a.get("status") == "CLOSED")

    by_severity = {s: sum(1 for a in alerts if a.get("severity") == s) for s in SEVERITIES}
    by_category = {}
    for a in alerts:
        cat = a.get("category", "other")
        by_category[cat] = by_category.get(cat, 0) + 1

    return {
        "project_id": project_id or "all",
        "total_incidents": total,
        "open_incidents": open_count,
        "active_incidents": open_count + investigating_count + mitigating_count,
        "investigating_incidents": investigating_count,
        "mitigating_incidents": mitigating_count,
        "resolved_incidents": resolved_count,
        "closed_incidents": closed_count,
        "by_severity": by_severity,
        "by_category": by_category,
        "keep_status": get_keep_status(),
    }
