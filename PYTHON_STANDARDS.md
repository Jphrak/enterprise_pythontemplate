# Python Development Standards

This document defines the coding standards and best practices for this Python project. All developers should follow these guidelines to maintain code quality and consistency.

## Project Overview

- **Language**: Python 3.12+
- **Testing Framework**: pytest
- **Linting & Formatting**: Ruff
- **Type Checking**: MyPy
- **Target Platforms**: Windows (PowerShell), Linux/Mac (Bash)

## Environment Setup

### Prerequisites

- Python 3.12 or higher
- Virtual environment (`.venv` directory)

### Initial Setup

1. **Create and activate virtual environment:**

   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\Activate.ps1
   # Linux/Mac
   source .venv/bin/activate
   ```

2. **Install development dependencies:**

   ```bash
   pip install -r requirements-dev.txt
   ```

   Note: `requirements-dev.txt` automatically includes `requirements.txt`

> **Note:** The included scripts use `pip` and the standard-library `venv`
> module so setup remains portable and easy to inspect.

## Build Commands

### Windows (PowerShell)

Use `.\scripts.ps1 <command>` for all build operations:

- `.\scripts.ps1 dev-setup` - Install development dependencies
- `.\scripts.ps1 build` - **Run full build pipeline** (format + lint + type check + test)
- `.\scripts.ps1 dev-check` - Quick validation (faster than full build)
- `.\scripts.ps1 test` - Run test suite
- `.\scripts.ps1 format` - Auto-format code with Ruff
- `.\scripts.ps1 check` - Lint code without making changes
- `.\scripts.ps1 fix` - Lint and auto-fix issues
- `.\scripts.ps1 mypy` - Type check main code
- `.\scripts.ps1 run` - Run the application
- `.\scripts.ps1 test-cov` - Run tests with coverage report
- `.\scripts.ps1 lint-all` - Run all linting checks

### Linux/Mac

Use `./scripts.sh <command>` with the same command names as above.

### Recommended Workflow

**Before committing changes:**

```bash
.\scripts.ps1 build  # Windows
./scripts.sh build   # Linux/Mac
```

This runs: format → lint → type check → tests (takes ~10-15 seconds)

**During development:**

```bash
.\scripts.ps1 dev-check  # Quick validation
.\scripts.ps1 test       # Run tests only
```

## Code Style Standards

### Type Hints

**Required** on all function parameters, return values, and class attributes.

**Use modern Python 3.12+ syntax:**

```python
# ✅ Correct - Modern union syntax
def process_data(name: str, age: int | None = None) -> list[str]:
    pass

# ❌ Incorrect - Old typing module syntax
from typing import Optional, List, Union
def process_data(name: str, age: Optional[int] = None) -> List[str]:
    pass
```

**Modern type hint syntax:**

- `str | None` instead of `Optional[str]` or `Union[str, None]`
- `list[str]` instead of `List[str]`
- `dict[str, int]` instead of `Dict[str, int]`

### Logging

**CRITICAL: Always use format strings, never f-strings in logging calls.**

```python
import logging

logger = logging.getLogger(__name__)

# ✅ Correct - Format string
logger.info("Processing user %s with status %s", username, status)
logger.error("Failed to connect to %s: %s", host, error)

# ❌ Incorrect - F-string (DO NOT USE)
logger.info(f"Processing user {username} with status {status}")
```

**Why?** Format strings are lazy-evaluated, improving performance when log level is disabled.

### String Formatting

For general string formatting (not logging), use f-strings:

```python
# ✅ Correct - F-strings for general formatting
message = f"User {username} logged in at {timestamp}"
output = f"{value!s}"  # str() conversion
debug = f"{obj!r}"     # repr() conversion

# For logging, use format strings (see Logging section)
logger.info("User %s logged in at %s", username, timestamp)
```

### Imports

```python
# ✅ Correct - Absolute imports
from src.module import function_name
from src.utils.helpers import helper_func

# ❌ Incorrect - Relative imports
from .module import function_name
from ..utils.helpers import helper_func
```

**Import logging:**

```python
import logging

