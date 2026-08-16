"""Audit persistence port."""
from __future__ import annotations

from typing import Protocol

from .models import AuditEntry


class AuditPort(Protocol):
    """Write and query audit records within an organization boundary."""

    def append(self, entry: AuditEntry) -> None:
        ...

    def list_for_organization(
        self,
        organization_id: str,
        *,
        limit: int = 100,
        action: str | None = None,
    ) -> tuple[AuditEntry, ...]:
        ...
