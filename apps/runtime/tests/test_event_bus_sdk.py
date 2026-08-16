"""Tests for the shared Event Bus SDK contract."""
from __future__ import annotations

import unittest

from packages.shared.events import EventBusPort, WorkflowStartedEvent, serialize_event


class EventBusPortTests(unittest.TestCase):
    def test_event_serialization_is_utf8_json(self) -> None:
        event = WorkflowStartedEvent(workflow_id="workflow-1", workflow_name="echo")

        payload = serialize_event(event)

        self.assertIsInstance(payload, bytes)
        self.assertIn(b'"workflow_id":"workflow-1"', payload)

    def test_port_remains_abstract(self) -> None:
        with self.assertRaises(TypeError):
            EventBusPort()  # type: ignore[abstract]

