"""TaskExecutionError — raised when the TaskOrchestrator fails to execute a task."""
from __future__ import annotations

from apps.runtime.src.domain.exceptions.base import AsteraError


class TaskExecutionError(AsteraError):
    """Raised when TaskOrchestrator.execute() encounters an unrecoverable error."""

    def __init__(self, request_id: str, reason: str) -> None:
        super().__init__(
            f"Task '{request_id}' failed: {reason}",
            code="TASK_EXECUTION_ERROR",
        )
        self.request_id = request_id