logger = logging.getLogger(__name__)
```

**Import order:**

- Standard library → Third-party → Local imports (Ruff handles sorting automatically)
- No `__init__.py` files - Use implicit namespace packages

**TYPE_CHECKING imports:**

Use `TYPE_CHECKING` blocks for imports that are only needed for type annotations. This avoids runtime import overhead and helps prevent circular imports. Requires `from __future__ import annotations` at the top of the module.

```python
# Use TYPE_CHECKING for imports only needed by type hints
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.utils.config import Config  # Only used in type hints
```

### Code Style

**Formatting standards:**

- **Line length**: 100 characters maximum
- **Indentation**: 4 spaces (never tabs)
- **File ending**: All .py files must end with exactly one blank line
- **No trailing whitespace**: Ruff will remove it
- **Characters**: No unicode characters in code -- use ASCII only

**Function calls:**

Prefer keyword arguments over positional arguments for clarity:

```python
# ✅ Correct - Keyword arguments (explicit and clear)
start_config_watcher(interval=600.0)
process_data(filename="data.json", max_retries=3, timeout=30)
Config(host="localhost", port=8080)

# ✅ Acceptable - Positional for obvious/simple cases
len(items)
str(value)
print("message")

# ❌ Incorrect - Positional arguments when unclear
start_config_watcher(600.0)  # What does 600.0 mean?
process_data("data.json", 3, 30)  # Unclear what 3 and 30 represent
```

**noqa comments:**

Use sparingly with clear justification. The reason must be on the same line as the `noqa` comment, in the format `# noqa: <RULE> - <reason>`:

```python
# ✅ Acceptable - Clear reason
try:
    setup_logging()
except:  # noqa: E722 - Fallback before logging configured
    print("Logging setup failed")

# ❌ Not acceptable - No justification
def function():
    pass  # noqa: E501
```

### Date and Time Handling

**ALWAYS use Pendulum, never Python's datetime:**

```python
import pendulum  # ALWAYS use pendulum, never datetime

# ✅ Correct - Pendulum
now: pendulum.DateTime = pendulum.now()
parsed: pendulum.DateTime = pendulum.parse("2024-01-15")
formatted: str = now.to_iso8601_string()

# ❌ Incorrect - datetime
from datetime import datetime
now = datetime.now()
```

**Why Pendulum?**

- Better timezone handling
- Human-readable date differences
- Cleaner, more intuitive API
- Industry-standard for Python date/time operations

### Exception Handling

```python
# ✅ Correct - Specific exception types
try:
    result = risky_operation()
except ValueError as e:
    logger.error("Invalid value: %s", e)
except FileNotFoundError as e:
    logger.error("File not found: %s", e)

# ❌ Incorrect - Bare except
try:
    result = risky_operation()
except:
    logger.error("Something went wrong")
```

- Use specific exception types
- Log errors with sufficient context
- Place try-except close to the error source
- Don't suppress exceptions without good reason

### Assert Usage

**Outside of tests, `assert` should only be used for mypy type narrowing, not runtime validation.** Assertions are stripped when Python runs with `-O` (optimized mode), so any validation relying on `assert` silently disappears in production. Use `if`/`raise` for runtime validation as early as practical.

```python
# ✅ Correct - Runtime validation with early check
def process(data: dict[str, str] | None) -> str:
    if data is None:
        raise ValueError("data is required")
    return data["key"]

# ✅ Correct - Assert for mypy type narrowing only
result = get_optional_value()
assert isinstance(result, str)  # Narrowing for mypy
process_string(result)

# ❌ Wrong - Assert for runtime validation
def process(data: dict[str, str] | None) -> str:
    assert data is not None  # Stripped by python -O!
    return data["key"]
```

### Asynchronous Code

Use async/await for I/O-bound operations:

```python
# ✅ Correct - Async for I/O operations
async def fetch_data(url: str) -> dict[str, str]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Use asyncio.TaskGroup for concurrent operations (Python 3.11+)
async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(fetch_data(url1))
    task2 = tg.create_task(fetch_data(url2))
    task3 = tg.create_task(fetch_data(url3))
# All tasks are awaited and errors cancel sibling tasks automatically
results = [task1.result(), task2.result(), task3.result()]
```

**Best practices:**

