"""
Background configuration file watcher.

This module provides a background thread that periodically checks if the
configuration file has been modified and automatically refreshes the config.
Useful for detecting configuration file updates during development.
"""

from configparser import ConfigParser, ParsingError
import logging
from pathlib import Path
import threading

from src.utils.config import config_needs_refresh, refresh_config

logger = logging.getLogger(__name__)

# Module-level state for the watcher thread
_watcher_thread: threading.Thread | None = None
_watcher_stop_event: threading.Event = threading.Event()
_watcher_lock: threading.Lock = threading.Lock()  # Protects _watcher_thread access


def _config_watcher_loop(interval: float) -> None:
    """Background loop that checks for config changes and refreshes when needed.

    Runs in a daemon thread and checks every interval seconds.
    Stops when _watcher_stop_event is set.
    """
    logger.info("Config watcher started, checking every %s seconds", interval)

    while not _watcher_stop_event.is_set():
        try:
            if config_needs_refresh():
                logger.info("Config file changed, refreshing configuration")
                refresh_config()
                logger.info("Configuration refreshed successfully")
        except (OSError, ValueError):
            logger.exception("Failed to refresh config")

        # Wait for interval or until stop event is set
        _watcher_stop_event.wait(timeout=interval)

    logger.info("Config watcher stopped")


def start_config_watcher(interval: float = 900.0) -> None:
    """Start the background config watcher thread.

    Args:
        interval: Check interval in seconds. Default is 900.0 (15 minutes).

    Raises:
        RuntimeError: If watcher is already running.

    Example:
        >>> from src.utils.config_watcher import start_config_watcher
        >>> start_config_watcher(interval=900.0)  # Check every 15 minutes
    """
    if interval < 10.0:
        raise ValueError(f"Watcher interval must be >= 10 seconds, got {interval}")

    global _watcher_thread

    with _watcher_lock:
        if _watcher_thread is not None and _watcher_thread.is_alive():
            raise RuntimeError("Config watcher is already running")

        _watcher_stop_event.clear()

        _watcher_thread = threading.Thread(
            target=_config_watcher_loop, args=(interval,), name="ConfigWatcher", daemon=True
        )
        _watcher_thread.start()

    logger.info("Config watcher thread started with %s second interval", interval)


def stop_config_watcher(timeout: float = 5.0) -> None:
    """Stop the background config watcher thread.

    Args:
        timeout: Maximum seconds to wait for thread to stop. Default is 5.0.

    Example:
        >>> from src.utils.config_watcher import stop_config_watcher
        >>> stop_config_watcher()
    """
    global _watcher_thread

    with _watcher_lock:
        if _watcher_thread is None or not _watcher_thread.is_alive():
            logger.debug("Config watcher is not running")
            return

        logger.info("Stopping config watcher")
        _watcher_stop_event.set()

        # Release lock during join to avoid holding it while waiting
        thread_to_join = _watcher_thread

    # Join outside the lock to prevent deadlock
    thread_to_join.join(timeout=timeout)

    with _watcher_lock:
        if _watcher_thread is not None and _watcher_thread.is_alive():
            logger.warning("Config watcher thread did not stop within timeout")
        else:
            logger.info("Config watcher stopped successfully")
            _watcher_thread = None


def is_watcher_running() -> bool:
    """Check if the config watcher is currently running.

    Returns:
        bool: True if watcher thread is active, False otherwise.

    Example:
        >>> from src.utils.config_watcher import is_watcher_running
        >>> if is_watcher_running():
        ...     print("Watcher is active")
    """
    with _watcher_lock:
        return _watcher_thread is not None and _watcher_thread.is_alive()


def start_config_watcher_if_enabled(config_file: str = "config_watch.ini") -> bool:
    """Start config watcher if configuration file exists.

    Reads the config_watch.ini file (or custom path) to determine if the watcher
    should be enabled and what interval to use. Only starts if the file exists.

    Args:
        config_file: Path to the INI configuration file. Default is "config_watch.ini".

    Returns:
        bool: True if watcher was started, False if disabled (file not found).

    Example:
        >>> from src.utils.config_watcher import start_config_watcher_if_enabled
        >>> if start_config_watcher_if_enabled():
        ...     print("Config watcher enabled")
        ... else:
        ...     print("Config watcher disabled")
    """
    config_watch_path = Path(config_file)

    if not config_watch_path.exists():
        logger.info("Config watcher disabled (%s not found)", config_file)
        return False

    try:
        config_parser = ConfigParser()
        config_parser.read(config_watch_path)
        interval = config_parser.getfloat("DEFAULT", "INTERVAL", fallback=900.0)
        start_config_watcher(interval=interval)
        logger.info("Config watcher started with interval: %s seconds", interval)
        return True
    except (OSError, ValueError, RuntimeError, ParsingError) as e:
        logger.warning("Failed to start config watcher: %s", e)
        return False
