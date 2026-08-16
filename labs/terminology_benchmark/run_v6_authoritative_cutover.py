"""Evaluate the authoritative semantic projection cutover on frozen V6."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery

from .context_safety import NieDEPtBrSafetyRules
from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus, mention_span
from .cross_segment_context import CrossSegmentContextAdapter
from .context_harness import _actual_relations, _expected_relations
from .v6_harness import evaluate_v6


ROOT = Path(__file__).parent
MANIFEST = ROOT / "results" / "v6-official-freeze-manifest-2026-08-15.json"
BLIND = ROOT / "results" / "context-validation-v6-blind-2026-08-15.json"
V1 = ROOT / "results" / "context-validation-v6-cross-segment-repair-2026-08-15.json"
V2 = ROOT / "results" / "context-validation-v6-repair-v2-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "context-validation-v6-authoritative-cutover-2026-08-15.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _metrics(report: dict[str, Any]) -> dict[str, Any]:
    attrs = report["attribute_accuracy"]
    v6 = report["v6_metrics"]
    return {
        "mention_exact_match": attrs["mention_exact_match"],
        "relation_exact_match": attrs["relation_exact_match"],
        "scope_accuracy": attrs["scope_accuracy"],
        "cross_mention_isolation": attrs["cross_mention_isolation"],
        "cross_segment_resolution": v6["cross_segment_resolution"],
        "speaker_attribution": v6["speaker_attribution"],
        "provenance": attrs["provenance"],
        "hard_gate_passed": report["hard_gate_passed"],
    }


async def _outcomes(adapter: CrossSegmentContextAdapter, cases: tuple[Any, ...]) -> dict[str, dict[str, int]]:
    fields = (
        "negated", "certainty", "temporality", "experiencer", "laterality",
        "dose", "dose_value", "dose_unit", "frequency", "route", "status",
    )
    result: dict[str, dict[str, int]] = {}
    for case in cases:
        mention_matches = 0
        relation_matches = 0
        relation_total = 0
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            actual = await adapter.analyze(ClinicalContextQuery(
                text=case.text, language=case.language, start=start, end=end, evidence_id=case.case_id,
            ))
            mention_matches += int(all(getattr(actual, field) == getattr(gold, field) for field in fields))
            expected_relations = _expected_relations(gold)
            if expected_relations:
                relation_total += 1
                relation_matches += int(_actual_relations(actual) == expected_relations)
        result[case.case_id] = {
            "mention_matches": mention_matches,
            "mention_total": len(case.gold),
            "relation_matches": relation_matches,
            "relation_total": relation_total,
        }
    return result


async def run(*, output: Path) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    corpus = CONTEXT_VALIDATION_V6_PATH
    checksum = _sha256(corpus)
    if checksum != manifest["official_corpus_sha256"]:
        raise RuntimeError("authoritative cutover corpus checksum mismatch")
    cases = load_corpus(corpus)
    if len(cases) != manifest["validation"]["official_readiness"]["cases"]:
        raise RuntimeError("authoritative cutover input is not the official corpus")
    reserve_ids = set(manifest.get("reserve_ids", ()))
    if any(case.case_id in reserve_ids for case in cases):
        raise RuntimeError("reserved cases are present in cutover input")

    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    report = await evaluate_v6(adapter, cases)
    authority_metrics = adapter.authority_metrics()
    outcome = await _outcomes(adapter, cases)
    prior_v2 = json.loads(V2.read_text(encoding="utf-8"))
    blind = json.loads(BLIND.read_text(encoding="utf-8"))
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    result = {
        "status": "executed",
        "run_type": "v6-authoritative-reference-attribute-ownership-cutover",
        "official_corpus_sha256": checksum,
        "blind": _metrics(blind["report"]),
        "repair_v1": v1["repaired"],
        "repair_v2": prior_v2["v2"],
        "authoritative_cutover": _metrics(report),
        "authority_metrics": authority_metrics,
        "case_outcomes": outcome,
        "holdout_evaluation": "NOT_EXECUTED",
        "v7": "NOT_EXECUTED",
        "shadow_integration": "BLOCKED",
        "production_promotion": "BLOCKED",
        "next_action": "HUMAN_GATE_AUTHORITATIVE_CUTOVER_FAIL" if not report["hard_gate_passed"] else "freeze-before-holdout",
    }
    if output.exists():
        raise RuntimeError(f"refusing to overwrite {output}")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(output=args.output)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
