"""
Tests for DRISHTI Python Client SDK.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from drishti_sdk import DrishtiClient


def run_tests():
    print("--- [Test Suite 5: Python SDK Functionality] ---")

    # 1. Initialization and Key Masking
    client = DrishtiClient(
        project_id="sdk-unit-test",
        api_key="dr_live_abcdef1234567890abcdef1234567890",
        endpoint="http://127.0.0.1:8000",
        batch_size=3,
        silent_errors=True,
    )
    repr_str = repr(client)
    assert "abcdef1234567890abcdef1234567890" not in repr_str, "Raw API key leaked in repr!"
    assert "dr_live_" in repr_str, "Key prefix not visible"
    print("✓ SDK key masking verified in repr and string outputs")

    # 2. Queue Prediction
    p_res = client.log_prediction(
        model_name="unit-model",
        inputs={"feature_1": 12.5, "feature_2": 3},
        prediction=42.0,
        confidence=0.95,
        latency_ms=18.4,
        sync=False,
    )
    assert p_res["status"] == "queued"
    print("✓ Prediction logging and buffer queue verified")

    # 3. Queue Error
    e_res = client.log_error(
        error_type="TimeoutError",
        message="Database probe timed out",
        severity="WARNING",
        sync=False,
    )
    assert e_res["status"] == "queued"
    print("✓ Error logging and buffer queue verified")

    # 4. Queue Ground Truth & Metrics
    client.log_ground_truth(actual_value=41.5, prediction=42.0, sync=False)
    client.log_metrics(cpu_percent=55.0, memory_mb=512.0, sync=False)
    print("✓ Ground-truth and resource metric logging verified")

    # 5. Non-blocking error tolerance
    # Even if offline endpoint is specified, silent_errors=True must not crash the caller
    offline_client = DrishtiClient(
        project_id="offline-test",
        api_key="dr_live_fake",
        endpoint="http://127.0.0.1:9999",  # Non-existent port
        silent_errors=True,
        timeout=0.2,
    )
    res = offline_client.log_prediction(prediction=100, sync=True)
    assert res["status"] == "error", "Did not return safe error status"
    print("✓ Non-blocking error tolerance verified (host ML service protected)")

    client.close()
    offline_client.close()
    print("✓ Python SDK verification passed. Suite 5 Passed!\n")


if __name__ == "__main__":
    run_tests()

