"""
DRISHTI AI — Universal Telemetry Ingestion & Adaptive Anomaly Normalization
Provides project-isolated telemetry storage, normalization of diverse ML application logs,
and inference integration with Loglizer IsolationForest.
"""

import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import joblib
import numpy as np

from integration.alert_manager import create_alert
from integration.response_engine import execute_remediation
from integration.metrics import (
    record_log_prediction,
    record_automated_response,
    record_batch_logs,
)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
TELEMETRY_DIR = DATA_DIR / "telemetry"
MODEL_PATH = ROOT / "models" / "log_anomaly_detector.joblib"

# Load Loglizer detector
_detector = None
if MODEL_PATH.exists():
    try:
        _detector = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Telemetry service: note loading detector: {e}")

SEVERITIES = ["INFO", "WARNING", "ERROR", "CRITICAL"]
EVENTS = [
    "database", "prediction", "memory", "inference",
    "latency", "authentication", "model", "api", "other"
]


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def get_telemetry_file(project_id: str) -> Path:
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
    clean_id = "".join(c for c in project_id.lower().replace(" ", "-") if c.isalnum() or c in "-_")
    return TELEMETRY_DIR / f"{clean_id}.jsonl"


def normalize_to_feature_vector(record: Dict[str, Any]) -> List[int]:
    """
    Map arbitrary third-party application telemetry into DRISHTI's 16-dimensional
    numerical feature space with safe imputation for missing fields.
    """
    raw_msg = str(record.get("log_message") or record.get("error_message") or record.get("message") or "").upper()
    event_type = str(record.get("event_type", "prediction")).lower()
    latency_ms = float(record.get("latency_ms") or 0.0)

    # 1. Determine Severity
    sev = str(record.get("severity") or "").upper()
    if sev not in SEVERITIES:
        if record.get("error_message") or record.get("error_type") or "ERROR" in raw_msg:
            sev = "ERROR"
        elif "CRITICAL" in raw_msg:
            sev = "CRITICAL"
        elif latency_ms > 1000.0 or "WARNING" in raw_msg:
            sev = "WARNING"
        else:
            sev = "INFO"

    features = [int(sev == s) for s in SEVERITIES]

    # 2. Determine Subsystem Category
    cat = "other"
    if "DATABASE" in raw_msg or "SQL" in raw_msg:
        cat = "database"
    elif latency_ms > 800.0 or "LATENCY" in raw_msg:
        cat = "latency"
    elif "MEMORY" in raw_msg or (record.get("resource_metrics") and record["resource_metrics"].get("memory_mb", 0) > 1500):
        cat = "memory"
    elif "INFERENCE" in raw_msg or record.get("error_type") == "InferenceError":
        cat = "inference"
    elif "AUTH" in raw_msg:
        cat = "authentication"
    elif event_type == "prediction" or record.get("prediction") is not None:
        cat = "prediction"
    elif "MODEL" in raw_msg:
        cat = "model"
    elif "API" in raw_msg or "HTTP" in raw_msg:
        cat = "api"

    features.extend([int(cat == c) for c in EVENTS])

    # 3. Problem Indicators
    is_timeout = int(latency_ms > 1500.0 or "TIMEOUT" in raw_msg)
    is_failed = int(bool(record.get("error_message")) or bool(record.get("error_type")) or "FAILED" in raw_msg)

    resource_metrics = record.get("resource_metrics") or {}
    cpu = resource_metrics.get("cpu_percent", 0.0)
    high_resource = cpu > 85.0 or resource_metrics.get("memory_mb", 0) > 1500
    is_high_usage = int(high_resource or "HIGH" in raw_msg or "EXCEEDED" in raw_msg)

    features.extend([is_timeout, is_failed, is_high_usage])
    return features


