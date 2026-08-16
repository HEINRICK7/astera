"""Audit semantic attribute writers in the LAB and runtime source trees."""
from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path


CRITICAL_FIELDS = {
    "negated", "temporality", "experiencer", "laterality", "dose",
    "dose_value", "dose_unit", "frequency", "route", "status",
}


def _classification(path: Path, line: str) -> str:
    name = path.name
    if name == "clinical_conversational_semantics.py" and "ProjectionWriter" in line:
        return "PROJECTION_WRITER"
    if name == "cross_segment_context.py":
        return "CONTEXT_RESOLVER"
    if name == "context_safety.py":
        return "LOCAL_CANDIDATE_PRODUCER"
    if "HybridClinicalContextAdapter" in line or name == "context_adapters.py":
        return "LEGACY_OVERRIDE"
    return "LOCAL_CANDIDATE_PRODUCER"


def audit(roots: tuple[Path, ...]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for root in roots:
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts or path.name.startswith("test_"):
                continue
            source_text = path.read_text(encoding="utf-8")
            if not any(token in source_text for token in (
                "ClinicalContextResult", "ClinicalMentionProjection", "ClinicalRelation",
                "ClinicalSemanticCandidate", "ResolvedClinicalSemantics", "context_safety",
                "cross_segment_context",
            )):
                continue
            try:
                tree = ast.parse(source_text)
            except SyntaxError as error:
                findings.append({"file": str(path), "line": error.lineno or 0, "classification": "AUDIT_ERROR", "operation": str(error)})
                continue
            lines = source_text.splitlines()
            for node in ast.walk(tree):
                if not isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Call)):
                    continue
                line = lines[node.lineno - 1] if node.lineno and node.lineno <= len(lines) else ""
                critical = sorted(field for field in CRITICAL_FIELDS if field in line)
                operation = ""
                if isinstance(node, ast.Call):
                    operation = ast.unparse(node.func)
                elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                    operation = type(node).__name__
                if not critical and not any(token in line for token in ("ClinicalContextResult", "ClinicalMentionProjection", "ClinicalRelation", "ClinicalSemanticCandidate", "ResolvedClinicalSemantics", "replace(result", "projection[")):
                    continue
                findings.append({
                    "file": str(path),
                    "line": node.lineno,
                    "classification": _classification(path, line),
                    "operation": operation,
                    "critical_fields": critical,
                    "source": line.strip(),
                })
    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    findings = audit((root / "labs" / "terminology_benchmark", root / "apps" / "runtime" / "src"))
    payload = {
        "status": "executed",
        "critical_fields": sorted(CRITICAL_FIELDS),
        "writer_count": len(findings),
        "writers": findings,
        "authority_rule": "LOCAL_CANDIDATE_PRODUCER -> CONTEXT_RESOLVER -> PROJECTION_WRITER",
        "legacy_override_count": sum(item["classification"] == "LEGACY_OVERRIDE" for item in findings),
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
