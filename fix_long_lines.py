#!/usr/bin/env python3
"""Script to find and fix Python files with lines over 100 characters."""

import os
import subprocess
from pathlib import Path


def check_line_length(file_path: Path) -> bool:
    """Check if file has any lines over 100 characters."""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if len(line.rstrip()) > 100:
                print(f"{file_path}:{line_num}: Line too long ({len(line.rstrip())} > 100 characters)")
                return True
    return False


def fix_file(file_path: Path) -> None:
    """Fix line length issues in a file."""
    print(f"\nFixing {file_path}...")
    
    # Run autopep8 first for basic formatting
    subprocess.run([
        "autopep8",
        "--in-place",
        "--aggressive",
        "--aggressive",
        "--max-line-length=100",
        str(file_path)
    ], check=True)
    
    # Run black for consistent formatting
    subprocess.run([
        "black",
        "--line-length=100",
        str(file_path)
    ], check=True)
    
    # Run isort for import sorting
    subprocess.run([
        "isort",
        "--profile=black",
        "--line-length=100",
        str(file_path)
    ], check=True)


def main():
    """Find and fix all Python files with long lines."""
    # Directories to scan
    scan_dirs = [
        "sdk",
        "server",
        "basyx_security",
        "tests",
        "examples"
    ]
    
    # Files to skip
    skip_dirs = {
        "__pycache__",
        "build",
        "dist",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "venv"
    }
    
    files_to_fix = []
    
    # Find all Python files with long lines
    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
            
        for root, dirs, files in os.walk(scan_dir):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if not file.endswith(".py"):
                    continue
                    
                file_path = Path(root) / file
                if check_line_length(file_path):
                    files_to_fix.append(file_path)
    
    if not files_to_fix:
        print("\nNo files found with lines over 100 characters.")
        return
        
    print(f"\nFound {len(files_to_fix)} files with long lines.")
    
    # Fix each file
    for file_path in files_to_fix:
        fix_file(file_path)
        
    print("\nDone! Please review the changes and run your tests.")


if __name__ == "__main__":
    main() 