"""Centralized logging configuration."""

import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    """Logger factory with consistent configuration."""

    _loggers = {}
    _configured = False

    @classmethod
    def setup(cls, log_file: Optional[str] = None, level: str = "INFO",
              log_to_console: bool = True):
        """Setup logging configuration once."""
        if cls._configured:
            return

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        root_logger.handlers = []

        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        cls._configured = True

    @classmethod
    def get(cls, name: str) -> logging.Logger:
        """Get logger instance by name."""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger

        return cls._loggers[name]
