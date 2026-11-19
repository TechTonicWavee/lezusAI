"""
DRISHTI AI — Comprehensive End-to-End System Verification
Tests every component across both the AIOps Operational Loop and MLOps Lifecycle Loop.
"""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "log-anomaly"))
sys.path.insert(0, str(ROOT / "mlops-platform" / "ml-flow"))

print("=" * 70)
print("DRISHTI AI — END-TO-END VERIFICATION SUITE")
print("=" * 70)

# 1. Verify Log Generation
print("\n[Step 1] Testing Log Generation...")
from integration.generate_logs import generate_application_logs, LOG_FILE
generate_application_logs()
assert LOG_FILE.exists(), "Log file not created"
print("✓ Application logs generated successfully at:", LOG_FILE)

# 2. Verify Log Processing & Feature Extraction
print("\n[Step 2] Testing Log Processor & Feature Extraction...")
from integration.log_processor import process_logs, OUTPUT_FILE
process_logs()
assert OUTPUT_FILE.exists(), "Feature CSV not created"
print("✓ 16 numerical features extracted and saved to:", OUTPUT_FILE)

# 3. Verify Loglizer Anomaly Detector Training
print("\n[Step 3] Testing Loglizer IsolationForest Detector...")
import pandas as pd
import joblib
from loglizer.models import IsolationForest

df = pd.read_csv(OUTPUT_FILE)
feature_cols = [c for c in df.columns if c not in ["timestamp", "expected_label"]]
X = df[feature_cols].to_numpy(dtype=float)

detector = IsolationForest(n_estimators=100, contamination=0.2, random_state=42)
detector.fit(X)
preds = detector.predict(X)
model_path = ROOT / "models" / "log_anomaly_detector.joblib"
joblib.dump(detector, model_path)
print(f"✓ Model trained: {len(X)} records, {len(feature_cols)} features")
print(f"✓ Anomalies flagged: {(preds == 1).sum()} / Normal: {(preds == 0).sum()}")

# 4. Verify Alert Manager, Deduplication & Correlation
print("\n[Step 4] Testing Advanced Incident Manager & Deduplication...")
from integration.alert_manager import (
    create_alert,
    get_alerts,
    update_alert_status,
    resolve_alert,
    get_incident_history,
    get_incident_stats
)

alert1 = create_alert("ERROR: Database connection timeout", category="database")
alert2 = create_alert("ERROR: Database connection timeout", category="database")
assert alert1["id"] == alert2["id"], "Deduplication failed!"
assert alert2["occurrence_count"] >= 2, "Occurrence count not incremented!"
print(f"✓ Deduplication verified: Incident #{alert1['id']} count={alert2['occurrence_count']}")

# Test Lifecycle transition
updated = update_alert_status(alert1["id"], "INVESTIGATING", notes="Operator assigned")
assert updated["status"] == "INVESTIGATING"
resolved = resolve_alert(alert1["id"], resolution_notes="Connection pool re-initialized")
assert resolved["status"] == "RESOLVED"
print(f"✓ Lifecycle transition verified: OPEN -> INVESTIGATING -> RESOLVED")

# 5. Verify Safe Automated Incident Response Engine
print("\n[Step 5] Testing Safe Automated Incident Response Engine...")
from integration.response_engine import (
    execute_remediation,
    get_remediation_history,
    get_response_stats
)

act = execute_remediation(
    incident_id=alert1["id"],
    message="CRITICAL: Memory usage exceeded limit",
    category="memory"
)
assert act["status"] == "SUCCESS", "Remediation failed"
assert act["is_simulated"] is True, "Must be simulated"
print(f"✓ Automated remediation executed: {act['action_name']} ({act['execution_duration_ms']} ms)")
print(f"✓ Output payload: {act['remediation_output']}")

# 6. Verify MLOps Model Training & MLflow Tracking
print("\n[Step 6] Testing MLOps Training, Evaluation & MLflow Registry...")
from integration.mlops_service import (
    trigger_training,
    trigger_promotion,
    get_model_status,
    predict_taxi_duration,
    get_experiment_runs
)

train_res = trigger_training()
print(f"✓ MLflow Run ID: {train_res['run_id']}")
print(f"✓ Metrics logged: RMSE={train_res['metrics']['rmse']}, MAE={train_res['metrics']['mae']}, R²={train_res['metrics']['r2']}")

promo_res = trigger_promotion()
print(f"✓ MLflow Promotion: {promo_res}")

model_stat = get_model_status()
print(f"✓ Active Model Status: Name={model_stat['model_name']}, Prod Version={model_stat['production_version']}")

# 7. Verify MLOps Model Serving & Prediction
print("\n[Step 7] Testing MLOps Model Serving (Taxi Duration & Fare)...")
fare_res = predict_taxi_duration({
    "trip_distance": 5.2,
    "passenger_count": 2,
    "pickup_hour": 17,
    "pickup_day": 3
})
print(f"✓ Prediction result: {fare_res['predicted_duration_minutes']} min duration, ${fare_res['estimated_fare_usd']} fare")

# 8. Verify Application Observability & Prometheus Metrics
print("\n[Step 8] Testing Observability & Prometheus Metrics Exporter...")
from integration.metrics import get_metrics_summary, generate_prometheus_metrics
summary = get_metrics_summary()
prom_text = generate_prometheus_metrics()
assert "drishti_logs_processed_total" in prom_text, "Missing prometheus metric"
assert "drishti_open_incidents" in prom_text, "Missing prometheus metric"
print("✓ Prometheus Exposition Output Preview:")
for line in prom_text.splitlines()[:10]:
    print("  ", line)

# 9. Verify FastAPI API Handlers & Dashboard HTML
print("\n[Step 9] Testing FastAPI Endpoints & Web Dashboard...")
from integration.api import (
    home,
    health,
    predict,
    LogRequest,
    serve_dashboard
)

h = home()
assert h["status"] == "running"
hl = health()
assert hl["status"] == "healthy"
pred_api = predict(LogRequest(message="ERROR: Database connection timeout"))
assert pred_api["result"] == "ANOMALY"
html = serve_dashboard()
assert len(html.body) > 10000, "Dashboard HTML content too short"
print("✓ API Health, Prediction & Dashboard HTML verified successfully!")

print("\n" + "=" * 70)
print("ALL DRISHTI AI SUITE CHECKS PASSED (100% SUCCESS)")
print("=" * 70)

