import os
import sys
import json
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    from sklearn.ensemble import GradientBoostingRegressor
    HAS_XGBOOST = False

import mlflow
import mlflow.sklearn
if HAS_XGBOOST:
    import mlflow.xgboost

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.download_data import download_taxi_data
from src.feature_engineering import preprocess_data, save_preprocessor


LOCAL_DB_PATH = (ROOT_DIR / "mlflow.db").as_posix()
DEFAULT_LOCAL_URI = f"sqlite:///{LOCAL_DB_PATH}"

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", DEFAULT_LOCAL_URI)
EXPERIMENT_NAME = "taxi_fare_prediction"
MODEL_NAME = "taxi_fare_predictor"


def setup_mlflow():
    if os.getenv("AWS_ACCESS_KEY_ID"):
        os.environ["AWS_ACCESS_KEY_ID"] = os.getenv("AWS_ACCESS_KEY_ID", "")
        os.environ["AWS_SECRET_ACCESS_KEY"] = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    if os.getenv("MLFLOW_S3_ENDPOINT_URL"):
        os.environ["MLFLOW_S3_ENDPOINT_URL"] = os.getenv("MLFLOW_S3_ENDPOINT_URL")

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)


def train(params: dict = None):
    if params is None:
        params = {
            "n_estimators": 100,
            "max_depth": 5,
            "learning_rate": 0.1,
            "random_state": 42,
        }

    setup_mlflow()

    train_df, test_df = download_taxi_data()
    print(f"Data loaded: train={train_df.shape}, test={test_df.shape}")

    X_train, y_train, preprocessor = preprocess_data(train_df, fit=True)
    X_test, y_test = preprocess_data(test_df, preprocessor, fit=False)

    preprocessor_path = str(ROOT_DIR / "mlops-platform" / "serving" / "preprocessor" / "preprocessor.joblib")
    save_preprocessor(preprocessor, preprocessor_path)
    # Also save to data/processed
    local_prep_path = str(Path(__file__).resolve().parent.parent / "data" / "processed" / "preprocessor.joblib")
    save_preprocessor(preprocessor, local_prep_path)
    print(f"Preprocessor saved to {preprocessor_path}")

    with mlflow.start_run(run_name="drishti-taxi-baseline") as run:
        mlflow.log_params(params)
        mlflow.log_metric("train_size", len(X_train))
        mlflow.log_metric("test_size", len(X_test))
        mlflow.log_param("num_features", X_train.shape[1])
        mlflow.log_param("model_type", "xgboost" if HAS_XGBOOST else "gradient_boosting")

        if HAS_XGBOOST:
            model = xgb.XGBRegressor(
                n_estimators=params.get("n_estimators", 100),
                max_depth=params.get("max_depth", 5),
                learning_rate=params.get("learning_rate", 0.1),
                random_state=params.get("random_state", 42),
            )
            model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
            mlflow.xgboost.log_model(model, artifact_path="model")
        else:
            model = GradientBoostingRegressor(
                n_estimators=params.get("n_estimators", 100),
                max_depth=params.get("max_depth", 5),
                learning_rate=params.get("learning_rate", 0.1),
                random_state=params.get("random_state", 42),
            )
            model.fit(X_train, y_train)
            mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                serialization_format="cloudpickle",
            )

        y_pred = model.predict(X_test)

        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))

        mlflow.log_metrics({
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
        })

        print(f"RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")

        # Save model locally for fast zero-overhead local serving
        local_model_dir = ROOT_DIR / "models"
        local_model_dir.mkdir(exist_ok=True)
        joblib.dump(model, local_model_dir / "taxi_fare_predictor.joblib")

        # Register model in MLflow Model Registry
        run_id = run.info.run_id
        try:
            result = mlflow.register_model(
                f"runs:/{run_id}/model",
                MODEL_NAME,
            )
            print(f"Registered model {MODEL_NAME} version {result.version}")

            client = mlflow.tracking.MlflowClient()
            client.transition_model_version_stage(
                name=MODEL_NAME,
                version=result.version,
                stage="Staging",
            )
            print(f"Model {MODEL_NAME} version {result.version} promoted to Staging")
        except Exception as e:
            print(f"Model registration note: {e}")

        # Log metrics JSON artifact
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({
                "rmse": rmse,
                "mae": mae,
                "r2": r2,
                "params": params,
                "model_type": "xgboost" if HAS_XGBOOST else "gradient_boosting",
            }, f, indent=2)
            temp_path = f.name
        mlflow.log_artifact(temp_path, artifact_path="metrics")
        try:
            os.remove(temp_path)
        except OSError:
            pass

        print(f"MLflow Run ID: {run_id}")
        return run_id, rmse, mae, r2


if __name__ == "__main__":
    train()
