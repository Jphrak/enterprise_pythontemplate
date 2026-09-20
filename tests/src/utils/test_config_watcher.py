"""Tests for src.utils.config_watcher module."""

from pathlib import Path
import time
from unittest.mock import MagicMock

import pytest

import src.utils.config_watcher
from src.utils.config_watcher import (
    is_watcher_running,
    start_config_watcher,
    start_config_watcher_if_enabled,
    stop_config_watcher,
)


def test_start_config_watcher_starts_thread() -> None:
    """Test start_config_watcher starts the background thread."""
    try:
        start_config_watcher(interval=10)  # Minimum allowed interval
        assert is_watcher_running() is True
    finally:
        stop_config_watcher()


def test_stop_config_watcher_stops_thread() -> None:
    """Test stop_config_watcher stops the background thread."""
    start_config_watcher(interval=10)
    assert is_watcher_running() is True

    stop_config_watcher()
    assert is_watcher_running() is False


def test_start_config_watcher_raises_if_already_running() -> None:
    """Test start_config_watcher raises RuntimeError if already running."""
    try:
        start_config_watcher(interval=10)

        with pytest.raises(RuntimeError, match="already running"):
            start_config_watcher(interval=10)
    finally:
        stop_config_watcher()


def test_stop_config_watcher_when_not_running() -> None:
    """Test stop_config_watcher is safe to call when watcher not running."""
    # Should not raise any errors
    stop_config_watcher()


def test_is_watcher_running_returns_false_initially() -> None:
    """Test is_watcher_running returns False before starting."""
    # Ensure watcher is stopped
    stop_config_watcher()
    assert is_watcher_running() is False