- Use `async with` for resource management
- Always await async functions
- Never mix sync and async patterns without proper handling
- Prefer `asyncio.TaskGroup` over `asyncio.gather()` for structured concurrency and better error handling
- Async code is not included in this template — when adding async features, use `pytest-asyncio` and test with `@pytest.mark.asyncio` to ensure proper coverage

### Dataclasses vs Regular Classes

**Use dataclasses for simple data containers:**

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    age: int | None = None

# For immutable data
@dataclass(frozen=True)
class Config:
    host: str
    port: int

# For memory efficiency with many instances
@dataclass(slots=True)
class Point:
    x: float
    y: float
```

**Use regular classes when you need:**

- Complex behavior or inheritance
- Custom `__init__` logic
- Methods that modify state in complex ways

### Code Organization

**Module Design:**

- **Prefer classes and structured patterns over module-level code**: Organize logic into classes or functions rather than executing code at module level
- **Use classes for stateful behavior**: When code needs to maintain state, use classes with clear initialization and lifecycle
- **Use functions for stateless operations**: Pure functions are acceptable for utility operations without state
- **Minimize module-level execution**: Avoid code that runs on import; prefer explicit initialization through functions or class constructors

**Minimize module-level state:**

- Prefer function-based or class-based patterns over global variables
- Use module-level constants for configuration defaults (UPPER_CASE naming)
- Avoid mutable global state
- When module-level variables are necessary (singletons, configuration), initialize them safely
- Document the purpose and lifecycle of any global variables

**Acceptable module-level patterns:**

- Constants (UPPER_CASE): `MAX_RETRIES = 3`
- Type aliases: `UserId = str`
- Configuration singletons: `Config = _init_config()`
- Entry points: `if __name__ == "__main__":`

**Avoid circular dependencies:**

- Use late imports (import inside functions) when necessary
- Pass dependencies as parameters
- Design modules with clear dependency hierarchies

**Module initialization:**

- Should not perform expensive operations
- Should not cause side effects
- Document any module-level variables

### Docstring Standards

#### When to Write Docstrings

**Required for:**

- All public functions and methods (used outside the module)
- All classes (dataclasses and regular classes)
- Complex or non-obvious private functions

**Optional for:**

- Simple private functions with obvious behavior
- Test functions (test name should be descriptive enough)
- Property getters/setters with obvious purpose

#### Docstring Format

```python
def process_batch(items: list[str], max_size: int = 100) -> list[str]:
    """Process a batch of items.

    Args:
        items: List of items to process
        max_size: Maximum batch size

    Returns:
        List of processed items

    Raises:
        ValueError: If items is empty
    """
    # implementation

class ExampleProcessor:
    """Example processor class for data processing operations.

    Attributes:
        name: Identifier for this processor instance
        max_items: Maximum number of items to process
    """
    # implementation
```

#### Docstring Best Practices

- **First line**: One-line summary ending with period
- **Args section**: One line per parameter with description
- **Returns section**: Describe what is returned
- **Raises section**: Document exceptions that can be raised (when not obvious)
- **Keep concise**: Don't repeat type information that's in type hints
- **Use present tense**: "Process items" not "Processes items"

### Print Statements

```python
# ❌ Never use print() in production code
print("Debug message")

# ✅ Use logging instead
logger.debug("Debug message")

# ✅ Exception: Infrastructure code initialization fallbacks
# (only when logging is not yet configured)
try:
    logger.info("Starting application")
except Exception:  # noqa: BLE001 - Fallback before logging is ready
    print("Starting application")
```

### File Formatting

- Files must end with a blank line
- Use consistent indentation (4 spaces)
- Follow Ruff formatting rules

### Code Quality Comments

Use `# noqa: <rule>` sparingly and only with clear justification on the same line, in the format `# noqa: <RULE> - <reason>`:

```python
# ✅ Acceptable - Clear reason
try:
    setup_logging()
except:  # noqa: E722 - Fallback before logging configured
    print("Logging setup failed")

# ❌ Not acceptable - No justification
def function():
    pass  # noqa: E501
```

## Testing Standards

### Test Framework

Use **pytest** for all testing:

