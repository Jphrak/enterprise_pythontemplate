# Standard Python entrypoint
import logging

from src.example import run_example
from src.utils.config_watcher import start_config_watcher_if_enabled, stop_config_watcher
from src.utils.logger import initialize_logging


def main() -> None:
    """
    Main entrypoint for the application.
    """
    logger: logging.Logger | None = None  # Initialize logger variable

    try:
        initialize_logging()
        # Get logger AFTER initialization to ensure proper configuration
        logger = logging.getLogger(__name__)
        logger.info("Logging initialized successfully")
    except Exception as e:  # noqa: BLE001 - Graceful exit before logging configured
        # Use basic logging since JSON logging failed
        print(f"Failed to initialize logging: {e}")
        print("Exiting application.")
        return

    logger.info("Starting application")

    # Start background config watcher if enabled via config_watch.ini
    start_config_watcher_if_enabled()

    try:
        run_example()  # TODO: replace with your code entrypoint here  # noqa: FIX002, TD002, TD003
        logger.info("All queries completed successfully")
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        raise
    except Exception:
        logger.exception("Application failed with error")
        raise
    finally:
        # Clean shutdown of config watcher
        stop_config_watcher()


if __name__ == "__main__":
    main()