def ingest_telemetry_event(
    project_id: str,
    record: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Ingest a single telemetry event, run Loglizer anomaly inference,
    trigger incident management on anomaly, and append to project storage.
    """
    start_time = time.perf_counter()
    telemetry_id = str(uuid.uuid4())[:8]
    now = record.get("timestamp") or _now_iso()

    # Extract normalized 16-feature vector
    features = normalize_to_feature_vector(record)

    # Run Loglizer IsolationForest Anomaly Inference
    is_anomaly = False
    anomaly_prediction = 0

    if _detector is not None:
        try:
            X = np.array([features], dtype=float)
            anomaly_prediction = int(_detector.predict(X)[0])
            is_anomaly = (anomaly_prediction == 1)
        except Exception as e:
            print(f"Detector inference note: {e}")

    # Fallback heuristic: explicit ERROR/CRITICAL severity or latency spike
    if not is_anomaly:
        if record.get("severity") in ["ERROR", "CRITICAL"] or record.get("error_message"):
            is_anomaly = True
            anomaly_prediction = 1

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    latency_to_record = float(record.get("latency_ms") or elapsed_ms)

    # Build standardized telemetry record
    clean_record = {
        "telemetry_id": telemetry_id,
        "project_id": project_id,
        "timestamp": now,
        "model_name": record.get("model_name"),
        "model_version": record.get("model_version"),
        "event_type": record.get("event_type", "prediction"),
        "log_message": record.get("log_message") or record.get("message") or f"Event from {project_id}",
        "severity": record.get("severity") or ("ERROR" if is_anomaly else "INFO"),
        "latency_ms": latency_to_record,
        "prediction": record.get("prediction"),
        "confidence": record.get("confidence"),
        "ground_truth": record.get("ground_truth"),
        "inputs": record.get("inputs"),
        "error_type": record.get("error_type"),
        "error_message": record.get("error_message"),
        "resource_metrics": record.get("resource_metrics"),
        "custom_tags": record.get("custom_tags") or {},
        "features_extracted": features,
        "is_anomaly": is_anomaly,
        "anomaly_score": anomaly_prediction,
    }

    # Project-level isolation: append to project-specific file
    target_file = get_telemetry_file(project_id)
    with open(target_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(clean_record) + "\n")

    # Record Prometheus metrics
    record_log_prediction(
        is_anomaly=is_anomaly,
        latency_ms=latency_to_record,
        project_id=project_id,
        is_error=bool(record.get("error_message") or record.get("error_type")),
    )

    alert = None
    remediation_action = None

    # On anomaly: create project-scoped incident and trigger safe remediation
    if is_anomaly:
        incident_msg = (
            record.get("error_message")
            or record.get("log_message")
            or f"[{clean_record['severity']}] Anomaly detected in {project_id} (latency: {latency_to_record}ms)"
        )
        alert = create_alert(
            message=incident_msg,
            severity=clean_record["severity"],
            category="inference" if record.get("error_type") else "prediction",
            source=f"Telemetry_{project_id}",
            project_id=project_id,
            metadata={"telemetry_id": telemetry_id, "model_name": record.get("model_name")},
        )

        remediation_action = execute_remediation(
            incident_id=alert["id"],
            message=incident_msg,
            category=alert.get("category", "general"),
            severity=alert.get("severity", "ERROR"),
            project_id=project_id,
            triggered_by=f"Auto_Response_{project_id}",
        )
        record_automated_response()

    return {
        "status": "success",
        "telemetry_id": telemetry_id,
        "project_id": project_id,
        "is_anomaly": is_anomaly,
        "result": "ANOMALY" if is_anomaly else "NORMAL",
        "alert": alert,
        "remediation_action": remediation_action,
        "processing_time_ms": elapsed_ms,
    }


def ingest_batch_telemetry(
    project_id: str,
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Ingest a batch of telemetry records with per-record fault tolerance."""
    results = []
    anomalies = 0
    errors = 0

    for idx, rec in enumerate(records):
        try:
            if not isinstance(rec, dict):
                results.append({"index": idx, "status": "error", "message": "Record must be an object"})
                errors += 1
                continue
            res = ingest_telemetry_event(project_id, rec)
            results.append(res)
            if res.get("is_anomaly"):
                anomalies += 1
        except Exception as e:
            results.append({"index": idx, "status": "error", "message": str(e)})
            errors += 1

    return {
        "project_id": project_id,
        "total_records": len(records),
        "successful": len(records) - errors,
        "failed": errors,
        "anomalies_detected": anomalies,
        "results": results,
    }


def get_project_telemetry(
    project_id: str,
    limit: int = 50,
    event_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Retrieve telemetry records strictly for the requested project."""
    target_file = get_telemetry_file(project_id)
    if not target_file.exists():
        return []

    records = []
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if event_type and item.get("event_type") != event_type:
                        continue
                    records.append(item)
    except Exception as e:
        print(f"Error reading telemetry for {project_id}: {e}")

    # Return latest records first
    return records[-limit:][::-1]


def get_project_drift_and_accuracy(project_id: str) -> Dict[str, Any]:
    """
    Calculate model accuracy and error drift when ground truth is submitted.
    """
    records = get_project_telemetry(project_id, limit=200)
    pairs = [
        (float(r["prediction"]), float(r["ground_truth"]))
        for r in records
        if r.get("prediction") is not None and r.get("ground_truth") is not None
        and str(r.get("prediction")).replace(".", "", 1).isdigit()
        and str(r.get("ground_truth")).replace(".", "", 1).isdigit()
    ]

    if not pairs:
        return {
            "evaluation_available": False,
            "sample_size": 0,
            "mae": None,
            "rmse": None,
            "message": "Ground-truth data not yet reported for this project.",
        }

    diffs = [p[0] - p[1] for p in pairs]
    mae = round(sum(abs(d) for d in diffs) / len(diffs), 4)
    rmse = round((sum(d**2 for d in diffs) / len(diffs)) ** 0.5, 4)

    return {
        "evaluation_available": True,
        "sample_size": len(pairs),
        "mae": mae,
        "rmse": rmse,
        "status": "HEALTHY" if rmse < 50000 else "POTENTIAL_DRIFT",
    }

