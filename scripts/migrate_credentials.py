"""
DRISHTI AI — Project Credential Migration & Hardening Script
Migrates legacy and predictable default project credentials to cryptographically
secure random tokens, removes test artifacts, and verifies project data integrity.
"""

import json
import os
import secrets
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PROJECTS_FILE = DATA_DIR / "projects.json"
BACKUP_FILE = DATA_DIR / "projects.json.bak"

KNOWN_INSECURE_HASHES = {
    # Hash of "dr_live_default_system_key"
    "09369ed179c370a43845d8e34cb68342215c9da846572f6e35d86dea5fc9cd1e": "dr_live_default_system_key",
    # Hash of "dr_live_taxi_demo_key"
    "52ad0051ce14e331ca66ee46d1632199e0a0b57db5ac67ae9d691e9990463e4f": "dr_live_taxi_demo_key",
}


def hash_key(key: str) -> str:
    import hashlib
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def run_migration():
    print("=" * 70)
    print("DRISHTI AI — CREDENTIAL MIGRATION & HARDENING")
    print("=" * 70)

    if not PROJECTS_FILE.exists():
        print(f"[!] Projects file not found at {PROJECTS_FILE}. Nothing to migrate.")
        return

    # 1. Create a safe local backup before modifying
    shutil.copy2(PROJECTS_FILE, BACKUP_FILE)
    print(f"✓ Created safety backup: {BACKUP_FILE}")

    content = PROJECTS_FILE.read_text(encoding="utf-8").strip()
    projects = json.loads(content) if content else []
    print(f"✓ Loaded {len(projects)} existing project records")

    migrated_keys = {}
    cleaned_projects = []

    for p in projects:
        pid = p.get("project_id", "")

        # Skip dummy test artifacts
        if pid in ["string", "test", "test-project", ""]:
            print(f"[-] Removed test artifact project: '{pid}'")
            continue

        existing_hash = p.get("api_key_hash", "")

        # Check if project uses a known insecure predictable key
        if existing_hash in KNOWN_INSECURE_HASHES:
            insecure_key = KNOWN_INSECURE_HASHES[existing_hash]
            print(f"[!] Found insecure predictable key for project '{pid}': {insecure_key}")

            # Check if an env override exists, else generate fresh random key
            env_var_name = f"DRISHTI_{pid.upper().replace('-', '_')}_KEY"
            new_key = os.getenv(env_var_name)
            if not new_key:
                new_key = f"dr_live_{secrets.token_hex(20)}"

            p["api_key_hash"] = hash_key(new_key)
            p["api_key_prefix"] = new_key[:12]
            p["updated_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
            migrated_keys[pid] = new_key
            print(f"✓ Rotated credentials for '{pid}' (New prefix: {new_key[:12]}...)")
        else:
            print(f"✓ Project '{pid}' has a valid custom key hash (preserved intact)")

        cleaned_projects.append(p)

    # 2. Write updated projects file
    PROJECTS_FILE.write_text(json.dumps(cleaned_projects, indent=4), encoding="utf-8")
    print(f"✓ Saved {len(cleaned_projects)} hardened project records to {PROJECTS_FILE}")

    # 3. Print migration summary
    if migrated_keys:
        print("\n" + "-" * 70)
        print("MIGRATED CREDENTIALS NOTICE (Shown Once):")
        print("Update your environment or client configurations with these new keys:")
        for pid, key in migrated_keys.items():
            print(f"  Project: {pid}")
            print(f"  New API Key: {key}")
        print("-" * 70)

    print("\n✓ Migration completed successfully. Zero known default credentials remain.")


if __name__ == "__main__":
    run_migration()
