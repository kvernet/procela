"""
Logger module for the Procela framework.

Examples
--------
>>> from procela import setup_logging
>>>
>>> logger = setup_logging()
>>>
>>> logger.info("Info message")
2026-03-21 17:20:30 | INFO     | procela | Info message
>>> logger.warning("Warning message")
2026-03-21 17:20:30 | WARNING  | procela | Warning message
>>> logger.critical("Critical message")
2026-03-21 17:20:30 | CRITICAL | procela | Critical message

Semantics Reference
-------------------
https://procela.org/docs/semantics/core/timer.html

Examples Reference
------------------
https://procela.org/docs/examples/core/timer.html
"""

from __future__ import annotations

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def _utc_converter(timestamp: float | None) -> time.struct_time:
    return time.gmtime(timestamp if timestamp is not None else 0.0)


class JsonFormatter(logging.Formatter):
    """Format logs as JSON for machine analysis."""

    def format(self, record: logging.LogRecord) -> str:
        """
        JSON format.

        Parameters
        ----------
            record : logging.LogRecord
                The record to format.
        """
        log = {
            "time": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra"):
            log["extra"] = record.extra

        return json.dumps(log)


class TextFormatter(logging.Formatter):
    """Human-readable formatter."""

    converter = staticmethod(_utc_converter)

    def __init__(self) -> None:
        """Text formatter constructor."""
        super().__init__(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )


def setup_logging(
    name: str = "procela",
    level: int = logging.INFO,
    console: bool = True,
    log_file: str | Path | None = None,
    json_file: str | Path | None = None,
) -> logging.Logger:
    """
    Configure logging.

    Parameters
    ----------
    name : str
        The logger name. Default is "procela".
    level : int
        The logging level. Default is logging.INFO.
    console : bool
        Enable console logging. Default is True.
    log_file : str | Path
        The path to text log file. Default is None.
    json_file : str | Path
        The path to JSON log file. Default is None.

    Examples
    --------
    >>> from procela import setup_logging
    >>>
    >>> logger = setup_logging()
    >>>
    >>> logger.info("Info message")
    2026-03-21 17:20:30 | INFO     | procela | Info message
    >>> logger.warning("Warning message")
    2026-03-21 17:20:30 | WARNING  | procela | Warning message
    >>> logger.critical("Critical message")
    2026-03-21 17:20:30 | CRITICAL | procela | Critical message
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    text_formatter = TextFormatter()
    json_formatter = JsonFormatter()

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(text_formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(text_formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    if json_file:
        json_path = Path(json_file)
        json_path.parent.mkdir(parents=True, exist_ok=True)

        json_handler = logging.FileHandler(json_path)
        json_handler.setFormatter(json_formatter)
        json_handler.setLevel(level)
        logger.addHandler(json_handler)

    return logger
