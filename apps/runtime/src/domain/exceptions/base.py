"""AsteraError — root exception for all Astera platform errors."""
from __future__ import annotations


class AsteraError(Exception):
    """
    Root exception for all Astera platform errors.

    WHY a root exception:
        HTTP adapters catch AsteraError and map it to appropriate status codes.
        Observability systems can filter by this root to capture all platform errors.
        No exception from domain code should ever be a bare Exception.
    """

    def __init__(self, message: str, code: str = "ASTERA_ERROR") -> None:
        super().__init__(message)
        self.code = code

    @property
    def message(self) -> str:
        return str(self)
