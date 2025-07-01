"""Tests for logging configuration."""

import logging
from unittest.mock import patch

import pytest

from src.openalex_mcp.logutil import setup_logging


class TestLoggingSetup:
    """Test logging setup functionality."""

    def test_setup_logging_default(self):
        """Test logging setup with default configuration."""
        logger = setup_logging()
        
        assert logger is not None
        assert logger.name == "openalex_mcp"
        assert logger.level == logging.INFO  # Default from config
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_setup_logging_custom_name(self):
        """Test logging setup with custom logger name."""
        logger = setup_logging("custom_logger")
        
        assert logger.name == "custom_logger"

    @patch('src.openalex_mcp.logutil.config')
    def test_setup_logging_debug_level(self, mock_config):
        """Test logging setup with DEBUG level."""
        mock_config.log_level = "DEBUG"
        
        logger = setup_logging()
        
        assert logger.level == logging.DEBUG

    @patch('src.openalex_mcp.logutil.config')
    def test_setup_logging_warning_level(self, mock_config):
        """Test logging setup with WARNING level."""
        mock_config.log_level = "WARNING"
        
        logger = setup_logging()
        
        assert logger.level == logging.WARNING

    @patch('src.openalex_mcp.logutil.config')
    def test_setup_logging_invalid_level(self, mock_config):
        """Test logging setup with invalid level defaults to INFO."""
        mock_config.log_level = "INVALID_LEVEL"
        
        logger = setup_logging()
        
        # Should default to INFO for invalid level
        assert logger.level == logging.INFO

    def test_logger_no_propagation(self):
        """Test that logger doesn't propagate to root logger."""
        logger = setup_logging()
        
        assert logger.propagate is False

    def test_logger_handler_configuration(self):
        """Test logger handler configuration."""
        logger = setup_logging()
        handler = logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        # Check it's using stderr (for MCP compatibility)
        import sys
        assert handler.stream is sys.stderr
        formatter = handler.formatter
        assert formatter is not None
        fmt = getattr(formatter, '_fmt', None)
        assert fmt is not None
        assert 'asctime' in fmt
        assert 'name' in fmt
        assert 'levelname' in fmt
        assert 'message' in fmt

    def test_logger_clears_existing_handlers(self):
        """Test that setup clears existing handlers."""
        # First setup
        logger1 = setup_logging("test_clear")
        initial_handler_count = len(logger1.handlers)
        
        # Second setup should clear and recreate
        logger2 = setup_logging("test_clear")
        
        assert len(logger2.handlers) == initial_handler_count
        assert logger1 is logger2  # Same logger instance

    def test_multiple_logger_instances(self):
        """Test creating multiple logger instances."""
        logger1 = setup_logging("logger1")
        logger2 = setup_logging("logger2")
        
        assert logger1.name == "logger1"
        assert logger2.name == "logger2"
        assert logger1 is not logger2


class TestDefaultLogger:
    """Test the default logger instance."""

    def test_default_logger_exists(self):
        """Test that default logger instance exists."""
        from src.openalex_mcp.logutil import logger
        
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "openalex_mcp"

    def test_default_logger_level(self):
        """Test default logger level."""
        from src.openalex_mcp.logutil import logger
        
        # Should be INFO by default
        assert logger.level == logging.INFO

    def test_default_logger_handlers(self):
        """Test default logger has handlers."""
        from src.openalex_mcp.logutil import logger
        
        assert len(logger.handlers) > 0
        assert isinstance(logger.handlers[0], logging.StreamHandler)


class TestLoggerFunctionality:
    """Test actual logging functionality."""

    def test_logger_log_messages(self, caplog):
        """Test that logger actually logs messages."""
        # Enable propagation temporarily for testing
        logger = setup_logging("test_logging")
        logger.propagate = True
        try:
            with caplog.at_level(logging.INFO, logger="test_logging"):
                logger.info("Test info message")
                logger.warning("Test warning message")
                logger.error("Test error message")
            # Use 'in' checks for log output
            assert any("Test info message" in r.message for r in caplog.records)
            assert any("Test warning message" in r.message for r in caplog.records)
            assert any("Test error message" in r.message for r in caplog.records)
        finally:
            logger.propagate = False

    def test_logger_debug_not_shown_at_info_level(self, caplog):
        """Test that debug messages aren't shown at INFO level."""
        logger = setup_logging("test_debug")
        logger.setLevel(logging.INFO)
        logger.propagate = True
        try:
            with caplog.at_level(logging.INFO, logger="test_debug"):
                logger.debug("Debug message")
                logger.info("Info message")
            assert not any("Debug message" in r.message for r in caplog.records)
            assert any("Info message" in r.message for r in caplog.records)
        finally:
            logger.propagate = False

    @patch('src.openalex_mcp.logutil.config')
    def test_logger_debug_shown_at_debug_level(self, mock_config, caplog):
        """Test that debug messages are shown at DEBUG level."""
        mock_config.log_level = "DEBUG"
        logger = setup_logging("test_debug_level")
        logger.propagate = True
        try:
            with caplog.at_level(logging.DEBUG, logger="test_debug_level"):
                logger.debug("Debug message")
                logger.info("Info message")
            assert any("Debug message" in r.message for r in caplog.records)
            assert any("Info message" in r.message for r in caplog.records)
        finally:
            logger.propagate = False


class TestLoggerFormat:
    """Test logger message formatting."""

    def test_log_message_format(self, caplog):
        """Test log message contains all expected parts."""
        logger = setup_logging("format_test")
        logger.propagate = True
        try:
            with caplog.at_level(logging.INFO, logger="format_test"):
                logger.info("Test message")
            log_record = caplog.records[0]
            assert log_record.name == "format_test"
            assert log_record.levelname == "INFO"
            assert log_record.message == "Test message"
            assert hasattr(log_record, 'created')
        finally:
            logger.propagate = False

    def test_log_message_formatting_in_output(self, caplog):
        """Test that formatted message contains expected elements."""
        logger = setup_logging("format_output_test")
        logger.propagate = True
        try:
            with caplog.at_level(logging.WARNING, logger="format_output_test"):
                logger.warning("Warning message")
            formatted_output = caplog.text
            assert "Warning message" in formatted_output
        finally:
            logger.propagate = False