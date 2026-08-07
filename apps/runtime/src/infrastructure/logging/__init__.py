"""
Astera Runtime — Infrastructure Logging.

Configures structured JSON logging for the entire Runtime.
All log output is structured and compatible with Loki / OpenTelemetry.

Usage:
    from apps.runtime.src.infrastructure.logging import configure_logging
    configure_logging(level="INFO")
"""
from __future__ import annotations

import logging
import sys
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Module-level logger for the Runtime itself
logger = logging.getLogger("astera.runtime")


def configure_logging(level: LogLevel = "INFO", *, json_format: bool = True) -> None:
    """
    Configure structured logging for the Astera Runtime.

    In production, emits JSON-formatted log lines for Loki ingestion.
    In development, emits human-readable colored output when json_format=False.

    This must be called once during platform startup, before any other
    module emits log messages.

    Args:
        level: The minimum log level to emit.
        json_format: If True, use JSON formatter (for production/Loki).
                     If False, use a simple human-readable formatter.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicate output
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if json_format:
        formatter = _JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("uvicorn.access", "httpx", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logger.info(
        "Logging configured",
        extra={"level": level, "format": "json" if json_format else "text"},
    )


class _JsonFormatter(logging.Formatter):
    """
    Minimal JSON log formatter.

    Produces one JSON object per line, suitable for Loki/Grafana ingestion.
    Does not depend on external libraries (structlog, python-json-logger).
    """

    import json as _json

    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime, timezone

        payload: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Include extra fields passed via extra={...}
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith("_"):
                if key not in payload:
                    payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str, ensure_ascii=False)
