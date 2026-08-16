"""Execute the single first blind run against the frozen V6 corpus."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .context_safety import NieDEPtBrSafetyRules
from .corpus import CONTEXT_VALIDATION_V6_PATH, load_corpus
from .v6_harness import evaluate_v6
from .v6_corpus import validate_v6_draft


ROOT = Path(__file__).parent
DEFAULT_MANIFEST = ROOT / "results" / "v6-official-freeze-manifest-2026-08-15.json"
DEFAULT_OUTPUT = ROOT / "results" / "context-validation-v6-blind-2026-08-15.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*, corpus_path: Path, manifest_path: Path, output_path: Path) -> dict[str, object]:
    if output_path.exists():
        raise RuntimeError(f"first blind run already recorded; refusing a second run: {output_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "frozen":
        raise RuntimeError("official V6 manifest is not frozen")
    expected_checksum = manifest.get("official_corpus_sha256")
    actual_checksum = _sha256(corpus_path)
    if actual_checksum != expected_checksum:
        raise RuntimeError("official V6 corpus checksum does not match the freeze manifest")

    cases = load_corpus(corpus_path)
    if len(cases) != 150:
        raise RuntimeError(f"frozen V6 corpus must contain 150 cases, got {len(cases)}")
    draft_validation = validate_v6_draft(cases)
    report = asyncio.run(evaluate_v6(NieDEPtBrSafetyRules(), cases))
    result = {
        "status": "executed",
        "run_type": "first-blind-run",
        "run_count": 1,
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "corpus": corpus_path.stem,
        "official_corpus": True,
        "official_corpus_path": str(corpus_path),
        "official_corpus_sha256": actual_checksum,
        "manifest_path": str(manifest_path),
        "production_promotion": False,
        "shadow_integration": False,
        "repair_applied": False,
        "corpus_validation": draft_validation,
        "report": report,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=CONTEXT_VALIDATION_V6_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(corpus_path=args.corpus, manifest_path=args.manifest, output_path=args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
