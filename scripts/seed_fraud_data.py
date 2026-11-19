"""
Seed script for Credit Card Fraud Detection Engine.
Populates data/projects.json, data/telemetry/fraud-detection-engine.jsonl,
and alerts/incidents.json with realistic fraud model telemetry.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
if str(ROOT / "log-anomaly") not in sys.path:
    sys.path.insert(0, str(ROOT / "log-anomaly"))
if str(ROOT / "mlops-platform" / "ml-flow") not in sys.path:
    sys.path.insert(0, str(ROOT / "mlops-platform" / "ml-flow"))

from integration.project_manager import register_project, load_projects
from integration.telemetry_service import ingest_telemetry_event, get_project_drift_and_accuracy
from integration.alert_manager import get_alerts

PROJECT_ID = "fraud-detection-engine"
PROJECT_NAME = "Credit Card Fraud Detection Engine"

print(f"[*] Registering/Checking project: {PROJECT_NAME} ({PROJECT_ID})")
projects = load_projects()
existing = [p for p in projects if p["project_id"] == PROJECT_ID]

if not existing:
    proj_dict, raw_key = register_project(
        project_id=PROJECT_ID,
        name=PROJECT_NAME,
        description="Real-time payment transaction risk scoring and fraud classification.",
        model_type="binary_classification",
        framework="scikit-learn",
        schema_mapping={
            "latency_field": "latency_ms",
            "prediction_field": "is_fraud_prediction",
            "target_field": "actual_chargeback_status",
        },
    )
    print(f"[+] Project registered. Key prefix: {proj_dict['api_key_masked']}")
else:
    print(f"[+] Project already exists: {existing[0]['name']}")

transactions = [
    {"tx_id": "tx_901", "amount": 42.50, "foreign": False, "midnight": False, "pred": 0, "conf": 0.96, "actual": 0, "lat": 8.5},
    {"tx_id": "tx_902", "amount": 115.00, "foreign": False, "midnight": False, "pred": 0, "conf": 0.94, "actual": 0, "lat": 11.2},
    {"tx_id": "tx_903", "amount": 890.00, "foreign": True, "midnight": False, "pred": 0, "conf": 0.72, "actual": 0, "lat": 14.8},
    {"tx_id": "tx_904", "amount": 2500.00, "foreign": True, "midnight": True, "pred": 1, "conf": 0.98, "actual": 1, "lat": 19.3},
    {"tx_id": "tx_905", "amount": 15.20, "foreign": False, "midnight": False, "pred": 0, "conf": 0.99, "actual": 0, "lat": 6.8},
    {"tx_id": "tx_906", "amount": 3400.00, "foreign": True, "midnight": True, "pred": 1, "conf": 0.97, "actual": 1, "lat": 24.1},
]

print(f"[*] Ingesting {len(transactions)} transaction telemetry events...")
for i, tx in enumerate(transactions, 1):
    verdict = "FRAUD" if tx["pred"] == 1 else "LEGITIMATE"
    res = ingest_telemetry_event(
        project_id=PROJECT_ID,
        record={
            "event_type": "PREDICTION",
            "model_name": "fraud-risk-lightgbm",
            "model_version": "2.1.0",
            "inputs": {"amount": tx["amount"], "foreign": tx["foreign"], "midnight": tx["midnight"]},
            "prediction": tx["pred"],
            "confidence": tx["conf"],
            "latency_ms": tx["lat"],
            "ground_truth": tx["actual"],
            "log_message": f"Payment risk evaluated for Tx {tx['tx_id']}: ${tx['amount']:.2f} -> {verdict}",
            "severity": "INFO",
            "custom_tags": {"tx_id": tx["tx_id"]},
        }
    )
    print(f"  [{i}/{len(transactions)}] Ingested Tx {tx['tx_id']} (${tx['amount']:.2f}) -> {verdict}")

print("[*] Ingesting simulated operational error incident (RedisCacheConnectionTimeout)...")
err_res = ingest_telemetry_event(
    project_id=PROJECT_ID,
    record={
        "event_type": "ERROR",
        "model_name": "fraud-risk-lightgbm",
        "model_version": "2.1.0",
        "error_type": "RedisCacheConnectionTimeout",
        "error_message": "Redis cluster timeout on node redis-cluster-02:6379 after 2500ms",
        "severity": "ERROR",
        "latency_ms": 2500.0,
    }
)
alert = err_res.get("alert")
if alert:
    print(f"[+] Incident recorded! ID: {alert['id']} | Status: {alert['status']}")

# Verify drift stats
drift = get_project_drift_and_accuracy(PROJECT_ID)
print("\n[+] Verification of Accuracy & Drift:")
print(f"    Total Verified Transactions: {drift.get('sample_size')}")
print(f"    Mean Absolute Error (MAE):   {drift.get('mae', 0):.4f}")
print(f"    Root Mean Sq Error (RMSE):   {drift.get('rmse', 0):.4f}")
print(f"    Evaluation Status:          {drift.get('status')}")

incidents = get_alerts(project_id=PROJECT_ID)
print(f"\n[+] Total Incidents for '{PROJECT_ID}': {len(incidents)}")
for inc in incidents:
    print(f"    - [{inc.get('status')}] {inc.get('id')}: {inc.get('message')}")
print("\n[SUCCESS] Fraud Detection Engine demo data ready!")

