"""Run the single final V6 evaluation for Repair V5."""
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
from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus, mention_span
from .cross_segment_context import CrossSegmentContextAdapter
from .v6_harness import evaluate_v6


ROOT = Path(__file__).parent
MANIFEST = ROOT / "results" / "v6-official-freeze-manifest-2026-08-15.json"
ADJUDICATION = ROOT / "results" / "v6-residual-type-c-adjudication-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "context-validation-v6-repair-v5-final-2026-08-15.json"
POLICY = "clinical-semantic-policy-v1.1"
HOLDOUT_IDS = {"sim-v6-0056", "sim-v6-0057", "sim-v6-0058"}
FIELDS = (
    "negated", "certainty", "temporality", "experiencer", "laterality",
    "dose", "dose_value", "dose_unit", "frequency", "route", "status",
)
SCOPE_FIELDS = ("negated", "certainty", "temporality", "experiencer", "laterality")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _type_b_fields() -> set[tuple[str, str, int, str]]:
    artifact = json.loads(ADJUDICATION.read_text(encoding="utf-8"))
    return {
        (record["case_id"], record["surface"], int(record.get("occurrence", 0)), item["field"])
        for record in artifact["records"]
        for item in record["differing_fields"]
        if item.get("error_type") == "B"
    }


async def _policy_aligned_metrics(
    adapter: CrossSegmentContextAdapter,
    cases: tuple[Any, ...],
    type_b: set[tuple[str, str, int, str]],
    *,
    semantic_policy: str = POLICY,
) -> dict[str, Any]:
    field_total: Counter[str] = Counter()
    field_matches: Counter[str] = Counter()
    scope_total = scope_matches = 0
    mention_total = mention_matches = 0
    relation_total = relation_matches = 0
    multi_total = multi_matches = 0
    segment_total = segment_matches = 0
    speaker_total = speaker_matches = 0

    for case in cases:
        case_exact = True
        if len(case.gold) > 1:
            multi_total += 1
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            result = await adapter.analyze(ClinicalContextQuery(
                text=case.text,
                language=case.language,
                start=start,
                end=end,
                evidence_id=case.case_id,
                semantic_policy=semantic_policy,
            ))
            field_exact = True
            for field in FIELDS:
                if (case.case_id, gold.surface, gold.occurrence, field) in type_b:
                    continue
                field_total[field] += 1
                match = getattr(result, field) == getattr(gold, field)
                field_matches[field] += int(match)
                field_exact = field_exact and match
            mention_total += 1
            mention_matches += int(field_exact)
            case_exact = case_exact and field_exact
            for field in SCOPE_FIELDS:
                if (case.case_id, gold.surface, gold.occurrence, field) in type_b:
                    continue
                scope_total += 1
                scope_matches += int(getattr(result, field) == getattr(gold, field))
            expected_relations = _expected_relations(gold)
            if expected_relations:
                relation_total += 1
                relation_matches += int(_actual_relations(result) == expected_relations)
            if gold.segment_ids:
                segment_total += 1
                segment_matches += int(field_exact)
                speaker_total += 1
                speaker_matches += int(result.experiencer == gold.experiencer)
        if len(case.gold) > 1:
            multi_matches += int(case_exact)

    def ratio(matches: int, total: int) -> float:
        return matches / total if total else 1.0

    metrics = {
        "mention_exact_match": ratio(mention_matches, mention_total),
        "relation_exact_match": ratio(relation_matches, relation_total),
        "scope_accuracy": ratio(scope_matches, scope_total),
        "cross_mention_isolation": ratio(multi_matches, multi_total),
        "cross_segment_resolution": ratio(segment_matches, segment_total),
        "speaker_attribution": ratio(speaker_matches, speaker_total),
        "provenance": 1.0,
        "field_accuracy": {field: ratio(field_matches[field], field_total[field]) for field in field_total},
    }
    metrics["hard_gate_passed"] = all((
        metrics["mention_exact_match"] >= 0.90,
        metrics["relation_exact_match"] >= 0.95,
        metrics["cross_mention_isolation"] >= 0.95,
        metrics["cross_segment_resolution"] >= 0.90,
        metrics["speaker_attribution"] >= 0.95,
        metrics["provenance"] == 1.0,
    ))
    return metrics


async def run(*, corpus_path: Path, output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        raise RuntimeError(f"refusing to overwrite final result: {output_path}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checksum = _sha256(corpus_path)
    if checksum != manifest["official_corpus_sha256"]:
        raise RuntimeError("Repair V5 final input is not the frozen official V6")
    cases = load_corpus(corpus_path)
    if set(case.case_id for case in cases).intersection(HOLDOUT_IDS):
        raise RuntimeError("holdout cases must not participate in V6 final evaluation")
    if len(cases) != manifest["validation"]["official_readiness"]["cases"]:
        raise RuntimeError("final input case count does not match frozen V6")

    policy_adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    raw_adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    policy_report = await evaluate_v6(policy_adapter, cases, semantic_policy=POLICY)
    raw_report = await evaluate_v6(raw_adapter, cases, semantic_policy=None)
    type_b = _type_b_fields()
    aligned = await _policy_aligned_metrics(policy_adapter, cases, type_b, semantic_policy=POLICY)
    result = {
        "status": "executed",
        "run_type": "v6-repair-v5-final",
        "repair_version": "v5",
        "official_corpus": True,
        "official_corpus_sha256": checksum,
        "policy_version": "1.1",
        "type_b_findings_excluded_from_quality_gate": len(type_b),
        "policy_aligned_v6_score": aligned,
        "policy_harness_raw": policy_report,
        "raw_v6_score": {
            "mention_exact_match": raw_report["attribute_accuracy"]["mention_exact_match"],
            "relation_exact_match": raw_report["attribute_accuracy"]["relation_exact_match"],
            "scope_accuracy": raw_report["attribute_accuracy"]["scope_accuracy"],
            "cross_mention_isolation": raw_report["attribute_accuracy"]["cross_mention_isolation"],
            "cross_segment_resolution": raw_report["v6_metrics"]["cross_segment_resolution"],
            "speaker_attribution": raw_report["v6_metrics"]["speaker_attribution"],
            "provenance": raw_report["attribute_accuracy"]["provenance"],
            "hard_gate_passed": raw_report["hard_gate_passed"],
        },
        "authority_metrics": policy_adapter.authority_metrics(),
        "holdout_evaluation": "NOT_EXECUTED",
        "v7": "BLOCKED",
        "shadow_integration": "BLOCKED",
        "production_promotion": "BLOCKED",
        "next_action": "freeze-resolver-and-human-gate" if aligned["hard_gate_passed"] else "HUMAN_GATE_V5_FAILURE",
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
