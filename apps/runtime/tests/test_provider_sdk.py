from __future__ import annotations

import unittest
from datetime import datetime, timezone

from packages.provider_sdk import (
    ProviderCertification,
    ProviderCertificationGate,
    ProviderExecutionResult,
    ProviderLifecycleStatus,
    ProviderTrace,
)


class ProviderSdkTests(unittest.TestCase):
    def test_execution_result_contains_trace_metrics_and_diagnostics(self) -> None:
        now = datetime.now(timezone.utc)
        trace = ProviderTrace(
            request_id="req-1",
            provider="parakeet",
            provider_version="0.1.0",
            capability="speech.transcription",
            plugin="speech-plugin",
            kernel_version="1.0",
            started_at=now,
            finished_at=now,
            latency_ms=12.5,
        )
        result = ProviderExecutionResult(
            output={"text": "dor torácica"},
            trace=trace,
            metrics={"confidence": 0.94},
            diagnostics={"segment_count": 1},
        )

        payload = result.to_dict()
        self.assertEqual(payload["trace"]["request_id"], "req-1")
        self.assertEqual(payload["metrics"]["confidence"], 0.94)
        self.assertEqual(payload["diagnostics"]["segment_count"], 1)

    def test_certification_requires_evidence_for_passing_gates(self) -> None:
        with self.assertRaises(ValueError):
            ProviderCertificationGate("engineering", True)

        certification = ProviderCertification(
            provider="parakeet",
            capability="speech.transcription",
            version="0.1.0",
            status=ProviderLifecycleStatus.BENCHMARKED,
            gates=(ProviderCertificationGate("engineering", True, ("test-run-1",)),),
        )
        self.assertFalse(certification.all_gates_pass())
        self.assertEqual(certification.status, ProviderLifecycleStatus.BENCHMARKED)
