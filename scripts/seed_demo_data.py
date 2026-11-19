"""
Seeds the 'House Price Valuation Engine' project with realistic telemetry,
ground truth actuals, and simulated error incidents for live dashboard viewing.
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

PROJECT_ID = "house-price-prediction"
PROJECT_NAME = "House Price Valuation Engine"

print(f"[*] Checking/Registering project: {PROJECT_NAME} ({PROJECT_ID})")
projects = load_projects()
existing = [p for p in projects if p["project_id"] == PROJECT_ID]

if not existing:
    proj_dict, raw_key = register_project(
        project_id=PROJECT_ID,
        name=PROJECT_NAME,
        description="Real estate appraisal regression model evaluating residential homes.",
        model_type="regression",
        framework="scikit-learn",
        schema_mapping={
            "latency_field": "latency_ms",
            "prediction_field": "predicted_price_usd",
            "target_field": "actual_sale_price_usd",
        },
    )
    print(f"[+] Project registered. Key prefix: {proj_dict['api_key_masked']}")
else:
    print(f"[+] Project already exists: {existing[0]['name']}")

# Sample realistic property valuations
properties = [
    {"sqft": 1850, "bedrooms": 3, "bathrooms": 2, "pred": 512400.0, "actual": 510000.0, "lat": 14.2, "conf": 0.95},
    {"sqft": 2400, "bedrooms": 4, "bathrooms": 3, "pred": 688500.0, "actual": 690000.0, "lat": 18.5, "conf": 0.94},
    {"sqft": 3100, "bedrooms": 4, "bathrooms": 4, "pred": 875000.0, "actual": 880000.0, "lat": 22.1, "conf": 0.93},
    {"sqft": 1400, "bedrooms": 2, "bathrooms": 1, "pred": 399000.0, "actual": 395000.0, "lat": 12.0, "conf": 0.96},
    {"sqft": 2800, "bedrooms": 4, "bathrooms": 3, "pred": 776000.0, "actual": 780000.0, "lat": 16.8, "conf": 0.92},
    {"sqft": 2100, "bedrooms": 3, "bathrooms": 2, "pred": 584000.0, "actual": 580000.0, "lat": 15.3, "conf": 0.94},
    {"sqft": 3600, "bedrooms": 5, "bathrooms": 4, "pred": 1015000.0, "actual": 1020000.0, "lat": 26.4, "conf": 0.91},
]

print(f"[*] Ingesting {len(properties)} normal prediction events with ground truth...")
for i, p in enumerate(properties, 1):
    res = ingest_telemetry_event(
        project_id=PROJECT_ID,
        record={
            "event_type": "PREDICTION",
            "model_name": "house-price-random-forest",
            "model_version": "1.0.0",
            "inputs": {"sqft": p["sqft"], "bedrooms": p["bedrooms"], "bathrooms": p["bathrooms"]},
            "prediction": p["pred"],
            "confidence": p["conf"],
            "latency_ms": p["lat"],
            "ground_truth": p["actual"],
            "log_message": f"Valuation computed for {p['sqft']} sqft home -> ${p['pred']:,.2f}",
            "severity": "INFO",
        }
    )
    print(f"  [{i}/{len(properties)}] Logged prediction for ${p['pred']:,.2f} (latency: {p['lat']}ms, ground_truth: ${p['actual']:,.2f})")

print("[*] Ingesting simulated operational error incident (FeatureStoreTimeoutError)...")
err_res = ingest_telemetry_event(
    project_id=PROJECT_ID,
    record={
        "event_type": "ERROR",
        "model_name": "house-price-random-forest",
        "model_version": "1.0.0",
        "error_type": "FeatureStoreTimeoutError",
        "error_message": "Database connection timeout while fetching property historical tax assessment",
        "severity": "ERROR",
        "latency_ms": 3200.0,
    }
)
alert = err_res.get("alert")
if alert:
    print(f"[+] Incident triggered & recorded! ID: {alert['id']} | Status: {alert['status']}")
else:
    print(f"[+] Error recorded: {err_res}")

# Verify drift stats
drift = get_project_drift_and_accuracy(PROJECT_ID)
print("\n[+] Verification of Ground Truth & Accuracy Drift:")
print(f"    Total Ground-Truth Samples: {drift.get('ground_truth_samples')}")
print(f"    Mean Absolute Error (MAE):  ${drift.get('mae', 0):,.2f}")
print(f"    Root Mean Sq Error (RMSE):  ${drift.get('rmse', 0):,.2f}")
print(f"    Mean Prediction Latency:    {drift.get('mean_latency_ms', 0):.2f} ms")

incidents = get_alerts(project_id=PROJECT_ID)
print(f"\n[+] Total Incidents for '{PROJECT_ID}': {len(incidents)}")
for inc in incidents:
    print(f"    - [{inc.get('status')}] {inc.get('id')}: {inc.get('message')}")
print("\n[SUCCESS] Demo data successfully seeded!")
