"""Execute Candidate Quality & Ownership Repair V3 on frozen V6 only."""
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
from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus, mention_span
from .cross_segment_context import CrossSegmentContextAdapter
from .v6_harness import evaluate_v6


ROOT = Path(__file__).parent
MANIFEST = ROOT / "results" / "v6-official-freeze-manifest-2026-08-15.json"
CANDIDATE_GATE = ROOT / "results" / "candidate-quality-gate-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "context-validation-v6-repair-v3-2026-08-15.json"
BLIND = ROOT / "results" / "context-validation-v6-blind-2026-08-15.json"
V1 = ROOT / "results" / "context-validation-v6-cross-segment-repair-2026-08-15.json"
V2 = ROOT / "results" / "context-validation-v6-repair-v2-2026-08-15.json"
AUTHORITATIVE = ROOT / "results" / "context-validation-v6-authoritative-cutover-2026-08-15.json"


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


def _stored_metrics(payload: dict[str, Any], key: str = "report") -> dict[str, Any]:
    if key in payload:
        return _metrics(payload[key])
    if key in payload and isinstance(payload[key], dict):
        return payload[key]
    return payload.get("repaired") or payload.get("v2") or payload.get("authoritative_cutover") or {}


async def _case_outcomes(adapter: Any, cases: tuple[Any, ...]) -> dict[str, dict[str, Any]]:
    outcomes: dict[str, dict[str, Any]] = {}
    fields = (
        "negated", "certainty", "temporality", "experiencer", "laterality",
        "dose", "dose_value", "dose_unit", "frequency", "route", "status",
    )
    for case in cases:
        mention_matches = 0
        relation_matches = 0
        relation_total = 0
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            result = await adapter.analyze(ClinicalContextQuery(
                text=case.text,
                language=case.language,
                start=start,
                end=end,
                evidence_id=case.case_id,
            ))
            mention_matches += int(all(getattr(result, field) == getattr(gold, field) for field in fields))
            expected = _expected_relations(gold)
            if expected:
                relation_total += 1
                relation_matches += int(_actual_relations(result) == expected)
        outcomes[case.case_id] = {
            "mention_exact": mention_matches == len(case.gold),
            "mention_matches": mention_matches,
            "mention_total": len(case.gold),
            "relation_exact": relation_matches == relation_total if relation_total else True,
            "relation_matches": relation_matches,
            "relation_total": relation_total,
        }
    return outcomes


async def run(*, corpus_path: Path, output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        raise RuntimeError(f"refusing to overwrite existing V3 result: {output_path}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    candidate_gate = json.loads(CANDIDATE_GATE.read_text(encoding="utf-8"))
    if not candidate_gate.get("internal_quality_gate"):
        raise RuntimeError("candidate quality gate did not authorize Repair V3")
    checksum = _sha256(corpus_path)
    if checksum != manifest["official_corpus_sha256"]:
        raise RuntimeError("Repair V3 corpus does not match the frozen checksum")
    cases = load_corpus(corpus_path)
    if len(cases) != manifest["validation"]["official_readiness"]["cases"]:
        raise RuntimeError("Repair V3 input is not the frozen official corpus")
    reserve_ids = set(manifest.get("reserve_ids", ()))
    if any(case.case_id in reserve_ids for case in cases):
        raise RuntimeError("Repair V3 input contains reserved cases")

    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    report = await evaluate_v6(adapter, cases)
    outcomes = await _case_outcomes(adapter, cases)
    baseline = json.loads(BLIND.read_text(encoding="utf-8"))
    v1 = json.loads(V1.read_text(encoding="utf-8"))
    v2 = json.loads(V2.read_text(encoding="utf-8"))
    authoritative = json.loads(AUTHORITATIVE.read_text(encoding="utf-8"))
    baseline_metrics = _stored_metrics(baseline)
    v1_metrics = _stored_metrics(v1)
    v2_metrics = _stored_metrics(v2)
    authoritative_metrics = _stored_metrics(authoritative)
    result = {
        "status": "executed",
        "run_type": "v6-repair-v3-candidate-quality-ownership",
        "official_corpus": True,
        "official_corpus_sha256": checksum,
        "repair_version": "v3",
        "components": [
            "ClinicalSemanticCandidate",
            "ClinicalAttributeCandidate",
            "QuestionContext",
            "ShortAnswerResolver",
            "ClinicalReferenceResolver",
            "ClinicalAttributeAttachmentResolver",
            "ClinicalRelationResolver",
            "CandidateTrace",
            "AuthoritativeProjectionWriter",
        ],
        "candidate_quality_gate": candidate_gate["metrics"],
        "comparison": {
            "Blind": baseline_metrics,
            "Repair V1": v1_metrics,
            "Repair V2": v2_metrics,
            "Authoritative Cutover": authoritative_metrics,
            "Repair V3": _metrics(report),
        },
        "v3": _metrics(report),
        "authority_metrics": adapter.authority_metrics(),
        "case_outcomes": outcomes,
        "provenance": _metrics(report)["provenance"],
        "holdout_evaluation": "NOT_EXECUTED",
        "v7": "NOT_EXECUTED",
        "shadow_integration": "BLOCKED",
        "production_promotion": "BLOCKED",
        "next_action": "holdout-gate" if report["hard_gate_passed"] else "HUMAN_GATE_V6_REPAIR_V3_FAIL",
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
