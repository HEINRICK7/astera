"""Execute Repair V2 against the frozen, selected V6 corpus only."""
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
DEFAULT_BLIND = ROOT / "results" / "context-validation-v6-blind-2026-08-15.json"
DEFAULT_V1 = ROOT / "results" / "context-validation-v6-cross-segment-repair-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "context-validation-v6-repair-v2-2026-08-15.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _metrics(report: dict[str, Any]) -> dict[str, Any]:
    attrs = report["attribute_accuracy"]
    v6 = report["v6_metrics"]
    return {
        "mention_exact": attrs["mention_exact_match"],
        "relation_exact": attrs["relation_exact_match"],
        "scope_accuracy": attrs["scope_accuracy"],
        "cross_mention_isolation": attrs["cross_mention_isolation"],
        "cross_segment": v6["cross_segment_resolution"],
        "speaker": v6["speaker_attribution"],
        "provenance": attrs["provenance"],
        "hard_gate_passed": report["hard_gate_passed"],
    }


async def _case_outcomes(adapter: Any, cases: tuple[Any, ...]) -> dict[str, dict[str, Any]]:
    outcomes: dict[str, dict[str, Any]] = {}
    fields = (
        "negated", "certainty", "temporality", "experiencer", "laterality",
        "dose", "dose_value", "dose_unit", "frequency", "route", "status",
    )
    for case in cases:
        exact = 0
        total = len(case.gold)
        relation_exact = 0
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
            exact += int(all(getattr(result, field) == getattr(gold, field) for field in fields))
            expected = _expected_relations(gold)
            if expected:
                relation_total += 1
                relation_exact += int(_actual_relations(result) == expected)
        outcomes[case.case_id] = {
            "mention_exact": exact == total,
            "mention_matches": exact,
            "mention_total": total,
            "relation_exact": relation_exact == relation_total if relation_total else True,
            "relation_matches": relation_exact,
            "relation_total": relation_total,
        }
    return outcomes


async def run(*, corpus_path: Path, blind_path: Path, v1_path: Path, output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        raise RuntimeError(f"refusing to overwrite existing V2 result: {output_path}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checksum = _sha256(corpus_path)
    if checksum != manifest["official_corpus_sha256"]:
        raise RuntimeError("Repair V2 corpus does not match the frozen checksum")
    cases = load_corpus(corpus_path)
    expected_cases = manifest["validation"]["official_readiness"]["cases"]
    if len(cases) != expected_cases:
        raise RuntimeError("Repair V2 input is not the frozen official corpus")
    reserve_ids = set(manifest.get("reserve_ids", ()))
    if any(case.case_id in reserve_ids for case in cases):
        raise RuntimeError("Repair V2 input contains reserved cases")

    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    report = await evaluate_v6(adapter, cases)
    outcomes = await _case_outcomes(adapter, cases)
    baseline = json.loads(blind_path.read_text(encoding="utf-8"))
    v1 = json.loads(v1_path.read_text(encoding="utf-8"))
    baseline_adapter = NieDEPtBrSafetyRules()
    baseline_outcomes = await _case_outcomes(baseline_adapter, cases)
    improved = sorted(case_id for case_id, item in outcomes.items() if (
        item["mention_exact"] and not baseline_outcomes[case_id]["mention_exact"]
    ) or (
        item["relation_exact"] and not baseline_outcomes[case_id]["relation_exact"]
    ))
    regressed = sorted(case_id for case_id, item in outcomes.items() if (
        not item["mention_exact"] and baseline_outcomes[case_id]["mention_exact"]
    ) or (
        not item["relation_exact"] and baseline_outcomes[case_id]["relation_exact"]
    ))
    unchanged = sorted(set(outcomes) - set(improved) - set(regressed))
    result = {
        "status": "executed",
        "run_type": "v6-repair-v2",
        "official_corpus": True,
        "official_corpus_sha256": checksum,
        "repair_version": "v2",
        "components": [
            "CrossSegmentContextState",
            "ClinicalReferenceResolver",
            "ClinicalAttributeAttachmentResolver",
            "ClinicalRelationResolver",
            "ContextLifetimePolicy",
            "AmbiguityPolicy",
        ],
        "baseline_path": str(blind_path),
        "v1_path": str(v1_path),
        "v2": _metrics(report),
        "baseline": _metrics(baseline["report"]),
        "v1": v1["repaired"],
        "improved_cases": improved,
        "unchanged_cases": unchanged,
        "regressed_cases": regressed,
        "newly_broken_cases": regressed,
        "case_outcomes": outcomes,
        "provenance": _metrics(report)["provenance"],
        "holdout_evaluation": "NOT_EXECUTED",
        "shadow_integration": "BLOCKED",
        "production_promotion": "BLOCKED",
        "next_action": "holdout-gate" if report["hard_gate_passed"] else "HUMAN_GATE_V6_REPAIR_V2_FAIL",
    }
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--blind", type=Path, default=DEFAULT_BLIND)
    parser.add_argument("--v1", type=Path, default=DEFAULT_V1)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(
        corpus_path=args.corpus,
        blind_path=args.blind,
        v1_path=args.v1,
        output_path=args.output,
    )), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
