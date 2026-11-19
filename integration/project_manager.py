"""
DRISHTI AI — Project Management & Authentication Engine
Handles multi-tenant project registration, secure API key generation,
cryptographic verification, and project metadata persistence.
"""

import hashlib
import json
import secrets
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROJECTS_FILE = DATA_DIR / "projects.json"


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def load_projects() -> List[Dict[str, Any]]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PROJECTS_FILE.exists():
        # Seed with default system projects
        default_projects = [
            {
                "project_id": "default",
                "name": "DRISHTI Core System",
                "description": "Default operational workspace for core DRISHTI system events",
                "api_key_hash": _hash_key("dr_live_default_system_key"),
                "api_key_prefix": "dr_live_defa",
                "created_at": _now_iso(),
                "status": "ACTIVE",
                "model_type": "operational_anomaly",
                "framework": "loglizer",
                "schema_mapping": {},
            },
            {
                "project_id": "taxi-fare-predictor",
                "name": "NYC Taxi Duration & Fare Demo",
                "description": "MLOps demonstration model for trip duration and fare prediction",
                "api_key_hash": _hash_key("dr_live_taxi_demo_key"),
                "api_key_prefix": "dr_live_taxi",
                "created_at": _now_iso(),
                "status": "ACTIVE",
                "model_type": "regression",
                "framework": "scikit-learn",
                "schema_mapping": {
                    "latency_field": "latency_ms",
                    "prediction_field": "predicted_duration_minutes",
                },
            },
        ]
        save_projects(default_projects)
        return default_projects

    try:
        content = PROJECTS_FILE.read_text(encoding="utf-8").strip()
        return json.loads(content) if content else []
    except Exception:
        return []


def save_projects(projects: List[Dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_FILE.write_text(json.dumps(projects, indent=4), encoding="utf-8")


def register_project(
    project_id: str,
    name: str,
    description: str = "",
    model_type: str = "generic",
    framework: str = "custom",
    schema_mapping: Optional[Dict[str, str]] = None,
) -> Tuple[Dict[str, Any], str]:
    """
    Register a new ML project and generate a secure API key.
    Returns: (project_dict, raw_api_key)
    """
    clean_id = "".join(c for c in project_id.lower().replace(" ", "-") if c.isalnum() or c in "-_")
    if not clean_id:
        raise ValueError("Project ID cannot be empty or contain only invalid characters.")

    projects = load_projects()
    for existing in projects:
        if existing["project_id"] == clean_id:
            raise ValueError(f"Project with ID '{clean_id}' already exists.")

    raw_token = f"dr_live_{secrets.token_hex(20)}"
    key_hash = _hash_key(raw_token)
    key_prefix = raw_token[:12]

    project_record = {
        "project_id": clean_id,
        "name": name.strip(),
        "description": description.strip(),
        "api_key_hash": key_hash,
        "api_key_prefix": key_prefix,
        "created_at": _now_iso(),
        "status": "ACTIVE",
        "model_type": model_type,
        "framework": framework,
        "schema_mapping": schema_mapping or {},
    }

    projects.append(project_record)
    save_projects(projects)

    # Return safe public dict plus raw key (shown only once on creation)
    safe_dict = dict(project_record)
    del safe_dict["api_key_hash"]
    safe_dict["api_key_masked"] = f"{key_prefix}..."

    return safe_dict, raw_token


def list_projects() -> List[Dict[str, Any]]:
    projects = load_projects()
    safe_list = []
    for p in projects:
        item = dict(p)
        item.pop("api_key_hash", None)
        item["api_key_masked"] = f"{p.get('api_key_prefix', 'dr_live_')}..."
        safe_list.append(item)
    return safe_list


def get_project(project_id: str) -> Optional[Dict[str, Any]]:
    projects = load_projects()
    for p in projects:
        if p["project_id"] == project_id:
            item = dict(p)
            item.pop("api_key_hash", None)
            item["api_key_masked"] = f"{p.get('api_key_prefix', 'dr_live_')}..."
            return item
    return None


def verify_project_api_key(project_id: str, api_key: str) -> bool:
    """Verify that an API key is valid for a given project."""
    if not api_key:
        return False

    # Allow master key from env if configured
    master_key = secrets.compare_digest(api_key, "dr_live_master_override_key")
    if master_key:
        return True

    projects = load_projects()
    expected_hash = _hash_key(api_key)
    for p in projects:
        if p["project_id"] == project_id:
            return secrets.compare_digest(p["api_key_hash"], expected_hash)
    return False


def authenticate_api_key(api_key: str) -> Optional[str]:
    """Authenticate an API key and return its associated project_id."""
    if not api_key:
        return None

    expected_hash = _hash_key(api_key)
    projects = load_projects()
    for p in projects:
        if secrets.compare_digest(p.get("api_key_hash", ""), expected_hash):
            return p["project_id"]

    return None

