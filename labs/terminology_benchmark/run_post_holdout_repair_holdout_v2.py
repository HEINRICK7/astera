"""Run the new post-repair unseen holdout-v2 exactly once."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery

from .context_harness import _actual_relations, _expected_relations
from .context_safety import NieDEPtBrSafetyRules
from .cross_segment_context import CrossSegmentContextAdapter
from .models import BenchmarkCase, ConversationSegment, GoldMention, GoldRelation


ROOT = Path(__file__).parent
FREEZE = ROOT / "results/post-holdout-generalization-repair-freeze-2026-08-15.json"
SOURCE = ROOT / "data/post_holdout_generalization_holdout_v2.json"
DEFAULT_OUTPUT = ROOT / "results/post-holdout-generalization-holdout-v2-2026-08-15.json"
POLICY = "clinical-semantic-policy-v1.2"
OLD_IDS = {"sim-v6-0056", "sim-v6-0057", "sim-v6-0058"}
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
    records = json.loads(SOURCE.read_text(encoding="utf-8"))
    if not records or any(item["candidate_id"] in OLD_IDS for item in records):
        raise RuntimeError("holdout-v2 source is empty or contains consumed holdout ids")
    cases = []
    for record in records:
        if record.get("decision") != "APPROVED" or record.get("review_status") != "REVIEWED":
            raise RuntimeError(f"holdout-v2 case is not approved: {record['candidate_id']}")
        cases.append(BenchmarkCase(
            case_id=record["candidate_id"],
            text=record["text"],
            language=record.get("language", "pt-BR"),
            source="post-holdout-approved-v2",
            segments=tuple(ConversationSegment(**segment) for segment in record["segments"]),
            gold=tuple(_gold(item) for item in record["gold"]),
        ))
    return tuple(cases)


def _policy_status_excluded(gold: GoldMention) -> bool:
    entity_type = gold.concept_id.split(".", 1)[0]
    return entity_type not in {"medication", "device"} and gold.status in {"present", "historical"}


def _ownership_ok(result: Any) -> bool:
    ownership = result.provenance.get("attribute_ownership", {})
    return isinstance(ownership, dict) and all(
        isinstance(item, dict) and bool(item.get("owner_mention_id"))
        for item in ownership.values()
    )


def _provenance_ok(result: Any, case: BenchmarkCase) -> bool:
    provenance = result.provenance
    known = {segment.segment_id for segment in case.segments}
    return bool(
        provenance.get("provider")
        and provenance.get("source_text") == case.text
        and provenance.get("source_scope") == "conversation"
        and set(provenance.get("conversation_segment_ids", ())).issubset(known)
        and all(set(sources).issubset(known) for sources in provenance.get("segment_provenance", {}).values())
    )


def _mention_report(case: BenchmarkCase, gold: GoldMention, result: Any) -> dict[str, Any]:
    excluded_status = _policy_status_excluded(gold)
    fields = {
        field: {
            "expected": getattr(gold, field),
            "actual": getattr(result, field),
            "match": True if field == "status" and excluded_status else getattr(gold, field) == getattr(result, field),
            "excluded_from_policy_gate": field == "status" and excluded_status,
        }
        for field in FIELDS
    }
    expected_relations = _expected_relations(gold)
    actual_relations = _actual_relations(result)
    event_temporality = result.provenance.get("event_temporality")
    temporal_ownership = True
    if gold.temporality == "current" and any(
        cue in case.segments[-1].text.casefold() for cue in ("ontem", "semana passada", "mês passado")
    ) and gold.dose:
        temporal_ownership = (
            result.temporality == "current"
            and isinstance(event_temporality, dict)
            and event_temporality.get("owner") == "dose_change_event"
        )
    return {
        "surface": gold.surface,
        "concept_id": gold.concept_id,
        "fields": fields,
        "mention_exact": all(item["match"] for item in fields.values()),
        "relations_expected": expected_relations,
        "relations_actual": actual_relations,
        "relation_exact": actual_relations == expected_relations,
        "attribute_ownership": _ownership_ok(result),
        "provenance": _provenance_ok(result, case),
        "temporal_ownership": temporal_ownership,
        "event_temporality": event_temporality,
    }


async def run(output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        raise RuntimeError(f"holdout-v2 output already exists; rerun is forbidden: {output_path}")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze.get("status") != "FROZEN_BEFORE_POST_HOLDOUT_V2" or freeze.get("holdout_v2_run_count") != 0:
        raise RuntimeError("post-holdout repair freeze is missing, invalid, or already consumed")
    if freeze.get("semantic_policy_version") != "1.2" or _sha256(SOURCE) != freeze.get("new_holdout_source_sha256"):
        raise RuntimeError("holdout-v2 source or policy does not match the freeze")
    cases = _load_cases()
    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    reports = []
    relation_total = relation_pass = 0
    mention_total = mention_pass = ownership_pass = provenance_pass = 0
    temporal_total = temporal_pass = 0
    field_totals: dict[str, int] = {field: 0 for field in FIELDS}
    field_matches: dict[str, int] = {field: 0 for field in FIELDS}
    for case in cases:
        mention_reports = []
        for gold in case.gold:
            start = case.text.index(gold.surface)
            result = await adapter.analyze(ClinicalContextQuery(
                text=case.text, language=case.language, start=start,
                end=start + len(gold.surface), evidence_id=case.case_id,
                semantic_policy=POLICY,
            ))
            report = _mention_report(case, gold, result)
            mention_reports.append(report)
            mention_total += 1
            mention_pass += int(report["mention_exact"])
            ownership_pass += int(report["attribute_ownership"])
            provenance_pass += int(report["provenance"])
            if report["relations_expected"]:
                relation_total += 1
                relation_pass += int(report["relation_exact"])
            if gold.temporality == "current" and gold.dose and any(
                cue in case.segments[-1].text.casefold() for cue in ("ontem", "semana passada", "mês passado")
            ):
                temporal_total += 1
                temporal_pass += int(report["temporal_ownership"])
            for field, item in report["fields"].items():
                if item["excluded_from_policy_gate"]:
                    continue
                field_totals[field] += 1
                field_matches[field] += int(item["match"])
        reports.append({
            "case_id": case.case_id,
            "text": case.text,
            "mentions": mention_reports,
            "case_pass": all(item["mention_exact"] and item["relation_exact"] and item["attribute_ownership"] and item["provenance"] and item["temporal_ownership"] for item in mention_reports),
        })
    metrics = {
        "mention_exact_match": mention_pass / mention_total if mention_total else 1.0,
        "relation_exact_match": relation_pass / relation_total if relation_total else 1.0,
        "cross_segment_resolution": mention_pass / mention_total if mention_total else 1.0,
        "attribute_ownership": ownership_pass / mention_total if mention_total else 1.0,
        "provenance_contract_rate": provenance_pass / mention_total if mention_total else 1.0,
        "temporal_ownership_accuracy": temporal_pass / temporal_total if temporal_total else 1.0,
        "status": field_matches["status"] / field_totals["status"] if field_totals["status"] else 1.0,
        "temporality": field_matches["temporality"] / field_totals["temporality"] if field_totals["temporality"] else 1.0,
        "experiencer": field_matches["experiencer"] / field_totals["experiencer"] if field_totals["experiencer"] else 1.0,
        "laterality": field_matches["laterality"] / field_totals["laterality"] if field_totals["laterality"] else 1.0,
        "dose": field_matches["dose"] / field_totals["dose"] if field_totals["dose"] else 1.0,
        "frequency": field_matches["frequency"] / field_totals["frequency"] if field_totals["frequency"] else 1.0,
    }
    pass_gate = all(report["case_pass"] for report in reports)
    return {
        "status": "executed_once",
        "run_count": 1,
        "holdout_kind": "NEW_UNSEEN_POST_REPAIR_V2",
        "policy": POLICY,
        "freeze_manifest": str(FREEZE),
        "source": str(SOURCE),
        "source_sha256": _sha256(SOURCE),
        "old_holdouts": {"ids": sorted(OLD_IDS), "consumed": True, "rerun": False, "used_for_approval": False},
        "cases": reports,
        "aggregate": {"cases_total": len(cases), "mentions_total": mention_total, "relations_total": relation_total, "metrics": metrics, "field_totals": field_totals, "field_matches": field_matches},
        "policy_aligned_holdout_pass": pass_gate,
        "repair_after_holdout_v2": False,
        "v7": "AUTHORIZED_ONLY_IF_NEW_HOLDOUT_V2_PASS",
        "shadow_integration": "BLOCKED",
        "production": "BLOCKED",
        "next_action": "V7_FOUNDATION" if pass_gate else "HUMAN_GATE_NEW_HOLDOUT_FAILURE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = asyncio.run(run(args.output))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
