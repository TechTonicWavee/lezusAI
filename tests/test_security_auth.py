"""
DRISHTI AI — Security & Authentication Hardening Test Suite
Verifies:
1. Missing credentials return 401 Unauthorized
2. Invalid credentials return 403 Forbidden
3. Project A key cannot access Project B (telemetry, drift, incidents, remediation)
4. Default project requires valid authentication (no bypass)
5. Legacy hardcoded master key ('dr_live_master_override_key') is rejected
6. Legacy default system key ('dr_live_default_system_key') is rejected
7. Missing administrator secret fails closed (safe default)
8. Admin authentication succeeds with configured master key
9. Unauthenticated users cannot register projects or promote models
10. Incident resolution and remediation triggers enforce project boundaries
"""

import os
import sys
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import HTTPException
from integration.project_manager import (
    register_project,
    verify_project_api_key,
    verify_admin_key,
    verify_operator_key,
    authenticate_api_key,
    load_projects,
    save_projects,
)
from integration.security import (
    require_admin_auth,
    require_operator_or_admin_auth,
    verify_project_ownership_or_admin,
    get_authenticated_scope,
    extract_api_key,
)
from integration.api import (
    api_register_project,
    api_list_projects,
    api_get_project,
    api_ingest_telemetry,
    api_ingest_telemetry_batch,
    api_get_telemetry,
    api_get_drift,
    predict,
    list_alerts,
    resolve_incident_endpoint,
    manual_trigger_remediation,
    mlops_train,
    mlops_promote,
    ProjectRegisterRequest,
    TelemetryIngestRequest,
    TelemetryEventPayload,
    LogRequest,
)


