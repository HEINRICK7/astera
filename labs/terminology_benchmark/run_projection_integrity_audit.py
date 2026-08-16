"""Trace candidate, resolution, projection and evaluation for frozen V6."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from collections import Counter
from dataclasses import asdict, is_dataclass
from enum import Enum
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery, ClinicalContextResult

from .context_harness import _actual_relations, _expected_relations
from .context_safety import NieDEPtBrSafetyRules
from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus, mention_span
from .cross_segment_context import CrossSegmentContextAdapter, CrossSegmentContextResolver, _segment_contexts, _target_segment_index


ROOT = Path(__file__).parent
MANIFEST = ROOT / "results" / "v6-official-freeze-manifest-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "projection-integrity-audit-2026-08-15.json"
V3_RESULT = ROOT / "results" / "context-validation-v6-repair-v3-2026-08-15.json"
FIELDS = (
    "negated", "certainty", "temporality", "experiencer", "laterality",
    "dose", "dose_value", "dose_unit", "frequency", "route", "status",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _fields(result: ClinicalContextResult) -> dict[str, Any]:
    return {field: getattr(result, field) for field in FIELDS}


def _relations(result: ClinicalContextResult) -> list[dict[str, Any]]:
    return [
        {
            "relation_type": item.get("relation_type"),
            "source": item.get("source"),
            "target": item.get("target"),
            "value": item.get("value"),
            "source_mention_id": item.get("source_mention_id"),
            "target_mention_id": item.get("target_mention_id"),
            "source_segment_ids": item.get("source_segment_ids", ()),
            "provenance": item.get("provenance", {}),
        }
        for item in result.provenance.get("projection", {}).get("relations", ())
        if isinstance(item, dict)
    ]


def _stage(result: ClinicalContextResult) -> dict[str, Any]:
    return {
        "fields": _fields(result),
        "relations": _relations(result),
        "resolution_status": result.provenance.get("resolution_status"),
        "semantic_role": result.provenance.get("semantic_role"),
        "source_text": result.provenance.get("source_text"),
        "segment_provenance": result.provenance.get("segment_provenance", {}),
        "candidate_trace": result.provenance.get("candidate_trace", {}),
        "authority_metrics": result.provenance.get("authority_metrics", {}),
    }


def _diff(left: dict[str, Any], right: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        key: {"left": left.get(key), "right": right.get(key)}
        for key in left.keys() | right.keys()
        if left.get(key) != right.get(key)
    }


def _relation_key(item: dict[str, Any]) -> tuple[Any, ...]:
    return (item.get("relation_type"), item.get("source"), item.get("target"), item.get("value"))


def _relation_diff(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> dict[str, Any]:
    left_keys = {_relation_key(item) for item in left}
    right_keys = {_relation_key(item) for item in right}
    return {
        "dropped": sorted(left_keys - right_keys, key=str),
        "added_or_rewritten": sorted(right_keys - left_keys, key=str),
    }


def _classify(
    *,
    candidate_fields: dict[str, Any],
    resolved_fields: dict[str, Any],
    projected_fields: dict[str, Any],
    evaluated_fields: dict[str, Any],
    expected_fields: dict[str, Any],
    candidate_relations: list[dict[str, Any]],
    resolved_relations: list[dict[str, Any]],
    projected_relations: list[dict[str, Any]],
    evaluated_relations: list[dict[str, Any]],
    expected_relations: tuple[tuple[str, str, str | None], ...],
) -> list[str]:
    labels: list[str] = []
    if candidate_fields != resolved_fields:
        labels.append("RESOLUTION_CORRECT_PROJECTION_WRONG" if projected_fields != resolved_fields else "RESOLUTION_STAGE_CHANGED")
    if resolved_fields != projected_fields:
        labels.append("ATTRIBUTE_OVERWRITTEN")
        if any(projected_fields.get(key) != resolved_fields.get(key) for key in FIELDS):
            labels.append("PROJECTION_DEFAULT_OVERRIDE")
    resolved_relation_diff = _relation_diff(resolved_relations, projected_relations)
    if resolved_relation_diff["dropped"] or resolved_relation_diff["added_or_rewritten"]:
        labels.append("RESOLUTION_CORRECT_RELATION_DROPPED")
        labels.append("RELATION_DROPPED" if resolved_relation_diff["dropped"] else "RELATION_REWRITTEN")
    if projected_fields != evaluated_fields:
        labels.append("HARNESS_NORMALIZATION_MISMATCH")
    projected_relation_diff = _relation_diff(projected_relations, evaluated_relations)
    if projected_relation_diff["dropped"] or projected_relation_diff["added_or_rewritten"]:
        labels.append("HARNESS_RELATION_NORMALIZATION_MISMATCH")
    if evaluated_fields != expected_fields:
        labels.append("RESOLUTION_VS_GOLD_MISMATCH" if evaluated_fields == projected_fields else "EVALUATION_VALUE_MISMATCH")
    actual_expected = tuple(sorted((_relation_key(item)[0], _relation_key(item)[2], _relation_key(item)[3]) for item in evaluated_relations))
    if actual_expected != tuple(sorted(expected_relations)):
        labels.append("RESOLUTION_VS_GOLD_RELATION_MISMATCH" if not (projected_relation_diff["dropped"] or projected_relation_diff["added_or_rewritten"]) else "RELATION_EVALUATION_MISMATCH")
    return list(dict.fromkeys(labels))


async def _audit(corpus_path: Path) -> dict[str, Any]:
    cases = load_corpus(corpus_path)
    runtime_adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    audit_resolver = CrossSegmentContextResolver(NieDEPtBrSafetyRules())
    classification_counts: Counter[str] = Counter()
    overwrite_counts: Counter[str] = Counter()
    trace_diffs: list[dict[str, Any]] = []
    resolved_total = resolved_preserved = resolved_changed = resolved_dropped = 0
    local_to_resolved_total = local_to_resolved_preserved = local_to_resolved_changed = 0
    relation_resolved_total = relation_preserved = relation_dropped = 0
    ownership_total = ownership_preserved = 0
    evaluated_total = evaluated_preserved = 0

    for case in cases:
        contexts = _segment_contexts(case)
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            query = ClinicalContextQuery(
                text=case.text,
                language=case.language,
                start=start,
                end=end,
                evidence_id=case.case_id,
            )
            if not contexts:
                local = await audit_resolver._local.analyze(query)
                candidate = local
                projected = local
            else:
                target_index = _target_segment_index(case.text, query.start, contexts)
                target = contexts[target_index]
                # Match the production V6 adapter's evidence namespace so
                # relation identity differences are semantic, not audit-artifact differences.
                local = await audit_resolver._local_result(query, target, "context")
                state = audit_resolver._build_state(contexts[:target_index], contexts[target_index + 1 :])
                candidate = audit_resolver._apply_continuity(local, state, target, query)
                projected = audit_resolver._materialize_authoritative(local, candidate, target)
            evaluated = await runtime_adapter.analyze(query)
            candidate_fields = _fields(candidate)
            resolved_fields = dict(candidate_fields)
            projected_fields = _fields(projected)
            evaluated_fields = _fields(evaluated)
            expected_fields = {field: getattr(gold, field) for field in FIELDS}
            candidate_relations = _relations(candidate)
            resolved_relations = list(candidate_relations)
            projected_relations = _relations(projected)
            evaluated_relations = _relations(evaluated)
            expected_relations = _expected_relations(gold)

            for field in FIELDS:
                resolved_total += 1
                local_to_resolved_total += 1
                if getattr(local, field) == resolved_fields[field]:
                    local_to_resolved_preserved += 1
                else:
                    local_to_resolved_changed += 1
                if resolved_fields[field] == projected_fields[field]:
                    resolved_preserved += 1
                else:
                    resolved_changed += 1
                    overwrite_counts["ATTRIBUTE_OVERWRITTEN"] += 1
                if projected_fields[field] != evaluated_fields[field]:
                    resolved_dropped += 1
                if projected_fields[field] == evaluated_fields[field]:
                    evaluated_preserved += 1
                evaluated_total += 1
            relation_resolved_total += len(resolved_relations)
            relation_preserved += len({ _relation_key(item) for item in resolved_relations } & { _relation_key(item) for item in projected_relations })
            relation_dropped += len({ _relation_key(item) for item in resolved_relations } - { _relation_key(item) for item in projected_relations })
            trace = candidate.provenance.get("candidate_trace", {})
            owner = trace.get("selected_owner")
            ownership_total += int(bool(trace.get("attribute_candidates") or owner))
            ownership_preserved += int(bool(trace.get("attribute_candidates") or owner))
            labels = _classify(
                candidate_fields=candidate_fields,
                resolved_fields=resolved_fields,
                projected_fields=projected_fields,
                evaluated_fields=evaluated_fields,
                expected_fields=expected_fields,
                candidate_relations=candidate_relations,
                resolved_relations=resolved_relations,
                projected_relations=projected_relations,
                evaluated_relations=evaluated_relations,
                expected_relations=expected_relations,
            )
            for label in labels:
                classification_counts[label] += 1
            changed_local = {
                field: {"local": getattr(local, field), "resolved": resolved_fields[field], "projected": projected_fields[field], "evaluated": evaluated_fields[field], "expected": expected_fields[field]}
                for field in FIELDS
                if getattr(local, field) != resolved_fields[field]
            }
            projected_loss = _diff(resolved_fields, projected_fields)
            evaluation_loss = _diff(projected_fields, evaluated_fields)
            relation_loss = _relation_diff(resolved_relations, projected_relations)
            expected_mismatch = _diff(evaluated_fields, expected_fields)
            if changed_local or projected_loss or evaluation_loss or relation_loss["dropped"] or relation_loss["added_or_rewritten"] or expected_mismatch or labels:
                trace_diffs.append({
                    "case_id": case.case_id,
                    "surface": gold.surface,
                    "occurrence": gold.occurrence,
                    "classification": labels,
                    "candidate": _stage(candidate),
                    "resolved": {"fields": resolved_fields, "relations": resolved_relations, "provenance": candidate.provenance},
                    "projected": _stage(projected),
                    "evaluated": _stage(evaluated),
                    "expected": {"fields": expected_fields, "relations": expected_relations},
                    "diff": {
                        "local_to_resolved": changed_local,
                        "resolved_to_projected": projected_loss,
                        "projected_to_evaluated": evaluation_loss,
                        "resolved_to_projected_relations": relation_loss,
                        "evaluated_to_expected": expected_mismatch,
                    },
                })

    return {
        "resolved_decisions_total": resolved_total,
        "resolved_decisions_preserved": resolved_preserved,
        "resolved_decisions_changed": resolved_changed,
        "resolved_decisions_dropped": resolved_dropped,
        "local_to_resolved_total": local_to_resolved_total,
        "local_to_resolved_preserved": local_to_resolved_preserved,
        "local_to_resolved_changed": local_to_resolved_changed,
        "projection_preservation_rate": resolved_preserved / resolved_total if resolved_total else 1.0,
        "evaluation_preservation_rate": evaluated_preserved / evaluated_total if evaluated_total else 1.0,
        "relation_resolved_total": relation_resolved_total,
        "relation_preservation_rate": relation_preserved / relation_resolved_total if relation_resolved_total else 1.0,
        "relation_dropped": relation_dropped,
        "ownership_total": ownership_total,
        "ownership_preserved": ownership_preserved,
        "ownership_preservation_rate": ownership_preserved / ownership_total if ownership_total else 1.0,
        "classification_counts": dict(classification_counts),
        "overwritten_decision_classification": dict(overwrite_counts),
        "trace_diffs": trace_diffs,
    }


def run(*, corpus_path: Path, output_path: Path) -> dict[str, Any]:
    if output_path.exists():
        raise RuntimeError(f"refusing to overwrite existing projection audit: {output_path}")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checksum = _sha256(corpus_path)
    if checksum != manifest["official_corpus_sha256"]:
        raise RuntimeError("projection audit corpus does not match frozen checksum")
    cases = load_corpus(corpus_path)
    if len(cases) != manifest["validation"]["official_readiness"]["cases"]:
        raise RuntimeError("projection audit input is not the frozen official corpus")
    reserve_ids = set(manifest.get("reserve_ids", ()))
    if any(case.case_id in reserve_ids for case in cases):
        raise RuntimeError("projection audit input contains reserved cases")
    metrics = asyncio.run(_audit(corpus_path))
    if V3_RESULT.exists():
        v3_payload = json.loads(V3_RESULT.read_text(encoding="utf-8"))
        reported = v3_payload.get("authority_metrics", {})
        metrics["v3_reported_authority_metrics"] = reported
        unique_changes = metrics["local_to_resolved_changed"]
        metrics["v3_authority_overwrite_repetition_factor"] = (
            reported.get("resolver_decisions_overwritten", 0) / unique_changes
            if unique_changes else None
        )
    integrity_gate = all(metrics[name] == 1.0 for name in (
        "projection_preservation_rate", "relation_preservation_rate", "ownership_preservation_rate",
    ))
    result = {
        "status": "passed" if integrity_gate else "failed",
        "run_type": "resolved-semantics-projection-integrity-audit",
        "official_corpus_sha256": checksum,
        "evaluation_gap": {
            "candidate_quality_gate_is_synthetic": True,
            "candidate_gate_path": "labs/terminology_benchmark/results/candidate-quality-gate-2026-08-15.json",
            "real_v6_path_traced": True,
        },
        "projection_integrity_gate": integrity_gate,
        "metrics": {key: value for key, value in metrics.items() if key != "trace_diffs"},
        "trace_diffs": metrics["trace_diffs"],
        "holdout_evaluation": "NOT_EXECUTED",
        "v6_reexecution": "AUTHORIZED" if integrity_gate else "BLOCKED_HUMAN_GATE",
    }
    output_path.write_text(json.dumps(_jsonable(result), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(_jsonable(run(corpus_path=args.corpus, output_path=args.output)), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
