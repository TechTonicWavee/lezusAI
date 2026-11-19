import sys
from pathlib import Path

import pandas as pd
import joblib

# Project paths
ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "log-anomaly"))

from loglizer.models import IsolationForest

# Load processed log data
data_path = ROOT / "logs" / "log_features.csv"
df = pd.read_csv(data_path)

# Exclude timestamp and expected_label from model training
feature_columns = [
    col for col in df.columns
    if col not in ["timestamp", "expected_label"]
]

X = df[feature_columns].to_numpy(dtype=float)

# Initialize and train Loglizer Isolation Forest
detector = IsolationForest(
    n_estimators=100,
    contamination=0.2,
    random_state=42
)

detector.fit(X)

# Detect anomalies
predictions = detector.predict(X)

# Convert predictions: -1 = anomaly, 1 = normal
df["predicted_anomaly"] = (predictions == 1).astype(int)

# Save trained model and detection results
model_dir = ROOT / "models"
model_dir.mkdir(exist_ok=True)

joblib.dump(
    detector,
    model_dir / "log_anomaly_detector.joblib"
)

results_path = ROOT / "logs" / "anomaly_results.csv"
df.to_csv(results_path, index=False)

try:
    from integration.metrics import record_batch_logs
    anomalies_count = int(df['predicted_anomaly'].sum())
    record_batch_logs(
        total_logs=len(df),
        anomalies=anomalies_count,
        project_id="system_logs"
    )
except Exception:
    pass

# Display results
print("\n========== DRISHTI ANOMALY DETECTOR ==========")
print(f"Total logs analyzed: {len(df)}")
print(f"Features used: {len(feature_columns)}")
print(f"Anomalies detected: {df['predicted_anomaly'].sum()}")
print(f"Normal logs: {(df['predicted_anomaly'] == 0).sum()}")
print(f"Expected anomalies (demo labels): {df['expected_label'].sum()}")

print("\nSample detection results:")
print(
    df[["timestamp", "expected_label", "predicted_anomaly"]]
    .head(10)
    .to_string(index=False)
)

print("\nModel saved:", model_dir / "log_anomaly_detector.joblib")
print("Results saved:", results_path)
print("\nAnomaly detection completed!")