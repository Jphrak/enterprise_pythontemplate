"""Simple tests for the logger module."""

import json
import logging
import sys
from unittest.mock import MagicMock

import pytest

from src.utils.logger import (
    JsonFormatter,
    SanitizingFormatter,
    _sanitize_unicode,
    initialize_logging,
)


class TestSanitizeUnicode:
    """Test the _sanitize_unicode function."""

    def test_sanitize_ascii_unchanged(self) -> None:
        """Test that ASCII text passes through unchanged."""
        result = _sanitize_unicode("Hello, World!")
        assert result == "Hello, World!"

    def test_sanitize_empty_string(self) -> None:
        """Test that empty string returns empty string."""
        result = _sanitize_unicode("")
        assert result == ""

    def test_sanitize_accented_characters(self) -> None:
        """Test that accented characters are escaped."""
        result = _sanitize_unicode("café")
        assert result == "caf\\xe9"
        assert all(ord(c) < 128 for c in result)

    def test_sanitize_emoji(self) -> None:
        """Test that emoji are escaped."""
        result = _sanitize_unicode("Hello ☕ World")
        assert "\\u2615" in result  # ☕ is U+2615
        assert all(ord(c) < 128 for c in result)

    def test_sanitize_chinese_characters(self) -> None:
        """Test that Chinese characters are escaped."""
        result = _sanitize_unicode("你好")
        assert "\\u" in result
        assert all(ord(c) < 128 for c in result)

    def test_sanitize_mixed_content(self) -> None:
        """Test sanitization of mixed ASCII and unicode content."""
        result = _sanitize_unicode("Hello café ☕ 你好 World")
        # ASCII parts unchanged
        assert result.startswith("Hello caf")
        assert "World" in result
        # Unicode parts escaped
        assert "\\xe9" in result  # é
        assert "\\u" in result  # emoji and Chinese
        # All ASCII
        assert all(ord(c) < 128 for c in result)

    def test_sanitize_newlines_preserved(self) -> None:
        """Test that newlines are not escaped."""
        result = _sanitize_unicode("Line1\nLine2\r\nLine3")
        assert "\\n" not in result
        assert "\\r" not in result

    def test_sanitize_special_ascii_characters(self) -> None:
        """Test that special ASCII characters pass through."""
        special = "!@#$%^&*()[]{}|;':\",./<>?"
        result = _sanitize_unicode(special)
        # Most special chars should be unchanged
        assert "@" in result
        assert "#" in result
        assert "$" in result


