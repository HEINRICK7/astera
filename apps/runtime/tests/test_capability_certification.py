"""Tests for the capability certification contract."""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from packages.capability_sdk import (
    REQUIRED_GATES,
    CapabilityCertification,
    CapabilityGate,
    CertificationStatus,
    GateStatus,
)


class CapabilityCertificationTests(unittest.TestCase):
    def test_incomplete_speech_certification_cannot_be_production_ready(self) -> None:
        certification = CapabilityCertification(
            capability="speech.transcription",
            version="1.0.0",
            providers=("parakeet",),
            gates=(
                CapabilityGate(
                    gate="engineering",
                    status=GateStatus.PASS,
                    evidence_refs=("test_speech_plugin.py",),
                ),
            ),
            status=CertificationStatus.ENGINEERING_COMPLETE,
        )

        self.assertFalse(certification.is_production_ready())
        self.assertEqual(
            certification.missing_gates(),
            tuple(gate for gate in REQUIRED_GATES if gate != "engineering"),
        )
        self.assertFalse(certification.to_dict()["production_ready"])

    def test_all_passing_gates_issue_production_ready(self) -> None:
        gates = tuple(
            CapabilityGate(
                gate=gate,
                status=GateStatus.PASS,
                evidence_refs=(f"evidence/{gate}/report.md",),
            )
            for gate in REQUIRED_GATES
        )
        certification = CapabilityCertification(
            capability="speech.transcription",
            version="1.0.0",
            providers=("parakeet", "whisper"),
            gates=gates,
            status=CertificationStatus.PRODUCTION_READY,
            reviewer="medical-board",
            issued_at=datetime.now(timezone.utc),
        )

        self.assertTrue(certification.is_production_ready())
        self.assertEqual(certification.missing_gates(), ())
        self.assertTrue(certification.to_dict()["production_ready"])

    def test_passing_gate_requires_evidence(self) -> None:
        with self.assertRaises(ValueError):
            CapabilityGate(gate="cqa", status=GateStatus.PASS)