def run_tests():
    print("=" * 70)
    print("DRISHTI AI — SECURITY & AUTHENTICATION AUDIT TEST SUITE")
    print("=" * 70)

    # Setup isolated test environment
    original_master = os.getenv("DRISHTI_MASTER_API_KEY")
    test_admin_key = f"dr_master_test_{secrets.token_hex(16)}"
    os.environ["DRISHTI_MASTER_API_KEY"] = test_admin_key

    proj_a_id = "sec-test-proj-alpha"
    proj_b_id = "sec-test-proj-beta"

    # Clean any leftover
    projs = [p for p in load_projects() if p["project_id"] not in [proj_a_id, proj_b_id]]
    save_projects(projs)

    # 1. Register two test projects
    p_a, key_a = register_project(project_id=proj_a_id, name="Security Alpha")
    p_b, key_b = register_project(project_id=proj_b_id, name="Security Beta")
    assert key_a != key_b
    print("✓ Created two isolated test projects with distinct credentials")

    # 2. Reject Legacy Hardcoded Credentials
    assert not verify_admin_key("dr_live_master_override_key"), "Legacy master key was accepted!"
    assert not verify_project_api_key(proj_a_id, "dr_live_master_override_key"), "Legacy master key bypassed project auth!"
    assert not verify_project_api_key(proj_a_id, "dr_live_default_system_key"), "Legacy default key bypassed project auth!"
    assert not verify_project_api_key("default", "dr_live_default_system_key"), "Legacy default key accepted on default!"
    print("✓ Legacy hardcoded keys ('dr_live_master_override_key', 'dr_live_default_system_key') completely rejected")

    # 3. Fail Closed on Missing Admin Secret
    saved_env = os.environ.pop("DRISHTI_MASTER_API_KEY", None)
    assert not verify_admin_key(test_admin_key), "Admin check did not fail closed when secret was unset!"
    try:
        require_admin_auth(test_admin_key)
        assert False, "require_admin_auth did not raise 403 when master key unset"
    except HTTPException as e:
        assert e.status_code == 403
    os.environ["DRISHTI_MASTER_API_KEY"] = test_admin_key
    print("✓ Missing administrator secret fails closed (HTTP 403)")

    # 4. Valid Admin Key Verification
    assert verify_admin_key(test_admin_key) is True
    admin_auth = require_admin_auth(test_admin_key)
    assert admin_auth == test_admin_key
    print("✓ Configured administrator master key verifies successfully")

    # 5. Missing & Invalid Credentials Error Codes
    try:
        verify_project_ownership_or_admin(proj_a_id, None)
        assert False, "Allowed None token"
    except HTTPException as e:
        assert e.status_code == 401, f"Expected 401, got {e.status_code}"
    print("✓ Missing credentials return HTTP 401 Unauthorized")

    try:
        verify_project_ownership_or_admin(proj_a_id, "dr_live_fake_invalid_token")
        assert False, "Allowed fake token"
    except HTTPException as e:
        assert e.status_code == 403, f"Expected 403, got {e.status_code}"
    print("✓ Invalid credentials return HTTP 403 Forbidden")

    # 6. Cross-Project Isolation (Tenant Boundary Enforced)
    # Key A must authenticate for Project A, but NEVER for Project B
    assert verify_project_api_key(proj_a_id, key_a) is True
    assert verify_project_api_key(proj_b_id, key_b) is True
    assert verify_project_api_key(proj_b_id, key_a) is False, "Project A key authenticated for Project B!"
    assert verify_project_api_key(proj_a_id, key_b) is False, "Project B key authenticated for Project A!"

    try:
        verify_project_ownership_or_admin(proj_b_id, key_a)
        assert False, "Project A key accessed Project B via ownership check"
    except HTTPException as e:
        assert e.status_code == 403
    print("✓ Strict cross-project credential boundary verified (Zero inter-project auth)")

    # 7. Unauthenticated Default Project Access Denied
    try:
        verify_project_ownership_or_admin("default", None)
        assert False, "Allowed unauthenticated access to 'default' project!"
    except HTTPException as e:
        assert e.status_code == 401
    print("✓ Default project unauthenticated access exception removed (HTTP 401)")

    # 8. Unauthenticated User Cannot Register Projects
    try:
        api_register_project(
            ProjectRegisterRequest(project_id="unauth-proj", name="Unauth"),
            admin_token=None  # Depends would raise 401
        )
        assert False, "Unauthenticated project registration succeeded!"
    except (HTTPException, TypeError):
        pass

    try:
        require_admin_auth("invalid_token")
        assert False, "Invalid admin token accepted"
    except HTTPException as e:
        assert e.status_code == 403
    print("✓ Project registration restricted strictly to Administrator")

    # 9. Telemetry Ingestion Cross-Project Prevention
    # Ingest into Project A using Key A -> Success
    telem_payload = TelemetryEventPayload(
        model_name="sec-model-a",
        prediction=105.0,
        latency_ms=12.5,
    )
    res_a = api_ingest_telemetry(
        TelemetryIngestRequest(project_id=proj_a_id, record=telem_payload),
        token=key_a,
    )
    assert res_a["status"] == "success"

    # Attempt to ingest into Project B using Key A -> 403 Forbidden
    try:
        api_ingest_telemetry(
            TelemetryIngestRequest(project_id=proj_b_id, record=telem_payload),
            token=key_a,
        )
        assert False, "Cross-project telemetry injection succeeded!"
    except HTTPException as e:
        assert e.status_code == 403
    print("✓ Cross-project telemetry injection prevented (HTTP 403)")

    # 10. Telemetry Read Cross-Project Prevention
    # Project B key attempting to read Project A telemetry -> 403 Forbidden
    try:
        api_get_telemetry(project_id=proj_a_id, token=key_b)
        assert False, "Project B read Project A telemetry!"
    except HTTPException as e:
        assert e.status_code == 403
    print("✓ Cross-project telemetry reading prevented (HTTP 403)")

    # 11. Operational Predict Project Scoping
    # Run predict for Project A using Key A -> Success
    pred_res = predict(
        LogRequest(message="ERROR: Database connection pool timeout", project_id=proj_a_id),
        token=key_a,
    )
    assert pred_res["result"] == "ANOMALY"
    alert_id = pred_res["alert"]["id"]

    # Attempt to run predict for Project B using Key A -> 403 Forbidden
    try:
        predict(
            LogRequest(message="ERROR: Memory overflow", project_id=proj_b_id),
            token=key_a,
        )
        assert False, "Predict allowed cross-project injection!"
    except HTTPException as e:
        assert e.status_code == 403
    print("✓ Operational log prediction project boundary enforced (HTTP 403)")

    # 12. Incident Cross-Project Access & Resolution Prevention
    # Project B key viewing alerts filtered to Project A -> 403 Forbidden
    try:
        list_alerts(project_id=proj_a_id, token=key_b)
        assert False, "Project B listed Project A alerts!"
    except HTTPException as e:
        assert e.status_code == 403

    # Project B key attempting to resolve Project A's incident -> 403 Forbidden
    try:
        resolve_incident_endpoint(alert_id=alert_id, token=key_b)
        assert False, "Project B resolved Project A's incident!"
    except HTTPException as e:
        assert e.status_code == 403
    print("✓ Cross-project incident access and resolution prevented (HTTP 403)")

    # 13. Remediation Trigger Cross-Project Prevention
    # Project B attempting to trigger remediation for Project A's incident -> 403 Forbidden
    try:
        manual_trigger_remediation(incident_id=alert_id, token=key_b)
        assert False, "Project B triggered remediation for Project A's incident!"
    except HTTPException as e:
        assert e.status_code == 403
    print("✓ Cross-project automated remediation trigger prevented (HTTP 403)")

    # 14. MLOps Administrative Protections
    # Non-admin token cannot trigger training or model promotion
    try:
        mlops_train(admin_token=key_a)
        assert False, "Project key triggered MLOps training!"
    except HTTPException as e:
        assert e.status_code == 403

    try:
        mlops_promote(admin_token=key_a)
        assert False, "Project key triggered MLOps promotion!"
    except HTTPException as e:
        assert e.status_code == 403
    print("✓ MLOps training and model promotion restricted strictly to Administrator")

    # Clean up test artifacts
    projs = [p for p in load_projects() if p["project_id"] not in [proj_a_id, proj_b_id]]
    save_projects(projs)
    f_a = ROOT / "data" / "telemetry" / f"{proj_a_id}.jsonl"
    f_b = ROOT / "data" / "telemetry" / f"{proj_b_id}.jsonl"
    if f_a.exists():
        f_a.unlink()
    if f_b.exists():
        f_b.unlink()

    # Restore environment
    if original_master is not None:
        os.environ["DRISHTI_MASTER_API_KEY"] = original_master
    else:
        os.environ.pop("DRISHTI_MASTER_API_KEY", None)

    print("=" * 70)
    print("✓ ALL 14 SECURITY & AUTHENTICATION AUDIT TESTS PASSED (100% SUCCESS)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_tests()
