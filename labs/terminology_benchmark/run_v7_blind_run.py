"""Execute the frozen V7 resolver exactly once and record the blind baseline."""
from __future__ import annotations

import asyncio
import hashlib
import json
import subprocess
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery

from .context_harness import _actual_relations, _expected_relations
from .context_safety import NieDEPtBrSafetyRules
from .cross_segment_context import CrossSegmentContextAdapter
from .corpus import mention_span
from .models import BenchmarkCase, ConversationSegment, GoldMention, GoldRelation


ROOT = Path(__file__).parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
OFFICIAL = DATA / "v7_unseen_generalization_official.jsonl"
MANIFEST = RESULTS / "v7-official-freeze-manifest-2026-08-15.json"
EXECUTION_RECORD = RESULTS / "v7-blind-run-execution-record-2026-08-15.json"
OUTPUT = RESULTS / "v7-blind-run-2026-08-15.json"
OUTPUT_MD = ROOT.parent.parent / "docs/clinical-conversational-semantics/V7_BLIND_RUN_REPORT.md"
POLICY = ROOT.parent.parent / "docs/clinical-conversational-semantics/CLINICAL_SEMANTIC_POLICY.md"
RESOLVER_FILES = (
    ROOT / "cross_segment_context.py",
    ROOT / "clinical_conversational_semantics.py",
    ROOT / "clinical_projection.py",
    ROOT / "context_safety.py",
    ROOT / "context_harness.py",
    ROOT / "models.py",
)
THRESHOLDS = {
    "mention_exact_match": 0.90,
    "relation_exact_match": 0.95,
    "cross_mention_isolation": 0.95,
    "cross_segment_resolution": 0.90,
    "provenance": 1.00,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _config_checksum() -> str:
    digest = hashlib.sha256()
    for path in RESOLVER_FILES:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(_sha256(path).encode())
    return digest.hexdigest()


def _git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "UNAVAILABLE"


def _gold(item: dict[str, Any]) -> GoldMention:
    return GoldMention(
        **{
            **{key: value for key, value in item.items() if key not in {"relations", "segment_ids", "attribute_provenance", "relation_provenance"}},
            "relations": tuple(
                GoldRelation(relation_type=relation["relation_type"], target=relation["target"], value=relation.get("value"))
                for relation in item.get("relations", ())
            ),
            "segment_ids": tuple(item.get("segment_ids", ())),
            "attribute_provenance": {key: tuple(value) for key, value in item.get("attribute_provenance", {}).items()},
            "relation_provenance": {key: tuple(value) for key, value in item.get("relation_provenance", {}).items()},
        }
    )


def _cases() -> tuple[BenchmarkCase, ...]:
    records = [json.loads(line) for line in OFFICIAL.read_text(encoding="utf-8").splitlines() if line.strip()]
    return tuple(
        BenchmarkCase(
            case_id=record["case_id"],
            text=record["text"],
            language=record["language"],
            source="v7-official-frozen",
            segments=tuple(ConversationSegment(**segment) for segment in record["segments"]),
            gold=tuple(_gold(item) for item in record["gold"]),
        )
        for record in records
    )


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 1.0


def _group_update(groups: defaultdict[str, dict[str, int]], key: str, mention_exact: bool, relation_exact: bool | None) -> None:
    groups[key]["mentions"] += 1
    groups[key]["mention_exact"] += int(mention_exact)
    if relation_exact is not None:
        groups[key]["relation_total"] += 1
        groups[key]["relation_exact"] += int(relation_exact)


async def _execute(cases: tuple[BenchmarkCase, ...]) -> dict[str, Any]:
    adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), cases)
    fields = ("negated", "certainty", "temporality", "experiencer", "laterality", "dose", "dose_value", "dose_unit", "frequency", "route", "status")
    totals: Counter[str] = Counter()
    matches: Counter[str] = Counter()
    mention_total = mention_exact = relation_total = relation_exact = 0
    cross_total = cross_exact = 0
    multi_cases = isolated_cases = 0
    provenance_total = provenance_ok = 0
    latencies: list[float] = []
    groups: defaultdict[str, dict[str, int]] = defaultdict(lambda: Counter())
    failures: Counter[str] = Counter()

    for case in cases:
        case_exact = True
        if len(case.gold) > 1:
            multi_cases += 1
        for gold in case.gold:
            start, end = mention_span(case.text, gold.surface, gold.occurrence)
            started = perf_counter()
            result = await adapter.analyze(ClinicalContextQuery(
                text=case.text,
                language=case.language,
                start=start,
                end=end,
                evidence_id=case.case_id,
                semantic_policy="clinical-semantic-policy-v1.3",
            ))
            latencies.append((perf_counter() - started) * 1000)
            mention_is_exact = all(getattr(result, field) == getattr(gold, field) for field in fields)
            mention_total += 1
            mention_exact += int(mention_is_exact)
            case_exact = case_exact and mention_is_exact
            expected_relations = _expected_relations(gold)
            relation_is_exact: bool | None = None
            if expected_relations:
                relation_is_exact = _actual_relations(result) == expected_relations
                relation_total += 1
                relation_exact += int(relation_is_exact)
            if len(gold.segment_ids) > 1:
                cross_total += 1
                cross_exact += int(mention_is_exact)
            provenance_total += 1
            provenance_ok += int(bool(result.provenance.get("provider") and result.provenance.get("source_text")))
            entity_type = gold.concept_id.split(".", 1)[0]
            turn_depth = "turns_1_5" if len(case.segments) <= 5 else "turns_6_plus"
            _group_update(groups, f"family:{_family(case.case_id)}", mention_is_exact, relation_is_exact)
            _group_update(groups, f"entity_type:{entity_type}", mention_is_exact, relation_is_exact)
            _group_update(groups, f"scope:{'cross_segment' if len(gold.segment_ids) > 1 else 'single_segment'}", mention_is_exact, relation_is_exact)
            _group_update(groups, f"turn_depth:{turn_depth}", mention_is_exact, relation_is_exact)
            if not mention_is_exact:
                for field in fields:
                    if getattr(result, field) != getattr(gold, field):
                        failures[f"mention:{field}"] += 1
            if relation_is_exact is False:
                failures["relation_mismatch"] += 1
            if not result.provenance.get("provider") or not result.provenance.get("source_text"):
                failures["provenance_missing"] += 1
            for field in fields:
                expected = getattr(gold, field)
                actual = getattr(result, field)
                if expected is not None or actual is not None:
                    totals[field] += 1
                    matches[field] += int(expected == actual)
        if len(case.gold) > 1 and case_exact:
            isolated_cases += 1

    metrics = {field: _ratio(matches[field], totals[field]) for field in fields}
    metrics.update({
        "mention_exact_match": _ratio(mention_exact, mention_total),
        "relation_exact_match": _ratio(relation_exact, relation_total),
        "cross_mention_isolation": _ratio(isolated_cases, multi_cases),
        "cross_segment_resolution": _ratio(cross_exact, cross_total),
        "provenance": _ratio(provenance_ok, provenance_total),
    })
    group_metrics = {}
    for key, values in sorted(groups.items()):
        group_metrics[key] = {
            "mentions": values["mentions"],
            "mention_exact_match": _ratio(values["mention_exact"], values["mentions"]),
            "relation_exact_match": _ratio(values["relation_exact"], values["relation_total"]),
            "relation_total": values["relation_total"],
        }
    gate = {key: metrics[key] >= threshold for key, threshold in THRESHOLDS.items()}
    return {
        "provider": adapter.provider,
        "cases": len(cases),
        "metrics": metrics,
        "group_metrics": group_metrics,
        "failure_taxonomy": dict(failures),
        "counts": {"mentions": mention_total, "mention_exact": mention_exact, "relations_evaluated": relation_total, "relation_exact": relation_exact, "cross_segment_mentions": cross_total, "multi_mention_cases": multi_cases, "isolated_multi_mention_cases": isolated_cases, "provenance_total": provenance_total, "provenance_ok": provenance_ok},
        "thresholds": THRESHOLDS,
        "gate": gate,
        "hard_gate_passed": all(gate.values()),
        "mean_latency_ms": mean(latencies) if latencies else 0.0,
        "authority_metrics": adapter.authority_metrics(),
    }


