import logging
import structlog
import sys
from .config import settings

def setup_logger():
    """
    Configures structlog to output JSON formatted logs.
    This is highly valued in production environments for log aggregation.
    """
    log_level = logging.getLevelName(settings.LOG_LEVEL.upper())
    
    # Configure standard logging to be captured by structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # In development, output pretty logs; in production, use JSON
    if settings.ENVIRONMENT.lower() == "development":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Create a logger instance for the application
logger = structlog.get_logger()
