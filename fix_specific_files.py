import os
import subprocess

FILES_TO_FIX = [
    "sdk/basyx/aas/adapter/http.py",
    "sdk/basyx/aas/adapter/json/json_deserialization.py",
]


def fix_file(file_path):
    """Fix line length issues in a single file"""
    print(f"Fixing {file_path}...")

    # Run autopep8 with aggressive settings
    subprocess.run(
        [
            "autopep8",
            "--in-place",
            "--aggressive",
            "--aggressive",
            "--aggressive",
            "--max-line-length=88",  # More aggressive line length
            file_path,
        ]
    )

    # Then run black
    subprocess.run(["black", "--line-length=88", file_path])  # More aggressive line length

    # Finally run yapf
    subprocess.run(["yapf", "--in-place", "--style=pep8", file_path])


def main():
    for file_path in FILES_TO_FIX:
        if os.path.exists(file_path):
            fix_file(file_path)
        else:
            print(f"File not found: {file_path}")


if __name__ == "__main__":
    main()
