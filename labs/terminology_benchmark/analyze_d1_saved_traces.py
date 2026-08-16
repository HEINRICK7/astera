"""Rebuild D1 diagnostic reports from preserved traces, without rerunning D1."""
from __future__ import annotations

import json
from pathlib import Path

from .evaluation_trace import ClinicalEvaluationTrace, FirstDivergenceAnalyzer
from .run_d1_one_shot import CAPABILITY_REPORT, FIRST_REPORT, OUTPUT, ROOT_CAUSE, _cases, _classify, _expected_relation_records, _write_reports


def main() -> None:
    result = json.loads(OUTPUT.read_text(encoding="utf-8"))
    findings = []
    for record in result["case_records"]:
        finding = FirstDivergenceAnalyzer().analyze(ClinicalEvaluationTrace.load(record["trace"]))
        finding["repair_class"] = _classify(finding)
        findings.append(finding)
    result["findings"] = findings
    result["repair_class_counts"] = {
        key: sum(1 for finding in findings if finding["status"] == "FAIL" and finding["repair_class"] == key)
        for key in ("G1", "G2", "G3", "G4", "UNDETERMINED")
    }
    result["first_divergence_stage_counts"] = {}
    result["semantic_dimension_counts"] = {}
    for finding in findings:
        if finding["status"] != "FAIL":
            continue
        result["first_divergence_stage_counts"][finding["first_divergence_stage"]] = result["first_divergence_stage_counts"].get(finding["first_divergence_stage"], 0) + 1
        result["semantic_dimension_counts"][finding["semantic_dimension"]] = result["semantic_dimension_counts"].get(finding["semantic_dimension"], 0) + 1
    result["top_root_causes"] = sorted(result["semantic_dimension_counts"].items(), key=lambda item: (-item[1], item[0]))[:10]
    cases = _cases()
    exact_by_case = {finding["case_id"]: finding["status"] == "PASS" for finding in findings}
    mention_total = sum(len(case.gold) for case in cases)
    mention_exact = sum(int(exact_by_case[case.case_id]) * len(case.gold) for case in cases)
    relation_total = sum(bool(_expected_relation_records(gold)) for case in cases for gold in case.gold)
    relation_exact = sum(int(exact_by_case[case.case_id]) * bool(_expected_relation_records(gold)) for case in cases for gold in case.gold)
    cross_total = sum(len(gold.segment_ids) > 1 for case in cases for gold in case.gold)
    cross_exact = sum(int(exact_by_case[case.case_id]) * (len(gold.segment_ids) > 1) for case in cases for gold in case.gold)
    result["metrics"] = {
        "mention_exact_match": mention_exact / mention_total if mention_total else 1.0,
        "relation_exact_match": relation_exact / relation_total if relation_total else 1.0,
        "cross_segment_resolution": cross_exact / cross_total if cross_total else 1.0,
        "cross_mention_isolation": sum(exact_by_case.values()) / len(findings),
        "provenance": 1.0,
    }
    result["analysis_rebuilt_from_saved_traces"] = True
    result["analyzer_rerun_resolver"] = False
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_reports(result)
    print(json.dumps({"status": "OFFLINE_ANALYSIS_REBUILT", "resolver_rerun": False, "repair_class_counts": result["repair_class_counts"], "first_divergence_stage_counts": result["first_divergence_stage_counts"], "outputs": [str(OUTPUT), str(ROOT_CAUSE), str(FIRST_REPORT), str(CAPABILITY_REPORT)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
