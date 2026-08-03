import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formats each log as a structured JSON line."""

    SERVICE_NAME = "requests-api"

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.SERVICE_NAME,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Enriched optional fields
        for field in (
            "request_id",
            "external_id",
            "method",
            "endpoint",
            "status_code",
            "duration_ms",
            "attempt",
            "error",
        ):
            value = getattr(record, field, None)
            if value is not None:
                log_entry[field] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False, default=str)


def setup_logging(log_level: str = "INFO") -> None:
    formatter = JSONFormatter()

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    log_file = os.getenv("LOG_FILE", "logs/api.log")
    os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(stream_handler)
    root.addHandler(file_handler)

    # Silence verbose logs from external libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class TimingContext:
    """Context for measuring operation duration."""

    def __init__(self) -> None:
        self._start: float = 0.0

    def __enter__(self) -> "TimingContext":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_: object) -> None:
        pass

    @property
    def elapsed_ms(self) -> int:
        return int((time.perf_counter() - self._start) * 1000)
