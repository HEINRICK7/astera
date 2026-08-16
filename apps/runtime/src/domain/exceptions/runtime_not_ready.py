"""RuntimeNotReadyError — raised when Kernel is not ready to serve requests."""
from __future__ import annotations

from apps.runtime.src.domain.exceptions.base import AsteraError


class RuntimeNotReadyError(AsteraError):
    """Raised when a request reaches the API before the Kernel is READY."""

    def __init__(self) -> None:
        super().__init__(
            "The Kernel is not ready to serve requests.",
            code="KERNEL_NOT_READY",
        )
