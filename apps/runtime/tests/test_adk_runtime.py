"""Tests for the Google ADK Runtime bridge."""
from __future__ import annotations

import unittest

from apps.runtime.src.adapters.agents.google_adk import AdkRuntime
from apps.runtime.src.application.agents import FoundationModel, PythonToolAdapter
from apps.runtime.src.domain.entities.context_scope import ContextScope


class FakeFoundationModel:
    provider = "test"
    model_name = "test-model"

    def build_adk_model(self):
        return "test-model"


class AdkRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_agent_app_and_contextual_session(self) -> None:
        runtime = AdkRuntime.from_definition(
            app_name="astera_test",
            agent_name="astera_test_agent",
            model_name="gemini-2.0-flash",
            instruction="Respond briefly.",
        )
        context = ContextScope(
            organization_id="org-1",
            workspace_id="workspace-1",
        )
        session = await runtime.create_session(
            user_id="professional-1",
            context=context,
            session_id="session-1",
        )

        self.assertEqual(runtime.app_name, "astera_test")
        self.assertEqual(session.id, "session-1")
        self.assertEqual(
            session.state["astera_context"]["organization_id"],
            "org-1",
        )
        self.assertEqual(runtime.build_app().name, "astera_test")

    async def test_foundation_model_is_resolved_through_adapter(self) -> None:
        foundation_model: FoundationModel = FakeFoundationModel()
        runtime = AdkRuntime.from_definition(
            app_name="astera_adapter_test",
            agent_name="astera_adapter_agent",
            foundation_model=foundation_model,
            instruction="Respond briefly.",
        )

        self.assertEqual(runtime.root_agent.model, "test-model")

    async def test_tool_is_resolved_through_tool_adapter(self) -> None:
        foundation_model: FoundationModel = FakeFoundationModel()
        runtime = AdkRuntime.from_definition(
            app_name="astera_tool_adapter_test",
            agent_name="astera_tool_adapter_agent",
            foundation_model=foundation_model,
            instruction="Use tools when needed.",
            tools=[PythonToolAdapter(name="local_tool", handler=lambda: "ok")],
        )

        self.assertEqual(runtime.root_agent.tools[0].__name__, "local_tool")
