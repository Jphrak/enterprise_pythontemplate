# Python Engineering Template

A public, environment-agnostic template for building maintainable Python 3.12+
applications. It focuses on code quality, typing, testing, logging, and local
configuration while remaining tool- and organization-neutral.

## What It Demonstrates

- Modern Python 3.12+ syntax and complete type hints
- Ruff linting and formatting
- Strict MyPy type checking
- Pytest with branch coverage
- Structured JSON and human-readable text logging
- Dataclass-based JSON configuration with validation
- Optional configuration file watching
- Cross-platform development scripts for PowerShell and Bash

## Project Structure

```text
python-template/
├── .github/
│   └── copilot-instructions.md
├── src/
│   ├── example.py
│   └── utils/
│       ├── config.py
│       ├── config_watcher.py
│       └── logger.py
├── tests/
│   ├── fixtures/
│   ├── src/
│   └── test_app.py
├── app.py
├── config.example.json
├── config_watch.example.ini
├── CONTRIBUTING.md
├── pyproject.toml
├── PYTHON_STANDARDS.md
├── requirements.txt
├── requirements-dev.txt
├── scripts.ps1
└── scripts.sh
```

## Getting Started

### Prerequisites

- Python 3.12 or newer
- The standard-library `venv` module

### Setup

Windows:

```powershell
python -m venv .venv
& .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item config.example.json config.json
.\scripts.ps1 build
```

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp config.example.json config.json
./scripts.sh build
```

## Development Commands

| Action | Windows | Linux/macOS |
|---|---|---|
| Full validation | `.\scripts.ps1 build` | `./scripts.sh build` |
| Tests | `.\scripts.ps1 test` | `./scripts.sh test` |
| Tests with coverage | `.\scripts.ps1 test-cov` | `./scripts.sh test-cov` |
| Type checking | `.\scripts.ps1 mypy` | `./scripts.sh mypy` |
| Lint check | `.\scripts.ps1 check` | `./scripts.sh check` |
| Format | `.\scripts.ps1 format` | `./scripts.sh format` |
| Apply safe fixes | `.\scripts.ps1 fix` | `./scripts.sh fix` |

The `build` command runs formatting checks, linting, MyPy, and tests. Use
`test-cov` to generate the detailed coverage report.

## Configuration

Copy `config.example.json` to the ignored `config.json` file. The example
application loads configuration from the project working directory and validates
required fields before startup.

`log_type` accepts:

- `TEXT` for human-readable logs
- `JSON` for structured logs

Do not commit credentials or other sensitive values. The included configuration
file is intentionally an example; applications should integrate an appropriate
secret-management mechanism for their own requirements.

To enable automatic reload during development, copy
`config_watch.example.ini` to the ignored `config_watch.ini`.

## Engineering Guidelines

- Add type hints to every function and method.
- Use lazy logging arguments: `logger.info("Processed %s", item_id)`.
- Use explicit validation and exceptions instead of runtime `assert` statements.
- Use absolute imports.
- Add tests for new behavior and failure paths.
- Use `tmp_path` for files created by tests.
- Run the full build before committing.

See [PYTHON_STANDARDS.md](PYTHON_STANDARDS.md) for the complete development
guidelines and [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow.

## Scope

This repository deliberately excludes operational manifests, organization-specific
automation, service references, and environment topology. Those concerns belong in
the consuming application's private operational configuration.
