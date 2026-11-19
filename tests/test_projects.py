"""
Tests for Project Registration, Management, and API Key Authentication.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from integration.project_manager import (
    register_project,
    list_projects,
    get_project,
    verify_project_api_key,
    authenticate_api_key,
    load_projects,
    save_projects,
)


def run_tests():
    print("--- [Test Suite 1: Projects & Authentication] ---")

    test_pid = "test-unit-project"

    # Clean any leftover
    projs = [p for p in load_projects() if p["project_id"] != test_pid]
    save_projects(projs)

    # 1. Register Project
    proj, raw_key = register_project(
        project_id=test_pid,
        name="Unit Test Model",
        description="Test project for unit test suite",
        model_type="classification",
        framework="pytorch",
    )
    assert proj["project_id"] == test_pid, "Project ID mismatch"
    assert raw_key.startswith("dr_live_"), "Invalid key prefix"
    assert "api_key_hash" not in proj, "Hash exposed in public dict"
    print("✓ Project registration passed")

    # 2. Reject Duplicate Project ID
    try:
        register_project(project_id=test_pid, name="Duplicate")
        assert False, "Duplicate project allowed"
    except ValueError:
        print("✓ Duplicate project ID rejected properly")

    # 3. Authenticate with Valid Key
    is_valid = verify_project_api_key(test_pid, raw_key)
    assert is_valid is True, "Valid API key failed verification"
    resolved_pid = authenticate_api_key(raw_key)
    assert resolved_pid == test_pid, "Failed to resolve project_id from API key"
    print("✓ API Key authentication verified")

    # 4. Reject Invalid Key
    is_invalid = verify_project_api_key(test_pid, "dr_live_invalid_bad_key")
    assert is_invalid is False, "Invalid key falsely authenticated"
    assert authenticate_api_key("dr_live_wrong") is None, "Wrong key resolved project"
    print("✓ Invalid API Key correctly rejected")

    # 5. List Projects & Key Masking
    all_projs = list_projects()
    found = next((p for p in all_projs if p["project_id"] == test_pid), None)
    assert found is not None, "Registered project not in list"
    assert "..." in found["api_key_masked"], "API key not masked"
    print("✓ Project listing and key masking verified")

    # Clean up
    projs = [p for p in load_projects() if p["project_id"] != test_pid]
    save_projects(projs)
    print("✓ Cleaned up test project. Suite 1 Passed!\n")


if __name__ == "__main__":
    run_tests()