def test_config_watcher_refreshes_on_file_change(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    fixtures_dir: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test config watcher detects file changes and refreshes config."""
    # Patch the watcher's config module references
    monkeypatch.setattr(
        "src.utils.config_watcher.config_needs_refresh",
        lambda: True,  # Simulate file change detected
    )

    mock_refresh = MagicMock()
    monkeypatch.setattr("src.utils.config_watcher.refresh_config", mock_refresh)

    # Make the watcher loop cycle immediately instead of waiting 10s
    original_wait = src.utils.config_watcher._watcher_stop_event.wait
    monkeypatch.setattr(
        src.utils.config_watcher._watcher_stop_event,
        "wait",
        lambda timeout=None: original_wait(0.05),
    )

    try:
        with caplog.at_level("INFO"):
            start_config_watcher(interval=10)
            time.sleep(0.3)  # Wait for at least one check

        # Verify refresh was called
        assert mock_refresh.call_count >= 1
        assert "Config file changed" in caplog.text
    finally:
        stop_config_watcher()


def test_config_watcher_handles_refresh_errors(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Test config watcher handles errors during refresh gracefully."""

    def mock_needs_refresh() -> bool:
        return True

    def mock_refresh_error() -> None:
        raise ValueError("Test error")

    monkeypatch.setattr("src.utils.config_watcher.config_needs_refresh", mock_needs_refresh)
    monkeypatch.setattr("src.utils.config_watcher.refresh_config", mock_refresh_error)

    # Make the watcher loop cycle immediately instead of waiting 10s
    original_wait = src.utils.config_watcher._watcher_stop_event.wait
    monkeypatch.setattr(
        src.utils.config_watcher._watcher_stop_event,
        "wait",
        lambda timeout=None: original_wait(0.05),
    )

    try:
        with caplog.at_level("ERROR"):
            start_config_watcher(interval=10)
            time.sleep(0.3)  # Wait for at least one check

        # Verify error was logged but watcher continues
        assert "Failed to refresh config" in caplog.text
        assert is_watcher_running() is True  # Watcher should still be running
    finally:
        stop_config_watcher()


def test_config_watcher_stops_on_event(caplog: pytest.LogCaptureFixture) -> None:
    """Test config watcher stops cleanly when stop event is set."""
    try:
        with caplog.at_level("INFO"):
            start_config_watcher(interval=10)  # Long interval
            time.sleep(0.1)  # Let it start
            stop_config_watcher()

        assert "Config watcher started" in caplog.text
        assert "Config watcher stopped" in caplog.text
    finally:
        stop_config_watcher()  # Ensure cleanup


def test_start_config_watcher_if_enabled_starts_when_ini_exists(
    tmp_path: Path,
    fixtures_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test start_config_watcher_if_enabled starts watcher when config_watch.ini exists."""
    # Change working directory to fixtures_dir where config_watch.ini exists
    monkeypatch.chdir(fixtures_dir)

    try:
        with caplog.at_level("INFO"):
            result = start_config_watcher_if_enabled()

        assert result is True
        assert is_watcher_running() is True
        assert "Config watcher started with interval: 600.0 seconds" in caplog.text
    finally:
        stop_config_watcher()


def test_start_config_watcher_if_enabled_skips_when_ini_not_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Test start_config_watcher_if_enabled skips when config_watch.ini does not exist."""
    # Change working directory to tmp_path (no config_watch.ini)
    monkeypatch.chdir(tmp_path)

    with caplog.at_level("INFO"):
        result = start_config_watcher_if_enabled()

    assert result is False
    assert is_watcher_running() is False
    assert "Config watcher disabled (config_watch.ini not found)" in caplog.text


def test_start_config_watcher_if_enabled_uses_default_interval(
    tmp_path: Path,
    fixtures_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test start_config_watcher_if_enabled uses default interval when not in INI."""
    # Change working directory to fixtures_dir and use renamed fixture
    monkeypatch.chdir(fixtures_dir)

    try:
        with caplog.at_level("INFO"):
            result = start_config_watcher_if_enabled("config_watch_no_interval.ini")

        assert result is True
        assert is_watcher_running() is True
        assert "Config watcher started with interval: 900.0 seconds" in caplog.text
    finally:
        stop_config_watcher()


def test_start_config_watcher_if_enabled_handles_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Test start_config_watcher_if_enabled handles errors gracefully."""
    # Create malformed config_watch.ini file
    config_watch_path = tmp_path / "config_watch.ini"
    config_watch_path.write_text("[DEFAULT]\nINTERVAL = not_a_number")

    # Change working directory to tmp_path
    monkeypatch.chdir(tmp_path)

    with caplog.at_level("WARNING"):
        result = start_config_watcher_if_enabled()

    assert result is False
    assert is_watcher_running() is False
    assert "Failed to start config watcher" in caplog.text


def test_start_config_watcher_if_enabled_with_custom_path(
    tmp_path: Path, fixtures_dir: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Test start_config_watcher_if_enabled with custom config file path."""
    # Pass fixture path directly - no copying needed
    config_watch_path = fixtures_dir / "config_watch_custom.ini"

    try:
        with caplog.at_level("INFO"):
            result = start_config_watcher_if_enabled(config_file=str(config_watch_path))

        assert result is True
        assert is_watcher_running() is True
        assert "Config watcher started with interval: 300.0 seconds" in caplog.text
    finally:
        stop_config_watcher()


def test_stop_config_watcher_warns_on_timeout(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Test stop_config_watcher logs warning when thread doesn't stop within timeout."""
    # Start watcher
    start_config_watcher(interval=10)
    assert is_watcher_running() is True

    # Mock join to make thread appear to not stop
    import threading
    from unittest.mock import MagicMock

    from src.utils import config_watcher

    original_thread = config_watcher._watcher_thread
    mock_thread = MagicMock(spec=threading.Thread)
    mock_thread.is_alive.return_value = True  # Simulate thread not stopping
    monkeypatch.setattr("src.utils.config_watcher._watcher_thread", mock_thread)

    try:
        with caplog.at_level("WARNING"):
            stop_config_watcher(timeout=0.1)

        # Should log warning about timeout
        assert "Config watcher thread did not stop within timeout" in caplog.text
    finally:
        # Clean up - stop the actual thread
        monkeypatch.setattr("src.utils.config_watcher._watcher_thread", original_thread)
        stop_config_watcher()


def test_start_config_watcher_accepts_float_interval() -> None:
    """Test start_config_watcher accepts float intervals without truncation."""
    try:
        start_config_watcher(interval=10.5)  # Float interval above minimum
        assert is_watcher_running() is True
    finally:
        stop_config_watcher()


def test_start_config_watcher_rejects_short_interval() -> None:
    """Test start_config_watcher raises ValueError for intervals below 10 seconds."""
    with pytest.raises(ValueError, match="Watcher interval must be >= 10 seconds"):
        start_config_watcher(interval=0.5)
