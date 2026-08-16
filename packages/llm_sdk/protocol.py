"""LLM provider and gateway ports."""
from __future__ import annotations

from typing import Protocol

from .models import CompletionRequest, CompletionResponse


class LlmProvider(Protocol):
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Complete a request against one model provider."""


class LlmRouter(Protocol):
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Select a provider and apply fallback policy."""
