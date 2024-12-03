import os
import subprocess
from pathlib import Path


def fix_file(file_path):
    """Fix line length issues in a single file"""
    print(f"Fixing {file_path}...")

    # Run autopep8 first
    subprocess.run([
        "autopep8",
        "--in-place",
        "--aggressive",
        "--aggressive",
        "--max-line-length=100",
        str(file_path),
    ])

    # Then run black
    subprocess.run(["black", "--line-length=100", str(file_path)])

    # Finally run yapf
    subprocess.run(["yapf", "--in-place", "--style=.style.yapf", str(file_path)])


def main():
    # Walk through all Python files in the project
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                fix_file(file_path)


if __name__ == "__main__":
    main()
