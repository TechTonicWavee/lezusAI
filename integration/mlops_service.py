"""
DRISHTI AI - MLOps Lifecycle Service
Integrates mlops-platform (MLflow, Scikit-learn, Model Registry, and Serving)
with the DRISHTI AI API and dashboard.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import joblib

ROOT = Path(__file__).resolve().parent.parent
MLFLOW_SRC = ROOT / "mlops-platform" / "ml-flow"

if str(MLFLOW_SRC) not in sys.path:
    sys.path.insert(0, str(MLFLOW_SRC))

import mlflow
from mlflow.tracking import MlflowClient

LOCAL_DB_PATH = (ROOT / "mlflow.db").as_posix()
DEFAULT_LOCAL_URI = f"sqlite:///{LOCAL_DB_PATH}"
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", DEFAULT_LOCAL_URI)
EXPERIMENT_NAME = "taxi_fare_prediction"
MODEL_NAME = "taxi_fare_predictor"


def get_mlflow_client() -> MlflowClient:
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    return MlflowClient()


def get_experiment_runs(limit: int = 10) -> List[Dict[str, Any]]:
    """List recent experiment runs with parameters and metrics."""
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        client = get_mlflow_client()
        experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
        if not experiment:
            return []

        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            max_results=limit,
            order_by=["start_time DESC"],
        )

        formatted_runs = []
        for r in runs:
            formatted_runs.append({
                "run_id": r.info.run_id,
                "run_name": r.info.run_name or "run",
                "status": r.info.status,
                "start_time": r.info.start_time,
                "end_time": r.info.end_time,
                "metrics": {k: round(v, 4) for k, v in r.data.metrics.items()},
                "params": r.data.params,
            })
        return formatted_runs
    except Exception as e:
        print(f"Error fetching MLflow runs: {e}")
        return []


def get_model_status() -> Dict[str, Any]:
    """Retrieve current registered model versions and staging/production statuses."""
    try:
        client = get_mlflow_client()
        versions = client.search_model_versions(f"name='{MODEL_NAME}'")
        version_list = []
        for v in versions:
            version_list.append({
                "version": v.version,
                "stage": getattr(v, "current_stage", "None"),
                "run_id": v.run_id,
                "status": v.status,
                "created_at": getattr(v, "creation_timestamp", None),
            })

        prod_versions = [v for v in version_list if v["stage"] == "Production"]
        staging_versions = [v for v in version_list if v["stage"] == "Staging"]

        return {
            "model_name": MODEL_NAME,
            "registered_versions": version_list,
            "total_versions": len(version_list),
            "production_version": prod_versions[0]["version"] if prod_versions else None,
            "staging_version": staging_versions[0]["version"] if staging_versions else None,
            "tracking_uri": MLFLOW_TRACKING_URI,
        }
    except Exception as e:
        return {
            "model_name": MODEL_NAME,
            "error": str(e),
            "total_versions": 0,
            "production_version": None,
        }


def trigger_training(params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute training pipeline."""
    from src.train import train
    run_id, rmse, mae, r2 = train(params)
    return {
        "status": "success",
        "run_id": run_id,
        "metrics": {"rmse": round(rmse, 4), "mae": round(mae, 4), "r2": round(r2, 4)},
    }


def trigger_promotion() -> Dict[str, Any]:
    """Promote latest staging model to Production."""
    from src.promote_model import promote_model
    return promote_model()


def predict_taxi_duration(trip_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run inference using the promoted production model and preprocessor.
    """
    prep_path = ROOT / "mlops-platform" / "serving" / "preprocessor" / "preprocessor.joblib"
    if not prep_path.exists():
        prep_path = ROOT / "mlops-platform" / "ml-flow" / "data" / "processed" / "preprocessor.joblib"

    if not prep_path.exists():
        raise FileNotFoundError("Preprocessor artifact not found. Please train model first.")

    preprocessor = joblib.load(prep_path)

    # Load local production model or MLflow model
    local_model_path = ROOT / "models" / "taxi_fare_predictor.joblib"
    if not local_model_path.exists():
        raise FileNotFoundError("Model artifact not found. Please train model first.")

    model = joblib.load(local_model_path)

    # Format into DataFrame
    default_record = {
        "passenger_count": 1,
        "trip_distance": 2.5,
        "pickup_hour": 14,
        "pickup_day": 2,
        "pickup_month": 6,
        "PULocationID": 100,
        "DOLocationID": 200,
        "rate_code": 1,
    }
    default_record.update(trip_data)

    cols = [
        "passenger_count", "trip_distance", "pickup_hour", "pickup_day", "pickup_month",
        "PULocationID", "DOLocationID", "rate_code"
    ]
    df = pd.DataFrame([default_record])[cols]

    X_processed = preprocessor.transform(df)
    predicted_duration = float(model.predict(X_processed)[0])

    # Estimate fare based on duration and distance
    estimated_fare = round(2.50 + (default_record["trip_distance"] * 2.50) + (predicted_duration * 0.50), 2)

    return {
        "predicted_duration_minutes": round(predicted_duration, 2),
        "estimated_fare_usd": estimated_fare,
        "input_features": default_record,
        "model_used": MODEL_NAME,
        "status": "success",
    }