def _family(case_id: str) -> str:
    number = int(case_id.rsplit("-", 1)[-1])
    families = ("MEDICATION_RECONCILIATION", "DOSE_TRANSITION", "FREQUENCY_STATUS_TRANSITION", "MULTIPLE_SYMPTOMS", "FAMILY_PATIENT_EXPERIENCER", "NEGATION_REVERSAL", "DISTRIBUTED_TEMPORALITY", "TOPIC_SWITCH", "ELLIPTICAL_ANSWER", "CLINICIAN_CORRECTION", "PATIENT_SELF_CORRECTION", "ANAPHORA_SPEAKER_TRANSITION")
    return families[(number - 1) % 12]


def main() -> None:
    if OUTPUT.exists() or EXECUTION_RECORD.exists():
        raise RuntimeError("V7 blind run is one-shot and an execution record already exists")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    corpus_checksum = _sha256(OFFICIAL)
    if manifest.get("status") != "V7_OFFICIAL_FROZEN" or not manifest.get("frozen") or manifest.get("official_corpus_checksum") != corpus_checksum:
        raise RuntimeError("frozen corpus manifest/checksum gate failed")
    execution_id = f"v7-blind-{uuid.uuid4()}"
    started_at = datetime.now(timezone.utc).isoformat()
    record = {
        "status": "STARTED",
        "execution_id": execution_id,
        "started_at_utc": started_at,
        "resolver_commit": _git_head(),
        "resolver_config_checksum": _config_checksum(),
        "policy_version": "1.3",
        "policy_checksum": _sha256(POLICY),
        "corpus_checksum": corpus_checksum,
        "corpus_manifest_checksum": _sha256(MANIFEST),
        "gold_predictions_used": False,
        "runtime_predictions_used_for_gold": False,
        "one_shot": True,
    }
    EXECUTION_RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cases = _cases()
    result = asyncio.run(_execute(cases))
    passed = result["hard_gate_passed"]
    finished = dict(record)
    finished.update({"status": "V7_BLIND_BASELINE_PASS" if passed else "V7_BLIND_BASELINE_FAIL", "finished_at_utc": datetime.now(timezone.utc).isoformat(), "evaluation": result})
    OUTPUT.write_text(json.dumps(finished, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    EXECUTION_RECORD.write_text(json.dumps(finished, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# V7 Blind Run Report",
        "",
        f"Status: **{finished['status']}**",
        "",
        f"- Execution ID: `{execution_id}`",
        f"- Cases: `{result['cases']}`",
        f"- Resolver commit: `{finished['resolver_commit']}`",
        f"- Resolver/config checksum: `{finished['resolver_config_checksum']}`",
        f"- Corpus checksum: `{corpus_checksum}`",
        "- One-shot: `true`",
        "",
        "## Metrics",
        "",
    ]
    for key, value in result["metrics"].items():
        lines.append(f"- `{key}`: `{value:.6f}`")
    lines.extend(["", "## Gate", ""])
    for key, value in result["gate"].items():
        lines.append(f"- `{key}`: `{'PASS' if value else 'FAIL'}`")
    lines.extend(["", "No repair, rerun, gold change, or corpus change is authorized after this baseline.", ""])
    lines.append("Next gate: **SHADOW INTEGRATION AUTHORIZATION**" if passed else "Next gate: **POST-V7 HUMAN GATE**")
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not passed:
        taxonomy = RESULTS / "V7_BLIND_ERROR_TAXONOMY.md"
        taxonomy.write_text("# V7 Blind Error Taxonomy\n\n" + "\n".join(f"- `{key}`: {value}" for key, value in sorted(result["failure_taxonomy"].items())) + "\n", encoding="utf-8")
    print(json.dumps({"status": finished["status"], "execution_id": execution_id, "cases": result["cases"], "metrics": result["metrics"], "gate": result["gate"], "output": str(OUTPUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
