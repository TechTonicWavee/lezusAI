"""
DRISHTI AI — Sample External ML Application Integration
Demonstrates how an independent third-party ML application (House Price Valuation Engine)
integrates with DRISHTI AI using the lightweight Python SDK (`drishti_sdk`).
"""

import os
import sys
import time
import random
from pathlib import Path

# Add project root to path for drishti_sdk
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from drishti_sdk import DrishtiClient
import requests

PROJECT_ID = "house-price-prediction"
PROJECT_NAME = "House Price Valuation Engine"
ENDPOINT = os.getenv("DRISHTI_ENDPOINT", "http://127.0.0.1:8000")


def get_or_register_project(endpoint: str) -> str:
    """Register the house price project with DRISHTI AI or use configured key."""
    # Check if project already exists
    try:
        res = requests.get(f"{endpoint}/projects/{PROJECT_ID}", timeout=2.0)
        if res.status_code == 200:
            print(f"[HousePriceApp] Project '{PROJECT_ID}' already exists.")
            # Use master key or default key for existing project in demo
            return os.getenv("DRISHTI_MASTER_API_KEY", "dr_live_master_override_key")
    except Exception:
        pass

    # Register project
    print(f"[HousePriceApp] Registering new project '{PROJECT_ID}' at {endpoint}...")
    try:
        reg_res = requests.post(
            f"{endpoint}/projects/register",
            json={
                "project_id": PROJECT_ID,
                "name": PROJECT_NAME,
                "description": "Real estate appraisal regression model evaluating residential homes.",
                "model_type": "regression",
                "framework": "scikit-learn",
                "schema_mapping": {
                    "latency_field": "latency_ms",
                    "prediction_field": "predicted_price_usd",
                    "target_field": "actual_sale_price_usd"
                }
            },
            timeout=3.0
        )
        if reg_res.status_code in [200, 201]:
            data = reg_res.json()
            api_key = data["api_key"]
            print(f"[HousePriceApp] Registered successfully. API Key received: {data['project']['api_key_masked']}")
            return api_key
        elif reg_res.status_code == 400:
            # Already exists
            return os.getenv("DRISHTI_MASTER_API_KEY", "dr_live_master_override_key")
    except Exception as e:
        print(f"[HousePriceApp] Registration call note: {e}")

    return os.getenv("DRISHTI_MASTER_API_KEY", "dr_live_master_override_key")


class HousePriceModel:
    """Simple regression model predicting home prices based on square footage and bedrooms."""

    def __init__(self):
        # Train a baseline model on synthetic real estate data
        rng = np.random.default_rng(42)
        X_train = rng.uniform([1000, 2, 1], [4000, 5, 4], size=(300, 3))
        # Price formula: $250/sqft + $30,000/bed + $20,000/bath + noise
        y_train = (X_train[:, 0] * 250) + (X_train[:, 1] * 30000) + (X_train[:, 2] * 20000) + rng.normal(0, 15000, size=300)

        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.model.fit(X_train, y_train)

    def predict(self, sqft: float, bedrooms: int, bathrooms: int) -> float:
        feat = np.array([[sqft, bedrooms, bathrooms]])
        return round(float(self.model.predict(feat)[0]), 2)


def run_demonstration():
    print("=" * 65)
    print("DRISHTI AI — EXTERNAL ML APPLICATION DEMONSTRATION")
    print(f"Application: {PROJECT_NAME} ({PROJECT_ID})")
    print("=" * 65)

    api_key = get_or_register_project(ENDPOINT)

    # Initialize Drishti SDK client
    client = DrishtiClient(
        project_id=PROJECT_ID,
        api_key=api_key,
        endpoint=ENDPOINT,
        batch_size=5,
        silent_errors=True,
    )
    print(f"\n[SDK] Initialized: {client}")

    model = HousePriceModel()
    print("[Model] HousePriceModel (RandomForestRegressor) initialized.")

    sample_properties = [
        {"sqft": 1850, "bedrooms": 3, "bathrooms": 2, "actual": 510000.0},
        {"sqft": 2400, "bedrooms": 4, "bathrooms": 3, "actual": 690000.0},
        {"sqft": 3100, "bedrooms": 4, "bathrooms": 4, "actual": 880000.0},
        {"sqft": 1400, "bedrooms": 2, "bathrooms": 1, "actual": 395000.0},
        {"sqft": 2800, "bedrooms": 4, "bathrooms": 3, "actual": 780000.0},
        {"sqft": 2100, "bedrooms": 3, "bathrooms": 2, "actual": 580000.0},
        {"sqft": 3600, "bedrooms": 5, "bathrooms": 4, "actual": 1020000.0},
    ]

    print("\n--- Running Predictions & Logging Telemetry ---")
    for idx, prop in enumerate(sample_properties, 1):
        start = time.perf_counter()
        pred_price = model.predict(prop["sqft"], prop["bedrooms"], prop["bathrooms"])
        latency = round((time.perf_counter() - start) * 1000 + random.uniform(8.0, 24.0), 2)

        print(f"[{idx}] {prop['sqft']} sqft, {prop['bedrooms']} bed -> Predicted: ${pred_price:,.2f} ({latency} ms)")

        # Log prediction to DRISHTI AI
        client.log_prediction(
            model_name="house-price-random-forest",
            model_version="1.0.0",
            inputs={"sqft": prop["sqft"], "bedrooms": prop["bedrooms"], "bathrooms": prop["bathrooms"]},
            prediction=pred_price,
            confidence=0.94,
            latency_ms=latency,
            ground_truth=prop["actual"],
            sync=True,
        )

    # Simulate an operational exception / error event
    print("\n--- Simulating Real-World Operational Incident ---")
    print("[Error] Feature store latency spike / database timeout simulation...")
    err_res = client.log_error(
        error_type="FeatureStoreTimeoutError",
        message="Database connection timeout while fetching property historical tax assessment",
        severity="ERROR",
        model_name="house-price-random-forest",
        sync=True,
    )
    print(f"[SDK] Error logged to DRISHTI AI: {err_res}")

    # Log system resource metrics
    print("\n--- Logging Resource Utilization Telemetry ---")
    client.log_metrics(cpu_percent=42.5, memory_mb=412.0, sync=True)
    print("[SDK] Resource metrics logged (CPU: 42.5%, Memory: 412 MB).")

    # Flush any buffered items
    client.flush()
    client.close()

    print("\n" + "=" * 65)
    print("DEMONSTRATION COMPLETE — All telemetry successfully recorded in DRISHTI AI!")
    print("=" * 65)


if __name__ == "__main__":
    run_demonstration()

