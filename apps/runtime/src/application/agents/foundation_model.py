"""Provider-neutral foundation model port."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class FoundationModel(Protocol):
    """Boundary between Astera agent configuration and a model runtime."""

    provider: str
    model_name: str

    def build_model(self) -> Any:
        """Return the provider model representation for this model."""
