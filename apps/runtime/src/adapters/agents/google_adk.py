"""Google ADK adapter for the provider-neutral agent runtime port."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from apps.runtime.src.application.agents import FoundationModel, ToolAdapter
from apps.runtime.src.domain.entities.context_scope import ContextScope
from apps.runtime.src.ports.outbound.agent_runtime import AgentRuntimePort


def _build_model(foundation_model: FoundationModel) -> Any:
    """Build a model while accepting the pre-boundary method temporarily."""
    builder = getattr(foundation_model, "build_model", None)
    if builder is None:
        builder = getattr(foundation_model, "build_adk_model", None)
    if builder is None:
        raise TypeError("foundation_model must expose build_model()")
    return builder()


@dataclass(frozen=True, slots=True)
class GeminiAdapter:
    """Adapt a Gemini model to Google ADK."""

    model_name: str
    provider: str = "gemini"

    def __post_init__(self) -> None:
        if not self.model_name.strip():
            raise ValueError("model_name must not be empty")

    def build_model(self) -> Any:
        from google.adk.models import Gemini

        return Gemini(model=self.model_name)


@dataclass(frozen=True, slots=True)
class LiteLlmAdapter:
    """Adapt a LiteLLM-compatible model to Google ADK."""

    model_name: str
    provider: str = "litellm"

    def __post_init__(self) -> None:
        if not self.model_name.strip():
            raise ValueError("model_name must not be empty")

    def build_model(self) -> Any:
        from google.adk.models.lite_llm import LiteLlm

        return LiteLlm(model=self.model_name)


class AdkRuntime(AgentRuntimePort):
    """Concrete Google ADK implementation of the agent runtime port."""

    def __init__(self, app_name: str, root_agent: Any) -> None:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService

        self._app_name = app_name
        self._root_agent = root_agent
        self._session_service = InMemorySessionService()
        self._runner = Runner(
            agent=root_agent,
            app_name=app_name,
            session_service=self._session_service,
        )

    @classmethod
    def from_definition(
        cls,
        *,
        app_name: str,
        agent_name: str,
        instruction: str,
        tools: Iterable[Callable[..., Any] | ToolAdapter] = (),
        foundation_model: FoundationModel | None = None,
        model_name: str | None = None,
    ) -> "AdkRuntime":
        from google.adk.agents import Agent

        if foundation_model is None:
            if model_name is None:
                raise ValueError("foundation_model or model_name is required")
            foundation_model = GeminiAdapter(model_name=model_name)
        runtime_tools = [
            tool.build_tool() if isinstance(tool, ToolAdapter) else tool
            for tool in tools
        ]
        agent = Agent(
            name=agent_name,
            model=_build_model(foundation_model),
            instruction=instruction,
            tools=runtime_tools,
        )
        return cls(app_name=app_name, root_agent=agent)

    @property
    def app_name(self) -> str:
        return self._app_name

    @property
    def root_agent(self) -> Any:
        return self._root_agent

    @property
    def session_service(self) -> Any:
        return self._session_service

    async def create_session(
        self,
        *,
        user_id: str,
        context: ContextScope | None = None,
        session_id: str | None = None,
        state: dict[str, Any] | None = None,
    ) -> Any:
        session_state = dict(state or {})
        if context:
            session_state["astera_context"] = context.to_dict()
        return await self._session_service.create_session(
            app_name=self._app_name,
            user_id=user_id,
            session_id=session_id,
            state=session_state,
        )

    async def run_text(
        self,
        *,
        user_id: str,
        session_id: str,
        text: str,
    ) -> list[Any]:
        from google.genai import types

        message = types.Content(
            role="user",
            parts=[types.Part(text=text)],
        )
        events: list[Any] = []
        async for event in self._runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            events.append(event)
        return events

    def build_app(self) -> Any:
        from google.adk.apps import App

        return App(name=self._app_name, root_agent=self._root_agent)
