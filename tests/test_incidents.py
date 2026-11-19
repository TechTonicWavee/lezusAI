"""
Tests for Incident Lifecycle, Deduplication, and Safe Automated Remediation.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from integration.alert_manager import (
    create_alert,
    get_alerts,
    update_alert_status,
    resolve_alert,
    get_incident_history,
    get_incident_stats,
    load_alerts,
    save_alerts,
)
from integration.response_engine import execute_remediation, get_remediation_history


def run_tests():
    print("--- [Test Suite 3: Incident Management & Automated Response] ---")

    test_pid_1 = "test-inc-proj-1"
    test_pid_2 = "test-inc-proj-2"

    # 1. Create Incident in Project 1
    msg = "ERROR: Database connection timeout"
    a1 = create_alert(message=msg, severity="ERROR", category="database", project_id=test_pid_1)
    assert a1["project_id"] == test_pid_1
    assert a1["status"] == "OPEN"
    print("✓ Incident creation verified")

    # 2. Test Deduplication within Project 1
    a2 = create_alert(message=msg, severity="ERROR", category="database", project_id=test_pid_1)
    assert a1["id"] == a2["id"], "Deduplication failed within same project"
    assert a2["occurrence_count"] >= 2, "Occurrence count not incremented"
    print(f"✓ Deduplication verified (Occurrences: {a2['occurrence_count']})")

    # 3. Test Project Scoped Isolation in Incidents
    # Same error message in Project 2 must create a SEPARATE incident
    a3 = create_alert(message=msg, severity="ERROR", category="database", project_id=test_pid_2)
    assert a3["id"] != a1["id"], "Cross-project duplicate collision occurred!"
    assert a3["project_id"] == test_pid_2
    print("✓ Project isolation in incident management verified")

    # 4. Incident Lifecycle Transitions
    updated = update_alert_status(a1["id"], "INVESTIGATING", notes="Assigned to on-call DBA")
    assert updated["status"] == "INVESTIGATING"

    resolved = resolve_alert(a1["id"], resolution_notes="DB connection pool recycled", resolved_by="DBA_Lead")
    assert resolved["status"] == "RESOLVED"
    assert resolved["resolved_at"] is not None
    assert resolved["resolution_notes"] == "DB connection pool recycled"
    print("✓ Lifecycle transitions verified: OPEN -> INVESTIGATING -> RESOLVED")

    # 5. Safe Automated Remediation
    action = execute_remediation(
        incident_id=a3["id"],
        message=msg,
        category="database",
        project_id=test_pid_2,
    )
    assert action["status"] == "SUCCESS"
    assert action["is_simulated"] is True
    assert action["action_type"] == "DATABASE_POOL_RECYCLE"
    assert "pool_size" in action["remediation_output"]
    print(f"✓ Safe automated response verified: {action['action_name']} ({action['execution_duration_ms']} ms)")

    # 6. Incident Stats
    stats_p1 = get_incident_stats(project_id=test_pid_1)
    stats_p2 = get_incident_stats(project_id=test_pid_2)
    assert stats_p1["resolved_incidents"] >= 1
    assert stats_p2["active_incidents"] >= 1
    print("✓ Project-filtered incident statistics verified")

    # Clean up test alerts
    alerts = [a for a in load_alerts() if a.get("project_id") not in [test_pid_1, test_pid_2]]
    save_alerts(alerts)
    print("✓ Cleaned up test incidents. Suite 3 Passed!\n")


if __name__ == "__main__":
    run_tests()