class TestJsonFormatter:
    """Test the JsonFormatter class."""

    def test_format_basic_record(self) -> None:
        """Test basic record formatting."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert parsed["level"] == "INFO"
        assert parsed["logger_name"] == "test_logger"
        assert parsed["message"] == "Test message"
        assert "timestamp" in parsed

    def test_format_with_args(self) -> None:
        """Test record formatting with message arguments."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="Error: %s",
            args=("Something went wrong",),
            exc_info=None,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert parsed["message"] == "Error: Something went wrong"

    def test_format_timestamp_is_iso8601(self) -> None:
        """Test that timestamp is in ISO8601 format with timezone."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        # Set a specific timestamp for consistent testing
        record.created = 1693930496.789123  # 2023-09-05T16:14:56.789123Z

        result = formatter.format(record)
        parsed = json.loads(result)

        timestamp = parsed["timestamp"]
        # Should be ISO8601 format with timezone
        assert timestamp == "2023-09-05T16:14:56.789123Z"
        # Should contain timezone indicator
        assert timestamp.endswith("Z") or "+" in timestamp or "-" in timestamp[-6:]

    def test_format_handles_different_log_levels(self) -> None:
        """Test JsonFormatter with different log levels."""
        formatter = JsonFormatter()
        test_levels = [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL"),
        ]

        for level_int, level_name in test_levels:
            record = logging.LogRecord(
                name="test_logger",
                level=level_int,
                pathname="",
                lineno=0,
                msg="Test message for %s",
                args=(level_name,),
                exc_info=None,
            )

            result = formatter.format(record)
            parsed = json.loads(result)

            assert parsed["level"] == level_name
            assert parsed["message"] == f"Test message for {level_name}"

    def test_format_handles_special_characters(self) -> None:
        """Test JsonFormatter with special characters in messages."""
        formatter = JsonFormatter()
        special_messages = [
            'Message with "quotes"',
            "Message with \\n newlines \\n",
            "Message with special chars: !@#$%^&*()",
            "Message with backslashes: C:\\\\path\\\\to\\\\file",
            "",  # Empty message
        ]

        for msg in special_messages:
            record = logging.LogRecord(
                name="test_logger",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg=msg,
                args=(),
                exc_info=None,
            )

            result = formatter.format(record)
            # Should not raise exception and should be valid JSON
            parsed = json.loads(result)
            assert "message" in parsed

    def test_format_sanitizes_unicode(self) -> None:
        """Test JsonFormatter sanitizes unicode characters to escape sequences."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Unicode test: café ☕ 你好",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        # Verify unicode characters are escaped
        assert "caf\\xe9" in parsed["message"]  # café -> caf\xe9
        assert "\\u" in parsed["message"]  # Unicode characters escaped
        # Ensure no actual unicode characters remain (only ASCII)
        assert all(ord(c) < 128 for c in parsed["message"])

    def test_format_includes_exception_info(self) -> None:
        """Test JsonFormatter includes exception details when present."""
        formatter = JsonFormatter()

        try:
            raise ValueError("Test error message")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="",
            lineno=0,
            msg="An error occurred",
            args=(),
            exc_info=exc_info,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert "exception" in parsed
        assert parsed["exception"]["type"] == "ValueError"
        assert parsed["exception"]["message"] == "Test error message"
        assert "Traceback" in parsed["exception"]["traceback"]
        assert "ValueError: Test error message" in parsed["exception"]["traceback"]

    def test_format_no_exception_when_none(self) -> None:
        """Test JsonFormatter excludes exception field when no exception present."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Normal message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert "exception" not in parsed


class TestSanitizingFormatter:
    """Test the SanitizingFormatter class."""

    def test_format_basic_record(self) -> None:
        """Test basic record formatting."""
        formatter = SanitizingFormatter("%(levelname)s - %(message)s")
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        assert "INFO" in result
        assert "Test message" in result

    def test_format_sanitizes_unicode(self) -> None:
        """Test SanitizingFormatter sanitizes unicode characters."""
        formatter = SanitizingFormatter("%(message)s")
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Unicode: café ☕",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)

        # Verify unicode characters are escaped
        assert "caf\\xe9" in result
        assert "\\u2615" in result  # ☕
        assert all(ord(c) < 128 for c in result)

    def test_format_restores_original_message(self) -> None:
        """Test SanitizingFormatter restores original message after formatting."""
        formatter = SanitizingFormatter("%(message)s")
        original_msg = "Unicode: café"
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=original_msg,
            args=(),
            exc_info=None,
        )

        formatter.format(record)

        # Original message should be restored
        assert record.msg == original_msg

    def test_format_handles_non_string_message(self) -> None:
        """Test SanitizingFormatter handles non-string messages gracefully."""
        formatter = SanitizingFormatter("%(message)s")
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=12345,  # Non-string message
            args=(),
            exc_info=None,
        )

        # Should not raise exception
        result = formatter.format(record)
        assert "12345" in result


class TestInitializeLogging:
    """Test the initialize_logging function."""

    def test_initialize_logging_json_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test logging initialization in JSON mode."""
        mock_config = MagicMock()
        mock_config.log_level = "INFO"
        mock_config.log_type = "JSON"

        monkeypatch.setattr("src.utils.logger.Config", mock_config)

        mock_basic_config = MagicMock()
        monkeypatch.setattr("logging.basicConfig", mock_basic_config)

        initialize_logging()

        # Should call basicConfig with custom handler
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        assert call_args[1]["level"] == "INFO"
        assert "handlers" in call_args[1]

    def test_initialize_logging_text_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test logging initialization in text mode."""
        mock_config = MagicMock()
        mock_config.log_level = "DEBUG"
        mock_config.log_type = "TEXT"

        monkeypatch.setattr("src.utils.logger.Config", mock_config)

        mock_basic_config = MagicMock()
        monkeypatch.setattr("logging.basicConfig", mock_basic_config)

        initialize_logging()

        # Should call basicConfig with handlers (not format directly)
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        assert call_args[1]["level"] == "DEBUG"
        assert "handlers" in call_args[1]
        # Verify handler has SanitizingFormatter
        handlers = call_args[1]["handlers"]
        assert len(handlers) == 1
        assert handlers[0].formatter.__class__.__name__ == "SanitizingFormatter"

    def test_initialize_logging_uses_config_log_level(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that initialize_logging uses log level from Config and handles case insensitivity."""
        # Test lowercase conversion
        mock_config = MagicMock()
        mock_config.log_level = "warning"  # lowercase
        mock_config.log_type = "JSON"

        monkeypatch.setattr("src.utils.logger.Config", mock_config)

        mock_basic_config = MagicMock()
        monkeypatch.setattr("logging.basicConfig", mock_basic_config)

        initialize_logging()

        # Should convert to uppercase
        call_args = mock_basic_config.call_args
        assert call_args[1]["level"] == "WARNING"

    def test_initialize_logging_produces_log_messages(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that initialize_logging produces appropriate log messages for both modes."""
        # Test JSON mode
        mock_config = MagicMock()
        mock_config.log_level = "INFO"
        mock_config.log_type = "JSON"
        monkeypatch.setattr("src.utils.logger.Config", mock_config)

        with caplog.at_level(logging.INFO):
            initialize_logging()

        assert "Logging initialized in JSON format" in caplog.text

        # Clear logs for next test
        caplog.clear()

        # Test text mode
        mock_config.log_type = "TEXT"
        monkeypatch.setattr("src.utils.logger.Config", mock_config)

        with caplog.at_level(logging.INFO):
            initialize_logging()

        assert "Logging initialized in text format" in caplog.text
