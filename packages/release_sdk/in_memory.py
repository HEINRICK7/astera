"""Deterministic release history for deployment orchestration tests."""
from __future__ import annotations

from dataclasses import replace
from threading import RLock
from uuid import uuid4

from .models import ReleaseRecord


class InMemoryReleaseManager:
    def __init__(self) -> None:
        self._lock = RLock()
        self._history: list[ReleaseRecord] = []

    def deploy(self, image_tag: str) -> ReleaseRecord:
        with self._lock:
            previous = self._history[-1].image_tag if self._history else None
            record = ReleaseRecord(
                release_id=uuid4().hex,
                image_tag=image_tag,
                previous_image_tag=previous,
            )
            self._history.append(record)
            return record

    def rollback(self) -> ReleaseRecord:
        with self._lock:
            if len(self._history) < 2:
                raise RuntimeError("rollback requires at least two releases")
            current = self._history[-1]
            target = self._history[-2]
            record = ReleaseRecord(
                release_id=uuid4().hex,
                image_tag=target.image_tag,
                status="rolled_back",
                previous_image_tag=current.image_tag,
            )
            self._history.append(record)
            return record

    def history(self) -> tuple[ReleaseRecord, ...]:
        with self._lock:
            return tuple(reversed(self._history))
