"""Provider-neutral tool adapters."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Protocol, runtime_checkable


@runtime_checkable
class ToolAdapter(Protocol):
    """Boundary for REST, MCP, local, workflow, CLI or FHIR tools."""

    name: str

    def build_tool(self) -> Any:
        """Return a callable tool representation for an agent runtime."""


@dataclass(frozen=True, slots=True)
class PythonToolAdapter:
    """Adapt a local callable while keeping tool ownership outside the ADK."""

    name: str
    handler: Callable[..., Any]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must not be empty")

    def build_tool(self) -> Callable[..., Any]:
        def tool(*args: Any, **kwargs: Any) -> Any:
            return self.handler(*args, **kwargs)

        tool.__name__ = self.name
        tool.__doc__ = f"Astera tool: {self.name}"
        return tool
