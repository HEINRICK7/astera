"""Execute the authorized V6 status-only repair on the frozen V6 corpus."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from .context_safety import NieDEPtBrSafetyRules
from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus
from .cross_segment_context import CrossSegmentContextAdapter
from .run_repair_v5_final import _policy_aligned_metrics, _sha256, _type_b_fields
from .v6_harness import evaluate_v6


ROOT = Path(__file__).parent
MANIFEST = ROOT / "results" / "v6-official-freeze-manifest-2026-08-15.json"
STATUS_RECLASSIFICATION = ROOT.parent.parent / "docs" / "clinical-conversational-semantics" / "STATUS_V1_2_RECLASSIFICATION.json"
DEFAULT_OUTPUT = ROOT / "results" / "context-validation-v6-repair-v6-status-2026-08-15.json"
POLICY = "clinical-semantic-policy-v1.2"
HOLDOUT_IDS = {"sim-v6-0056", "sim-v6-0057", "sim-v6-0058"}


def _status_type_b_fields() -> set[tuple[str, str, int, str]]:
    artifact = json.loads(STATUS_RECLASSIFICATION.read_text(encoding="utf-8"))
    return {
        (record["case_id"], record["surface"], int(record.get("occurrence", 0)), "status")
        for record in artifact["records"]
        if record["classification"] == "TYPE_B_GOLD_ISSUE"
    }


def _full_policy_status_review_fields(cases: tuple[Any, ...]) -> tuple[set[tuple[str, str, int, str]], list[dict[str, Any]]]:
    """Find gold statuses invalidated by v1.2, including prior matches.

    The original 90-finding queue only contained divergences under v1.1. A
    policy change can expose gold values that previously matched the resolver;
    those remain review-only and must be excluded from the policy gate too.
    """
    fields: set[tuple[str, str, int, str]] = set()
    records: list[dict[str, Any]] = []
    for case in cases:
        for gold in case.gold:
            entity_type = gold.concept_id.split(".", 1)[0]
            if entity_type in {"medication", "device"}:
                continue
            if gold.status not in {"present", "historical"}:
                continue
            key = (case.case_id, gold.surface, gold.occurrence, "status")
            fields.add(key)
            records.append({
                "case_id": case.case_id,
                "surface": gold.surface,
                "occurrence": gold.occurrence,
                "entity_type": entity_type,
                "gold_status": gold.status,
                "reason": "v1.2 reserves status for explicit lifecycle; assertion/past status requires gold review",
            })
    return fields, records


def _summary_metrics(report: dict[str, Any]) -> dict[str, Any]:
    accuracy = report["attribute_accuracy"]
    return {
        "mention_exact_match": accuracy["mention_exact_match"],
        "relation_exact_match": accuracy["relation_exact_match"],
        "scope_accuracy": accuracy["scope_accuracy"],
        "cross_mention_isolation": accuracy["cross_mention_isolation"],
        "cross_segment_resolution": report["v6_metrics"]["cross_segment_resolution"],
        "speaker_attribution": report["v6_metrics"]["speaker_attribution"],
        "provenance": accuracy["provenance"],
        "hard_gate_passed": report["hard_gate_passed"],
        "field_accuracy": accuracy,
    }


async def run(*, corpus_path: Path, output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        raise RuntimeError(f"refusing to overwrite V6 result: {output_path}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checksum = _sha256(corpus_path)
    if checksum != manifest["official_corpus_sha256"]:
        raise RuntimeError("Repair V6 input is not the frozen official V6")
    cases = load_corpus(corpus_path)
    if set(case.case_id for case in cases).intersection(HOLDOUT_IDS):
        raise RuntimeError("holdout cases must not participate in V6 evaluation")
    if len(cases) != manifest["validation"]["official_readiness"]["cases"]:
        raise RuntimeError("V6 input case count does not match frozen V6")

    policy_adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    raw_adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    policy_report = await evaluate_v6(policy_adapter, cases, semantic_policy=POLICY)
    raw_report = await evaluate_v6(raw_adapter, cases, semantic_policy=None)

    preexisting_type_b = _type_b_fields()
    status_type_b_findings = _status_type_b_fields()
    status_type_b, status_gold_review_queue = _full_policy_status_review_fields(cases)
    type_b = preexisting_type_b | status_type_b
    aligned = await _policy_aligned_metrics(
        policy_adapter,
        cases,
        type_b,
        semantic_policy=POLICY,
    )
    result = {
        "status": "executed",
        "run_type": "v6-repair-v6-status-only",
        "repair_version": "v6",
        "repair_scope": "STATUS_ONLY",
        "official_corpus": True,
        "official_corpus_sha256": checksum,
        "policy": "SEM-STATUS-001",
        "policy_version": "1.2",
        "type_b_status_findings_excluded_from_quality_gate": len(status_type_b),
        "status_findings_from_prior_v1_1_queue": len(status_type_b_findings),
        "new_status_gold_review_findings_exposed_by_v1_2": len(status_type_b - status_type_b_findings),
        "status_gold_review_queue": status_gold_review_queue,
        "preexisting_type_b_fields_excluded_from_quality_gate": len(preexisting_type_b),
        "type_b_fields_excluded_from_quality_gate": len(type_b),
        "policy_aligned_v6_score": aligned,
        "policy_harness_v1_2": _summary_metrics(policy_report),
        "raw_v6_score": _summary_metrics(raw_report),
        "authority_metrics": policy_adapter.authority_metrics(),
        "resolver_changes": 1,
        "gold_changes": 0,
        "corpus_changes": 0,
        "holdout_evaluation": "NOT_EXECUTED",
        "v7": "BLOCKED",
        "shadow_integration": "BLOCKED",
        "production_promotion": "BLOCKED",
        "next_action": (
            "FREEZE_RESOLVER_AND_HUMAN_GATE_FOR_HOLDOUTS"
            if aligned["hard_gate_passed"]
            else "HUMAN_GATE_V6_FAILURE"
        ),
    }
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(corpus_path=args.corpus, output_path=args.output)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
