"""
DRISHTI SDK — Client Library
Enables any external ML application to submit telemetry, predictions, errors,
and performance metrics to the DRISHTI AI platform.
"""

import atexit
import json
import threading
import time
from typing import Dict, Any, List, Optional
import requests

from drishti_sdk.models import TelemetryEvent, _now_iso


class DrishtiClient:
    """
    Client for interacting with DRISHTI AI Telemetry API.

    Features:
    - Thread-safe buffering and batching
    - Automatic background flush
    - Non-blocking error handling (never crashes host ML service)
    - Safe key masking in strings and logs
    """

    def __init__(
        self,
        project_id: str,
        api_key: str,
        endpoint: str = "http://localhost:8001",
        batch_size: int = 10,
        flush_interval_seconds: float = 3.0,
        silent_errors: bool = True,
        timeout: float = 3.0,
    ):
        self.project_id = project_id
        self._api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.batch_size = max(1, batch_size)
        self.flush_interval = flush_interval_seconds
        self.silent_errors = silent_errors
        self.timeout = timeout

        self._buffer: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        # Background worker for periodic auto-flush
        self._flush_thread = threading.Thread(target=self._auto_flush_worker, daemon=True)
        self._flush_thread.start()

        # Register cleanup on process exit
        atexit.register(self.close)

    def __repr__(self) -> str:
        masked_key = f"{self._api_key[:8]}***" if len(self._api_key) > 8 else "***"
        return f"DrishtiClient(project_id='{self.project_id}', endpoint='{self.endpoint}', api_key='{masked_key}')"

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-API-Key": self._api_key,
        }

    def _enqueue(self, event_dict: Dict[str, Any], sync: bool = False) -> Dict[str, Any]:
        if sync:
            return self._send_single(event_dict)

        with self._lock:
            self._buffer.append(event_dict)
            should_flush = len(self._buffer) >= self.batch_size

        if should_flush:
            self.flush()

        return {"status": "queued", "project_id": self.project_id}

    def _send_single(self, event_dict: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.endpoint}/telemetry/ingest"
        payload = {"project_id": self.project_id, "record": event_dict}
        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            if resp.status_code in [200, 201]:
                return resp.json()
            else:
                msg = f"HTTP {resp.status_code}: {resp.text}"
                if not self.silent_errors:
                    raise RuntimeError(msg)
                return {"status": "error", "message": msg}
        except Exception as e:
            if not self.silent_errors:
                raise e
            return {"status": "error", "message": str(e)}

    def log_prediction(
        self,
        prediction: Any,
        model_name: Optional[str] = None,
        model_version: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None,
        latency_ms: Optional[float] = None,
        ground_truth: Optional[Any] = None,
        custom_tags: Optional[Dict[str, Any]] = None,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Log a model prediction event."""
        event = TelemetryEvent(
            event_type="prediction",
            timestamp=_now_iso(),
            model_name=model_name,
            model_version=model_version,
            log_message=f"Prediction executed for {model_name or self.project_id}",
            severity="INFO",
            latency_ms=latency_ms,
            prediction=prediction,
            confidence=confidence,
            ground_truth=ground_truth,
            inputs=inputs,
            custom_tags=custom_tags or {},
        )
        return self._enqueue(event.to_dict(), sync=sync)

    def log_error(
        self,
        error_type: str = "InferenceError",
        message: str = "",
        severity: str = "ERROR",
        stack_trace: Optional[str] = None,
        model_name: Optional[str] = None,
        custom_tags: Optional[Dict[str, Any]] = None,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Log an application or inference error event."""
        event = TelemetryEvent(
            event_type="error",
            timestamp=_now_iso(),
            model_name=model_name,
            log_message=f"{severity}: [{error_type}] {message}",
            severity=severity,
            error_type=error_type,
            error_message=message,
            custom_tags={"stack_trace": stack_trace, **(custom_tags or {})},
        )
        return self._enqueue(event.to_dict(), sync=sync)

    def log_ground_truth(
        self,
        actual_value: Any,
        prediction: Optional[Any] = None,
        model_name: Optional[str] = None,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Log true outcome labels for accuracy tracking and drift analysis."""
        event = TelemetryEvent(
            event_type="ground_truth",
            timestamp=_now_iso(),
            model_name=model_name,
            log_message=f"Ground truth reported for {model_name or self.project_id}",
            severity="INFO",
            prediction=prediction,
            ground_truth=actual_value,
        )
        return self._enqueue(event.to_dict(), sync=sync)

    def log_metrics(
        self,
        cpu_percent: Optional[float] = None,
        memory_mb: Optional[float] = None,
        custom_metrics: Optional[Dict[str, float]] = None,
        sync: bool = False,
    ) -> Dict[str, Any]:
        """Log resource utilization and performance metrics."""
        res: Dict[str, float] = {}
        if cpu_percent is not None:
            res["cpu_percent"] = cpu_percent
        if memory_mb is not None:
            res["memory_mb"] = memory_mb
        if custom_metrics:
            res.update(custom_metrics)

        sev = "WARNING" if (cpu_percent and cpu_percent > 85.0) or (memory_mb and memory_mb > 1500) else "INFO"

        event = TelemetryEvent(
            event_type="system_metrics",
            timestamp=_now_iso(),
            log_message=f"Telemetry metrics for {self.project_id}",
            severity=sev,
            resource_metrics=res,
        )
        return self._enqueue(event.to_dict(), sync=sync)

    def flush(self) -> int:
        """Send all currently buffered events in a single batch."""
        with self._lock:
            if not self._buffer:
                return 0
            items_to_send = list(self._buffer)
            self._buffer.clear()

        url = f"{self.endpoint}/telemetry/batch"
        payload = {"project_id": self.project_id, "records": items_to_send}
        try:
            resp = requests.post(url, json=payload, headers=self._headers(), timeout=self.timeout)
            if resp.status_code in [200, 201]:
                return len(items_to_send)
            else:
                if not self.silent_errors:
                    raise RuntimeError(f"Batch flush error {resp.status_code}: {resp.text}")
                return 0
        except Exception as e:
            if not self.silent_errors:
                raise e
            return 0

    def _auto_flush_worker(self) -> None:
        while not self._stop_event.is_set():
            time.sleep(self.flush_interval)
            try:
                self.flush()
            except Exception:
                pass

    def close(self) -> None:
        """Flush remaining events and terminate worker thread."""
        self._stop_event.set()
        try:
            self.flush()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

