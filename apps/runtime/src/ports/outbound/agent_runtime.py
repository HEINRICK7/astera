"""Outbound port for provider-independent agent execution."""
from __future__ import annotations

from typing import Any

from apps.runtime.src.domain.entities.context_scope import ContextScope


class AgentRuntimePort:
    """Contract used by application services to execute agent turns.

    Provider-specific objects such as Google ADK agents, runners and session
    services stay behind the adapter implementing this port.
    """

    async def create_session(
        self,
        *,
        user_id: str,
        context: ContextScope | None = None,
        session_id: str | None = None,
        state: dict[str, Any] | None = None,
    ) -> Any:
        """Create a provider-backed session with Astera context attached."""
        raise NotImplementedError

    async def run_text(
        self,
        *,
        user_id: str,
        session_id: str,
        text: str,
    ) -> list[Any]:
        """Execute one text turn and return provider-neutral event values."""
        raise NotImplementedError
