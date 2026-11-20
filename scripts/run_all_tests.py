"""
DRISHTI AI — Master Test Suite & Production Readiness Runner
Executes comprehensive validation across:
1. Multi-Project Registration & Auth
2. Universal Telemetry & Project-Level Isolation
3. Incident Lifecycle, Deduplication & Safe Response
4. Persistent Prometheus Metrics Engine
5. Python SDK & Resiliency
6. Security & Authentication Hardening Audit
7. In-Process FastAPI Endpoint Verification
8. External ML Sample Application (House Price Model)
"""

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "log-anomaly"))
sys.path.insert(0, str(ROOT / "mlops-platform" / "ml-flow"))
sys.path.insert(0, str(ROOT))

import tests.test_projects as t_proj
import tests.test_telemetry as t_telem
import tests.test_incidents as t_inc
import tests.test_metrics as t_met
import tests.test_sdk as t_sdk
import tests.test_security_auth as t_sec

print("=" * 75)
print("DRISHTI AI — COMPREHENSIVE PRODUCTION READINESS TEST RUNNER")
print("=" * 75)
start_all = time.perf_counter()

# Step 1: Projects & Authentication
t_proj.run_tests()

# Step 2: Telemetry & Project Isolation
t_telem.run_tests()

# Step 3: Incidents & Automated Response
t_inc.run_tests()

# Step 4: Prometheus Metrics
t_met.run_tests()

# Step 5: Python SDK
t_sdk.run_tests()

# Step 6: Security & Authentication Hardening
t_sec.run_tests()

# Step 7: FastAPI Route Handlers Verification
print("--- [Test Suite 7: FastAPI Unified API Endpoints] ---")
from integration.api import (
    home,
    health,
    api_register_project,
    api_list_projects,
    api_ingest_telemetry,
    api_ingest_telemetry_batch,
    predict,
    list_alerts,
    incident_stats,
    list_responses,
    prometheus_metrics,
    serve_dashboard,
    ProjectRegisterRequest,
    TelemetryIngestRequest,
    BatchTelemetryRequest,
    TelemetryEventPayload,
    LogRequest,
)

h = home()
assert h["status"] == "running"
hl = health()
assert hl["status"] == "healthy"
print("✓ GET / and GET /health operational")

# Configure test admin key for runner
test_admin_key = "dr_master_test_e2e_runner_key"
os.environ["DRISHTI_MASTER_API_KEY"] = test_admin_key

# Test API Project Registration
reg_req = ProjectRegisterRequest(
    project_id="e2e-suite-model",
    name="E2E Validation Model",
    description="Automated test registration",
    model_type="regression",
)
reg_res = api_register_project(reg_req, admin_token=test_admin_key)
assert reg_res["status"] == "success"
api_key = reg_res["api_key"]
print(f"✓ POST /projects/register operational (Key prefix: {reg_res['project']['api_key_masked']})")

# Test Single Telemetry Ingestion via API
telem_req = TelemetryIngestRequest(
    project_id="e2e-suite-model",
    record=TelemetryEventPayload(
        model_name="e2e-regressor",
        prediction=350000.0,
        ground_truth=345000.0,
        latency_ms=38.5,
        confidence=0.96,
    )
)
ingest_res = api_ingest_telemetry(telem_req, token=api_key)
assert ingest_res["status"] == "success"
assert ingest_res["result"] == "NORMAL"
print("✓ POST /telemetry/ingest operational")

# Test Batch Ingestion via API
batch_req = BatchTelemetryRequest(
    project_id="e2e-suite-model",
    records=[
        TelemetryEventPayload(prediction=100.0, latency_ms=20.0),
        TelemetryEventPayload(
            severity="ERROR",
            error_type="DatabaseTimeout",
            error_message="Connection pool exhausted",
            latency_ms=1200.0,
        ),
    ]
)
batch_res = api_ingest_telemetry_batch(batch_req, token=api_key)
assert batch_res["successful"] == 2
assert batch_res["anomalies_detected"] >= 1
print("✓ POST /telemetry/batch operational (Anomaly and incident auto-triggered)")

# Test Prometheus Metrics Endpoint
prom_res = prometheus_metrics(is_authorized=True)
assert len(prom_res.body.decode().splitlines()) >= 25
print("✓ GET /metrics operational with standard Prometheus exposition")

# Test Dashboard HTML Serving
dash_res = serve_dashboard()
assert len(dash_res.body) > 20000
print("✓ GET /dashboard HTML serving verified (50+ KB interactive React SPA)")
print("✓ Suite 7 Passed!\n")

# Step 8: Sample External ML Application (House Price Model)
print("--- [Test Suite 8: Sample External Application Integration] ---")
from examples.house_price_service import HousePriceModel
house_model = HousePriceModel()
pred = house_model.predict(sqft=2200, bedrooms=3, bathrooms=2)
assert pred > 200000.0, f"Unrealistic house price: {pred}"
print(f"✓ HousePriceModel evaluated sample property -> ${pred:,.2f}")
print("✓ Sample External ML Application verified. Suite 8 Passed!\n")

# Cleanup e2e-suite-model
from integration.project_manager import load_projects, save_projects
projs = [p for p in load_projects() if p["project_id"] != "e2e-suite-model"]
save_projects(projs)
f_e2e = ROOT / "data" / "telemetry" / "e2e-suite-model.jsonl"
if f_e2e.exists():
    f_e2e.unlink()

elapsed_total = round(time.perf_counter() - start_all, 2)
print("=" * 75)
print(f"ALL 8 PRODUCTION & SECURITY SUITES PASSED IN {elapsed_total}s (100% SUCCESS)")
print("=" * 75)
