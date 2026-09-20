"""
Tests for the main application entry point.

This module contains unit tests for the app.py main function,
including logging initialization and error handling scenarios.
"""

from unittest.mock import MagicMock

import pytest

import app


@pytest.fixture
def mock_run_example(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Fixture to mock the run_example function."""
    mock = MagicMock()
    monkeypatch.setattr(app, "run_example", mock)
    return mock


@pytest.fixture
def mock_initialize_logging(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Fixture to mock the initialize_logging function."""
    mock = MagicMock()
    monkeypatch.setattr(app, "initialize_logging", mock)
    return mock


@pytest.fixture
def mock_start_config_watcher_if_enabled(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Fixture to mock the start_config_watcher_if_enabled function."""
    mock = MagicMock(return_value=True)
    monkeypatch.setattr(app, "start_config_watcher_if_enabled", mock)
    return mock


@pytest.fixture
def mock_stop_config_watcher(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Fixture to mock the stop_config_watcher function."""
    mock = MagicMock()
    monkeypatch.setattr(app, "stop_config_watcher", mock)
    return mock


def test_main_calls_run_example(
    mock_run_example: MagicMock,
    mock_initialize_logging: MagicMock,
    mock_start_config_watcher_if_enabled: MagicMock,
    mock_stop_config_watcher: MagicMock,
) -> None:
    """Test main function calls run_example."""
    app.main()
    mock_initialize_logging.assert_called_once()
    mock_run_example.assert_called_once()
    mock_stop_config_watcher.assert_called_once()


def test_main_starts_and_stops_config_watcher(
    mock_run_example: MagicMock,
    mock_initialize_logging: MagicMock,
    mock_start_config_watcher_if_enabled: MagicMock,
    mock_stop_config_watcher: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test main function properly manages config watcher lifecycle."""
    with caplog.at_level("INFO"):
        app.main()

    # Verify watcher is started after logging initialization
    mock_start_config_watcher_if_enabled.assert_called_once()
    # Verify watcher is stopped in finally block
    mock_stop_config_watcher.assert_called_once()

    # Verify call order: logging -> watcher -> run_example
    assert mock_initialize_logging.call_count == 1
    assert mock_start_config_watcher_if_enabled.call_count == 1
    assert mock_run_example.call_count == 1


def test_main_propagates_exceptions(
    mock_run_example: MagicMock,
    mock_initialize_logging: MagicMock,
    mock_start_config_watcher_if_enabled: MagicMock,
    mock_stop_config_watcher: MagicMock,
) -> None:
    """Test main function propagates exceptions from run_example."""
    mock_run_example.side_effect = RuntimeError("Query execution failed")

    with pytest.raises(RuntimeError, match="Query execution failed"):
        app.main()

    mock_stop_config_watcher.assert_called_once()


def test_main_logs_lifecycle_messages(
    mock_run_example: MagicMock,
    mock_initialize_logging: MagicMock,
    mock_start_config_watcher_if_enabled: MagicMock,
    mock_stop_config_watcher: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that main function logs initialization, start, and completion messages."""
    with caplog.at_level("INFO"):
        app.main()

    info_messages = [record.message for record in caplog.records if record.levelname == "INFO"]

    # Check all lifecycle messages are logged
    assert any("Logging initialized successfully" in msg for msg in info_messages)
    assert any("Starting application" in msg for msg in info_messages)
    assert any("All queries completed successfully" in msg for msg in info_messages)


def test_main_handles_keyboard_interrupt(
    mock_run_example: MagicMock,
    mock_initialize_logging: MagicMock,
    mock_start_config_watcher_if_enabled: MagicMock,
    mock_stop_config_watcher: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that main function handles KeyboardInterrupt properly."""
    mock_run_example.side_effect = KeyboardInterrupt("User interrupted")

    with pytest.raises(KeyboardInterrupt):
        with caplog.at_level("INFO"):
            app.main()

    # Check that interrupt was logged
    log_messages = [record.message for record in caplog.records if record.levelname == "INFO"]
    assert any("Application interrupted by user" in msg for msg in log_messages)


def test_main_logs_error_on_exception(
    mock_run_example: MagicMock,
    mock_initialize_logging: MagicMock,
    mock_start_config_watcher_if_enabled: MagicMock,
    mock_stop_config_watcher: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that main function logs errors on general exceptions."""
    mock_run_example.side_effect = ValueError("Query execution failed")

    with pytest.raises(ValueError, match="Query execution failed"):
        with caplog.at_level("ERROR"):
            app.main()

    # Check that error was logged
    error_messages = [record.message for record in caplog.records if record.levelname == "ERROR"]
    assert any("Application failed with error" in msg for msg in error_messages)


def test_main_handles_logging_initialization_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that main function handles logging initialization errors gracefully."""
    # Mock run_example to track if it gets called
    mock_run_example = MagicMock()
    monkeypatch.setattr(app, "run_example", mock_run_example)

    # Mock initialize_logging to raise an exception
    mock_initialize_logging = MagicMock(side_effect=RuntimeError("Logging init failed"))
    monkeypatch.setattr(app, "initialize_logging", mock_initialize_logging)

    # Should not raise exception and should return early
    app.main()

    # Check that fallback message was printed
    captured = capsys.readouterr()
    assert "Failed to initialize logging" in captured.out
    assert "Exiting application" in captured.out

    # Verify run_example was NOT called (early return)
    mock_run_example.assert_not_called()
