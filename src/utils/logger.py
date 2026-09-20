"""
Logging configuration module.

This module provides structured JSON and human-readable text logging.
"""

import json
import logging
import traceback
from typing import TextIO

import pendulum

from src.utils.config import LOG_TYPE_JSON, Config


def _sanitize_unicode(text: str) -> str:
    """Sanitize non-ASCII characters by converting to escape sequences.

    Args:
        text: The text to sanitize.

    Returns:
        str: Text with non-ASCII characters converted to escape sequences.
    """
    return text.encode(encoding="ascii", errors="backslashreplace").decode("ascii")


class JsonFormatter(logging.Formatter):
    """
    Custom logging formatter that outputs log records as JSON.

    This formatter converts log records to JSON format with structured fields
    including timestamp (ISO8601 UTC), level, logger name, and message.
    Exception information is included when present.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a LogRecord as JSON.

        Args:
            record: The LogRecord to format.

        Returns:
            str: JSON-formatted log record.
        """
        log_record: dict[str, str | dict[str, str]] = {
            "timestamp": pendulum.from_timestamp(record.created, tz="UTC").to_iso8601_string(),
            "level": record.levelname,
            "logger_name": record.name,
            "message": _sanitize_unicode(record.getMessage()),
        }

        # Include exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": _sanitize_unicode(str(record.exc_info[1])),
                "traceback": _sanitize_unicode(
                    "".join(traceback.format_exception(*record.exc_info))
                ),
            }

        return json.dumps(log_record)


class SanitizingFormatter(logging.Formatter):
    """
    Custom logging formatter that sanitizes unicode characters.

    This formatter extends the standard formatter to convert non-ASCII
    characters to escape sequences before outputting.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a LogRecord with unicode sanitization.

        Args:
            record: The LogRecord to format.

        Returns:
            str: Formatted log record with sanitized unicode.
        """
        # Sanitize the message before formatting
        sanitized_record = logging.makeLogRecord(record.__dict__)
        if isinstance(sanitized_record.msg, str):
            sanitized_record.msg = _sanitize_unicode(sanitized_record.msg)
        return super().format(sanitized_record)


def initialize_logging() -> None:
    """Initialize logging configuration."""
    log_level: str = Config.log_level.upper()
    if Config.log_type.upper() == LOG_TYPE_JSON:
        handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
        handler.setLevel(log_level)
        formatter: JsonFormatter = JsonFormatter()
        handler.setFormatter(formatter)
        logging.basicConfig(level=log_level, handlers=[handler])
        logger = logging.getLogger(__name__)
        logger.info("Logging initialized in JSON format")
    else:
        text_handler: logging.StreamHandler[TextIO] = logging.StreamHandler()
        text_handler.setLevel(log_level)
        formatter_instance: SanitizingFormatter = SanitizingFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        text_handler.setFormatter(formatter_instance)
        logging.basicConfig(level=log_level, handlers=[text_handler])
        logger = logging.getLogger(__name__)
        logger.info("Logging initialized in text format")
