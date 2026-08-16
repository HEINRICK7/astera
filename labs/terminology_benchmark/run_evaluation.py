"""Run all configured experimental providers without touching production."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, Callable

from .asset_registry import load_registry
from .adapters import (
    DeterministicBaselineAdapter,
    MedCATAdapter,
    OptionalProviderUnavailable,
    QuickUMLSAdapter,
)
from .context_adapters import (
    DeterministicContextAdapter,
    MedSpaCyContextAdapter,
    OptionalContextProviderUnavailable,
)
from .context_harness import evaluate as evaluate_context
from .corpus import benchmark_target_terms
from .harness import run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quickumls-path", type=Path)
    parser.add_argument("--medcat-path", type=Path)
    parser.add_argument("--medspacy-model")
    parser.add_argument("--context-rules-path", type=Path)
    parser.add_argument("--run-medspacy", action="store_true")
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    registry = load_registry(args.registry)

    result: dict[str, Any] = {
        "status": "experimental-only",
        "corpus": "pt_br_terminology_v1",
        "production_promotion": False,
        "terminology": {
            "deterministic-baseline": _run_report(lambda: DeterministicBaselineAdapter())
        },
        "clinical_context": {
            "deterministic-context-baseline": _run_async_report(
                lambda: evaluate_context(DeterministicContextAdapter())
            )
        },
    }
    if args.quickumls_path:
        decision = registry.authorize("quickumls", "benchmark")
        result["terminology"]["quickumls"] = (
            _run_report(lambda: QuickUMLSAdapter(args.quickumls_path))
            if decision.allowed
            else _blocked(decision.to_dict())
        )
    else:
        result["terminology"]["quickumls"] = _not_configured(
            "--quickumls-path was not supplied; no vocabulary was downloaded"
        )
    if args.medcat_path:
        decision = registry.authorize("medcat", "benchmark")
        result["terminology"]["medcat"] = (
            _run_report(lambda: MedCATAdapter(args.medcat_path))
            if decision.allowed
            else _blocked(decision.to_dict())
        )
    else:
        result["terminology"]["medcat"] = _not_configured(
            "--medcat-path was not supplied; no model pack was downloaded"
        )
    if args.run_medspacy or args.medspacy_model or args.context_rules_path:
        rules_path = args.context_rules_path or Path(__file__).with_name("data") / "pt_br_context_rules_v1.json"
        decision = registry.authorize("medspacy", "benchmark")
        if decision.allowed and not registry.verify_path("niede-pt-br-context-rules-v1", rules_path):
            decision = decision.__class__(
                provider=decision.provider,
                purpose=decision.purpose,
                allowed=False,
                status="BLOCKED",
                reasons=decision.reasons + ("NIEDE context-rule checksum mismatch",),
                assets=decision.assets,
            )
        result["clinical_context"]["medspacy+niede-pt-br"] = (
            _run_async_report(
                lambda: evaluate_context(
                    MedSpaCyContextAdapter(
                        model_name=args.medspacy_model,
                        rules_path=rules_path,
                        target_terms=benchmark_target_terms(),
                    )
                )
            )
            if decision.allowed
            else _blocked(decision.to_dict())
        )
    else:
        result["clinical_context"]["medspacy+niede-pt-br"] = _not_configured(
            "--medspacy-model or --context-rules-path was not supplied"
        )
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


def _run_report(factory: Callable[[], Any]) -> dict[str, Any]:
    try:
        return {"status": "executed", "report": run(factory()).to_dict()}
    except OptionalProviderUnavailable as error:
        return {"status": "unavailable", "reason": str(error)}
    except Exception as error:  # provider/API mismatch must be visible in the report
        return {"status": "error", "reason": f"{type(error).__name__}: {error}"}


def _run_async_report(factory: Callable[[], Any]) -> dict[str, Any]:
    try:
        return {"status": "executed", "report": asyncio.run(factory())}
    except OptionalContextProviderUnavailable as error:
        return {"status": "unavailable", "reason": str(error)}
    except Exception as error:  # provider/API mismatch must be visible in the report
        return {"status": "error", "reason": f"{type(error).__name__}: {error}"}


def _not_configured(reason: str) -> dict[str, str]:
    return {"status": "not_configured", "reason": reason}


def _blocked(decision: dict[str, Any]) -> dict[str, Any]:
    return {"status": "blocked", "authorization": decision}


if __name__ == "__main__":
    main()
