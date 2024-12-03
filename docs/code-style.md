# Code Style Guide

This document outlines the code style guidelines and formatting tools used in the BaSyx Security Layer project.

## Code Formatting Tools

We use several tools to maintain consistent code formatting and quality:

### 1. Black (Code Formatter)
- Primary code formatter
- Line length: 100 characters
- Run first in the formatting pipeline
- Configuration in `pyproject.toml`

### 2. isort (Import Sorter)
- Sorts and formats imports
- Configured to be compatible with Black
- Run after Black
- Configuration in `pyproject.toml`

### 3. Flake8 (Linter)
- Style guide enforcement
- Run last in the pipeline
- Includes additional plugins for enhanced checking
- Configuration in `pyproject.toml`

## Pre-commit Hooks

We use pre-commit hooks to automate code formatting. To set up:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

The hooks will run automatically on `git commit`. You can also run them manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files
pre-commit run
```

## Tool Order and Workflow

The correct order for running formatting tools is:

1. **Black** (Major formatting)
   ```bash
   black .
   ```

2. **isort** (Import sorting)
   ```bash
   isort .
   ```

3. **Flake8** (Style checking)
   ```bash
   flake8
   ```

## Common Issues and Solutions

### Line Length Issues
- Maximum line length is 100 characters
- Black will automatically handle most line wrapping
- For long strings or comments, manual wrapping may be needed

### Import Sorting
- Imports are grouped into three sections:
  1. Standard library imports
  2. Third-party imports
  3. Local imports
- Each section should be separated by a blank line
- Use absolute imports over relative imports

### Code Style Rules

1. **Docstrings**
   - Use Google-style docstrings
   - Required for all public modules, functions, classes, and methods
   - Include type hints in function signatures

2. **Type Hints**
   - Use type hints for all function arguments and return values
   - Use Optional[] for optional parameters
   - Use Union[] for multiple types

3. **Naming Conventions**
   - Classes: PascalCase
   - Functions and variables: snake_case
   - Constants: UPPER_CASE
   - Private attributes: _leading_underscore

4. **Comments**
   - Write clear, concise comments
   - Focus on why, not what
   - Keep comments up-to-date with code changes

## IDE Integration

### VS Code
Recommended settings for VS Code (`settings.json`):
```json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "100"],
    "editor.formatOnSave": true,
    "python.linting.flake8Enabled": true,
    "python.linting.enabled": true,
    "python.sortImports.args": ["--profile", "black"]
}
```

### PyCharm
- Install the Black and Flake8 plugins
- Configure line length to 100
- Enable "Format on Save"
- Set Black as the formatter

## Continuous Integration

Our GitHub Actions workflow includes automated checks for:
- Code formatting (Black)
- Import sorting (isort)
- Style guide compliance (Flake8)
- Type checking (mypy)
- Security vulnerabilities (Bandit, Safety)

Failed checks will block PR merging. 