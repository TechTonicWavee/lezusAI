"""
DRISHTI SDK - Data Schemas
Defines structured telemetry event models for ML applications.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass
class TelemetryEvent:
    event_type: str = "prediction"
    timestamp: str = field(default_factory=_now_iso)
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    log_message: Optional[str] = None
    severity: str = "INFO"
    latency_ms: Optional[float] = None
    prediction: Optional[Any] = None
    confidence: Optional[float] = None
    ground_truth: Optional[Any] = None
    inputs: Optional[Dict[str, Any]] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    resource_metrics: Optional[Dict[str, float]] = None
    custom_tags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}

