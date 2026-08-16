"""In-memory recovery plan registry."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from threading import RLock

from .models import RecoveryPlan, RecoveryStatus


class InMemoryRecoveryCoordinator:
    def __init__(self) -> None:
        self._lock = RLock()
        self._plans: dict[str, RecoveryPlan] = {}

    def register(self, plan: RecoveryPlan) -> None:
        with self._lock:
            self._plans[plan.service] = plan

    def record_drill(self, service: str, *, passed: bool) -> None:
        with self._lock:
            if service not in self._plans:
                raise KeyError(service)
            self._plans[service] = replace(
                self._plans[service],
                last_drill_at=datetime.now(timezone.utc),
                last_drill_passed=passed,
            )

    def status(self) -> RecoveryStatus:
        with self._lock:
            return RecoveryStatus(plans=tuple(self._plans.values()))
