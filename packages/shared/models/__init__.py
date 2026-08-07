"""
Astera Shared Models.

This package contains value objects, DTOs, enums, and base models
that are shared across multiple packages in the platform.

Rule: Only pure Python or Pydantic here.
      No framework-specific imports (no FastAPI, no NATS, no SQLAlchemy).
"""
from .base import AsteraModel, AsteraEvent
from .enums import ComponentStatus, EventPriority

__all__ = [
    "AsteraModel",
    "AsteraEvent",
    "ComponentStatus",
    "EventPriority",
]
