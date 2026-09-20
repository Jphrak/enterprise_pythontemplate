# Contributing to This Project

Thank you for contributing! This guide will help you get started.

## Quick Start

1. Clone the repository
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\Activate.ps1
   # Linux/Mac
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

   The project scripts use `pip` and the standard-library `venv` module.

4. Verify setup:

   ```bash
   .\scripts.ps1 build  # Windows
   ./scripts.sh build   # Linux/Mac
   ```

## Development Workflow

### Branch Naming

Use descriptive branch names that clearly convey the purpose of the change (e.g., `add-user-auth`, `fix-config-loading`, `update-readme`).

### Making Changes

1. Create a branch from `main`
2. Make your changes
3. Run the build pipeline:

   ```bash
   .\scripts.ps1 build  # Windows
   ./scripts.sh build   # Linux/Mac
   ```

4. Commit with a clear message
5. Push and open a Pull Request

### Commit Messages

Use clear, descriptive commit messages:

```text
Add user authentication endpoint

- Implement JWT token generation
- Add password hashing utility
- Include unit tests for auth flow
```

## Build Commands

**Important**: `build` and `dev-check` run all steps even if one fails, showing all errors at once.

| Command                   | Purpose                                          |
|---------------------------|--------------------------------------------------|
| `.\scripts.ps1 build`     | Full pipeline: format + lint + type check + test |
| `.\scripts.ps1 dev-check` | Quick check during development                   |
| `.\scripts.ps1 test`      | Run tests only                                   |
| `.\scripts.ps1 test-cov`  | Run tests with coverage report                   |
| `.\scripts.ps1 format`    | Auto-format code                                 |
| `.\scripts.ps1 fix`       | Lint and auto-fix issues                         |

For Linux/Mac, use `./scripts.sh` instead.

## Code Standards

See [PYTHON_STANDARDS.md](PYTHON_STANDARDS.md) for complete guidelines.

### Key Rules

- **Type hints**: Required on all functions (use modern Python 3.12+ syntax)

  ```python
  def process(name: str, count: int | None = None) -> list[str]:
  ```

- **Date/Time**: Always use Pendulum, never datetime

  ```python
  # Correct
  import pendulum
  now = pendulum.now()

  # Wrong
  from datetime import datetime
  now = datetime.now()
  ```

- **Logging**: Use format strings, not f-strings
- **Log safety**: Unicode in log arguments is automatically sanitized to protect against log injection from external sources

  ```python
  # Correct
  logger.info("Processing %s", username)

  # Wrong
  logger.info(f"Processing {username}")
  ```

- **Function calls**: Prefer keyword arguments for clarity

  ```python
  # Correct
  process_data(filename="data.json", timeout=30)

  # Acceptable for obvious cases
  len(items)
  ```

- **Imports**: Absolute imports only

  ```python
  # Correct
  from src.utils.config import Config

  # Wrong
  from .utils.config import Config
  ```

- **Tests**: Required for all new functionality (aim for 90% coverage)

## Testing

### Test Location

Mirror the source structure:

- `src/utils/config.py` -> `tests/src/utils/test_config.py`

### Mocking

**Always use pytest's `monkeypatch`, never `unittest.mock.patch`.**

Grouping test functions in classes is fine, but do not inherit from `unittest.TestCase`.

Patch where the object is *used*, not where it's defined:

```python
from unittest.mock import MagicMock

# Correct - patch in the module that imports it
def test_example(monkeypatch):
    monkeypatch.setattr("src.example.Config", MagicMock())

# Wrong - patching the original location
def test_example(monkeypatch):
    monkeypatch.setattr("src.utils.config.Config", MagicMock())
```

### Coverage

- Aim for 90% test coverage
- Focus on critical paths and business logic
- Use `test-cov` command to check coverage locally

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] `.\scripts.ps1 build` passes
- [ ] Type hints added to new functions (modern syntax: `str | None`)
- [ ] Tests written for new functionality (90% coverage goal)
- [ ] Docstrings on public APIs
- [ ] Using Pendulum for date/time operations (not datetime)
- [ ] Using keyword arguments for function calls (when not obvious)
- [ ] No f-strings in logging calls
- [ ] No unicode characters in code (only ASCII)
- [ ] No debug code or temporary changes
- [ ] Using `monkeypatch` for mocking (not `unittest.mock.patch`)

## Getting Help

- Review existing code for patterns
- Check [PYTHON_STANDARDS.md](PYTHON_STANDARDS.md) for detailed guidelines
- Ask questions in your PR if unsure
