import os
import subprocess


def fix_file(file_path):
    # Run autopep8 with aggressive mode and line length 100
    subprocess.run([
        "autopep8",
        "--in-place",
        "--aggressive",
        "--aggressive",
        "--max-line-length=100",
        file_path,
    ])

    # Run black as a backup
    subprocess.run(["black", "--line-length=100", file_path])


def main():
    # Walk through all Python files in sdk directory
    for root, dirs, files in os.walk("sdk"):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                print(f"Fixing {file_path}...")
                fix_file(file_path)


if __name__ == "__main__":
    main()
