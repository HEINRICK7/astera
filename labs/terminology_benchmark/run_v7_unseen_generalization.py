"""Guarded V7 harness.

The harness can evaluate only a reviewed and frozen V7 corpus. In the current
foundation state it performs a gate check and refuses official execution.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from .context_harness import evaluate
from .context_safety import NieDEPtBrSafetyRules
from .cross_segment_context import CrossSegmentContextAdapter
from .models import BenchmarkCase, ConversationSegment, GoldMention, GoldRelation


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
DRAFT = DATA / "v7_unseen_generalization_draft.jsonl"
QUEUE = RESULTS / "v7-human-review-queue-2026-08-15.json"
MANIFEST = RESULTS / "v7-corpus-manifest-2026-08-15.json"
DISJOINTNESS = RESULTS / "v7-disjointness-report-2026-08-15.json"


class V7Blocked(RuntimeError):
    """Raised when V7 official evaluation is not authorized."""


def _load_draft() -> list[dict[str, Any]]:
    return [json.loads(line) for line in DRAFT.read_text(encoding="utf-8").splitlines() if line.strip()]


def readiness() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    disjointness = json.loads(DISJOINTNESS.read_text(encoding="utf-8"))
    records = _load_draft()
    blockers: list[str] = []
    if manifest.get("status") != "FROZEN":
        blockers.append("corpus_freeze_complete=false")
    if not manifest.get("human_review_complete"):
        blockers.append("human_review_complete=false")
    if not manifest.get("gold_validation_complete"):
        blockers.append("gold_validation_complete=false")
    if queue.get("pending_count") != 0 or queue.get("approved_count") != len(records):
        blockers.append("human_review_queue_not_closed")
    if any(record.get("gold") is None or record.get("review_status") != "APPROVED_FOR_CORPUS" for record in records):
        blockers.append("draft_contains_unapproved_or_goldless_cases")
    if disjointness.get("status") != "PASS_DRAFT_ONLY" or disjointness.get("text_overlaps"):
        blockers.append("disjointness_not_validated")
    if manifest.get("resolver_changed") or manifest.get("policy_version") != "1.2":
        blockers.append("resolver_or_policy_freeze_invalid")
    return {
        "status": "READY" if not blockers else "BLOCKED",
        "corpus": "V7 Unseen Generalization Foundation",
        "case_count": len(records),
        "blockers": blockers,
        "official_execution": False,
        "shadow_integration": "BLOCKED",
        "production": "BLOCKED",
    }


def _gold(item: dict[str, Any]) -> GoldMention:
    return GoldMention(
        **{
            **item,
            "relations": tuple(GoldRelation(**relation) for relation in item.get("relations", ())),
            "segment_ids": tuple(item.get("segment_ids", ())),
            "attribute_provenance": {key: tuple(value) for key, value in item.get("attribute_provenance", {}).items()},
            "relation_provenance": {key: tuple(value) for key, value in item.get("relation_provenance", {}).items()},
        }
    )


def _reviewed_cases() -> tuple[BenchmarkCase, ...]:
    records = _load_draft()
    return tuple(
        BenchmarkCase(
            case_id=record["case_id"],
            text=record["text"],
            language=record["language"],
            source="v7-reviewed-frozen",
            segments=tuple(ConversationSegment(**segment) for segment in record["segments"]),
            gold=tuple(_gold(item) for item in record["gold"]),
        )
        for record in records
    )


async def evaluate_official() -> dict[str, Any]:
    gate = readiness()
    if gate["status"] != "READY":
        raise V7Blocked("V7 official evaluation is blocked: " + ", ".join(gate["blockers"]))
    cases = _reviewed_cases()
    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    result = await evaluate(
        adapter,
        cases,
        enforce_composition_gate=True,
        semantic_policy="clinical-semantic-policy-v1.2",
    )
    return {"status": "EXECUTED", "gate": gate, "evaluation": result}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Run only after all V7 gates are closed")
    args = parser.parse_args()
    gate = readiness()
    if not args.execute:
        print(json.dumps({"status": gate["status"], "mode": "CHECK_ONLY", "gate": gate}, ensure_ascii=False, indent=2))
        return
    try:
        result = asyncio.run(evaluate_official())
    except V7Blocked as error:
        print(json.dumps({"status": "BLOCKED", "reason": str(error), "gate": gate}, ensure_ascii=False, indent=2))
        return
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
