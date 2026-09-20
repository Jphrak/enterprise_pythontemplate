# Python Project Instructions

## Scope

This repository is an environment-agnostic Python 3.12+ application template.
Keep operational topology, organization names, private URLs, and credentials out
of the repository.

## Development Setup

1. Create a virtual environment in `.venv`.
2. Install `requirements-dev.txt`.
3. Copy `config.example.json` to the ignored `config.json`.
4. Run `./scripts.sh build` or `.\scripts.ps1 build` before committing.

Add dependencies to a requirements file and pin exact versions. Do not install
undeclared packages as part of a change.

## Python Style

- Target Python 3.12 or newer.
- Add type hints to all function parameters and return values.
- Prefer `str | None`, `list[str]`, and other modern built-in syntax.
- Use absolute imports.
- Keep lines at or below 100 characters.
- Use Ruff for formatting and linting.
- Use MyPy for static type checking.
- Use Pendulum for date and time operations in this template.
- Add docstrings to public classes and functions.
- Use explicit validation with `if` and `raise`; runtime validation must not
  depend on `assert`.

## Logging

- Create loggers with `logging.getLogger(__name__)`.
- Pass values as lazy logging arguments:
  `logger.info("Processed %s", item_id)`.
- Do not use f-strings in logging calls.
- Do not log credentials, tokens, personal data, or full configuration objects.
- Use `TEXT` for human-readable output and `JSON` for structured output.

## Configuration

- The example application reads `config.json` from the working directory.
- Keep `config.json` ignored and maintain non-sensitive placeholders in
  `config.example.json`.
- Treat file permissions as part of secret hygiene when configuration contains
  sensitive values.
- Select and integrate a secret-management mechanism in the consuming
  application; this public template does not prescribe one.
- Keep `log_level` and `log_type` in the configuration dataclass because the
  logging module depends on them.

## Tests

- Use pytest and mirror source paths under `tests/`.
- Add tests for normal behavior, boundary conditions, and failure paths.
- Use pytest's `monkeypatch` fixture and patch objects where they are used.
- `Mock`, `MagicMock`, and `AsyncMock` are allowed as test doubles.
- Use `tmp_path` for files created by tests.
- Use `caplog` for logging assertions.
- Use `pytest.raises(..., match=...)` for expected errors.
- Run coverage with `coverage run -m pytest`.
- Aim for at least 90 percent coverage while prioritizing meaningful behavior.

## Error Handling

- Catch specific exception types whenever practical.
- Place exception handling close to the operation that can fail.
- Include useful context in error messages without exposing sensitive values.
- Log failures before suppressing or re-raising them.

## Concurrency

- Prefer `asyncio.TaskGroup` for related concurrent tasks.
- Ensure every coroutine is awaited or deliberately scheduled.
- Handle cancellation and cleanup explicitly.
- Protect shared mutable state.

## Change Checklist

- Read the surrounding implementation and existing tests first.
- Update tests whenever behavior changes.
- Preserve public interfaces unless the change intentionally revises them.
- Run formatting, linting, MyPy, tests, and coverage.
- Check the diff for credentials, personal data, private names, and temporary
  artifacts.
- Keep operational and organization-specific configuration outside this public
  repository.
