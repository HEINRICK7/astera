"""Run the three pre-registered V6 holdouts exactly once after freeze."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery

from .context_harness import _actual_relations, _expected_relations
from .context_safety import NieDEPtBrSafetyRules
from .corpus import mention_span
from .cross_segment_context import CrossSegmentContextAdapter
from .models import BenchmarkCase, ConversationSegment, GoldMention, GoldRelation


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
FREEZE = RESULTS / "v6-repair-v6-freeze-2026-08-15.json"
HOLDOUT_SOURCE = RESULTS / "v6-human-review-micro-expansion-submission-2026-08-15.json"
DEFAULT_OUTPUT = RESULTS / "context-validation-v6-holdout-0056-0058-2026-08-15.json"
POLICY = "clinical-semantic-policy-v1.2"
HOLDOUT_IDS = ("sim-v6-0056", "sim-v6-0057", "sim-v6-0058")
FIELDS = (
    "negated", "certainty", "temporality", "experiencer", "laterality",
    "dose", "dose_value", "dose_unit", "frequency", "route", "status",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _gold(item: dict[str, Any]) -> GoldMention:
    return GoldMention(
        **{
            **item,
            "relations": tuple(GoldRelation(**relation) for relation in item.get("relations", ())),
            "segment_ids": tuple(item.get("segment_ids", ())),
            "attribute_provenance": {
                key: tuple(value) for key, value in item.get("attribute_provenance", {}).items()
            },
            "relation_provenance": {
                key: tuple(value) for key, value in item.get("relation_provenance", {}).items()
            },
        }
    )


def _load_cases() -> tuple[BenchmarkCase, ...]:
    records = json.loads(HOLDOUT_SOURCE.read_text(encoding="utf-8"))
    by_id = {record["candidate_id"]: record for record in records}
    cases: list[BenchmarkCase] = []
    for case_id in HOLDOUT_IDS:
        record = by_id[case_id]
        if record.get("decision") != "APPROVED" or record.get("review_status") != "REVIEWED":
            raise RuntimeError(f"holdout is not approved: {case_id}")
        cases.append(BenchmarkCase(
            case_id=case_id,
            text=record["text"],
            language=record.get("language", "pt-BR"),
            source="approved-holdout",
            segments=tuple(ConversationSegment(**segment) for segment in record["segments"]),
            gold=tuple(_gold(item) for item in record["gold"]),
        ))
    return tuple(cases)


def _policy_status_excluded(gold: GoldMention) -> bool:
    entity_type = gold.concept_id.split(".", 1)[0]
    return entity_type not in {"medication", "device"} and gold.status in {"present", "historical"}


def _ownership_ok(result: Any) -> bool:
    ownership = result.provenance.get("attribute_ownership", {})
    if not isinstance(ownership, dict):
        return False
    for field, item in ownership.items():
        if not isinstance(item, dict) or not item.get("owner_mention_id"):
            return False
        if item.get("owner_mention_id") != item.get("owner_mention_id"):
            return False
    return True


def _provenance_ok(result: Any, case: BenchmarkCase) -> bool:
    provenance = result.provenance
    known_segments = {segment.segment_id for segment in case.segments}
    if not provenance.get("provider") or provenance.get("source_text") != case.text:
        return False
    for sources in provenance.get("segment_provenance", {}).values():
        if not set(sources).issubset(known_segments):
            return False
    return True


def _mention_report(case: BenchmarkCase, gold: GoldMention, raw: Any, policy: Any) -> dict[str, Any]:
    excluded_status = _policy_status_excluded(gold)
    raw_fields = {
        field: {"expected": getattr(gold, field), "actual": getattr(raw, field), "match": getattr(gold, field) == getattr(raw, field)}
        for field in FIELDS
    }
    policy_fields = {
        field: {
            "expected": getattr(gold, field),
            "actual": getattr(policy, field),
            "match": True if field == "status" and excluded_status else getattr(gold, field) == getattr(policy, field),
            "excluded_from_policy_gate": field == "status" and excluded_status,
        }
        for field in FIELDS
    }
    raw_relations = _actual_relations(raw)
    expected_relations = _expected_relations(gold)
    policy_relations = _actual_relations(policy)
    return {
        "surface": gold.surface,
        "concept_id": gold.concept_id,
        "raw": {
            "fields": raw_fields,
            "mention_exact": all(item["match"] for item in raw_fields.values()),
            "relations_expected": expected_relations,
            "relations_actual": raw_relations,
            "relation_exact": raw_relations == expected_relations,
            "attribute_ownership": _ownership_ok(raw),
            "provenance": _provenance_ok(raw, case),
        },
        "policy_aligned": {
            "fields": policy_fields,
            "mention_exact": all(item["match"] for item in policy_fields.values()),
            "relations_expected": expected_relations,
            "relations_actual": policy_relations,
            "relation_exact": policy_relations == expected_relations,
            "attribute_ownership": _ownership_ok(policy),
            "provenance": _provenance_ok(policy, case),
            "status_excluded_from_policy_gate": excluded_status,
        },
    }


async def run(*, output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        raise RuntimeError(f"holdout output already exists; rerun is forbidden: {output_path}")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["status"] != "FROZEN_BEFORE_HOLDOUT" or freeze["holdout_run_count"] != 0:
        raise RuntimeError("freeze is missing, invalid, or already consumed")
    if freeze["semantic_policy_version"] != "1.2":
        raise RuntimeError("holdout freeze is not policy v1.2")
    if _sha256(HOLDOUT_SOURCE) != freeze["holdout_source_sha256"]:
        raise RuntimeError("holdout source changed after freeze")
    cases = _load_cases()
    adapter_raw = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    adapter_policy = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)

    case_reports: list[dict[str, Any]] = []
    aggregate = {
        "cases_total": len(cases),
        "mentions_total": 0,
        "raw_mentions_exact": 0,
        "policy_mentions_exact": 0,
        "raw_relations_exact": 0,
        "policy_relations_exact": 0,
        "relations_total": 0,
        "cross_segment_total": 0,
        "raw_cross_segment_exact": 0,
        "policy_cross_segment_exact": 0,
        "raw_ownership_pass": 0,
        "policy_ownership_pass": 0,
        "raw_provenance_pass": 0,
        "policy_provenance_pass": 0,
    }
    for case in cases:
        mentions: list[dict[str, Any]] = []
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            raw = await adapter_raw.analyze(ClinicalContextQuery(
                text=case.text, language=case.language, start=start, end=end,
                evidence_id=case.case_id, semantic_policy=None,
            ))
            policy = await adapter_policy.analyze(ClinicalContextQuery(
                text=case.text, language=case.language, start=start, end=end,
                evidence_id=case.case_id, semantic_policy=POLICY,
            ))
            report = _mention_report(case, gold, raw, policy)
            mentions.append(report)
            aggregate["mentions_total"] += 1
            aggregate["raw_mentions_exact"] += int(report["raw"]["mention_exact"])
            aggregate["policy_mentions_exact"] += int(report["policy_aligned"]["mention_exact"])
            aggregate["raw_ownership_pass"] += int(report["raw"]["attribute_ownership"])
            aggregate["policy_ownership_pass"] += int(report["policy_aligned"]["attribute_ownership"])
            aggregate["raw_provenance_pass"] += int(report["raw"]["provenance"])
            aggregate["policy_provenance_pass"] += int(report["policy_aligned"]["provenance"])
            if report["raw"]["relations_expected"]:
                aggregate["relations_total"] += 1
                aggregate["raw_relations_exact"] += int(report["raw"]["relation_exact"])
                aggregate["policy_relations_exact"] += int(report["policy_aligned"]["relation_exact"])
            aggregate["cross_segment_total"] += 1
            aggregate["raw_cross_segment_exact"] += int(report["raw"]["mention_exact"])
            aggregate["policy_cross_segment_exact"] += int(report["policy_aligned"]["mention_exact"])
        case_reports.append({
            "case_id": case.case_id,
            "text": case.text,
            "mentions": mentions,
            "raw_case_pass": all(item["raw"]["mention_exact"] for item in mentions),
            "policy_aligned_case_pass": all(item["policy_aligned"]["mention_exact"] for item in mentions),
        })

    def ratio(value: int, total: int) -> float:
        return value / total if total else 1.0

    aggregate_metrics = {
        **aggregate,
        "raw_mention_exact_match": ratio(aggregate["raw_mentions_exact"], aggregate["mentions_total"]),
        "policy_mention_exact_match": ratio(aggregate["policy_mentions_exact"], aggregate["mentions_total"]),
        "raw_relation_exact_match": ratio(aggregate["raw_relations_exact"], aggregate["relations_total"]),
        "policy_relation_exact_match": ratio(aggregate["policy_relations_exact"], aggregate["relations_total"]),
        "raw_cross_segment_resolution": ratio(aggregate["raw_cross_segment_exact"], aggregate["cross_segment_total"]),
        "policy_cross_segment_resolution": ratio(aggregate["policy_cross_segment_exact"], aggregate["cross_segment_total"]),
        "policy_attribute_ownership": ratio(aggregate["policy_ownership_pass"], aggregate["mentions_total"]),
        "policy_provenance": ratio(aggregate["policy_provenance_pass"], aggregate["mentions_total"]),
    }
    policy_pass = all(
        report["policy_aligned_case_pass"]
        and all(item["policy_aligned"]["attribute_ownership"] and item["policy_aligned"]["provenance"] for item in report["mentions"])
        for report in case_reports
    )
    result = {
        "status": "executed_once",
        "run_count": 1,
        "freeze_manifest": str(FREEZE),
        "policy": POLICY,
        "holdout_ids": list(HOLDOUT_IDS),
        "holdout_source_sha256": _sha256(HOLDOUT_SOURCE),
        "raw_result_recorded_before_policy_analysis": True,
        "cases": case_reports,
        "aggregate": aggregate_metrics,
        "raw_holdout_pass": all(report["raw_case_pass"] for report in case_reports),
        "policy_aligned_holdout_pass": policy_pass,
        "semantically_relevant_failure": not policy_pass,
        "repair_after_holdout": False,
        "v7": "AUTHORIZED_ONLY_IF_HOLDOUT_PASS",
        "shadow_integration": "BLOCKED",
        "production_promotion": "BLOCKED",
        "next_action": "V7_UNSEEN_FOUNDATION" if policy_pass else "HUMAN_GATE_HOLDOUT_FAILURE",
    }
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(output_path=args.output)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
