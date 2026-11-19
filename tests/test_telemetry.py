"""
Tests for Universal Telemetry Ingestion, Project Isolation, and Drift Calculation.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from integration.telemetry_service import (
    ingest_telemetry_event,
    ingest_batch_telemetry,
    get_project_telemetry,
    get_project_drift_and_accuracy,
    normalize_to_feature_vector,
)


def run_tests():
    print("--- [Test Suite 2: Telemetry & Project Isolation] ---")

    proj_a = "test-project-alpha"
    proj_b = "test-project-beta"

    # 1. Feature normalization test
    raw_event = {
        "event_type": "prediction",
        "latency_ms": 120.5,
        "log_message": "Prediction request completed",
        "severity": "INFO",
    }
    vec = normalize_to_feature_vector(raw_event)
    assert len(vec) == 16, f"Expected 16 dimensions, got {len(vec)}"
    assert vec[0] == 1, "severity_INFO should be 1"
    print("✓ 16-feature space normalization verified")

    # 2. Ingest into Project Alpha
    res1 = ingest_telemetry_event(
        project_id=proj_a,
        record={
            "model_name": "alpha-classifier",
            "prediction": 1,
            "confidence": 0.98,
            "latency_ms": 32.0,
            "ground_truth": 1,
        }
    )
    assert res1["status"] == "success"
    assert res1["project_id"] == proj_a
    print("✓ Single telemetry ingestion verified")

    # 3. Batch Ingest into Project Alpha
    batch_records = [
        {"model_name": "alpha-classifier", "prediction": 0, "ground_truth": 0, "latency_ms": 28.0},
        {"model_name": "alpha-classifier", "prediction": 1, "ground_truth": 1, "latency_ms": 35.0},
        {"model_name": "alpha-classifier", "prediction": 1, "ground_truth": 0, "latency_ms": 42.0},
    ]
    batch_res = ingest_batch_telemetry(project_id=proj_a, records=batch_records)
    assert batch_res["successful"] == 3
    print("✓ Batch telemetry ingestion verified")

    # 4. Ingest into Project Beta
    res_b = ingest_telemetry_event(
        project_id=proj_b,
        record={
            "model_name": "beta-regressor",
            "prediction": 450.0,
            "ground_truth": 440.0,
            "latency_ms": 55.0,
        }
    )
    assert res_b["project_id"] == proj_b

    # 5. Verify Project Data Isolation
    telemetry_a = get_project_telemetry(proj_a)
    telemetry_b = get_project_telemetry(proj_b)

    # Project A must not contain Project B's records
    pids_in_a = set(t["project_id"] for t in telemetry_a)
    pids_in_b = set(t["project_id"] for t in telemetry_b)

    assert pids_in_a == {proj_a}, f"Project isolation breach in Alpha: {pids_in_a}"
    assert pids_in_b == {proj_b}, f"Project isolation breach in Beta: {pids_in_b}"
    print("✓ Project-level data isolation verified (Zero cross-project leakage)")

    # 6. Verify Drift and Accuracy Calculation
    drift = get_project_drift_and_accuracy(proj_a)
    assert drift["evaluation_available"] is True
    assert drift["sample_size"] >= 4
    assert drift["mae"] is not None
    print(f"✓ Drift & ground-truth accuracy verified (MAE={drift['mae']}, Samples={drift['sample_size']})")

    # Cleanup test files
    f_a = ROOT / "data" / "telemetry" / f"{proj_a}.jsonl"
    f_b = ROOT / "data" / "telemetry" / f"{proj_b}.jsonl"
    if f_a.exists():
        f_a.unlink()
    if f_b.exists():
        f_b.unlink()
    print("✓ Cleaned up telemetry test partitions. Suite 2 Passed!\n")


if __name__ == "__main__":
    run_tests()

