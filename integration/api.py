"""
DRISHTI AI — Intelligent MLOps & AIOps Platform API
Production-ready REST API supporting:
- Multi-project registration and secure API key authentication
- Role-based authorization: Admin, Operator, and isolated Project scopes
- Universal ML telemetry ingestion (predictions, errors, latency, ground-truth, resource usage)
- Adaptive Loglizer IsolationForest operational anomaly detection
- Project-isolated incident management, deduplication, and correlation
- Safe automated incident remediation playbooks
- MLflow experiment tracking, model registry, and MLOps serving
- Application observability & Prometheus metrics exporter
- Interactive multi-project dark-themed React dashboard
- Render and container deployment ready
"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, Response, Request, Header, Query, Depends, status as http_status
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
    verify_admin_key,
    verify_operator_key,
)
from integration.security import (
    extract_api_key,
    require_admin_auth,
    require_operator_or_admin_auth,
    verify_project_ownership_or_admin,
    get_authenticated_scope,
    require_metrics_auth,
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
    version="1.2.0",
)


# Startup initialization for required directories
@app.on_event("startup")
def startup_init():
    (ROOT / "data" / "telemetry").mkdir(parents=True, exist_ok=True)
    (ROOT / "alerts").mkdir(parents=True, exist_ok=True)
    (ROOT / "models").mkdir(parents=True, exist_ok=True)


# Configure CORS securely
allowed_origins_env = os.getenv("DRISHTI_ALLOWED_ORIGINS", "")
if allowed_origins_env.strip():
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
    allow_credentials = True
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    allow_credentials = True

if "*" in allowed_origins:
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
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
# Root & Health Endpoints (Public)
# ============================================================================

@app.get("/")
def home():
    """Public platform metadata and service status."""
    projects = list_projects()
    return {
        "project": "DRISHTI AI",
        "tagline": "Universal Intelligent MLOps & AIOps Platform",
        "version": "1.2.0",
        "status": "running",
        "dashboard_ui": "/dashboard",
        "prometheus_metrics": "/metrics",
        "documentation": "/docs",
        "registered_projects_count": len(projects),
        "security": {
            "authentication_mode": "Role-Based Token Isolation (Admin / Operator / Project)",
            "master_key_configured": bool(os.getenv("DRISHTI_MASTER_API_KEY")),
        },
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
    """Unauthenticated health probe for monitoring agents and container orchestrators."""
    projects = list_projects()
    telemetry_dir_exists = (ROOT / "data" / "telemetry").exists()
    return {
        "status": "healthy",
        "model_loaded": detector is not None,
        "detector_type": "Loglizer IsolationForest",
        "registered_projects": len(projects),
        "telemetry_storage": "operational" if telemetry_dir_exists else "initializing",
        "timestamp": time.time(),
    }


@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/ui", response_class=HTMLResponse)
def serve_dashboard():
    """Serve the complete Logtail-style terminal observability dashboard."""
    import importlib
    import integration.dashboard_html
    importlib.reload(integration.dashboard_html)
    return HTMLResponse(
        content=integration.dashboard_html.get_dashboard_html(),
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


# ============================================================================
# Project Management Endpoints
# ============================================================================

@app.post("/projects/register", status_code=201)
def api_register_project(
    req: ProjectRegisterRequest,
    admin_token: str = Depends(require_admin_auth),
):
    """
    Register a new ML project and generate a secure API key.
    Requires Administrator privileges (DRISHTI_MASTER_API_KEY).
    The raw API key is returned ONLY once in this response.
    """
    if not isinstance(admin_token, str) or not verify_admin_key(admin_token):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Forbidden. Administrator credentials required.",
        )
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
def api_list_projects(token: Optional[str] = Depends(extract_api_key)):
    """
    List registered ML projects (with masked API keys).
    - Administrators & Operators view all projects.
    - Project owners view only their own project.
    """
    scope = get_authenticated_scope(token)
    if not scope["authenticated"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to list projects.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    all_projs = list_projects()
    if scope["role"] in ["admin", "operator"]:
        return {
            "total_projects": len(all_projs),
            "projects": all_projs,
        }

    # Project scope: filter to own project only
    filtered = [p for p in all_projs if p["project_id"] == scope["project_id"]]
    return {
        "total_projects": len(filtered),
        "projects": filtered,
    }


@app.get("/projects/{project_id}")
def api_get_project(
    project_id: str,
    token: Optional[str] = Depends(extract_api_key),
):
    """
    Retrieve metadata and telemetry stats for a specific project.
    Caller must be the project owner or an administrator.
    """
    verify_project_ownership_or_admin(project_id, token)
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
# Universal Telemetry Ingestion Endpoints (Project-Isolated)
# ============================================================================

@app.post("/telemetry/ingest")
def api_ingest_telemetry(
    req: TelemetryIngestRequest,
    token: Optional[str] = Depends(extract_api_key),
):
    """
    Submit a single telemetry record from an external ML application.
    Requires authentication matching req.project_id or Administrator key.
    """
    verify_project_ownership_or_admin(req.project_id, token)
    try:
        result = ingest_telemetry_event(req.project_id, req.record.model_dump())
        return result
    except Exception as e:
        record_prediction_error(req.project_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/telemetry/batch")
def api_ingest_telemetry_batch(
    req: BatchTelemetryRequest,
    token: Optional[str] = Depends(extract_api_key),
):
    """
    Batch submit multiple telemetry records from an external ML application.
    Requires authentication matching req.project_id or Administrator key.
    """
    verify_project_ownership_or_admin(req.project_id, token)
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
    token: Optional[str] = Depends(extract_api_key),
):
    """
    Retrieve isolated telemetry events for a specific project.
    Enforces project ownership or Administrator privileges.
    """
    verify_project_ownership_or_admin(project_id, token)
    records = get_project_telemetry(project_id, limit=limit, event_type=event_type)
    return {
        "project_id": project_id,
        "total_records": len(records),
        "records": records,
    }


@app.get("/telemetry/{project_id}/drift")
def api_get_drift(
    project_id: str,
    token: Optional[str] = Depends(extract_api_key),
):
    """
    Compute ground-truth accuracy and drift metrics for a specific project.
    Enforces project ownership or Administrator privileges.
    """
    verify_project_ownership_or_admin(project_id, token)
    return get_project_drift_and_accuracy(project_id)


# ============================================================================
# Operational Log Prediction (Project-Scoped & Authenticated)
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
def predict(
    request: LogRequest,
    token: Optional[str] = Depends(extract_api_key),
):
    """
    Evaluate application log message for anomalies.
    Requires authentication matching request.project_id or Administrator key.
    """
    pid = request.project_id or "default"
    verify_project_ownership_or_admin(pid, token)

    if detector is None:
        raise HTTPException(status_code=503, detail="Log anomaly detection model is not loaded.")

    start_time = time.perf_counter()

    try:
        features = extract_features(request.message)
        X = np.array([features], dtype=float)

        prediction = int(detector.predict(X)[0])
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Record metrics telemetry
        record_log_prediction(
            is_anomaly=(prediction == 1),
            latency_ms=elapsed_ms,
            project_id=pid,
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
                project_id=pid,
            )

            # Trigger safe automated remediation
            remediation_action = execute_remediation(
                incident_id=alert["id"],
                message=request.message,
                category=category,
                severity=severity,
                project_id=pid,
            )
            record_automated_response()

        return {
            "log_message": request.message,
            "project_id": pid,
            "prediction": prediction,
            "result": "ANOMALY" if prediction == 1 else "NORMAL",
            "features_used": len(features),
            "latency_ms": elapsed_ms,
            "alert": alert,
            "remediation_action": remediation_action,
        }

    except HTTPException:
        raise
    except Exception as error:
        record_prediction_error(pid)
        raise HTTPException(status_code=500, detail=str(error))


@app.post("/logs/batch-predict")
def batch_predict(
    request: BatchLogRequest,
    token: Optional[str] = Depends(extract_api_key),
):
    """
    Process a batch of log records.
    Requires authentication matching request.project_id or Administrator key.
    """
    pid = request.project_id or "default"
    verify_project_ownership_or_admin(pid, token)

    results = []
    for line in request.logs:
        if line.strip():
            res = predict(LogRequest(message=line, project_id=pid), token=token)
            results.append(res)
    return {
        "project_id": pid,
        "total_processed": len(results),
        "anomalies_detected": sum(1 for r in results if r["result"] == "ANOMALY"),
        "results": results,
    }


# ============================================================================
# Incident Management Endpoints (Scoped & Role-Protected)
# ============================================================================

@app.get("/alerts")
def list_alerts(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    token: Optional[str] = Depends(extract_api_key),
):
    """
    List alerts and incidents with strict project scoping.
    - Administrators & Operators can view all or filter by project.
    - Project owners can ONLY view incidents belonging to their own project.
    """
    scope = get_authenticated_scope(token)
    if not scope["authenticated"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view incidents.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if scope["role"] == "project":
        if project_id and project_id != scope["project_id"]:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Cannot view alerts for foreign project '{project_id}'.",
            )
        project_id = scope["project_id"]

    alerts = get_alerts(project_id=project_id, status=status, severity=severity)
    return {
        "project_id": project_id or "all",
        "total_alerts": len(alerts),
        "alerts": alerts,
    }


@app.patch("/alerts/{alert_id}/resolve")
def resolve_incident_endpoint(
    alert_id: str,
    payload: Optional[ResolveRequest] = None,
    token: Optional[str] = Depends(extract_api_key),
):
    """
    Resolve an incident.
    - Administrators & Operators can resolve any incident.
    - Project owners can ONLY resolve incidents belonging to their own project.
    """
    scope = get_authenticated_scope(token)
    if not scope["authenticated"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to resolve incidents.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    alerts = get_alerts()
    target = next((a for a in alerts if a["id"] == alert_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Alert not found")

    if scope["role"] == "project" and target.get("project_id") != scope["project_id"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied. Cannot resolve another project's incident.",
        )

    notes = payload.resolution_notes if payload else "Resolved by operator"
    actor = payload.resolved_by if payload else (f"Project_{scope.get('project_id')}" if scope["role"] == "project" else "AIOps_Operator")

    alert = resolve_alert(alert_id, resolution_notes=notes, resolved_by=actor)
    return {
        "message": "Incident resolved successfully",
        "alert": alert,
    }


@app.patch("/alerts/{alert_id}/status")
def change_incident_status(
    alert_id: str,
    req: StatusUpdateRequest,
    token: Optional[str] = Depends(extract_api_key),
):
    """
    Transition incident lifecycle status.
    Enforces project ownership or operator/admin privileges.
    """
    scope = get_authenticated_scope(token)
    if not scope["authenticated"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to update incident status.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    alerts = get_alerts()
    target = next((a for a in alerts if a["id"] == alert_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Alert not found")

    if scope["role"] == "project" and target.get("project_id") != scope["project_id"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied. Cannot modify another project's incident.",
        )

    actor = req.actor or (f"Project_{scope.get('project_id')}" if scope["role"] == "project" else "AIOps_Operator")
    alert = update_alert_status(alert_id, new_status=req.status, notes=req.notes, actor=actor)
    return {"message": f"Status updated to {req.status}", "alert": alert}


@app.get("/incidents/stats")
def incident_stats(
    project_id: Optional[str] = None,
    token: Optional[str] = Depends(extract_api_key),
):
    """KPI summary for incidents, categories, and severities."""
    scope = get_authenticated_scope(token)
    if not scope["authenticated"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view incident stats.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if scope["role"] == "project":
        project_id = scope["project_id"]

    return get_incident_stats(project_id=project_id)


@app.get("/incidents/history")
def incident_history(
    incident_id: Optional[str] = None,
    project_id: Optional[str] = None,
    token: Optional[str] = Depends(extract_api_key),
):
    """Audit trail of incident lifecycle events."""
    scope = get_authenticated_scope(token)
    if not scope["authenticated"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view audit history.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if scope["role"] == "project":
        project_id = scope["project_id"]

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
    token: Optional[str] = Depends(extract_api_key),
):
    """List executed automated remediation actions."""
    scope = get_authenticated_scope(token)
    if not scope["authenticated"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view remediation actions.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if scope["role"] == "project":
        project_id = scope["project_id"]

    return {
        "project_id": project_id or "all",
        "stats": get_response_stats(project_id=project_id),
        "actions": get_remediation_history(incident_id=incident_id, project_id=project_id),
    }


@app.post("/responses/trigger/{incident_id}")
def manual_trigger_remediation(
    incident_id: str,
    token: Optional[str] = Depends(extract_api_key),
):
    """Manually trigger safe remediation for an open incident."""
    scope = get_authenticated_scope(token)
    if not scope["authenticated"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to trigger remediation.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    alerts = get_alerts()
    target = next((a for a in alerts if a["id"] == incident_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Incident not found")

    if scope["role"] == "project" and target.get("project_id") != scope["project_id"]:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access denied. Cannot trigger remediation for another project's incident.",
        )

    actor = f"Project_{scope.get('project_id')}" if scope["role"] == "project" else "Manual_Dashboard_Operator"

    action = execute_remediation(
        incident_id=target["id"],
        message=target["message"],
        category=target.get("category", "general"),
        severity=target.get("severity", "ERROR"),
        project_id=target.get("project_id", "default"),
        triggered_by=actor,
    )
    record_automated_response()
    return {"message": "Remediation executed", "action": action}


# ============================================================================
# MLOps Demonstration Model Endpoints
# ============================================================================

@app.get("/mlops/runs")
def mlops_runs(
    limit: int = 10,
    operator_token: str = Depends(require_operator_or_admin_auth),
):
    """List recent experiment runs tracked in MLflow."""
    return {"runs": get_experiment_runs(limit=limit)}


@app.get("/mlops/model-status")
def mlops_model_status(operator_token: str = Depends(require_operator_or_admin_auth)):
    """Show current registered models and staging/production stages."""
    return get_model_status()


@app.post("/mlops/train")
def mlops_train(admin_token: str = Depends(require_admin_auth)):
    """Trigger MLOps training pipeline (Administrator only)."""
    if not isinstance(admin_token, str) or not verify_admin_key(admin_token):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Forbidden. Administrator credentials required.",
        )
    try:
        result = trigger_training()
        record_mlops_training(rmse=result["metrics"]["rmse"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mlops/promote")
def mlops_promote(admin_token: str = Depends(require_admin_auth)):
    """Promote latest staging model to Production (Administrator only)."""
    if not isinstance(admin_token, str) or not verify_admin_key(admin_token):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Forbidden. Administrator credentials required.",
        )
    try:
        return trigger_promotion()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mlops/predict")
def mlops_predict(
    trip: TaxiTripRequest,
    operator_token: str = Depends(require_operator_or_admin_auth),
):
    """Inference against production taxi duration and fare model."""
    try:
        return predict_taxi_duration(trip.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Observability & Metrics Endpoints
# ============================================================================

@app.get("/metrics")
def prometheus_metrics(is_authorized: bool = Depends(require_metrics_auth)):
    """Standard Prometheus metrics exposition endpoint."""
    content = generate_prometheus_metrics()
    return Response(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")


@app.get("/system/stats")
def system_stats(
    project_id: Optional[str] = None,
    token: Optional[str] = Depends(extract_api_key),
):
    """Comprehensive observability telemetry payload."""
    scope = get_authenticated_scope(token)
    if not scope["authenticated"]:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view system stats.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if scope["role"] == "project":
        project_id = scope["project_id"]

    return {
        "project_id": project_id or "all",
        "metrics": get_metrics_summary(project_id=project_id),
        "incidents": get_incident_stats(project_id=project_id),
        "responses": get_response_stats(project_id=project_id),
        "projects_count": len(list_projects()),
        "mlops": get_model_status() if scope["role"] in ["admin", "operator"] else {"status": "restricted"},
    }


# ============================================================================
# Server Entrypoint (Render & Local Compatible)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("DRISHTI_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("DRISHTI_PORT", "8001")))
    log_level = os.getenv("DRISHTI_LOG_LEVEL", "info")
    uvicorn.run("integration.api:app", host=host, port=port, reload=True, log_level=log_level)
