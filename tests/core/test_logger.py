"""Pytest suite for procela logger."""

import json
import logging
import sys

import pytest

from procela.core.logger import JsonFormatter, TextFormatter, setup_logging


class TestJsonFormatter:
    def test_format_basic_record(self):
        """Test formatting a basic log record without extras or exception."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.created = 1609459200.0  # 2021-01-01 00:00:00 UTC

        result = json.loads(formatter.format(record))

        assert result["time"] == "2021-01-01T00:00:00+00:00"
        assert result["level"] == "INFO"
        assert result["logger"] == "test_logger"
        assert result["message"] == "Test message"
        assert result["module"] == "test"
        assert result["line"] == 42
        assert "exception" not in result
        assert "extra" not in result

    def test_format_with_exception(self):
        """Test formatting a record with exception info."""
        formatter = JsonFormatter()

        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        result = json.loads(formatter.format(record))

        assert "exception" in result
        assert "ValueError: Test exception" in result["exception"]
        assert "Traceback" in result["exception"]

    def test_format_with_extra_attribute(self):
        """Test formatting a record with custom extra attribute."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.extra = {"user_id": 123, "action": "login"}

        result = json.loads(formatter.format(record))

        assert result["extra"] == {"user_id": 123, "action": "login"}


class TestTextFormatter:
    def test_format(self):
        """Test text formatter produces expected format."""
        formatter = TextFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=42,
            msg="Warning message",
            args=(),
            exc_info=None,
        )
        record.created = 1609459200.0

        result = formatter.format(record)

        # Format: "YYYY-MM-DD HH:MM:SS | LEVEL     | logger | message"
        assert "2021-01-01 00:00:00" in result
        assert "| WARNING  |" in result
        assert "test_logger" in result
        assert "Warning message" in result


class TestSetupLogging:
    @pytest.fixture(autouse=True)
    def cleanup_loggers(self):
        """Clean up loggers after each test to avoid handler duplication."""
        yield
        # Remove any handlers added during the test
        for logger_name in ["test_app", "procela"]:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()

    def test_returns_logger_with_correct_name(self):
        """Test setup_logging returns logger with specified name."""
        logger = setup_logging(name="test_app", level=logging.DEBUG, console=False)

        assert logger.name == "test_app"
        assert logger.level == logging.DEBUG
        assert logger.propagate is False

    def test_console_handler_added_when_console_true(self):
        """Test console handler is added when console=True."""
        logger = setup_logging(console=True, log_file=None, json_file=None)

        handlers = logger.handlers
        assert len(handlers) == 1
        assert isinstance(handlers[0], logging.StreamHandler)
        assert handlers[0].stream == sys.stdout
        assert isinstance(handlers[0].formatter, TextFormatter)

    def test_no_console_handler_when_console_false(self):
        """Test no console handler when console=False."""
        logger = setup_logging(console=False)

        assert not any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    def test_text_file_handler_added(self, tmp_path):
        """Test text file handler is added when log_file provided."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(console=False, log_file=log_file)

        handlers = logger.handlers
        assert len(handlers) == 1
        handler = handlers[0]
        assert isinstance(handler, logging.FileHandler)
        assert handler.baseFilename == str(log_file)
        assert isinstance(handler.formatter, TextFormatter)

    def test_json_file_handler_added(self, tmp_path):
        """Test JSON file handler is added when json_file provided."""
        json_file = tmp_path / "test.json"
        logger = setup_logging(console=False, json_file=json_file)

        handlers = logger.handlers
        assert len(handlers) == 1
        handler = handlers[0]
        assert isinstance(handler, logging.FileHandler)
        assert handler.baseFilename == str(json_file)
        assert isinstance(handler.formatter, JsonFormatter)

    def test_multiple_handlers_added(self, tmp_path):
        """Test multiple handlers (console, text, JSON) are added."""
        log_file = tmp_path / "test.log"
        json_file = tmp_path / "test.json"

        logger = setup_logging(console=True, log_file=log_file, json_file=json_file)

        handlers = logger.handlers
        assert len(handlers) == 3

        # Check handler types
        console_handlers = [h for h in handlers if isinstance(h, logging.StreamHandler)]
        file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]

        assert len(console_handlers) == 3
        assert len(file_handlers) == 2

        for handler in file_handlers:
            if handler.baseFilename == str(log_file):
                assert isinstance(handler.formatter, TextFormatter)
            elif handler.baseFilename == str(json_file):
                assert isinstance(handler.formatter, JsonFormatter)

    def test_creates_parent_directory_for_log_file(self, tmp_path):
        """Test parent directories are created for log file."""
        log_file = tmp_path / "subdir" / "test.log"

        # Create the logger - this should create the directory
        setup_logging(console=False, log_file=log_file)

        # Verify directory was created
        assert log_file.parent.exists()
        assert log_file.parent.is_dir()

    def test_creates_parent_directory_for_json_file(self, tmp_path):
        """Test parent directories are created for JSON file."""
        json_file = tmp_path / "subdir" / "test.json"

        # Create the logger - this should create the directory
        setup_logging(console=False, json_file=json_file)

        # Verify directory was created
        assert json_file.parent.exists()
        assert json_file.parent.is_dir()

    def test_does_not_add_duplicate_handlers(self, tmp_path):
        """Test handlers are not duplicated when setup_logging called twice."""
        log_file = tmp_path / "test.log"

        logger1 = setup_logging(console=False, log_file=log_file)
        handlers_count1 = len(logger1.handlers)

        logger2 = setup_logging(console=False, log_file=log_file)
        handlers_count2 = len(logger2.handlers)

        # Same logger instance returned
        assert logger1 is logger2
        assert handlers_count1 == handlers_count2
        assert handlers_count1 == 1

    def test_logger_propagate_false(self):
        """Test logger.propagate is set to False."""
        logger = setup_logging(console=False)
        assert logger.propagate is False
