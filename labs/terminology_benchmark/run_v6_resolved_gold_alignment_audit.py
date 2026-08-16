"""Classify frozen V6 resolved-semantics versus gold divergences."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus


ROOT = Path(__file__).parent
MANIFEST = ROOT / "results" / "v6-official-freeze-manifest-2026-08-15.json"
TRACE = ROOT / "results" / "projection-integrity-audit-final-v2-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "v6-resolved-gold-alignment-audit-2026-08-15.json"
FIELDS = ("negated", "certainty", "temporality", "experiencer", "laterality", "dose", "dose_value", "dose_unit", "frequency", "route", "status")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _field_label(field: str) -> str:
    return {
        "negated": "WRONG_NEGATION",
        "certainty": "WRONG_CERTAINTY",
        "temporality": "WRONG_TEMPORALITY",
        "experiencer": "WRONG_EXPERIENCER",
        "laterality": "WRONG_LATERALITY",
        "status": "WRONG_STATUS",
        "dose": "WRONG_DOSE",
        "dose_value": "WRONG_DOSE",
        "dose_unit": "WRONG_DOSE",
        "frequency": "WRONG_FREQUENCY",
        "route": "WRONG_ROUTE",
    }.get(field, "WRONG_MENTION")


def _cue_reason(field: str, text: str, expected: Any, resolved: Any) -> tuple[str, str, float, bool]:
    folded = text.casefold()
    if field == "negated":
        if re.search(r"\b(?:nega|sem|não|nunca)\b", folded):
            if expected is True and resolved is False:
                return "explicit negation cue was not preserved for the target mention", "A", 0.98, False
            return "negation cue appears scoped to another mention; target ownership/scope is wrong", "A", 0.94, False
        return "negation differs without a decisive local cue", "C", 0.62, False
    if field == "laterality":
        if re.search(r"\b(?:esquerd[oa]|direit[oa])\b", folded):
            return "explicit laterality cue was not attached to the target mention", "A", 0.98, False
        return "laterality differs without an explicit target-side cue", "C", 0.60, False
    if field == "experiencer":
        if re.search(r"\b(?:mãe|pai|tia|tio|irmã|irmão|avó|avô|família|familiar)\b", folded):
            return "explicit family cue was not preserved as experiencer", "A", 0.96, False
        return "experiencer ownership is not determined by the available trace", "C", 0.60, False
    if field == "temporality":
        if expected == "past" and re.search(r"\b(?:há\s+\w+\s+anos?|mês passado|semana passada|ontem|antiga|aconteceu|teve|tinha|apresentou)\b", folded):
            return "historical-event cue conflicts with the resolved current temporality", "A", 0.90, False
        if expected == "current" and re.search(r"\b(?:depois do|desde ontem|hoje|ao levantar|ao acordar)\b", folded):
            return "event-time or onset cue was conflated with assertion temporality", "C", 0.88, False
        return "temporality requires an explicit event-time versus assertion-time policy", "C", 0.68, False
    if field == "status":
        if expected == "present" and resolved is None:
            return "gold uses present status while the resolver contract represents current assertion as null", "C", 0.95, True
        if resolved == "discontinued" and expected is None:
            return "discontinued medication state leaked to a non-owner mention", "A", 0.93, False
        return "status vocabulary or state ownership is not aligned", "C", 0.70, True
    if field in {"dose", "dose_value", "dose_unit", "frequency"}:
        if field in {"dose", "dose_value"} and len(re.findall(r"\b\d+(?:[.,]\d+)?\s*(?:mg|g|mcg|µg|ml)\b", folded)) > 1:
            return "latest in-segment dose was not selected under an explicit transition", "A", 0.92, False
        if field == "frequency" and len(re.findall(r"\b(?:ao dia|pela manhã|à noite|antes de dormir|a cada)\b", folded)) > 1:
            return "latest in-segment frequency was not selected under an explicit transition", "A", 0.90, False
        return "attribute value differs and needs ownership/transition policy review", "C", 0.65, False
    return "semantic value differs without a decisive policy-independent reason", "C", 0.55, False


def _relation_key(item: Any) -> tuple[Any, Any, Any]:
    if isinstance(item, dict):
        return item.get("relation_type"), item.get("target"), item.get("value")
    return tuple(item)


def _relation_findings(resolved: list[dict[str, Any]], expected: list[list[Any]]) -> list[dict[str, Any]]:
    actual = {_relation_key(item) for item in resolved}
    target = {_relation_key(item) for item in expected}
    findings: list[dict[str, Any]] = []
    for item in sorted(target - actual, key=str):
        same_target = [candidate for candidate in actual if candidate[:2] == item[:2]]
        label = "WRONG_RELATION" if same_target else "MISSING_RELATION"
        policy = item[0] == "DISCONTINUED_AT"
        findings.append({
            "classification": label,
            "relation": item,
            "semantic_reason": "gold relation vocabulary requires DISCONTINUED_AT while resolver emits no matching relation" if policy else "gold relation was not present in resolved projection",
            "error_type": "C" if policy else "A",
            "confidence": 0.94 if policy else 0.82,
            "gold_review_required": policy,
        })
    for item in sorted(actual - target, key=str):
        findings.append({
            "classification": "EXTRA_RELATION",
            "relation": item,
            "semantic_reason": "resolved relation has no corresponding gold relation",
            "error_type": "C",
            "confidence": 0.68,
            "gold_review_required": False,
        })
    return findings


def run(*, corpus_path: Path, trace_path: Path, output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        raise RuntimeError(f"refusing to overwrite alignment audit: {output_path}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checksum = _sha256(corpus_path)
    if checksum != manifest["official_corpus_sha256"]:
        raise RuntimeError("alignment audit corpus does not match frozen checksum")
    cases = {case.case_id: case for case in load_corpus(corpus_path)}
    if len(cases) != manifest["validation"]["official_readiness"]["cases"]:
        raise RuntimeError("alignment audit input is not the frozen official corpus")
    reserve_ids = set(manifest.get("reserve_ids", ()))
    if reserve_ids.intersection(cases):
        raise RuntimeError("alignment audit input contains reserved cases")
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    review_queue: list[dict[str, Any]] = []
    for item in trace["trace_diffs"]:
        case = cases[item["case_id"]]
        expected = item["expected"]["fields"]
        resolved = item["resolved"]["fields"]
        findings: list[dict[str, Any]] = []
        for field in FIELDS:
            if resolved.get(field) == expected.get(field):
                continue
            reason, error_type, confidence, review = _cue_reason(field, case.text, expected.get(field), resolved.get(field))
            finding = {
                "classification": _field_label(field),
                "field": field,
                "expected": expected.get(field),
                "resolved": resolved.get(field),
                "semantic_reason": reason,
                "error_type": error_type,
                "confidence": confidence,
                "gold_review_required": review,
            }
            findings.append(finding)
            counts[finding["classification"]] += 1
            type_counts[error_type] += 1
            if review:
                review_queue.append({"case_id": case.case_id, "surface": item["surface"], **finding})
        relation_findings = _relation_findings(item["resolved"]["relations"], item["expected"]["relations"])
        for finding in relation_findings:
            findings.append(finding)
            counts[finding["classification"]] += 1
            type_counts[finding["error_type"]] += 1
            if finding["gold_review_required"]:
                review_queue.append({"case_id": case.case_id, "surface": item["surface"], **finding})
        if not findings:
            continue
        records.append({
            "case_id": case.case_id,
            "text": case.text,
            "segments": [{"segment_id": segment.segment_id, "speaker": segment.speaker, "text": segment.text} for segment in case.segments],
            "surface": item["surface"],
            "occurrence": item["occurrence"],
            "expected": item["expected"],
            "resolved": item["resolved"],
            "differing_fields": findings,
            "confidence": min((finding["confidence"] for finding in findings), default=1.0),
        })
    result = {
        "status": "audit_only",
        "run_type": "v6-resolved-gold-alignment",
        "official_corpus_sha256": checksum,
        "gold_modified": False,
        "resolver_modified": False,
        "records": records,
        "summary": {
            "records_with_divergence": len(records),
            "field_and_relation_findings": sum(counts.values()),
            "classification_counts": dict(counts),
            "error_type_counts": dict(type_counts),
            "type_a": type_counts.get("A", 0),
            "type_b": type_counts.get("B", 0),
            "type_c": type_counts.get("C", 0),
            "gold_review_required": len(review_queue),
        },
        "gold_review_queue": review_queue,
        "holdout_evaluation": "NOT_EXECUTED",
        "next_step": "semantic-policy-review-before-repair",
    }
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--trace", type=Path, default=TRACE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(corpus_path=args.corpus, trace_path=args.trace, output_path=args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
