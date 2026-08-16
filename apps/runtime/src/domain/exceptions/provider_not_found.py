"""ProviderNotFoundError — raised when a Provider is not in the ProviderRegistry."""
from __future__ import annotations

from apps.runtime.src.domain.exceptions.base import AsteraError
from apps.runtime.src.domain.value_objects.provider_name import ProviderName


class ProviderNotFoundError(AsteraError):
    """Raised when ProviderRegistry.get() is called with an unknown ProviderName."""

    def __init__(self, provider: ProviderName) -> None:
        super().__init__(
            f"Provider '{provider}' is not registered in the ProviderRegistry.",
            code="PROVIDER_NOT_FOUND",
        )
        self.provider = provider
