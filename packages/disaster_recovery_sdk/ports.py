"""Disaster Recovery planning port."""
from __future__ import annotations

from typing import Protocol

from .models import RecoveryPlan, RecoveryStatus


class RecoveryPort(Protocol):
    def register(self, plan: RecoveryPlan) -> None:
        ...

    def record_drill(self, service: str, *, passed: bool) -> None:
        ...

    def status(self) -> RecoveryStatus:
        ...
