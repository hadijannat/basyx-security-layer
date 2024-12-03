#!/usr/bin/env python3
"""Script to fix import sorting in Python files."""

import subprocess

FILES_TO_FIX = [
    "sdk/basyx/aas/backend/couchdb.py",
    "sdk/examples/secure_aas_example.py",
    "sdk/test/test_security.py",
]


def fix_imports():
    """Fix import sorting in specified files."""
    for file_path in FILES_TO_FIX:
        print(f"Fixing imports in {file_path}")
        try:
            subprocess.run(
                [
                    "isort",
                    "--profile=black",
                    "--line-length=100",
                    "--multi-line=3",
                    "--trailing-comma",
                    file_path,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error fixing imports in {file_path}: {e}")


if __name__ == "__main__":
    fix_imports()
