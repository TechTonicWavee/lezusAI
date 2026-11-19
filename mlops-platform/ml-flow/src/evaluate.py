import os
import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import mlflow

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.download_data import download_taxi_data
from src.feature_engineering import preprocess_data, load_preprocessor

LOCAL_DB_PATH = (ROOT_DIR / "mlflow.db").as_posix()
DEFAULT_LOCAL_URI = f"sqlite:///{LOCAL_DB_PATH}"

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", DEFAULT_LOCAL_URI)
MODEL_NAME = os.getenv("MODEL_NAME", "taxi_fare_predictor")


def evaluate_model(model_uri: str = None):
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    _, test_df = download_taxi_data()

    prep_path = ROOT_DIR / "mlops-platform" / "serving" / "preprocessor" / "preprocessor.joblib"
    if not prep_path.exists():
        prep_path = Path(__file__).resolve().parent.parent / "data" / "processed" / "preprocessor.joblib"

    preprocessor = load_preprocessor(str(prep_path))
    X_test, y_test = preprocess_data(test_df, preprocessor, fit=False)

    model = None
    if model_uri is None:
        try:
            client = mlflow.tracking.MlflowClient()
            versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
            if not versions:
                versions = client.get_latest_versions(MODEL_NAME, stages=["Staging"])
            if not versions:
                versions = client.get_latest_versions(MODEL_NAME)

            if versions:
                model_uri = f"models:/{MODEL_NAME}/{versions[0].version}"
                print(f"Loading registered model: {model_uri}")
                model = mlflow.sklearn.load_model(model_uri)
        except Exception as e:
            print(f"Note loading from MLflow registry: {e}")

    if model is None:
        local_model_path = ROOT_DIR / "models" / "taxi_fare_predictor.joblib"
        if local_model_path.exists():
            print(f"Loading local model fallback: {local_model_path}")
            model = joblib.load(local_model_path)
        else:
            raise RuntimeError(f"No trained model found for {MODEL_NAME}")

    y_pred = model.predict(X_test)

    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    mae = float(mean_absolute_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))

    results = {
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
        "test_samples": len(test_df),
        "model_uri": model_uri or "local_joblib",
    }

    out_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"Evaluation results: RMSE={rmse:.4f}, MAE={mae:.4f}, R²={r2:.4f}")
    return results


if __name__ == "__main__":
    evaluate_model()
