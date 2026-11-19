"""
Tests for Prometheus Metrics Exposition and Increment Accuracy.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from integration.metrics import (
    record_log_prediction,
    record_batch_logs,
    record_prediction_error,
    get_metrics_summary,
    generate_prometheus_metrics,
)


def run_tests():
    print("--- [Test Suite 4: Prometheus Metrics Engine] ---")

    test_pid = "metric-test-model"

    before = get_metrics_summary()
    initial_logs = before["total_logs_processed"]
    initial_anomalies = before["total_anomalies_detected"]

    # 1. Record Normal Prediction
    record_log_prediction(is_anomaly=False, latency_ms=25.0, project_id=test_pid)
    after_1 = get_metrics_summary()
    assert after_1["total_logs_processed"] == initial_logs + 1, "Log counter did not increment"
    assert after_1["total_anomalies_detected"] == initial_anomalies, "Anomaly counter falsely incremented"
    print("✓ Normal prediction metric increment verified")

    # 2. Record Anomaly Prediction
    record_log_prediction(is_anomaly=True, latency_ms=85.0, project_id=test_pid)
    after_2 = get_metrics_summary()
    assert after_2["total_anomalies_detected"] == initial_anomalies + 1, "Anomaly counter did not increment"
    print("✓ Anomaly metric increment verified")

    # 3. Record Batch Events
    record_batch_logs(total_logs=10, anomalies=2, project_id=test_pid, avg_latency_ms=45.0)
    after_3 = get_metrics_summary()
    assert after_3["total_logs_processed"] == initial_logs + 12
    assert after_3["total_anomalies_detected"] == initial_anomalies + 3
    print("✓ Batch log metric updates verified")

    # 4. Record Prediction Error
    record_prediction_error(project_id=test_pid)
    after_4 = get_metrics_summary()
    assert after_4["prediction_errors_total"] >= 1
    print("✓ Error counter metric update verified")

    # 5. Verify Prometheus Exposition Format
    prom_text = generate_prometheus_metrics()
    assert "# HELP drishti_logs_processed_total" in prom_text
    assert "# TYPE drishti_logs_processed_total counter" in prom_text
    assert "# HELP drishti_anomalies_detected_total" in prom_text
    assert "# HELP drishti_prediction_latency_ms" in prom_text
    assert f'drishti_project_telemetry_total{{project_id="{test_pid}"}}' in prom_text
    assert f'drishti_project_anomalies_total{{project_id="{test_pid}"}}' in prom_text
    print("✓ Standard Prometheus format (v0.0.4) and project labels verified")

    print("✓ Prometheus metrics verified. Suite 4 Passed!\n")


if __name__ == "__main__":
    run_tests()

