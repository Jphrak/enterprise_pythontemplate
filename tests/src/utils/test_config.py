"""Tests for local JSON configuration management."""

import os
from pathlib import Path
import shutil

import pytest

from src.utils.config import (
    CONFIG_FILENAME,
    LOG_TYPE_JSON,
    LOG_TYPE_TEXT,
    Config,
    _Config,
    _load_config,
    _state,
    config_needs_refresh,
    refresh_config,
)


def _use_config(
    monkeypatch: pytest.MonkeyPatch, directory: Path, filename: str = "config.json"
) -> None:
    """Point the configuration module at a test directory."""
    monkeypatch.setattr("src.utils.config.CONFIG_FILENAME", filename)
    monkeypatch.setattr("src.utils.config.Path.cwd", lambda: directory)


def test_config_defaults() -> None:
    """Default values favor readable text logging."""
    config = _Config(example_uninitialized=123)

    assert config.log_level == "INFO"
    assert config.log_type == "TEXT"
    assert config.example_config == "default_value"


def test_config_custom_values() -> None:
    """Explicit values override dataclass defaults."""
    config = _Config(
        example_uninitialized=456,
        log_level="DEBUG",
        log_type="JSON",
        example_config="custom_value",
    )

    assert config.example_uninitialized == 456
    assert config.log_level == "DEBUG"
    assert config.log_type == "JSON"
    assert config.example_config == "custom_value"


def test_load_config_raises_when_file_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A missing configuration file produces a clear error."""
    _use_config(monkeypatch, tmp_path)

    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        _load_config()


def test_load_config_raises_when_path_is_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A directory with the configured name is not accepted as a file."""
    (tmp_path / "config.json").mkdir()
    _use_config(monkeypatch, tmp_path)

    with pytest.raises(FileNotFoundError, match="Configuration file not found"):
        _load_config()


def test_load_config_from_working_directory(
    monkeypatch: pytest.MonkeyPatch, fixtures_dir: Path
) -> None:
    """Configuration is loaded from the current working directory."""
    _use_config(monkeypatch, fixtures_dir, "test_config.json")

    config, mtime = _load_config()

    assert config.example_uninitialized == 42
    assert config.log_level == "DEBUG"
    assert config.log_type == "TEXT"
    assert config.example_config == "test_value"
    assert mtime == (fixtures_dir / "test_config.json").stat().st_mtime


def test_load_config_applies_optional_defaults(
    monkeypatch: pytest.MonkeyPatch, fixtures_dir: Path
) -> None:
    """Missing optional fields receive dataclass defaults."""
    _use_config(monkeypatch, fixtures_dir, "partial_config.json")

    config, _mtime = _load_config()

    assert config.example_uninitialized == 10
    assert config.log_level == "DEBUG"
    assert config.log_type == "TEXT"
    assert config.example_config == "default_value"


def test_load_config_rejects_missing_required_field(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Required configuration fields are validated."""
    (tmp_path / "config.json").write_text('{"log_level": "DEBUG"}', encoding="utf-8")
    _use_config(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="missing required fields: example_uninitialized"):
        _load_config()


def test_load_config_rejects_invalid_json(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Malformed JSON produces a contextual ValueError."""
    (tmp_path / "config.json").write_text("not valid json", encoding="utf-8")
    _use_config(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="Invalid JSON in"):
        _load_config()


def test_load_config_ignores_unknown_fields(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Unknown JSON keys are ignored instead of becoming attributes."""
    (tmp_path / "config.json").write_text(
        '{"example_uninitialized": 55, "unknown_field": "ignored"}',
        encoding="utf-8",
    )
    _use_config(monkeypatch, tmp_path)

    config, _mtime = _load_config()

    assert config.example_uninitialized == 55
    assert not hasattr(config, "unknown_field")


@pytest.mark.skipif(os.name == "nt", reason="Unix permission bits are unavailable")
def test_load_config_warns_for_world_accessible_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Potentially unsafe file permissions produce a warning."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"example_uninitialized": 1}', encoding="utf-8")
    config_file.chmod(0o644)
    _use_config(monkeypatch, tmp_path)

    with pytest.warns(UserWarning, match="world-accessible"):
        _load_config()


def test_refresh_config_updates_shared_object(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, fixtures_dir: Path
) -> None:
    """Refresh updates the shared Config object without replacing it."""
    config_file = tmp_path / "config.json"
    shutil.copy(fixtures_dir / "watcher_config.json", config_file)
    _use_config(monkeypatch, tmp_path)
    original_identity = id(Config)

    refresh_config()
    config_file.write_text(
        '{"example_uninitialized": 200, "log_level": "DEBUG", "log_type": "JSON"}',
        encoding="utf-8",
    )
    refresh_config()

    assert id(Config) == original_identity
    assert Config.example_uninitialized == 200
    assert Config.log_level == "DEBUG"
    assert Config.log_type == "JSON"


def test_refresh_config_preserves_mtime_after_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A failed refresh does not update the saved modification time."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"example_uninitialized": 1}', encoding="utf-8")
    _use_config(monkeypatch, tmp_path)
    refresh_config()
    original_mtime = _state.mtime

    config_file.write_text('{"log_level": "DEBUG"}', encoding="utf-8")
    with pytest.raises(ValueError, match="missing required fields"):
        refresh_config()

    assert _state.mtime == original_mtime


def test_config_needs_refresh_returns_true_before_initial_load() -> None:
    """An uninitialized state requires a refresh."""
    original_mtime = _state.mtime
    try:
        _state.mtime = None
        assert config_needs_refresh() is True
    finally:
        _state.mtime = original_mtime


def test_config_needs_refresh_returns_false_when_file_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A removed configuration file cannot be refreshed."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"example_uninitialized": 1}', encoding="utf-8")
    _use_config(monkeypatch, tmp_path)
    refresh_config()
    config_file.unlink()

    assert config_needs_refresh() is False


def test_config_needs_refresh_detects_mtime_change(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A modification-time change is detected."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"example_uninitialized": 1}', encoding="utf-8")
    _use_config(monkeypatch, tmp_path)
    refresh_config()
    original_stat = config_file.stat()
    os.utime(
        config_file,
        (original_stat.st_atime, original_stat.st_mtime + 1),
    )

    assert config_needs_refresh() is True


def test_public_constants() -> None:
    """Configuration constants describe generic formats and filenames."""
    assert CONFIG_FILENAME == "config.json"
    assert LOG_TYPE_JSON == "JSON"
    assert LOG_TYPE_TEXT == "TEXT"
