"""Immutable chat completion contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ChatMessage:
    role: str
    content: str

    def __post_init__(self) -> None:
        if not self.role.strip() or not self.content.strip():
            raise ValueError("role and content must not be empty")


@dataclass(frozen=True, slots=True)
class CompletionRequest:
    messages: tuple[ChatMessage, ...]
    model: str
    temperature: float = 0.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.messages:
            raise ValueError("messages must contain at least one item")
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")


@dataclass(frozen=True, slots=True)
class CompletionResponse:
    provider: str
    model: str
    content: str
    finish_reason: str = "stop"
    usage: Mapping[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.model.strip() or not self.content.strip():
            raise ValueError("provider, model and content must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "model": self.model,
            "content": self.content,
            "finish_reason": self.finish_reason,
            "usage": dict(self.usage),
        }
