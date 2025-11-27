"""Unit tests for Logger utility."""

import pytest
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from cascaded_fit.utils.logger import Logger


class TestLogger:
    """Test Logger class."""

    def test_get_logger(self):
        """Test getting a logger instance."""
        logger = Logger.get("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_cached(self):
        """Test logger instances are cached."""
        logger1 = Logger.get("test_module")
        logger2 = Logger.get("test_module")
        assert logger1 is logger2

    def test_setup_console_only(self):
        """Test logger setup with console only."""
        Logger._configured = False  # Reset for test
        Logger.setup(log_to_console=True)
        
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0

    @patch('cascaded_fit.utils.logger.Path.mkdir')
    def test_setup_with_file(self, mock_mkdir, tmp_path):
        """Test logger setup with file handler."""
        Logger._configured = False  # Reset for test
        log_file = str(tmp_path / "test.log")
        
        Logger.setup(log_file=log_file, log_to_console=False)
        
        root_logger = logging.getLogger()
        handlers = root_logger.handlers
        file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0

    def test_setup_only_once(self):
        """Test logger setup only configures once."""
        Logger._configured = False  # Reset for test
        Logger.setup()
        
        handler_count_before = len(logging.getLogger().handlers)
        
        # Try to setup again
        Logger.setup()
        
        # Should not add more handlers
        handler_count_after = len(logging.getLogger().handlers)
        assert handler_count_after == handler_count_before

    def test_setup_custom_level(self):
        """Test logger setup with custom log level."""
        Logger._configured = False  # Reset for test
        Logger.setup(level="DEBUG")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

