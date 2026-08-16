"""Experimental adapters; optional providers are imported only on demand."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import hashlib
import time
from typing import Any

from apps.runtime.src.application.clinical.normalization import ClinicalNormalizationLayer
from packages.terminology_sdk import TerminologyConcept, TerminologyQuery, TerminologyResult

from .models import BenchmarkAnnotation, ProviderMetadata


class OptionalProviderUnavailable(RuntimeError):
    """The benchmark provider or its assets are not installed/configured."""


class BenchmarkAdapter:
    metadata: ProviderMetadata
    startup_seconds: float = 0.0

    def annotate(self, text: str, *, language: str = "pt-BR") -> tuple[BenchmarkAnnotation, ...]:
        raise NotImplementedError

    async def lookup(self, query: TerminologyQuery) -> TerminologyResult:
        annotations = self.annotate(query.text or query.code or "")
        concepts = tuple(
            TerminologyConcept(
                system=query.system,
                code=item.concept_id,
                display=item.surface,
            )
            for item in annotations
        )
        return TerminologyResult(query=query, provider=self.metadata.provider, concepts=concepts)


class DeterministicBaselineAdapter(BenchmarkAdapter):
    """Measure the current deterministic Runtime normalization vocabulary."""

    def __init__(self) -> None:
        started = time.perf_counter()
        self._normalizer = ClinicalNormalizationLayer()
        self.metadata = ProviderMetadata(
            provider="deterministic-baseline",
            code_license="Astera project license",
            data_license="project-owned vocabulary; audit pending",
            model_license="not applicable",
            vocabulary="Astera deterministic clinical vocabulary",
            vocabulary_version="clinical-normalization-rules-v2",
            source_uri="local://apps/runtime/src/application/clinical/normalization.py",
            notes="Current production baseline; no external assets.",
        )
        self.startup_seconds = time.perf_counter() - started

    def annotate(self, text: str, *, language: str = "pt-BR") -> tuple[BenchmarkAnnotation, ...]:
        result = self._normalizer.normalize(text, metadata={"provider": self.metadata.provider})
        annotations: list[BenchmarkAnnotation] = []
        for mention in result.mentions:
            start = int(mention.provenance.get("offset_start", 0))
            end = int(mention.provenance.get("offset_end", start + len(mention.original_text)))
            annotations.append(
                BenchmarkAnnotation(
                    surface=mention.original_text,
                    concept_id=mention.concept_id,
                    start=start,
                    end=end,
                    score=mention.confidence,
                    semantic_types=(mention.semantic_type,),
                    negated=mention.negated,
                    certainty=mention.certainty,
                    temporality=mention.temporality,
                    experiencer="patient",
                    provenance={
                        "provider": self.metadata.provider,
                        "source_text": text,
                        "source_segment": mention.segment_id,
                        "concept_id": mention.concept_id,
                    },
                )
            )
        return tuple(annotations)


class QuickUMLSAdapter(BenchmarkAdapter):
    """Adapter for QuickUMLS approximate matching.

    QuickUMLS data is never downloaded by the benchmark. The caller supplies
    a prepared data directory and records its vocabulary/license metadata.
    """

    def __init__(
        self,
        data_path: str | Path,
        *,
        threshold: float = 0.7,
        metadata: ProviderMetadata | None = None,
    ) -> None:
        started = time.perf_counter()
        try:
            from quickumls import QuickUMLS
        except ImportError as error:  # pragma: no cover - optional dependency
            raise OptionalProviderUnavailable(
                "QuickUMLS is not installed; use the benchmark optional requirements"
            ) from error
        path = Path(data_path)
        if not path.exists():
            raise OptionalProviderUnavailable(f"QuickUMLS data directory does not exist: {path}")
        self._matcher = QuickUMLS(str(path), threshold=threshold)
        default_metadata = ProviderMetadata(
            provider="quickumls",
            code_license="MIT",
            data_license="must be recorded per UMLS release/license",
            model_license="not applicable",
            vocabulary="UMLS",
            vocabulary_version="UNSET",
            source_uri="https://github.com/Georgetown-IR-Lab/QuickUMLS",
            model_path=str(path),
            asset_bytes=_asset_bytes(path),
            asset_sha256=_asset_sha256(path),
            notes="Approximate matching; vocabulary is an external asset.",
        )
        self.metadata = _with_asset_metadata(metadata or default_metadata, path)
        self.startup_seconds = time.perf_counter() - started

    def annotate(self, text: str, *, language: str = "pt-BR") -> tuple[BenchmarkAnnotation, ...]:
        raw_matches = self._matcher.match(text, best_match=True, ignore_syntax=False)
        annotations: list[BenchmarkAnnotation] = []
        for candidates in raw_matches:
            candidate = candidates[0] if isinstance(candidates, (list, tuple)) else candidates
            start = int(candidate.get("start", 0))
            end = int(candidate.get("end", start))
            surface = str(candidate.get("ngram") or candidate.get("term") or text[start:end])
            semtypes = candidate.get("semtypes") or candidate.get("semantic_types") or ()
            if isinstance(semtypes, str):
                semtypes = (semtypes,)
            annotations.append(
                BenchmarkAnnotation(
                    surface=surface,
                    concept_id=str(candidate.get("cui") or candidate.get("CUI") or ""),
                    start=start,
                    end=end,
                    score=_float(candidate.get("similarity")),
                    semantic_types=tuple(str(item) for item in semtypes),
                    provenance={
                        "provider": self.metadata.provider,
                        "source_text": text,
                        "vocabulary": self.metadata.vocabulary,
                    },
                )
            )
        return tuple(item for item in annotations if item.concept_id)


class MedCATAdapter(BenchmarkAdapter):
    """Adapter for MedCAT v2 model packs supplied by the benchmark operator."""

    def __init__(self, model_path: str | Path, *, metadata: ProviderMetadata | None = None) -> None:
        started = time.perf_counter()
        try:
            from medcat.cat import CAT
        except ImportError as error:  # pragma: no cover - optional dependency
            raise OptionalProviderUnavailable(
                "MedCAT is not installed; use the benchmark optional requirements"
            ) from error
        path = Path(model_path)
        if not path.exists():
            raise OptionalProviderUnavailable(f"MedCAT model pack does not exist: {path}")
        self._cat = CAT.load_model_pack(str(path))
        default_metadata = ProviderMetadata(
            provider="medcat",
            code_license="Apache-2.0",
            data_license="must be recorded per model/vocabulary release",
            model_license="must be recorded per model pack",
            vocabulary="model-pack-defined",
            vocabulary_version="UNSET",
            source_uri="https://github.com/CogStack/cogstack-nlp",
            model_path=str(path),
            asset_bytes=_asset_bytes(path),
            asset_sha256=_asset_sha256(path),
            notes="NER+L; MetaCAT context fields depend on the selected model pack.",
        )
        self.metadata = _with_asset_metadata(metadata or default_metadata, path)
        self.startup_seconds = time.perf_counter() - started

    def annotate(self, text: str, *, language: str = "pt-BR") -> tuple[BenchmarkAnnotation, ...]:
        entities = self._cat.get_entities(text)
        if not isinstance(entities, dict):
            return ()
        annotations: list[BenchmarkAnnotation] = []
        for entity in entities.values():
            if not isinstance(entity, dict):
                continue
            start = int(entity.get("start", 0))
            end = int(entity.get("end", start))
            meta = entity.get("meta_anns") or {}
            annotations.append(
                BenchmarkAnnotation(
                    surface=str(entity.get("source_value") or text[start:end]),
                    concept_id=str(entity.get("cui") or ""),
                    start=start,
                    end=end,
                    score=_float(entity.get("acc")),
                    semantic_types=tuple(filter(None, (str(entity.get("type", "")), str(entity.get("tui", ""))))),
                    negated=_meta_bool(meta, ("Presence", "presence", "negation")),
                    certainty=_meta_value(meta, ("Presence", "presence", "certainty")),
                    temporality=_meta_value(meta, ("Tense", "tense", "temporality")),
                    experiencer=_meta_value(meta, ("Experiencer", "experiencer")),
                    provenance={
                        "provider": self.metadata.provider,
                        "source_text": text,
                        "model_path": self.metadata.model_path,
                    },
                )
            )
        return tuple(item for item in annotations if item.concept_id)


def _asset_bytes(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _asset_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    paths = [path] if path.is_file() else sorted(item for item in path.rglob("*") if item.is_file())
    for item in paths:
        digest.update(str(item.relative_to(path.parent if path.is_dir() else path)).encode())
        with item.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def _with_asset_metadata(metadata: ProviderMetadata, path: Path) -> ProviderMetadata:
    return replace(
        metadata,
        model_path=metadata.model_path or str(path),
        asset_bytes=metadata.asset_bytes if metadata.asset_bytes is not None else _asset_bytes(path),
        asset_sha256=metadata.asset_sha256 or _asset_sha256(path),
    )


def _float(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _meta_value(meta: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = meta.get(key)
        if isinstance(value, dict):
            value = value.get("value") or value.get("name")
        if value is not None:
            return str(value)
    return None


def _meta_bool(meta: dict[str, Any], keys: tuple[str, ...]) -> bool | None:
    value = _meta_value(meta, keys)
    if value is None:
        return None
    return value.casefold() in {"false", "absent", "negated", "no", "0"}
