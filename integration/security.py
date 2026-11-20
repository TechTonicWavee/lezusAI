"""
DRISHTI AI — Authentication & Access Control Dependencies
Provides role-appropriate FastAPI authorization dependencies:
- Admin-only routes (project registration, model promotion, training triggers)
- Operator / Auditor routes (incident management, remediation)
- Project-isolated routes (telemetry ingestion, logs, drift queries)
- Safe extraction from X-API-Key, Authorization Bearer, or query parameters
"""

import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, Header, Query, Request, Depends, status

from integration.project_manager import (
    verify_admin_key,
    verify_operator_key,
    verify_project_api_key,
    authenticate_api_key,
    get_project,
)


def extract_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    key: Optional[str] = Query(None, alias="key"),
    api_key: Optional[str] = Query(None, alias="api_key"),
) -> Optional[str]:
    """
    Extract the client API key from standard HTTP headers or query parameters.
    Supports:
    1. 'X-API-Key: <key>'
    2. 'Authorization: Bearer <key>' or 'Authorization: ApiKey <key>'
    3. '?key=<key>' or '?api_key=<key>' (convenience for dashboards and Prometheus scrapers)
    """
    if x_api_key and x_api_key.strip():
        return x_api_key.strip()

    if authorization and authorization.strip():
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() in ["bearer", "apikey", "key"]:
            return parts[1].strip()
        return authorization.strip()

    if key and key.strip():
        return key.strip()

    if api_key and api_key.strip():
        return api_key.strip()

    return None


def require_admin_auth(token: Optional[str] = Depends(extract_api_key)) -> str:
    """
    Enforce administrator authorization.
    Fails closed if master key is missing on the server or token is invalid.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing 'X-API-Key' or 'Authorization' header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not verify_admin_key(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden. Administrator credentials required.",
        )

    return token


def require_operator_or_admin_auth(token: Optional[str] = Depends(extract_api_key)) -> str:
    """
    Enforce operator or administrator authorization.
    Allows platform-wide incident triage, remediation triggering, and MLOps viewing.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing 'X-API-Key' or 'Authorization' header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if verify_admin_key(token) or verify_operator_key(token):
        return token

    # Check if this is a valid active project key (allowed for project-scoped operations)
    authenticated_pid = authenticate_api_key(token)
    if authenticated_pid:
        return token

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden. Operator or Administrator credentials required.",
    )


def verify_project_ownership_or_admin(project_id: str, token: Optional[str]) -> str:
    """
    Verify that the supplied token grants access to the specified project_id.
    Valid if:
    1. Token matches DRISHTI_MASTER_API_KEY (Administrator)
    2. Token is a valid active API key for project_id
    Fails with 401 if missing, 404 if project nonexistent, 403 if unauthorized.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing 'X-API-Key' or 'Authorization' header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # 1. Administrator override
    if verify_admin_key(token):
        return token

    # 2. Check project existence
    project = get_project(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found.",
        )

    # 3. Check project-specific key
    if not verify_project_api_key(project_id, token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied for project '{project_id}'. Invalid API key.",
        )

    return token


def get_authenticated_scope(token: Optional[str] = Depends(extract_api_key)) -> Dict[str, Any]:
    """
    Determine the caller's identity and privilege level:
    - { role: "admin", project_id: None }
    - { role: "operator", project_id: None }
    - { role: "project", project_id: "<project_id>" }
    - { role: "anonymous", project_id: None }
    """
    if not token:
        return {"role": "anonymous", "project_id": None, "authenticated": False}

    if verify_admin_key(token):
        return {"role": "admin", "project_id": None, "authenticated": True}

    if verify_operator_key(token):
        return {"role": "operator", "project_id": None, "authenticated": True}

    pid = authenticate_api_key(token)
    if pid:
        return {"role": "project", "project_id": pid, "authenticated": True}

    return {"role": "invalid", "project_id": None, "authenticated": False}


def require_metrics_auth(token: Optional[str] = Depends(extract_api_key)) -> bool:
    """
    Authorization for Prometheus /metrics endpoint.
    If DRISHTI_ALLOW_ANONYMOUS_METRICS=true is configured, scraping is public.
    Otherwise requires DRISHTI_METRICS_KEY, DRISHTI_MASTER_API_KEY, or operator key.
    """
    allow_public = os.getenv("DRISHTI_ALLOW_ANONYMOUS_METRICS", "false").lower() in ["true", "1", "yes"]
    if allow_public:
        return True

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to scrape Prometheus metrics.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    metrics_key = os.getenv("DRISHTI_METRICS_KEY")
    if metrics_key and metrics_key.strip():
        import secrets
        if secrets.compare_digest(token.strip(), metrics_key.strip()):
            return True

    if verify_admin_key(token) or verify_operator_key(token):
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden. Invalid metrics scraper credentials.",
    )
