"""
pytest configuration file for test suite.

This file contains shared fixtures and configuration that are automatically
available to all test files in this directory and subdirectories.
No imports are needed - pytest discovers and loads these fixtures automatically.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import warnings

import pytest

# ---------------------------------------------------------------------------
# Suppress InsecureRequestWarning ONLY in CI environments.
# The testburst CI plugin makes HTTPS requests with verify=False during
# pytest_sessionstart, triggering this warning. The "error" filterwarnings
# in pyproject.toml would promote it to an exception.
#
# We intentionally do NOT suppress this locally — if project code ever makes
# insecure requests, we want tests to catch it.
# ---------------------------------------------------------------------------
if os.environ.get("CI"):
    try:
        from urllib3.exceptions import InsecureRequestWarning  # type: ignore[import-not-found]  # noqa: I001

        warnings.filterwarnings("ignore", category=InsecureRequestWarning)
    except ModuleNotFoundError:
        pass

# ==============================================================================
# Config Module Loading - Temporary config.json Setup
# ==============================================================================
# This block copies test_config.json to config.json temporarily to allow the
# config module to load during test collection, then removes it after import.
#
# Problem: config.py executes `Config = _init_config()` at module level, which
#          tries to read config.json. With required fields (like example_uninitialized),
#          missing config.json causes FileNotFoundError during test collection.
#
# Solution: ONLY if config.json doesn't exist, copy the fixture file before importing,
#           then delete after import completes. If config.json already exists, use it.
# ==============================================================================

_fixture_path = Path(__file__).parent / "fixtures" / "test_config.json"

_config_path = Path(__file__).parent.parent / "config.json"

# Only create temporary config.json if it doesn't already exist
if not _config_path.exists():
    # Copy fixture to project root before importing config module
    shutil.copy(_fixture_path, _config_path)
    try:
        # Import config module - it will load from the temporary config.json
        # This caches the module, so tests can import it after cleanup
        from src.utils.config import Config
    finally:
        # Clean up - remove the temporary config.json we created
        if _config_path.exists():
            _config_path.unlink()
# If config.json already exists, test files will import Config naturally

# ==============================================================================
# End Config Module Loading
# ==============================================================================


@pytest.fixture
def fixtures_dir() -> Path:
    """Provide path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"