```python
# ✅ Correct - pytest style
def test_user_creation():
    user = create_user("John", "john@example.com")
    assert user.name == "John"
    assert user.email == "john@example.com"

# Use fixtures for setup
import pytest

@pytest.fixture
def sample_user():
    return User(name="John", email="john@example.com")

def test_user_email(sample_user):
    assert sample_user.email == "john@example.com"

# ❌ Incorrect - unittest.TestCase style (do NOT inherit from TestCase)
import unittest

class TestUser(unittest.TestCase):  # Don't do this
    def setUp(self):
        self.user = User("John", "john@example.com")

    def test_email(self):
        self.assertEqual(self.user.email, "john@example.com")
```

**Note:** Grouping test functions in plain classes (without inheriting from `TestCase`) is fine and encouraged for organization:

```python
# ✅ Correct - Plain class grouping (no TestCase inheritance)
class TestUserCreation:
    def test_creates_with_name(self):
        user = create_user("John", "john@example.com")
        assert user.name == "John"

    def test_creates_with_email(self):
        user = create_user("John", "john@example.com")
        assert user.email == "john@example.com"
```

### Mocking

**Use pytest's monkeypatch instead of unittest.mock.patch:**

```python
# ✅ Correct - monkeypatch (project standard)
def test_api_call(monkeypatch):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "value"}
    monkeypatch.setattr("requests.get", MagicMock(return_value=mock_response))
    result = fetch_data()
    assert result["data"] == "value"

# Use unittest.mock classes for mock objects
from unittest.mock import Mock, MagicMock, AsyncMock

def test_callback():
    callback = Mock()
    process_data(callback)
    callback.assert_called_once()
```

### Test Files and Fixtures

```python
# ❌ Don't write temporary files in tests
def test_config():
    with open("/tmp/test_config.json", "w") as f:
        json.dump({"key": "value"}, f)
    # ...

# ✅ Use tests/fixtures directory
def test_config(fixtures_dir):
    config_path = fixtures_dir / "test_config.json"
    with config_path.open() as f:
        config = json.load(f)
    # ...
```

### Testing Logging

```python
# ✅ Use caplog fixture to verify logging
def test_error_logging(caplog):
    with caplog.at_level(logging.ERROR):
        process_failing_operation()

    assert "Expected error message" in caplog.text
    assert len(caplog.records) == 1
```

### Testing Exceptions

```python
# ✅ Use pytest.raises context manager
import pytest

def test_invalid_input():
    with pytest.raises(ValueError, match="Invalid value"):
        process_data("invalid")
```

### Test Coverage

- **Target**: 90% code coverage
- **Focus**: Critical paths and business logic over arbitrary coverage targets
- Mock external dependencies (APIs, databases, files)
- Test both success and error conditions
- Write tests for all new functions/methods

**Coverage Tools:**

- **Use coverage directly**: `coverage run -m pytest`
- **Do not add pytest-cov**: the project scripts use the `coverage` command
- **Coverage config** lives in `[tool.coverage.*]` sections in `pyproject.toml` -- do not add `parallel = true`, `data_file`, or `[tool.coverage.xml]` sections.

### Test Organization

**Test structure mirrors source structure:**

- `src/utils/config.py` → `tests/src/utils/test_config.py`
- **Test file naming**: Prefix with `test_` (e.g., `test_config.py`, `test_logger.py`)
- **Test function naming**: Prefix with `test_` and use descriptive names (e.g., `test_config_loads_from_file`)
- **Test class naming**: Optional, prefix with `Test` (e.g., `class TestJsonFormatter:`)

### Mocking Best Practices

**CRITICAL: Patch where used, not where defined**

```python
# If src.example imports Config with:
# from src.utils.config import Config

# ✅ Correct - Patch where USED
def test_example(monkeypatch):
    monkeypatch.setattr("src.example.Config", MagicMock())

# ❌ Incorrect - Patching where defined
def test_example(monkeypatch):
    monkeypatch.setattr("src.utils.config.Config", MagicMock())  # Won't work!
```

**Mocking rules:**

- Use `monkeypatch` from pytest (project standard)
- Use `Mock`, `MagicMock`, `AsyncMock` from `unittest.mock` for mock objects
- NEVER use custom mock classes or `types.SimpleNamespace` for mocking
- NEVER use `unittest.mock.patch` - use monkeypatch instead
- Don't inherit from `unittest.TestCase` - use plain classes or pytest-style functions

### Test Data Management

**Use fixture files for test data:**

