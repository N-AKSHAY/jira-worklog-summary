"""Structured JSON logging configuration."""

import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
from pythonjsonlogger import jsonlogger


class StructuredLogger:
    """Structured JSON logger wrapper."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = jsonlogger.JsonFormatter(
                "%(timestamp)s %(level)s %(name)s %(message)s",
                timestamp=True
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None
    ):
        reserved_fields = {
            "message", "levelname", "levelno", "pathname", "filename",
            "module", "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "getMessage"
        }
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if extra:
            for key, value in extra.items():
                if key not in reserved_fields:
                    log_data[key] = value
        
        if exc_info:
            log_data["exception_type"] = type(exc_info).__name__
            log_data["exception_message"] = str(exc_info)
        
        self.logger.log(level, message, extra=log_data, exc_info=exc_info if exc_info else False)
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self._log(logging.INFO, message, extra)
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._log(logging.WARNING, message, extra)
    
    def error(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None
    ):
        """Log error message."""
        self._log(logging.ERROR, message, extra, exc_info)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self._log(logging.DEBUG, message, extra)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)
