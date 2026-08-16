"""ContextNotFoundError — raised when a ContextScope cannot be found."""
from __future__ import annotations

from apps.runtime.src.domain.exceptions.base import AsteraError


class ContextNotFoundError(AsteraError):
    """Raised when ContextManager cannot find the requested ContextScope."""

    def __init__(self, context_id: str) -> None:
        super().__init__(
            f"Context '{context_id}' not found.",
            code="CONTEXT_NOT_FOUND",
        )
        self.context_id = context_id
