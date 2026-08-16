"""Read-only review packet construction for V6 simulator candidates."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence


def load_candidate_records(path: Path) -> tuple[dict[str, Any], ...]:
    """Load pending candidates without converting or approving any gold."""
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError("candidate record must be a JSON object")
        records.append(record)
    return tuple(records)


def build_review_packet(records: Sequence[Mapping[str, Any]]) -> tuple[dict[str, Any], ...]:
    """Expose review evidence while keeping gold and approval absent."""
    packet: list[dict[str, Any]] = []
    for record in records:
        status = record.get("review_status", "PENDING_REVIEW")
        if status != "PENDING_REVIEW":
            raise ValueError(f"review queue accepts only PENDING_REVIEW records: {record.get('candidate_id')}")
        if record.get("gold") is not None:
            raise ValueError(f"candidate already contains gold: {record.get('candidate_id')}")
        segments = list(record.get("segments", ()))
        packet.append(
            {
                "candidate_id": record.get("candidate_id"),
                "language": record.get("language", "pt-BR"),
                "text": record.get("text", ""),
                "review_status": "PENDING_REVIEW",
                "decision": "PENDING_REVIEW",
                "reviewer": "",
                "review_notes": "",
                "source_case_ids": list(record.get("source_case_ids", ())),
                "source_error_types": list(record.get("source_error_types", ())),
                "provenance": dict(record.get("provenance", {})),
                "segment_id": None if len(segments) > 1 else f"{record.get('candidate_id')}:segment-01",
                "segments": segments,
                "gold": [],
                "mentions": None,
                "relations": None,
                "review_instruction": (
                    "Human reviewer must provide mentions, relations, source segment IDs, "
                    "attribute provenance and relation provenance."
                ),
            }
        )
    return tuple(packet)


def write_review_template(path: Path, packet: Sequence[Mapping[str, Any]]) -> None:
    """Write an editable review worksheet, never an official corpus."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(list(packet), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def format_review_packet(packet: Sequence[Mapping[str, Any]]) -> str:
    """Render a compact human-readable queue; this function has no write path."""
    sections: list[str] = []
    for item in packet:
        provenance = item["provenance"]
        sections.append(
            "\n".join(
                (
                    f"[{item['review_status']}] {item['candidate_id']}",
                    f"text: {item['text']}",
                    f"source cases: {', '.join(item['source_case_ids']) or '-'}",
                    f"error types: {', '.join(item['source_error_types']) or '-'}",
                    "mentions: PENDING_HUMAN_REVIEW",
                    "relations: PENDING_HUMAN_REVIEW",
                    "provenance:",
                    json.dumps(provenance, ensure_ascii=False, sort_keys=True),
                    f"instruction: {item['review_instruction']}",
                )
            )
        )
    return "\n\n".join(sections)
