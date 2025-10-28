"""Logging configuration and utilities."""

import logging
import structlog
from typing import Any, Dict

from app.core.shared.config import settings


def configure_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)


def log_request(method: str, path: str, **kwargs: Any) -> None:
    """Log HTTP request information."""
    logger = get_logger("api.request")
    logger.info("HTTP request", method=method, path=path, **kwargs)


def log_response(status_code: int, response_time: float, **kwargs: Any) -> None:
    """Log HTTP response information."""
    logger = get_logger("api.response")
    logger.info("HTTP response", status_code=status_code, response_time=response_time, **kwargs)