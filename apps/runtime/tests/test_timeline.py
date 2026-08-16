"""Tests for tenant-safe patient timelines."""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from packages.auth_sdk import Principal
from packages.timeline_sdk import TimelineDirectory


class TimelineTests(unittest.TestCase):
    def test_timeline_is_ordered_and_organization_isolated(self) -> None:
        directory = TimelineDirectory()
        principal = Principal("user-1", "doctor@example.com", "org-1")
        other = Principal("user-2", "other@example.com", "org-2")
        later = datetime(2026, 8, 7, 12, 0, tzinfo=timezone.utc)
        earlier = datetime(2026, 8, 7, 11, 0, tzinfo=timezone.utc)

        directory.append(principal, patient_id="patient-1", event_type="encounter.completed", occurred_at=later)
        directory.append(principal, patient_id="patient-1", event_type="encounter.started", occurred_at=earlier)
        directory.append(other, patient_id="patient-1", event_type="foreign.event", occurred_at=earlier)

        events = directory.list_for(principal, "patient-1")
        self.assertEqual([event.event_type for event in events], ["encounter.started", "encounter.completed"])
