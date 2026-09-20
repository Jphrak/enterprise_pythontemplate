"""Load and refresh application configuration from a local JSON file."""

from dataclasses import MISSING, dataclass, field, fields
import json
import os
from pathlib import Path
import stat
import threading
from typing import Final
import warnings

LOG_TYPE_JSON: Final[str] = "JSON"
LOG_TYPE_TEXT: Final[str] = "TEXT"
CONFIG_FILENAME: Final[str] = "config.json"


@dataclass(slots=True)
class _ConfigState:
    """Track configuration state used for safe refresh checks."""

    mtime: float | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)


_state = _ConfigState()


@dataclass(slots=True)
class _Config:
    """Application configuration values."""

    example_uninitialized: int
    log_level: str = "INFO"
    log_type: str = LOG_TYPE_TEXT
    example_config: str = "default_value"


def _get_config_path() -> Path:
    """Return the configuration path for the current working directory."""
    return Path.cwd() / CONFIG_FILENAME


def _load_config() -> tuple[_Config, float]:
    """Load and validate configuration from the local JSON file.

    Returns:
        Loaded configuration and the file modification time.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If JSON is invalid or a required field is missing.
    """
    config_path = _get_config_path()
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path!s}")

    file_stat = config_path.stat()
    if os.name != "nt" and file_stat.st_mode & (stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH):
        warnings.warn(
            f"Config file {config_path} is world-accessible (mode {file_stat.st_mode:o}). "
            "Restrict access when configuration contains sensitive values.",
            UserWarning,
            stacklevel=2,
        )

    with config_path.open(mode="r", encoding="utf-8") as config_file:
        try:
            config_data: dict[str, str | int] = json.load(config_file)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON in {config_path}: {error}") from error

    config_fields = {config_field.name: config_field for config_field in fields(_Config)}
    missing_required = [
        field_name
        for field_name, config_field in config_fields.items()
        if config_field.default is MISSING
        and config_field.default_factory is MISSING
        and field_name not in config_data
    ]
    if missing_required:
        missing_names = ", ".join(missing_required)
        raise ValueError(
            f"Configuration file {config_path!s} is missing required fields: {missing_names}"
        )

    filtered_config = {key: value for key, value in config_data.items() if key in config_fields}
    return _Config(**filtered_config), file_stat.st_mtime  # type: ignore[arg-type]


def config_needs_refresh() -> bool:
    """Return whether the configuration file changed since the last load."""
    with _state.lock:
        if _state.mtime is None:
            return True
        saved_mtime = _state.mtime

    config_path = _get_config_path()
    if not config_path.is_file():
        return False
    return config_path.stat().st_mtime != saved_mtime


def refresh_config() -> None:
    """Reload configuration and update the shared object in place.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If JSON is invalid or a required field is missing.
    """
    new_config, new_mtime = _load_config()
    with _state.lock:
        for config_field in fields(_Config):
            setattr(Config, config_field.name, getattr(new_config, config_field.name))
        _state.mtime = new_mtime


_initial_config, _initial_mtime = _load_config()
_state.mtime = _initial_mtime
Config = _initial_config
