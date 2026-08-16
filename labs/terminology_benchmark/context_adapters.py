"""Experimental clinical-context adapters for the separate context track."""
from __future__ import annotations

import time
from pathlib import Path

from apps.runtime.src.application.clinical.normalization import ClinicalNormalizationLayer
from apps.runtime.src.ports.outbound.clinical_semantics import (
    ClinicalContextPort,
    ClinicalContextQuery,
    ClinicalContextResult,
)
from .context_rules import RULES_PATH, asset_sha256, load_context_rules
from .models import ProviderMetadata


class OptionalContextProviderUnavailable(RuntimeError):
    """The optional context provider is not installed or configured."""


class DeterministicContextAdapter:
    """Expose the current PT-BR deterministic rules through ClinicalContextPort."""

    provider = "deterministic-context-baseline"

    def __init__(self) -> None:
        self._normalizer = ClinicalNormalizationLayer()
        self.startup_seconds = 0.0

    async def analyze(self, query: ClinicalContextQuery) -> ClinicalContextResult:
        result = self._normalizer.normalize(
            query.text,
            metadata={
                "provider": self.provider,
                "segment_id": query.evidence_id or "context-benchmark",
            },
        )
        selected = next(
            (
                mention
                for mention in result.mentions
                if int(mention.provenance.get("offset_start", -1)) == query.start
                and (
                    query.end is None
                    or int(mention.provenance.get("offset_end", -1)) == query.end
                )
            ),
            None,
        )
        if selected is None:
            return ClinicalContextResult(
                provenance={"provider": self.provider, "source_text": query.text}
            )
        return ClinicalContextResult(
            negated=selected.negated,
            certainty=selected.certainty,
            temporality=selected.temporality,
            experiencer="patient",
            provenance={
                "provider": self.provider,
                "source_text": query.text,
                "concept_id": selected.concept_id,
            },
        )


class MedSpaCyContextAdapter:
    """Run medspaCy ConText with caller-supplied PT-BR rules/model assets."""

    provider = "medspacy"

    def __init__(
        self,
        *,
        model_name: str | None = None,
        target_terms: tuple[str, ...] = (),
        rules_path: str | Path = RULES_PATH,
    ) -> None:
        started = time.perf_counter()
        try:
            import medspacy
            from medspacy.ner import TargetRule
            from medspacy.context import ConTextRule
        except ImportError as error:  # pragma: no cover - optional dependency
            raise OptionalContextProviderUnavailable(
                "medspaCy is not installed; use the benchmark optional requirements"
            ) from error
        rules_file = Path(rules_path)
        rules = load_context_rules(rules_file)
        self._nlp = medspacy.load(model_name) if model_name else medspacy.load()
        if target_terms:
            matcher = self._nlp.get_pipe("medspacy_target_matcher")
            matcher.add([TargetRule(term, "CLINICAL_CONCEPT") for term in target_terms])
        context = self._nlp.get_pipe("medspacy_context")
        context.add(
            [
                ConTextRule(
                    literal=item["literal"],
                    category=item["category"],
                    direction=item.get("direction", "BIDIRECTIONAL"),
                    max_scope=item.get("max_scope"),
                )
                for item in rules["rules"]
            ]
        )
        self.metadata = ProviderMetadata(
            provider=self.provider,
            code_license="MIT",
            data_license="not applicable",
            model_license=(
                "not applicable (default medspaCy pipeline)"
                if model_name is None
                else "caller-supplied spaCy model; record separately"
            ),
            vocabulary="NIEDE PT-BR context rules",
            vocabulary_version=rules["rule_set"],
            source_uri="local://labs/terminology_benchmark/data/pt_br_context_rules_v1.json",
            model_path=model_name,
            asset_bytes=rules_file.stat().st_size,
            asset_sha256=asset_sha256(rules_file),
            notes="medspaCy ConText plus project-owned PT-BR rules.",
        )
        self.startup_seconds = time.perf_counter() - started

    async def analyze(self, query: ClinicalContextQuery) -> ClinicalContextResult:
        doc = self._nlp(query.text)
        target = next(
            (
                entity
                for entity in doc.ents
                if entity.start_char <= query.start
                and (query.end is None or entity.end_char >= query.end)
            ),
            None,
        )
        if target is None:
            return ClinicalContextResult(
                provenance={"provider": self.provider, "source_text": query.text}
            )
        return ClinicalContextResult(
            negated=bool(_extension(target, "is_negated", False)),
            certainty=_certainty(target),
            temporality="past" if bool(_extension(target, "is_historical", False)) else "current",
            experiencer="family" if bool(_extension(target, "is_family", False)) else "patient",
            provenance={
                "provider": self.provider,
                "source_text": query.text,
                "target": target.text,
            },
        )


def _extension(entity: object, name: str, default: object) -> object:
    extensions = getattr(entity, "_", None)
    value = getattr(extensions, name, default) if extensions is not None else default
    return default if value is None else value


def _certainty(entity: object) -> str:
    if bool(_extension(entity, "is_uncertain", False)):
        return "possible"
    if bool(_extension(entity, "is_hypothetical", False)):
        return "suspected"
    return "confirmed"
