"""Deterministic LLM providers and fallback router for contract tests."""
from __future__ import annotations

from typing import Mapping

from .models import CompletionRequest, CompletionResponse
from .protocol import LlmProvider


class DeterministicLlmProvider:
    """Return a configured response while preserving the provider contract."""

    def __init__(self, content: str, *, provider: str) -> None:
        if not content.strip() or not provider.strip():
            raise ValueError("content and provider must not be empty")
        self._content = content
        self._provider = provider

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        return CompletionResponse(
            provider=self._provider,
            model=request.model,
            content=self._content,
            usage={"prompt_tokens": sum(len(message.content.split()) for message in request.messages)},
        )


class ModelRouter:
    """Route to ordered providers and continue through configured fallbacks."""

    def __init__(
        self,
        providers: Mapping[str, LlmProvider],
        *,
        fallback_order: tuple[str, ...],
    ) -> None:
        if not fallback_order:
            raise ValueError("fallback_order must not be empty")
        missing = [name for name in fallback_order if name not in providers]
        if missing:
            raise ValueError(f"fallback providers not registered: {missing}")
        self._providers = dict(providers)
        self._fallback_order = fallback_order

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        failures: list[str] = []
        for provider_name in self._fallback_order:
            try:
                return await self._providers[provider_name].complete(request)
            except Exception as exc:  # provider boundary must preserve fallback behavior
                failures.append(f"{provider_name}: {exc}")
        raise RuntimeError("All LLM providers failed: " + "; ".join(failures))