Store reusable test data files in `tests/fixtures/` directory:

```python
# ✅ Correct - Read fixture files directly when possible
def test_config(fixtures_dir):
    config_path = fixtures_dir / "test_config.json"
    with config_path.open() as f:
        config = json.load(f)
    # test code

# ✅ Use tmp_path for test-created files
def test_file_operation(tmp_path):
    test_file = tmp_path / "test.json"
    test_file.write_text('{"key": "value"}')
    # test code

# ❌ Never write to project directories
def test_bad():
    with open("./test_output.json", "w") as f:  # Wrong!
        json.dump(data, f)
```

**When to use `tmp_path`:** Use `tmp_path` when testing file-writing behavior, when a test needs temporary output, or when the input is trivial enough that creating a fixture file would be overkill (e.g., a one-line text file specific to a single test).

**When to copy fixture files:**

- Simulating specific directory structures
- Tests might modify the file
- Multiple files need to coexist in a hierarchy

**When to read fixture files directly:**

- Only file content matters, not location
- Test only reads the file (read-only access)
- Path can be mocked to point to fixtures directory

### Test Requirements

**Before writing code:**

1. Check if tests already exist
2. Write test first (TDD approach when practical)
3. Ensure tests cover new functionality

**Test structure:**

- Use pytest fixtures for common setup
- Keep tests focused and independent
- Name tests descriptively: `test_<functionality>_<condition>_<expected>`

## Python Version Compatibility

### Target Version: Python 3.12+

**Modern syntax to use:**

- Union types: `str | None`
- Generic types: `list[str]`, `dict[str, int]`
- Match statements for complex conditionals
- New f-string features
- Improved error messages

**Forward compatibility:**

```python
from __future__ import annotations  # Only when needed (see below)

def process(data: list[dict[str, str | int]]) -> None:
    pass
```

