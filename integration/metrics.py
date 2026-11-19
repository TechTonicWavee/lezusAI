"""
DRISHTI AI — Application Observability & Prometheus Metrics Engine
Thread-safe, file-persisted operational telemetry engine.
Exposes standard Prometheus exposition format text at /metrics.
"""

import json
import threading
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

ROOT = Path(__file__).resolve().parent.parent
ALERTS_DIR = ROOT / "alerts"
METRICS_FILE = ALERTS_DIR / "metrics_state.json"

_lock = threading.Lock()

# Default in-memory metric state
_state: Dict[str, Any] = {
    "logs_processed_total": 0,
    "anomalies_detected_total": 0,
    "normal_events_total": 0,
    "prediction_requests_total": 0,
    "prediction_errors_total": 0,
    "incidents_created_total": 0,
    "incidents_resolved_total": 0,
    "automated_responses_total": 0,
    "mlops_training_runs_total": 0,
    "latest_mlops_rmse": 3.4949,
    "project_events": {},
    "project_anomalies": {},
    "project_errors": {},
}

_latencies: List[float] = []


def _load_persisted_state() -> None:
    global _state
    try:
        ALERTS_DIR.mkdir(parents=True, exist_ok=True)
        if METRICS_FILE.exists():
            data = json.loads(METRICS_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for k, v in data.items():
                    if k in _state:
                        _state[k] = v
    except Exception as e:
        print(f"Metrics state load note: {e}")


def _persist_state() -> None:
    try:
        ALERTS_DIR.mkdir(parents=True, exist_ok=True)
        METRICS_FILE.write_text(json.dumps(_state, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"Metrics state persist note: {e}")


# Initialize from disk
_load_persisted_state()


def record_log_prediction(
    is_anomaly: bool,
    latency_ms: float = 0.0,
    project_id: str = "default",
    is_error: bool = False,
) -> None:
    """Record an individual or batch log evaluation."""
    with _lock:
        _state["logs_processed_total"] += 1
        _state["prediction_requests_total"] += 1

        if is_error:
            _state["prediction_errors_total"] += 1
            _state["project_errors"][project_id] = _state["project_errors"].get(project_id, 0) + 1

        if is_anomaly:
            _state["anomalies_detected_total"] += 1
            _state["project_anomalies"][project_id] = _state["project_anomalies"].get(project_id, 0) + 1
        else:
            _state["normal_events_total"] += 1

        # Track per-project events
        _state["project_events"][project_id] = _state["project_events"].get(project_id, 0) + 1

        if latency_ms > 0:
            _latencies.append(latency_ms)
            if len(_latencies) > 500:
                _latencies.pop(0)

        _persist_state()


def record_batch_logs(
    total_logs: int,
    anomalies: int,
    project_id: str = "default",
    avg_latency_ms: float = 0.0,
) -> None:
    """Record batch log processing events."""
    with _lock:
        _state["logs_processed_total"] += total_logs
        _state["prediction_requests_total"] += total_logs
        _state["anomalies_detected_total"] += anomalies
        _state["normal_events_total"] += max(0, total_logs - anomalies)

        _state["project_events"][project_id] = _state["project_events"].get(project_id, 0) + total_logs
        _state["project_anomalies"][project_id] = _state["project_anomalies"].get(project_id, 0) + anomalies

        if avg_latency_ms > 0:
            _latencies.extend([avg_latency_ms] * min(total_logs, 20))
            if len(_latencies) > 500:
                _latencies[:] = _latencies[-500:]

        _persist_state()


def record_prediction_error(project_id: str = "default") -> None:
    with _lock:
        _state["prediction_requests_total"] += 1
        _state["prediction_errors_total"] += 1
        _state["project_errors"][project_id] = _state["project_errors"].get(project_id, 0) + 1
        _persist_state()


def record_incident_created(project_id: str = "default") -> None:
    with _lock:
        _state["incidents_created_total"] += 1
        _persist_state()


def record_incident_resolved(project_id: str = "default") -> None:
    with _lock:
        _state["incidents_resolved_total"] += 1
        _persist_state()


def record_automated_response() -> None:
    with _lock:
        _state["automated_responses_total"] += 1
        _persist_state()


def record_mlops_training(rmse: float) -> None:
    with _lock:
        _state["mlops_training_runs_total"] += 1
        _state["latest_mlops_rmse"] = rmse
        _persist_state()


def get_metrics_summary(project_id: Optional[str] = None) -> Dict[str, Any]:
    from integration.alert_manager import load_alerts
    from integration.response_engine import load_remediation_actions

    alerts = load_alerts()
    if project_id and project_id != "all":
        alerts = [a for a in alerts if a.get("project_id", "default") == project_id]

    open_count = sum(1 for a in alerts if a.get("status") in ["OPEN", "INVESTIGATING", "MITIGATING"])
    resolved_count = sum(1 for a in alerts if a.get("status") in ["RESOLVED", "CLOSED"])

    remediations = load_remediation_actions()
    if project_id and project_id != "all":
        remediations = [r for r in remediations if r.get("project_id", "default") == project_id]

    with _lock:
        latencies = list(_latencies)
        avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
        p95_latency = round(sorted(latencies)[int(len(latencies) * 0.95)], 2) if latencies else 0.0

        if project_id and project_id != "all":
            logs_total = _state["project_events"].get(project_id, 0)
            anomalies_total = _state["project_anomalies"].get(project_id, 0)
            errors_total = _state["project_errors"].get(project_id, 0)
            normal_total = max(0, logs_total - anomalies_total)
        else:
            logs_total = _state["logs_processed_total"]
            anomalies_total = _state["anomalies_detected_total"]
            normal_total = _state["normal_events_total"]
            errors_total = _state["prediction_errors_total"]

        responses_total = max(_state["automated_responses_total"], len(remediations))
        created_total = _state["incidents_created_total"]
        resolved_total = _state["incidents_resolved_total"]
        rmse = _state["latest_mlops_rmse"]

    anomaly_rate = round((anomalies_total / logs_total) * 100, 2) if logs_total > 0 else 0.0
    error_rate = round((errors_total / logs_total) * 100, 2) if logs_total > 0 else 0.0

    return {
        "total_logs_processed": logs_total,
        "total_anomalies_detected": anomalies_total,
        "total_normal_events": normal_total,
        "anomaly_rate_percent": anomaly_rate,
        "prediction_requests_total": logs_total,
        "prediction_errors_total": errors_total,
        "error_rate_percent": error_rate,
        "open_incidents": open_count,
        "resolved_incidents": resolved_count,
        "total_incidents": len(alerts),
        "incidents_created_total": max(created_total, len(alerts)),
        "incidents_resolved_total": max(resolved_total, resolved_count),
        "automated_responses_count": responses_total,
        "avg_prediction_latency_ms": avg_latency,
        "p95_prediction_latency_ms": p95_latency,
        "latest_mlops_rmse": round(rmse, 4),
    }


def generate_prometheus_metrics() -> str:
    """Generate Prometheus standard text exposition format (version 0.0.4)."""
    summary = get_metrics_summary()

    lines = [
        "# HELP drishti_logs_processed_total Total application logs evaluated by DRISHTI AI",
        "# TYPE drishti_logs_processed_total counter",
        f"drishti_logs_processed_total {summary['total_logs_processed']}",
        "",
        "# HELP drishti_anomalies_detected_total Total anomalies detected by Loglizer model",
        "# TYPE drishti_anomalies_detected_total counter",
        f"drishti_anomalies_detected_total {summary['total_anomalies_detected']}",
        "",
        "# HELP drishti_normal_events_total Total normal application logs",
        "# TYPE drishti_normal_events_total counter",
        f"drishti_normal_events_total {summary['total_normal_events']}",
        "",
        "# HELP drishti_prediction_requests_total Total model prediction and telemetry requests",
        "# TYPE drishti_prediction_requests_total counter",
        f"drishti_prediction_requests_total {summary['prediction_requests_total']}",
        "",
        "# HELP drishti_prediction_errors_total Total failed predictions or telemetry processing errors",
        "# TYPE drishti_prediction_errors_total counter",
        f"drishti_prediction_errors_total {summary['prediction_errors_total']}",
        "",
        "# HELP drishti_open_incidents Current active or open operational incidents",
        "# TYPE drishti_open_incidents gauge",
        f"drishti_open_incidents {summary['open_incidents']}",
        "",
        "# HELP drishti_resolved_incidents Total operational incidents resolved",
        "# TYPE drishti_resolved_incidents gauge",
        f"drishti_resolved_incidents {summary['resolved_incidents']}",
        "",
        "# HELP drishti_automated_responses_total Total safe automated remediation actions executed",
        "# TYPE drishti_automated_responses_total counter",
        f"drishti_automated_responses_total {summary['automated_responses_count']}",
        "",
        "# HELP drishti_prediction_latency_ms Average model inference latency in milliseconds",
        "# TYPE drishti_prediction_latency_ms gauge",
        f"drishti_prediction_latency_ms {summary['avg_prediction_latency_ms']}",
        "",
        "# HELP drishti_prediction_latency_p95_ms 95th percentile inference latency in milliseconds",
        "# TYPE drishti_prediction_latency_p95_ms gauge",
        f"drishti_prediction_latency_p95_ms {summary['p95_prediction_latency_ms']}",
        "",
        "# HELP drishti_mlops_rmse Latest MLOps model Root Mean Squared Error",
        "# TYPE drishti_mlops_rmse gauge",
        f"drishti_mlops_rmse {summary['latest_mlops_rmse']}",
        "",
    ]

    # Add per-project labeled metrics
    with _lock:
        if _state["project_events"]:
            lines.extend([
                "# HELP drishti_project_telemetry_total Telemetry events submitted per project",
                "# TYPE drishti_project_telemetry_total counter",
            ])
            for pid, count in _state["project_events"].items():
                lines.append(f'drishti_project_telemetry_total{{project_id="{pid}"}} {count}')
            lines.append("")

        if _state["project_anomalies"]:
            lines.extend([
                "# HELP drishti_project_anomalies_total Anomalies detected per project",
                "# TYPE drishti_project_anomalies_total counter",
            ])
            for pid, count in _state["project_anomalies"].items():
                lines.append(f'drishti_project_anomalies_total{{project_id="{pid}"}} {count}')
            lines.append("")

    return "\n".join(lines)
