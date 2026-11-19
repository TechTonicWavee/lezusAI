import os
import sys
from pathlib import Path

import mlflow

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
LOCAL_DB_PATH = (ROOT_DIR / "mlflow.db").as_posix()
DEFAULT_LOCAL_URI = f"sqlite:///{LOCAL_DB_PATH}"

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", DEFAULT_LOCAL_URI)
MODEL_NAME = os.getenv("MODEL_NAME", "taxi_fare_predictor")
RETRAIN_THRESHOLD = float(os.getenv("RETRAIN_RMSE_THRESHOLD", "0.05"))


def promote_model():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = mlflow.tracking.MlflowClient()

    print("Checking model versions in MLflow Registry...")
    staging_versions = client.get_latest_versions(MODEL_NAME, stages=["Staging"])
    prod_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])

    if not staging_versions and not prod_versions:
        all_versions = client.get_latest_versions(MODEL_NAME)
        if all_versions:
            target = all_versions[0]
            client.transition_model_version_stage(
                name=MODEL_NAME,
                version=target.version,
                stage="Production",
            )
            print(f"Model {MODEL_NAME} v{target.version} promoted to Production")
            return {"promoted": True, "version": target.version, "stage": "Production"}
        else:
            print("No model versions found in registry.")
            return {"promoted": False, "reason": "No model versions found"}

    if staging_versions and not prod_versions:
        target = staging_versions[0]
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=target.version,
            stage="Production",
        )
        print(f"Model {MODEL_NAME} v{target.version} promoted from Staging to Production")
        return {"promoted": True, "version": target.version, "stage": "Production"}

    if staging_versions and prod_versions:
        target = staging_versions[0]
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=target.version,
            stage="Production",
        )
        print(f"Model {MODEL_NAME} v{target.version} promoted to Production")
        return {"promoted": True, "version": target.version, "stage": "Production"}

    return {"promoted": False, "reason": "Production model already active"}


if __name__ == "__main__":
    result = promote_model()
    print("Promotion result:", result)
