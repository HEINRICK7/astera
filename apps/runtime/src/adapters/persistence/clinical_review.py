"""In-memory clinical review projection adapter.

This adapter owns the process-local representation used by the development
bootstrap. The application consumes it through ``ReviewRepositoryPort``.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any

from packages.streaming_sdk import StreamEvent


def _live_metrics() -> dict[str, Any]:
    return {
        "partial_events": 0,
        "done_events": 0,
        "error_events": 0,
        "first_partial_latency_ms": None,
        "time_to_first_partial_ms": None,
        "time_to_first_final_ms": None,
        "time_to_first_clinical_object_ms": None,
        "time_to_first_hypothesis_ms": None,
        "time_to_soap_ms": None,
        "clinical_objects": 0,
        "knowledge_updates": 0,
        "workspace_updates": 0,
        "mentions_detected": 0,
        "mentions_normalized": 0,
        "mentions_negated": 0,
        "mentions_review_required": 0,
        "normalization_latency_ms": 0.0,
        "normalization_errors": 0,
    }


class InMemoryClinicalReviewStore:
    """Process-local review projection; replaceable by a durable adapter."""

    def __init__(self) -> None:
        self._records: dict[str, dict[str, Any]] = {}

    def restore(self, record: dict[str, Any]) -> None:
        """Hydrate one persisted projection before applying a new event."""
        encounter_id = record.get("encounter_id")
        if encounter_id:
            self._records[str(encounter_id)] = record

    def begin(self, encounter_id: str, patient_id: str) -> None:
        self._records[encounter_id] = {
            "encounter_id": encounter_id,
            "patient_id": patient_id,
            "status": "in_progress",
            "events": [],
            "a2ui_events": [],
            "transcript": {
                "segments": [],
                "final_segments": [],
                "current_partial": None,
                "text": "",
                "is_final": False,
            },
            "clinical_facts": {"items": []},
            "clinical_mentions": {"items": []},
            "knowledge": None,
            "context": None,
            "reasoning": None,
            "representations": {},
            "metrics": _live_metrics(),
            "error": None,
        }

    def record(self, event: StreamEvent) -> None:
        record = self._records.setdefault(
            event.stream_id,
            {
                "encounter_id": event.stream_id,
                "patient_id": None,
                "status": "in_progress",
                "events": [],
                "a2ui_events": [],
                "transcript": {
                    "segments": [],
                    "final_segments": [],
                    "current_partial": None,
                    "text": "",
                    "is_final": False,
                },
                "clinical_facts": {"items": []},
                "clinical_mentions": {"items": []},
                "knowledge": None,
                "context": None,
                "reasoning": None,
                "representations": {},
                "metrics": _live_metrics(),
                "error": None,
            },
        )
        payload = dict(event.payload)
        event_type = event.event_type
        metrics = record["metrics"]
        if event_type == "clinical.runtime.metrics":
            for key in (
                "first_partial_latency_ms",
                "time_to_first_partial_ms",
                "time_to_first_final_ms",
                "time_to_first_clinical_object_ms",
                "time_to_first_hypothesis_ms",
                "time_to_soap_ms",
                "clinical_objects",
                "knowledge_updates",
                "mentions_detected",
                "mentions_normalized",
                "mentions_negated",
                "mentions_review_required",
                "normalization_latency_ms",
                "normalization_errors",
            ):
                if key in payload:
                    metrics[key] = payload[key]
        elif event_type == "clinical.session.completed":
            metrics.update(payload.get("metrics", {}))
            record["transcript"].update({
                "status": payload.get("status", "completed"),
                "updated_at": payload.get("timestamp"),
                "lifecycle": payload.get("lifecycle"),
                "snapshot": payload.get("snapshot"),
            })

        if event_type in {"transcript.created", "transcript.partial", "transcript.done", "transcript.error"}:
            transcript = record["transcript"]
            if event_type == "transcript.created":
                transcript.update({
                    "session_id": payload.get("session"),
                    "language": payload.get("language"),
                    "started_at": payload.get("started_at"),
                    "lifecycle": payload.get("lifecycle"),
                    "status": "streaming",
                })
            elif event_type == "transcript.partial":
                transcript["current_partial"] = payload.get("partial") or {
                    "id": payload.get("id"),
                    "revision": payload.get("revision", 0),
                    "sequence": payload.get("sequence"),
                    "text": payload.get("text", ""),
                    "start_ms": payload.get("start_ms"),
                    "end_ms": payload.get("end_ms"),
                    "is_final": False,
                }
                transcript["text"] = payload.get("transcript", payload.get("text", ""))
                transcript["version"] = payload.get("version")
                metrics["partial_events"] += 1
            elif event_type == "transcript.done":
                segment = {
                    "id": payload.get("id"),
                    "revision": payload.get("revision", 0),
                    "sequence": payload.get("sequence"),
                    "text": payload.get("text", ""),
                    "start_ms": payload.get("start_ms"),
                    "end_ms": payload.get("end_ms"),
                    "is_final": True,
                }
                if not any(item.get("id") == segment["id"] for item in transcript["final_segments"]):
                    transcript["final_segments"].append(segment)
                transcript["segments"] = list(transcript["final_segments"])
                transcript["current_partial"] = None
                transcript["text"] = payload.get("transcript", payload.get("text", ""))
                transcript["version"] = payload.get("version")
                metrics["done_events"] += 1
            elif event_type == "transcript.error":
                metrics["error_events"] += 1
                record["error"] = payload
            record["events"].append(event.to_dict())
            return

        if event_type == "clinical.mention.detected":
            mention = payload.get("mention")
            if isinstance(mention, dict):
                mentions = record["clinical_mentions"]["items"]
                mention_id = mention.get("id")
                existing = next((index for index, item in enumerate(mentions) if item.get("id") == mention_id), None)
                if existing is None:
                    mentions.append(mention)
                else:
                    mentions[existing] = {**mentions[existing], **mention}
        elif event_type == "clinical.fact.detected":
            fact = payload.get("fact")
            if isinstance(fact, dict):
                facts = record["clinical_facts"]["items"]
                fact_id = fact.get("fact_id") or fact.get("id")
                existing = next((index for index, item in enumerate(facts) if (item.get("fact_id") or item.get("id")) == fact_id), None)
                if existing is None:
                    facts.append(fact)
                else:
                    facts[existing] = {**facts[existing], **fact}
        elif event_type == "clinical.knowledge.updated":
            record["knowledge"] = payload.get("knowledge")
            metrics["knowledge_updates"] += 1
        elif event_type == "clinical.deep.context.updated":
            record["context"] = payload.get("context")
        elif event_type == "clinical.deep.reasoning.updated":
            record["reasoning"] = payload.get("reasoning")
        elif event_type == "clinical.deep.soap.updated":
            record["representations"]["soap"] = payload.get("soap")
        elif event_type == "clinical.representation.updated":
            representation_format = str(payload.get("format", "")).strip()
            if representation_format:
                record["representations"][representation_format] = payload.get("content")
        elif event_type == "clinical.fhir.updated":
            record["representations"]["fhir"] = payload.get("fhir")
        elif event_type == "consultation.pipeline.completed":
            record["status"] = "processed"
            record["completed_at"] = event.occurred_at.isoformat()
        elif event_type in {"consultation.pipeline.error", "clinical.deep.error"}:
            record["error"] = payload

        if event_type == "a2ui.cognitive.stream":
            record["a2ui_events"].append(event.to_dict())
            metrics["workspace_updates"] += 1
        else:
            record["events"].append(event.to_dict())

    def complete(self, encounter_id: str, status: str = "completed") -> None:
        record = self._records.get(encounter_id)
        if record is None:
            return
        record["status"] = status
        record.setdefault("completed_at", datetime.now(timezone.utc).isoformat())

    def set_representation(self, encounter_id: str, format_name: str, content: Any) -> None:
        record = self._records.get(encounter_id)
        if record is not None:
            record["representations"][format_name] = content

    def save_result(self, encounter_id: str, patient_id: str, result: dict[str, Any]) -> None:
        completed_at = result.get("finished_at") or datetime.now(timezone.utc).isoformat()
        steps = result.get("steps") if isinstance(result.get("steps"), list) else []
        events = [
            {
                "event_id": f"review-step-{encounter_id}-{index}",
                "stream_id": encounter_id,
                "event_type": f"clinical.step.{step.get('name', 'unknown')}",
                "sequence": index,
                "payload": step.get("payload", {}),
                "occurred_at": step.get("completed_at", completed_at),
            }
            for index, step in enumerate(steps)
            if isinstance(step, dict)
        ]
        self._records[encounter_id] = {
            "encounter_id": encounter_id,
            "patient_id": patient_id,
            "status": "processed",
            "completed_at": completed_at,
            "events": events,
            "a2ui_events": [],
            "transcript": result.get("transcript"),
            "clinical_facts": result.get("clinical_facts"),
            "knowledge": result.get("knowledge"),
            "context": result.get("clinical_context"),
            "reasoning": result.get("reasoning"),
            "representations": {
                name: result.get(name)
                for name in ("soap", "fhir", "summary")
                if result.get(name) is not None
            },
            "metrics": {"source": "mvp_clinical_journey"},
            "error": None,
        }

    def get(self, encounter_id: str) -> dict[str, Any] | None:
        record = self._records.get(encounter_id)
        return _copy_review_record(record) if record else None

    def list_for(self, patient_id: str | None = None) -> list[dict[str, Any]]:
        records = (
            record for record in self._records.values()
            if patient_id is None or record.get("patient_id") == patient_id
        )
        return [_copy_review_record(record) for record in records]


def _copy_review_record(record: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(record, ensure_ascii=False, default=str))
