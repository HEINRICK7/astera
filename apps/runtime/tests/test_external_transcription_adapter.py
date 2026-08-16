"""Contract tests for the current astera-live-transcriber wire format."""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from apps.runtime.src.adapters.transcription import ExternalTranscriptionAdapter
from packages.contracts.transcription import (
    TranscriptCommitted,
    TranscriptPartial,
    TranscriptRevised,
)


RECEIVED_AT = datetime(2026, 8, 14, 12, 30, tzinfo=timezone.utc)


def _payload(event_type: str, revision: int, text: str) -> dict[str, object]:
    return {
        "type": event_type,
        "session_id": "sess_123",
        "segment_id": "seg_0001",
        "revision": revision,
        "text": text,
        "start_ms": 300,
        "end_ms": 4200 if event_type == "transcript.committed" else 1800,
        "language": "pt-BR",
        "provider": "xai",
        "projected_text": text,
        "projected_text_clean": text,
        "confidence": 0.94,
        "words": [
            {"word": "Eu", "start_ms": 300, "end_ms": 450, "confidence": 0.98},
            {"word": "comecei", "start_ms": 500, "end_ms": 900, "confidence": 0.96},
        ],
    }


def test_external_partial_preserves_transport_identity_and_received_time() -> None:
    event = ExternalTranscriptionAdapter().to_contract(
        _payload("transcript.partial", 1, "Eu comecei"),
        received_at=RECEIVED_AT,
    )

    assert isinstance(event, TranscriptPartial)
    assert event.segment.segment_id == "seg_0001"
    assert event.segment.revision == 1
    assert event.segment.text == "Eu comecei"
    assert event.segment.projected_text == "Eu comecei"
    assert event.segment.words[0].text == "Eu"
    assert event.envelope.source == "astera-live-transcriber"
    assert event.envelope.source_event_id is None
    assert event.envelope.event_id == "sess_123:seg_0001:1:transcript.partial"
    assert event.envelope.occurred_at is None
    assert event.envelope.received_at == RECEIVED_AT
    assert event.envelope.schema_version == 1


def test_external_revision_keeps_segment_identity_and_replaces_hypothesis() -> None:
    adapter = ExternalTranscriptionAdapter()
    partial = adapter.to_contract(
        _payload("transcript.partial", 1, "Eu comecei"),
        received_at=RECEIVED_AT,
    )
    revised = adapter.to_contract(
        _payload("transcript.revised", 2, "Eu comecei a sentir"),
        received_at=RECEIVED_AT,
    )

    assert isinstance(partial, TranscriptPartial)
    assert isinstance(revised, TranscriptRevised)
    assert revised.segment.segment_id == partial.segment.segment_id
    assert revised.segment.revision > partial.segment.revision
    assert revised.segment.text == "Eu comecei a sentir"
    assert revised.segment.text != partial.segment.text + revised.segment.text


def test_external_commit_preserves_raw_and_derived_views_and_provenance() -> None:
    payload = _payload("transcript.committed", 3, "Eu comecei a sentir uma dor")
    payload["technical"] = {"runtime_metrics": {"latency_ms": 12}}

    event = ExternalTranscriptionAdapter().to_contract(
        payload,
        received_at=RECEIVED_AT,
        encounter_id="encounter-1",
        patient_id="patient-1",
    )

    assert isinstance(event, TranscriptCommitted)
    assert event.text == "Eu comecei a sentir uma dor"
    assert event.segments[0].text == payload["text"]
    assert event.segments[0].projected_text == payload["projected_text"]
    assert event.segments[0].projected_text_clean == payload["projected_text_clean"]
    assert event.envelope.raw_payload == payload
    assert event.envelope.metadata["technical"] == payload["technical"]
    assert event.encounter_id == "encounter-1"
    assert event.patient_id == "patient-1"


def test_committed_contract_is_immutable() -> None:
    event = ExternalTranscriptionAdapter().to_contract(
        _payload("transcript.committed", 3, "Eu comecei a sentir uma dor"),
        received_at=RECEIVED_AT,
    )

    assert isinstance(event, TranscriptCommitted)
    with pytest.raises(FrozenInstanceError):
        event.segments[0].text = "texto alterado"  # type: ignore[misc]


def test_external_non_transcription_events_are_not_evidence() -> None:
    event = ExternalTranscriptionAdapter().to_contract(
        {"type": "session.created", "session_id": "sess_123"},
        received_at=RECEIVED_AT,
    )

    assert event is None


def test_external_origin_metadata_is_preserved_when_provided() -> None:
    occurred_at = datetime(2026, 8, 14, 12, 29, tzinfo=timezone.utc)
    payload = _payload("transcript.committed", 3, "texto confirmado")
    payload["event_id"] = "producer-event-7"
    payload["occurred_at"] = occurred_at.isoformat()

    event = ExternalTranscriptionAdapter().to_contract(
        payload,
        received_at=RECEIVED_AT,
    )

    assert isinstance(event, TranscriptCommitted)
    assert event.envelope.event_id == "producer-event-7"
    assert event.envelope.source_event_id == "producer-event-7"
    assert event.envelope.occurred_at == occurred_at
    assert event.envelope.received_at == RECEIVED_AT
