#!/usr/bin/env python3
"""Script to fix import sorting in Python files."""

import subprocess
from pathlib import Path

FILES_TO_FIX = [
    "sdk/test/adapter/json/test_json_serialization.py",
    "sdk/test/adapter/json/test_json_serialization_deserialization.py",
    "sdk/test/adapter/aasx/test_aasx.py",
    "sdk/basyx/aas/adapter/http.py",
    "sdk/basyx/aas/adapter/json/json_serialization.py",
    "sdk/basyx/aas/adapter/json/json_deserialization.py",
    "sdk/basyx/aas/model/submodel.py",
    "sdk/basyx/aas/model/provider.py",
    "sdk/basyx/aas/backend/couchdb.py",
]

def fix_imports():
    """Fix import sorting in specified files."""
    for file_path in FILES_TO_FIX:
        print(f"Fixing imports in {file_path}")
        subprocess.run(["isort", "--profile=black", file_path], check=True)

if __name__ == "__main__":
    fix_imports() 