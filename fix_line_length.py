#!/usr/bin/env python3
"""Script to fix line length issues in Python files."""

import subprocess
from pathlib import Path


def find_python_files(directory="."):
    """Find all Python files in the given directory and subdirectories."""
    return list(Path(directory).rglob("*.py"))


def fix_line_length(file_path):
    """Fix line length issues in a single file."""
    print(f"Fixing line length in {file_path}")

    # First use autopep8 to handle basic line wrapping
    subprocess.run(
        [
            "autopep8",
            "--in-place",
            "--aggressive",
            "--max-line-length=100",
            str(file_path),
        ],
        check=True,
    )

    # Then use black to ensure consistent formatting
    subprocess.run(["black", "--line-length=100", str(file_path)], check=True)


def main():
    """Find and fix all Python files with line length issues."""
    # Directories to scan
    scan_dirs = ["sdk", "server", "tests", "examples"]

    # Directories to skip
    skip_dirs = {
        "__pycache__",
        "build",
        "dist",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "venv",
    }

    for scan_dir in scan_dirs:
        if not Path(scan_dir).exists():
            continue

        for file_path in Path(scan_dir).rglob("*.py"):
            # Skip files in excluded directories
            if any(d in file_path.parts for d in skip_dirs):
                continue

            fix_line_length(file_path)


if __name__ == "__main__":
    main()
