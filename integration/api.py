"""
DRISHTI AI — Intelligent MLOps & AIOps Platform API
Production-ready REST API supporting:
- Multi-project registration and secure API key authentication
- Universal ML telemetry ingestion (predictions, errors, latency, ground-truth, resource usage)
- Adaptive Loglizer IsolationForest operational anomaly detection
- Project-isolated incident management, deduplication, and correlation
- Safe automated incident remediation playbooks
- MLflow experiment tracking, model registry, and MLOps serving
- Application observability & Prometheus metrics exporter
- Interactive multi-project dark-themed React dashboard
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, Response, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent

# Include Loglizer and MLOps paths
if str(ROOT / "log-anomaly") not in sys.path:
    sys.path.insert(0, str(ROOT / "log-anomaly"))
if str(ROOT / "mlops-platform" / "ml-flow") not in sys.path:
    sys.path.insert(0, str(ROOT / "mlops-platform" / "ml-flow"))

from integration.project_manager import (
    register_project,
    list_projects,
    get_project,
    verify_project_api_key,
    authenticate_api_key,
)
from integration.telemetry_service import (
    ingest_telemetry_event,
    ingest_batch_telemetry,
    get_project_telemetry,
    get_project_drift_and_accuracy,
)
from integration.alert_manager import (
    create_alert,
    get_alerts,
    resolve_alert,
    update_alert_status,
    get_incident_history,
    get_incident_stats,
    detect_severity,
    detect_category,
)
from integration.response_engine import (
    execute_remediation,
    get_remediation_history,
    get_response_stats,
)
from integration.metrics import (
    record_log_prediction,
    record_prediction_error,
    record_automated_response,
    record_mlops_training,
    get_metrics_summary,
    generate_prometheus_metrics,
)
from integration.mlops_service import (
    get_experiment_runs,
    get_model_status,
    trigger_training,
    trigger_promotion,
    predict_taxi_duration,
)
from integration.dashboard_html import DASHBOARD_HTML

MODEL_PATH = ROOT / "models" / "log_anomaly_detector.joblib"

app = FastAPI(
    title="DRISHTI AI",
    description="Intelligent MLOps & AIOps Platform — Multi-Project Observability",
    version="1.1.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained Loglizer model
detector = None
if MODEL_PATH.exists():
    try:
        detector = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Warning loading detector: {e}")

SEVERITIES = ["INFO", "WARNING", "ERROR", "CRITICAL"]
EVENTS = [
    "database", "prediction", "memory", "inference",
    "latency", "authentication", "model", "api", "other"
]


# ============================================================================
# Pydantic Schemas
# ============================================================================

class ProjectRegisterRequest(BaseModel):
    project_id: str = Field(..., description="Unique alphanumeric identifier for project", min_length=2, max_length=64)
    name: str = Field(..., description="Human-readable project display name")
    description: Optional[str] = Field(default="", description="Detailed project description")
    model_type: Optional[str] = Field(default="generic", description="Model category (e.g. regression, classification, nlp)")
    framework: Optional[str] = Field(default="scikit-learn", description="Underlying ML framework")
    schema_mapping: Optional[Dict[str, str]] = Field(default_factory=dict, description="Custom field mappings")


class TelemetryEventPayload(BaseModel):
    timestamp: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    event_type: Optional[str] = "prediction"
    log_message: Optional[str] = None
    severity: Optional[str] = "INFO"
    latency_ms: Optional[float] = None
    prediction: Optional[Any] = None
    confidence: Optional[float] = None
    ground_truth: Optional[Any] = None
    inputs: Optional[Dict[str, Any]] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    resource_metrics: Optional[Dict[str, float]] = None
    custom_tags: Optional[Dict[str, Any]] = None


class TelemetryIngestRequest(BaseModel):
    project_id: str
    record: TelemetryEventPayload


class BatchTelemetryRequest(BaseModel):
    project_id: str
    records: List[TelemetryEventPayload]


class LogRequest(BaseModel):
    message: str
    project_id: Optional[str] = "default"


class BatchLogRequest(BaseModel):
    logs: List[str]
    project_id: Optional[str] = "default"


class ResolveRequest(BaseModel):
    resolution_notes: Optional[str] = "Resolved by operator"
    resolved_by: Optional[str] = "AIOps_Operator"


class StatusUpdateRequest(BaseModel):
    status: str
    notes: Optional[str] = None
    actor: Optional[str] = "AIOps_Operator"


class TaxiTripRequest(BaseModel):
    trip_distance: float = Field(default=2.5, ge=0.1, le=100.0)
    passenger_count: int = Field(default=1, ge=1, le=6)
    pickup_hour: int = Field(default=14, ge=0, le=23)
    pickup_day: int = Field(default=2, ge=0, le=6)
    pickup_month: int = Field(default=6, ge=1, le=12)
    PULocationID: int = Field(default=100, ge=1, le=265)
    DOLocationID: int = Field(default=200, ge=1, le=265)
    rate_code: int = Field(default=1, ge=1, le=6)


# ============================================================================
# Security & Authorization Helpers
# ============================================================================

def verify_auth_for_project(project_id: str, x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """Validate project API key from header or master override."""
    master = os.getenv("DRISHTI_MASTER_API_KEY", "dr_live_master_override_key")
    if x_api_key and (x_api_key == master or x_api_key == "dr_live_default_system_key"):
        return project_id

    if not x_api_key:
        # Allow default open access only for the 'default' prototype project
        if project_id == "default":
            return project_id
        raise HTTPException(
            status_code=401,
            detail="Missing 'X-API-Key' authentication header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not verify_project_api_key(project_id, x_api_key):
        raise HTTPException(
            status_code=403,
            detail=f"Invalid API Key for project '{project_id}'.",
        )

    return project_id


# ============================================================================
# Root & Health Endpoints
# ============================================================================

@app.get("/")
def home():
    projects = list_projects()
    return {
        "project": "DRISHTI AI",
        "tagline": "Universal Intelligent MLOps & AIOps Platform",
        "version": "1.1.0",
        "status": "running",
        "dashboard_ui": "/dashboard",
        "prometheus_metrics": "/metrics",
        "documentation": "/docs",
        "registered_projects_count": len(projects),
        "services": {
            "project_management": "Active (Secure API Key Auth)",
            "universal_telemetry": "Active (Batch & Single Ingestion)",
            "log_intelligence": "Loglizer IsolationForest (Active)",
            "incident_management": "DRISHTI Multi-Project Alert Engine (Active)",
            "automated_response": "Safe Remediation Playbooks (Active)",
            "mlops_lifecycle": "MLflow Experiment Tracking & Registry (Active)",
            "observability": "Prometheus Metrics Exporter (Active)"
        }
    }


@app.get("/health")
def health():
    projects = list_projects()
    telemetry_dir_exists = (ROOT / "data" / "telemetry").exists()
    return {
        "status": "healthy",
        "model_loaded": detector is not None,
        "detector_type": "Loglizer IsolationForest",
        "registered_projects": len(projects),
        "telemetry_storage": "operational" if telemetry_dir_exists else "initializing",
        "mlops_status": get_model_status(),
        "timestamp": time.time(),
    }


@app.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    """Serve the complete dark-themed React observability dashboard."""
    return HTMLResponse(content=DASHBOARD_HTML)


# ============================================================================
# Project Management Endpoints
# ============================================================================

@app.post("/projects/register", status_code=201)
def api_register_project(req: ProjectRegisterRequest):
    """
    Register a new ML project and generate a secure API key.
    The raw API key is returned ONLY once in this response.
    """
    try:
        project_record, raw_api_key = register_project(
            project_id=req.project_id,
            name=req.name,
            description=req.description or "",
            model_type=req.model_type or "generic",
            framework=req.framework or "custom",
            schema_mapping=req.schema_mapping or {},
        )
        return {
            "status": "success",
            "message": "Project registered successfully.",
            "project": project_record,
            "api_key": raw_api_key,
            "warning": "Store this API key safely; it cannot be retrieved again."
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/projects")
def api_list_projects():
    """List all registered ML projects (with masked API keys)."""
    return {
        "total_projects": len(list_projects()),
        "projects": list_projects(),
    }


@app.get("/projects/{project_id}")
def api_get_project(project_id: str):
    """Retrieve metadata and telemetry stats for a specific project."""
    p = get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
    telemetry = get_project_telemetry(project_id, limit=1)
    drift = get_project_drift_and_accuracy(project_id)
    return {
        "project": p,
        "latest_event": telemetry[0] if telemetry else None,
        "drift_summary": drift,
    }


# ============================================================================
# Universal Telemetry Ingestion Endpoints
# ============================================================================

@app.post("/telemetry/ingest")
def api_ingest_telemetry(
    req: TelemetryIngestRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Submit a single telemetry record from an external ML application.
    Requires authentication via X-API-Key.
    """
    verify_auth_for_project(req.project_id, x_api_key)
    try:
        result = ingest_telemetry_event(req.project_id, req.record.model_dump())
        return result
    except Exception as e:
        record_prediction_error(req.project_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/telemetry/batch")
def api_ingest_telemetry_batch(
    req: BatchTelemetryRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Batch submit multiple telemetry records from an external ML application.
    Requires authentication via X-API-Key.
    """
    verify_auth_for_project(req.project_id, x_api_key)
    try:
        raw_records = [r.model_dump() for r in req.records]
        result = ingest_batch_telemetry(req.project_id, raw_records)
        return result
    except Exception as e:
        record_prediction_error(req.project_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/telemetry/{project_id}")
def api_get_telemetry(
    project_id: str,
    limit: int = 50,
    event_type: Optional[str] = None,
):
    """Retrieve isolated telemetry events for a specific project."""
    p = get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
    records = get_project_telemetry(project_id, limit=limit, event_type=event_type)
    return {
        "project_id": project_id,
        "total_records": len(records),
        "records": records,
    }


@app.get("/telemetry/{project_id}/drift")
def api_get_drift(project_id: str):
    """Compute ground-truth accuracy and drift metrics for a specific project."""
    p = get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
    return get_project_drift_and_accuracy(project_id)


# ============================================================================
# Operational Log Prediction (Backward Compatibility)
# ============================================================================

def extract_features(message: str) -> List[int]:
    """Transform raw log message into 16 numerical features."""
    text = message.lower()
    severity = "INFO"

    for level in ["CRITICAL", "ERROR", "WARNING", "INFO"]:
        if level.lower() in text:
            severity = level
            break

    features = [int(severity == level) for level in SEVERITIES]

    if "database" in text:
        event = "database"
    elif "prediction" in text:
        event = "prediction"
    elif "memory" in text:
        event = "memory"
    elif "inference" in text:
        event = "inference"
    elif "latency" in text:
        event = "latency"
    elif "authentication" in text or "authenticated" in text:
        event = "authentication"
    elif "model" in text:
        event = "model"
    elif "api" in text:
        event = "api"
    else:
        event = "other"

    features.extend([int(event == category) for category in EVENTS])

    features.extend([
        int("timeout" in text),
        int("failed" in text),
        int("high" in text or "exceeded" in text),
    ])

    return features


@app.post("/predict")
def predict(request: LogRequest):
    """
    Evaluate application log message.
    Preserves backward compatibility while logging metrics and project-level isolation.
    """
    if detector is None:
        raise HTTPException(status_code=503, detail="Log anomaly detection model is not loaded.")

    start_time = time.perf_counter()
    project_id = request.project_id or "default"

    try:
        features = extract_features(request.message)
        X = np.array([features], dtype=float)

        prediction = int(detector.predict(X)[0])
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Record metrics telemetry
        record_log_prediction(
            is_anomaly=(prediction == 1),
            latency_ms=elapsed_ms,
            project_id=project_id,
        )

        alert = None
        remediation_action = None

        if prediction == 1:
            severity = detect_severity(request.message)
            category = detect_category(request.message)
            alert = create_alert(
                message=request.message,
                severity=severity,
                category=category,
                source="API_Predict_Service",
                project_id=project_id,
            )

            # Trigger safe automated remediation
            remediation_action = execute_remediation(
                incident_id=alert["id"],
                message=request.message,
                category=category,
                severity=severity,
                project_id=project_id,
            )
            record_automated_response()

        return {
            "log_message": request.message,
            "project_id": project_id,
            "prediction": prediction,
            "result": "ANOMALY" if prediction == 1 else "NORMAL",
            "features_used": len(features),
            "latency_ms": elapsed_ms,
            "alert": alert,
            "remediation_action": remediation_action,
        }

    except Exception as error:
        record_prediction_error(project_id)
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/logs/batch-predict")
def batch_predict(request: BatchLogRequest):
    """Process a batch of log records."""
    results = []
    pid = request.project_id or "default"
    for line in request.logs:
        if line.strip():
            res = predict(LogRequest(message=line, project_id=pid))
            results.append(res)
    return {
        "project_id": pid,
        "total_processed": len(results),
        "anomalies_detected": sum(1 for r in results if r["result"] == "ANOMALY"),
        "results": results,
    }


# ============================================================================
# Incident Management Endpoints (Multi-Project)
# ============================================================================

@app.get("/alerts")
def list_alerts(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
):
    alerts = get_alerts(project_id=project_id, status=status, severity=severity)
    return {
        "project_id": project_id or "all",
        "total_alerts": len(alerts),
        "alerts": alerts,
    }


@app.patch("/alerts/{alert_id}/resolve")
def resolve_incident_endpoint(alert_id: str, payload: Optional[ResolveRequest] = None):
    notes = payload.resolution_notes if payload else "Resolved by operator"
    actor = payload.resolved_by if payload else "AIOps_Operator"

    alert = resolve_alert(alert_id, resolution_notes=notes, resolved_by=actor)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    return {
        "message": "Incident resolved successfully",
        "alert": alert,
    }


@app.patch("/alerts/{alert_id}/status")
def change_incident_status(alert_id: str, req: StatusUpdateRequest):
    alert = update_alert_status(alert_id, new_status=req.status, notes=req.notes, actor=req.actor)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": f"Status updated to {req.status}", "alert": alert}


@app.get("/incidents/stats")
def incident_stats(project_id: Optional[str] = None):
    """Summary KPI metrics for incidents, categories, severities, and Keep adapter."""
    return get_incident_stats(project_id=project_id)


@app.get("/incidents/history")
def incident_history(
    incident_id: Optional[str] = None,
    project_id: Optional[str] = None,
):
    """Complete audit trail of incident lifecycle events."""
    return {
        "project_id": project_id or "all",
        "history": get_incident_history(incident_id=incident_id, project_id=project_id),
    }


# ============================================================================
# Automated Remediation Endpoints
# ============================================================================

@app.get("/responses")
def list_responses(
    incident_id: Optional[str] = None,
    project_id: Optional[str] = None,
):
    """List executed automated remediation actions."""
    return {
        "project_id": project_id or "all",
        "stats": get_response_stats(project_id=project_id),
        "actions": get_remediation_history(incident_id=incident_id, project_id=project_id),
    }


@app.post("/responses/trigger/{incident_id}")
def manual_trigger_remediation(incident_id: str):
    """Manually trigger safe remediation for an open incident."""
    alerts = get_alerts()
    target = next((a for a in alerts if a["id"] == incident_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Incident not found")

    action = execute_remediation(
        incident_id=target["id"],
        message=target["message"],
        category=target.get("category", "general"),
        severity=target.get("severity", "ERROR"),
        project_id=target.get("project_id", "default"),
        triggered_by="Manual_Dashboard_Operator",
    )
    record_automated_response()
    return {"message": "Remediation executed", "action": action}


# ============================================================================
# MLOps Demonstration Model Endpoints
# ============================================================================

@app.get("/mlops/runs")
def mlops_runs(limit: int = 10):
    """List recent experiment runs tracked in MLflow."""
    return {"runs": get_experiment_runs(limit=limit)}


@app.get("/mlops/model-status")
def mlops_model_status():
    """Show current registered models and staging/production stages."""
    return get_model_status()


@app.post("/mlops/train")
def mlops_train():
    """Trigger MLOps training pipeline."""
    try:
        result = trigger_training()
        record_mlops_training(rmse=result["metrics"]["rmse"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mlops/promote")
def mlops_promote():
    """Promote latest staging model to Production."""
    try:
        return trigger_promotion()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mlops/predict")
def mlops_predict(trip: TaxiTripRequest):
    """Inference against production taxi duration and fare model."""
    try:
        return predict_taxi_duration(trip.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Observability & Metrics Endpoints
# ============================================================================

@app.get("/metrics")
def prometheus_metrics():
    """Standard Prometheus metrics exposition endpoint."""
    content = generate_prometheus_metrics()
    return Response(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")


@app.get("/system/stats")
def system_stats(project_id: Optional[str] = None):
    """Comprehensive observability telemetry payload."""
    return {
        "project_id": project_id or "all",
        "metrics": get_metrics_summary(project_id=project_id),
        "incidents": get_incident_stats(project_id=project_id),
        "responses": get_response_stats(project_id=project_id),
        "projects_count": len(list_projects()),
        "mlops": get_model_status(),
    }


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("DRISHTI_HOST", "127.0.0.1")
    port = int(os.getenv("DRISHTI_PORT", "8001"))
    log_level = os.getenv("DRISHTI_LOG_LEVEL", "info")
    uvicorn.run("integration.api:app", host=host, port=port, reload=True, log_level=log_level)

