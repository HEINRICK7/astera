"""Performance monitoring port."""
from __future__ import annotations

from typing import Mapping, Protocol

from .models import PerformanceSnapshot


class PerformancePort(Protocol):
    def record(self, operation: str, duration_ms: float, *, success: bool = True) -> None:
        ...

    def snapshot(self) -> PerformanceSnapshot:
        ...
