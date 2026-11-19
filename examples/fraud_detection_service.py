"""
DRISHTI AI — Sample ML Application #2: Credit Card Fraud Detection Engine
Demonstrates how to integrate an independent binary classification model
with DRISHTI AI using `drishti_sdk`.
"""

import os
import sys
import time
import random
from pathlib import Path

# Add project root to path for drishti_sdk
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import requests
from drishti_sdk import DrishtiClient

PROJECT_ID = "fraud-detection-engine"
PROJECT_NAME = "Credit Card Fraud Detection Engine"
ENDPOINT = os.getenv("DRISHTI_ENDPOINT", "http://127.0.0.1:8000")


def get_or_register_project(endpoint: str) -> str:
    """Register the fraud detection project with DRISHTI AI or retrieve API key."""
    # Check if project already exists
    try:
        res = requests.get(f"{endpoint}/projects/{PROJECT_ID}", timeout=2.0)
        if res.status_code == 200:
            print(f"[FraudApp] Project '{PROJECT_ID}' already exists.")
            return os.getenv("DRISHTI_MASTER_API_KEY", "dr_live_master_override_key")
    except Exception:
        pass

    # Register project
    print(f"[FraudApp] Registering new project '{PROJECT_ID}' at {endpoint}...")
    try:
        reg_res = requests.post(
            f"{endpoint}/projects/register",
            json={
                "project_id": PROJECT_ID,
                "name": PROJECT_NAME,
                "description": "Real-time payment transaction risk scoring and fraud classification.",
                "model_type": "binary_classification",
                "framework": "scikit-learn",
                "schema_mapping": {
                    "latency_field": "latency_ms",
                    "prediction_field": "is_fraud_prediction",
                    "target_field": "actual_chargeback_status",
                },
            },
            timeout=3.0,
        )
        if reg_res.status_code in [200, 201]:
            data = reg_res.json()
            api_key = data["api_key"]
            print(f"[FraudApp] Registered successfully. API Key received: {data['project']['api_key_masked']}")
            return api_key
    except Exception as e:
        print(f"[FraudApp] Registration note: {e}")

    return os.getenv("DRISHTI_MASTER_API_KEY", "dr_live_master_override_key")


class FraudRiskClassifier:
    """Mock payment risk evaluation model."""

    def evaluate_transaction(self, amount: float, foreign_country: bool, midnight_hour: bool) -> tuple[int, float]:
        # High risk if high amount + foreign + midnight
        risk_score = 0.05
        if foreign_country:
            risk_score += 0.40
        if midnight_hour:
            risk_score += 0.25
        if amount > 1000.0:
            risk_score += 0.25

        risk_score = min(0.99, risk_score + random.uniform(-0.02, 0.02))
        is_fraud = 1 if risk_score >= 0.50 else 0
        return is_fraud, round(risk_score, 4)


def run_demonstration():
    print("=" * 70)
    print("DRISHTI AI — INTEGRATING SECOND ML APPLICATION")
    print(f"Application: {PROJECT_NAME} ({PROJECT_ID})")
    print("=" * 70)

    # 1. Register and get API key
    api_key = get_or_register_project(ENDPOINT)

    # 2. Initialize Drishti SDK client
    client = DrishtiClient(
        project_id=PROJECT_ID,
        api_key=api_key,
        endpoint=ENDPOINT,
        batch_size=5,
        silent_errors=True,
    )
    print(f"\n[SDK] Initialized client: {client}")

    classifier = FraudRiskClassifier()

    transactions = [
        {"tx_id": "tx_901", "amount": 42.50, "foreign": False, "midnight": False, "actual_chargeback": 0},
        {"tx_id": "tx_902", "amount": 115.00, "foreign": False, "midnight": False, "actual_chargeback": 0},
        {"tx_id": "tx_903", "amount": 890.00, "foreign": True, "midnight": False, "actual_chargeback": 0},
        {"tx_id": "tx_904", "amount": 2500.00, "foreign": True, "midnight": True, "actual_chargeback": 1},
        {"tx_id": "tx_905", "amount": 15.20, "foreign": False, "midnight": False, "actual_chargeback": 0},
        {"tx_id": "tx_906", "amount": 3400.00, "foreign": True, "midnight": True, "actual_chargeback": 1},
    ]

    print("\n--- Phase 1: Logging Real-Time Inferences & Telemetry ---")
    for idx, tx in enumerate(transactions, 1):
        start = time.perf_counter()
        is_fraud, risk_score = classifier.evaluate_transaction(tx["amount"], tx["foreign"], tx["midnight"])
        latency = round((time.perf_counter() - start) * 1000 + random.uniform(5.0, 15.0), 2)

        verdict = "FRAUD RISK" if is_fraud else "LEGITIMATE"
        print(f"[{idx}] Tx #{tx['tx_id']}: ${tx['amount']:.2f} -> {verdict} (Risk: {risk_score*100:.1f}%, Latency: {latency}ms)")

        # Log to DRISHTI AI
        client.log_prediction(
            model_name="fraud-risk-lightgbm",
            model_version="2.1.0",
            inputs={"amount": tx["amount"], "foreign": tx["foreign"], "midnight": tx["midnight"]},
            prediction=is_fraud,
            confidence=risk_score if is_fraud else round(1.0 - risk_score, 4),
            latency_ms=latency,
            ground_truth=tx["actual_chargeback"],
            custom_tags={"tx_id": tx["tx_id"]},
            sync=True,
        )

    print("\n--- Phase 2: Simulating Real-World Operational Incident ---")
    print("[Error] Redis cache cluster unreachable during blacklist lookup...")
    err_res = client.log_error(
        error_type="RedisCacheConnectionTimeout",
        message="Redis cluster timeout on node redis-cluster-02:6379 after 2500ms",
        severity="ERROR",
        model_name="fraud-risk-lightgbm",
        custom_tags={"subsystem": "cache_layer", "cluster": "eu-west-1"},
        sync=True,
    )
    print(f"[SDK] Operational Error Logged: {err_res}")

    print("\n--- Phase 3: Logging System Resource Telemetry ---")
    client.log_metrics(cpu_percent=58.2, memory_mb=680.0, sync=True)
    print("[SDK] Resource telemetry logged (CPU: 58.2%, Memory: 680 MB)")

    client.flush()
    client.close()

    print("\n" + "=" * 70)
    print(f"INTEGRATION DEMONSTRATION COMPLETE for '{PROJECT_ID}'!")
    print("Now open http://127.0.0.1:8000/dashboard to inspect live telemetry and incidents.")
    print("=" * 70)


if __name__ == "__main__":
    run_demonstration()

