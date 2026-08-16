"""Freeze the post-holdout repair before consuming new holdout-v2 cases."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
OLD_FREEZE = RESULTS / "v6-repair-v6-freeze-2026-08-15.json"
INTERNAL_GATE = RESULTS / "post-holdout-generalization-repair-internal-gate-2026-08-15.json"
HOLDOUT_SOURCE = ROOT / "data/post_holdout_generalization_holdout_v2.json"
OUTPUT = RESULTS / "post-holdout-generalization-repair-freeze-2026-08-15.json"
CODE_FILES = (
    ROOT / "cross_segment_context.py",
    ROOT / "clinical_conversational_semantics.py",
    ROOT / "context_safety.py",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _code_sha256() -> str:
    digest = hashlib.sha256()
    for path in CODE_FILES:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"repair freeze already exists: {OUTPUT}")
    old_freeze = json.loads(OLD_FREEZE.read_text(encoding="utf-8"))
    gate = json.loads(INTERNAL_GATE.read_text(encoding="utf-8"))
    if gate.get("status") != "PASS":
        raise RuntimeError("internal post-holdout repair gate did not pass")
    if any(case_id in HOLDOUT_SOURCE.read_text(encoding="utf-8") for case_id in ("sim-v6-0056", "sim-v6-0057", "sim-v6-0058")):
        raise RuntimeError("new holdout-v2 source contains a consumed holdout id")
    try:
        git_revision = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        git_revision = "unavailable"
    report = {
        "status": "FROZEN_BEFORE_POST_HOLDOUT_V2",
        "freeze_version": "post-holdout-generalization-repair",
        "resolver_version": "post-holdout-generalization-repair",
        "semantic_policy_version": "1.2",
        "policy_checksum": old_freeze["policy_checksum"],
        "v6_corpus_checksum": old_freeze["v6_corpus_sha256"],
        "repair_code_checksum": _code_sha256(),
        "repair_code_files": [str(path.relative_to(ROOT)) for path in CODE_FILES],
        "internal_gate": str(INTERNAL_GATE),
        "internal_gate_status": gate["status"],
        "new_holdout_source": str(HOLDOUT_SOURCE),
        "new_holdout_source_sha256": _sha256(HOLDOUT_SOURCE),
        "old_holdouts": {
            "ids": ["sim-v6-0056", "sim-v6-0057", "sim-v6-0058"],
            "consumed": True,
            "rerun": False,
            "used_for_approval": False,
        },
        "v6_corpus_frozen": True,
        "gold_changed": False,
        "policy_changed": False,
        "holdout_v2_run_count": 0,
        "git_revision": git_revision,
        "worktree_dirty_preserved": True,
        "v7": "BLOCKED",
        "shadow_integration": "BLOCKED",
        "production": "BLOCKED",
    }
    OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
