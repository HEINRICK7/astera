"""Freeze the authorized V6 resolver/policy state before holdout evaluation."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .corpus import CONTEXT_VALIDATION_V6_PATH


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
DOCS = ROOT.parent.parent / "docs" / "clinical-conversational-semantics"
OUTPUT = RESULTS / "v6-repair-v6-freeze-2026-08-15.json"
V6_RESULT = RESULTS / "context-validation-v6-repair-v6-status-final-2026-08-15.json"
HOLDOUT_SOURCE = RESULTS / "v6-human-review-micro-expansion-submission-2026-08-15.json"
POLICY = DOCS / "CLINICAL_SEMANTIC_POLICY.md"
HOLDOUT_IDS = ("sim-v6-0056", "sim-v6-0057", "sim-v6-0058")
RESOLVER_FILES = (
    ROOT / "context_safety.py",
    ROOT / "cross_segment_context.py",
    ROOT / "clinical_conversational_semantics.py",
    Path("apps/runtime/src/ports/outbound/clinical_semantics.py"),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(("git", *args), text=True).strip()


def _git_diff_sha256(paths: tuple[Path, ...]) -> str:
    diff = subprocess.check_output(("git", "diff", "--binary", "--", *(str(path) for path in paths)))
    return hashlib.sha256(diff).hexdigest()


def freeze() -> dict[str, object]:
    if OUTPUT.exists():
        raise RuntimeError(f"freeze already exists; refusing to overwrite: {OUTPUT}")
    v6 = json.loads(V6_RESULT.read_text(encoding="utf-8"))
    if not v6["policy_aligned_v6_score"]["hard_gate_passed"]:
        raise RuntimeError("cannot freeze a failed policy-aligned V6 result")
    if v6["policy_version"] != "1.2" or v6["repair_scope"] != "STATUS_ONLY":
        raise RuntimeError("freeze input is not the authorized status-only V6 result")
    holdouts = json.loads(HOLDOUT_SOURCE.read_text(encoding="utf-8"))
    by_id = {item["candidate_id"]: item for item in holdouts}
    if not set(HOLDOUT_IDS).issubset(by_id):
        raise RuntimeError("holdout source does not contain all three reserved IDs")
    for case_id in HOLDOUT_IDS:
        item = by_id[case_id]
        if item.get("decision") != "APPROVED" or item.get("review_status") != "REVIEWED":
            raise RuntimeError(f"holdout is not human-approved: {case_id}")
        if not item.get("gold") or not item.get("segments"):
            raise RuntimeError(f"holdout is incomplete: {case_id}")

    test_command = [
        "./.venv/bin/pytest", "-q",
        "apps/runtime/tests/test_clinical_conversational_semantics.py",
        "apps/runtime/tests/test_terminology_benchmark.py",
    ]
    test = subprocess.run(test_command, capture_output=True, text=True, check=False)
    if test.returncode != 0:
        raise RuntimeError(f"freeze test suite failed:\n{test.stdout}\n{test.stderr}")
    test_summary = next(
        (line.strip() for line in reversed(test.stdout.splitlines()) if "passed" in line),
        "unknown",
    )
    manifest = {
        "status": "FROZEN_BEFORE_HOLDOUT",
        "freeze_version": "v6-status-only",
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "resolver_version": "repair-v6-status-only",
        "semantic_policy": "SEM-STATUS-001",
        "semantic_policy_version": "1.2",
        "resolver_rule_checksum": {
            str(path): _sha256(path)
            for path in RESOLVER_FILES
        },
        "policy_checksum": _sha256(POLICY),
        "v6_corpus_path": str(CONTEXT_VALIDATION_V6_PATH),
        "v6_corpus_sha256": _sha256(CONTEXT_VALIDATION_V6_PATH),
        "v6_result_path": str(V6_RESULT),
        "v6_policy_aligned_score": v6["policy_aligned_v6_score"],
        "v6_raw_score": v6["raw_v6_score"],
        "code_revision": {
            "git_head": _git("rev-parse", "HEAD"),
            "worktree_status": "dirty-preserved",
            "resolver_worktree_diff_sha256": _git_diff_sha256(RESOLVER_FILES),
        },
        "test_suite": {
            "command": test_command,
            "result": test_summary,
            "returncode": test.returncode,
        },
        "holdout_source_path": str(HOLDOUT_SOURCE),
        "holdout_source_sha256": _sha256(HOLDOUT_SOURCE),
        "holdout_ids": list(HOLDOUT_IDS),
        "holdout_run_count": 0,
        "freeze_invariants": {
            "resolver_mutable": False,
            "policy_mutable": False,
            "rules_mutable": False,
            "gold_mutable": False,
            "corpus_mutable": False,
            "holdout_reruns_allowed": False,
            "v7": "BLOCKED",
            "shadow": "BLOCKED",
            "production": "BLOCKED",
        },
    }
    OUTPUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(freeze(), ensure_ascii=False, indent=2))
