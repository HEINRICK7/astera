"""Bounded in-memory audit log for the Runtime foundation."""
from __future__ import annotations

from collections import deque
from threading import RLock

from .models import AuditEntry


class InMemoryAuditLog:
    """Append-only store with tenant-scoped reads and bounded retention."""

    def __init__(self, *, max_entries: int = 2048) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self._entries: deque[AuditEntry] = deque(maxlen=max_entries)
        self._lock = RLock()

    def append(self, entry: AuditEntry) -> None:
        with self._lock:
            self._entries.append(entry)

    def list_for_organization(
        self,
        organization_id: str,
        *,
        limit: int = 100,
        action: str | None = None,
    ) -> tuple[AuditEntry, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        with self._lock:
            matches = [
                entry
                for entry in reversed(self._entries)
                if entry.organization_id == organization_id and (action is None or entry.action == action)
            ]
            return tuple(matches[:limit])
