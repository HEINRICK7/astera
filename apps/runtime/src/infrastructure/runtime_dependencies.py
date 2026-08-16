"""Production dependency lifecycle and readiness supervision.

This module is infrastructure orchestration.  It is intentionally outside
Application and Domain so retry, health and teardown policy cannot leak into
use cases.
"""
from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Awaitable, Callable, Mapping
from typing import Any

logger = logging.getLogger("astera.infrastructure.dependencies")

Check = Callable[[], Any]


class RuntimeDependencySupervisor:
    """Own startup validation, readiness reporting and reverse-order cleanup."""

    def __init__(
        self,
        *,
        startup_checks: Mapping[str, Check] = (),
        health_checks: Mapping[str, Check] = (),
        close_callbacks: tuple[Callable[[], Any], ...] = (),
        retries: int = 3,
        backoff_seconds: float = 0.25,
    ) -> None:
        self._startup_checks = dict(startup_checks)
        self._health_checks = dict(health_checks)
        self._close_callbacks = close_callbacks
        self._retries = max(1, retries)
        self._backoff_seconds = max(0.0, backoff_seconds)
        self._started = False

    async def start(self) -> None:
        """Validate critical dependencies before the Runtime accepts traffic."""
        for name, check in self._startup_checks.items():
            await self._retry(name, check)
        self._started = True

    async def health(self) -> dict[str, Any]:
        """Return per-dependency readiness without hiding the failing cause."""
        result: dict[str, Any] = {}
        for name, check in self._health_checks.items():
            try:
                value = check()
                if inspect.isawaitable(value):
                    value = await value
                result[name] = {"ready": True, **value} if isinstance(value, dict) else {"ready": True}
            except Exception as exc:
                result[name] = {"ready": False, "error": str(exc)}
        return result

    async def is_ready(self) -> bool:
        if not self._started:
            return False
        statuses = await self.health()
        return bool(statuses) and all(status.get("ready", False) for status in statuses.values())

    async def close(self) -> None:
        """Close owned resources in reverse construction order."""
        for callback in reversed(self._close_callbacks):
            try:
                result = callback()
                if inspect.isawaitable(result):
                    await result
            except Exception:
                logger.exception("Dependency shutdown callback failed")
        self._started = False

    async def _retry(self, name: str, check: Check) -> None:
        last_error: Exception | None = None
        for attempt in range(1, self._retries + 1):
            try:
                value = check()
                if inspect.isawaitable(value):
                    await value
                return
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Dependency startup check failed",
                    extra={"dependency": name, "attempt": attempt, "error": str(exc)},
                )
                if attempt < self._retries:
                    await asyncio.sleep(self._backoff_seconds * (2 ** (attempt - 1)))
        assert last_error is not None
        raise RuntimeError(f"Dependency '{name}' is not ready: {last_error}") from last_error