**`from __future__ import annotations`**: Only use when needed for forward references (referencing a class before it's defined) or circular import avoidance in type hints. Do not add it as a blanket rule to every file.

## Project Architecture

### File Editing Guardrails

Certain files have restricted editing rules to prevent accidental breakage:

- **`config.py`** (`src/utils/config.py`): Unless specifically instructed, only update `_Config` class member variables. `log_level` and `log_type` must always remain (required by `logger.py`).
- **`app.py`** (project root): Unless specifically instructed, only change the application call (`run_example()` and its import). The rest of the file structure should remain as-is.
- **`logger.py`** (`src/utils/logger.py`): Unless specifically instructed, no updates should be made.

### Package Structure

- **No `__init__.py` files** - Use implicit namespace packages
- Use absolute imports throughout
- Organize code into logical modules

### Configuration Management

The example application reads `config.json` from the working directory.

1. Copy `config.example.json` to `config.json`.
2. Keep example values synthetic and non-sensitive.
3. Never commit `config.json` with credentials or private data.
4. Restrict file permissions when configuration contains sensitive values.
5. Select a secret-management mechanism appropriate to the consuming
   application's threat model and runtime.

This public template intentionally excludes operational tooling, network layout,
and organization-specific configuration.

## Dependency Management

### Adding New Dependencies

1. Determine if dependency is for production or development
2. Add to appropriate requirements file (`requirements.txt` or `requirements-dev.txt`)
3. Pin exact versions for reproducibility:

   ```text
   requests==2.31.0
   pytest==9.0.3
   ```

   Use exact pins (`==`) for all dependencies — both production and development. This ensures consistent builds across environments and makes upgrades intentional.

4. Install dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

5. Update documentation and tool configuration if needed
6. Test that installation works correctly

## Code Classification

Different rules may apply to different code categories:

### Production Code

Application logic, business rules, data processing, API endpoints:

- No print statements (use logging)
- Comprehensive error handling
- Full test coverage required
- All functions must have type hints
- Use format strings in logging

### Infrastructure Code

Configuration, logging setup, environment initialization:

- Print statements allowed as fallbacks (before logging configured)
- Focus on robustness and reliability
- Clear documentation required
- Minimal external dependencies

### Test Code

Unit tests, integration tests, test utilities:

- Use pytest patterns and fixtures
- Mock external dependencies
- Focus on clarity over optimization
- Descriptive test names
- Use monkeypatch for mocking

### Development Code

Scripts, debugging utilities, development-only features:

- Relaxed standards acceptable
- Emphasize utility over formality
- Document usage clearly
- Keep separate from production code

## Pre-Commit Checklist

Before committing code, ensure:

1. ✅ Virtual environment is activated
2. ✅ All type hints are present on new/modified functions
3. ✅ Logging uses format strings (not f-strings)
4. ✅ Tests written for new functionality
5. ✅ Run `.\scripts.ps1 build` successfully
6. ✅ No debug code or temporary changes remain
7. ✅ Files end with a blank line
8. ✅ Absolute imports used (not relative)

## Decision Flowcharts

### Adding New Code

1. **Is there an existing test?** → If no, write test first (test-driven development)
2. **Does function have type hints?** → If no, add them to parameters and return type
3. **Is function public?** → If yes and no docstring, add one following docstring standards
4. **Are you using f-strings in logging?** → If yes, convert to format strings `logger.info("Message %s", var)`
5. **Does it use datetime?** → If yes, switch to Pendulum (`pendulum.now()`, `pendulum.parse()`)
6. **Does it use positional arguments?** → Consider keyword arguments for clarity
7. **Run local checks** → `.\scripts.ps1 dev-check` during iteration, `.\scripts.ps1 build` before committing

### Modifying Existing Code

1. **Read surrounding context first** → Understand existing patterns before making changes
2. **Check if existing tests cover the change** → Look in mirrored test directory
3. **Update tests if behavior changes** → Ensure test assertions match new behavior
4. **Maintain existing code style** → Follow patterns in surrounding code
5. **Update type hints if signatures change** → Keep type annotations accurate
6. **Verify docstrings are still accurate** → Update if function behavior or parameters changed
7. **Run checks** → `.\scripts.ps1 build` before finalizing to catch all issues

### Installing Packages

1. **Check if virtual environment is configured** → Run `python -m venv .venv` and activate if needed
2. **Add to requirements file first** → `requirements.txt` or `requirements-dev.txt`
3. **Install using pip** → `pip install -r requirements-dev.txt`
4. **Verify installation worked** → Check that package is importable
5. **NEVER install single packages directly** → Always use requirements files
6. **Update documentation if needed** → Document new dependencies
7. **Test that project still builds** → Run `.\scripts.ps1 build`

## Summary of Critical Rules

### Always Do

- ✅ Use logging format strings: `logger.info("Message %s", variable)`
- ✅ Add type hints to all functions (parameters and return values)
- ✅ Write tests for new functionality (aim for 90% coverage)
- ✅ Use absolute imports (never relative)
- ✅ Use Pendulum for date/time operations (never datetime)
- ✅ Run build pipeline before committing (`.\scripts.ps1 build`)
- ✅ Use modern Python 3.12+ syntax (`str | None`, `list[str]`)
- ✅ Prefer keyword arguments over positional arguments for clarity
- ✅ Read file contents before modifying
- ✅ Use `monkeypatch` for mocking in tests
- ✅ Configure Python environment before operations

### Never Do

- ❌ Use f-strings in logging calls (use format strings)
- ❌ Skip writing tests for new functionality
- ❌ Ignore type checking errors without investigation
- ❌ Use `print()` in production code (except config.py fallback)
- ❌ Use bare `except:` clauses (use specific exceptions)
- ❌ Use relative imports (use absolute imports)
- ❌ Commit without running build pipeline
- ❌ Use old type syntax (`Optional[str]`, `List[int]`, `Dict[str, int]`)
- ❌ Commit credentials or sensitive configuration
- ❌ Install single packages directly (use requirements files)
- ❌ Use `pytest-cov` or add `parallel = true`, `data_file`, or `[tool.coverage.xml]` to pyproject.toml
- ❌ Use custom mock classes or `types.SimpleNamespace` for mocking
- ❌ Inherit from `unittest.TestCase` (use plain classes or pytest-style functions)
- ❌ Use `unittest.mock.patch` (use monkeypatch)
- ❌ Write to project directories in tests (use tmp_path)
- ❌ Modify files without reading current contents first
- ❌ Use datetime/date/time (use pendulum)

---

**Questions?** Refer to `pyproject.toml` for tool configuration or review existing code for patterns and examples.
