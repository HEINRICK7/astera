"""Provider-neutral adversarial case generation for the clinical language lab.

This module deliberately stops at candidate generation.  It never creates a
``GoldMention`` and never writes to an official corpus.  A future LLM-backed
generator can implement :class:`ClinicalLanguageGenerator` without changing
the review or harness boundaries.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, Sequence

from .corpus import load_corpus, mention_span
from .error_taxonomy import ERROR_TYPES
from .models import BenchmarkCase, ConversationSegment, GoldMention


@dataclass(frozen=True, slots=True)
class FailureSeed:
    """A historical signal used to guide generation, not a gold annotation."""

    source_corpus: str
    source_case_id: str
    error_types: tuple[str, ...]
    source_text: str
    history_status: str = "historical-signal"


@dataclass(frozen=True, slots=True)
class CandidateCase:
    """Unreviewed candidate.  ``gold`` is intentionally always absent."""

    candidate_id: str
    text: str
    language: str
    source_case_ids: tuple[str, ...]
    source_error_types: tuple[str, ...]
    generator: str
    review_status: str = "PENDING_REVIEW"
    gold: None = None
    provenance: dict[str, object] = field(default_factory=dict)
    segments: tuple[ConversationSegment, ...] = ()

    def to_dict(self) -> dict[str, object]:
        payload = {
            "candidate_id": self.candidate_id,
            "text": self.text,
            "language": self.language,
            "source_case_ids": list(self.source_case_ids),
            "source_error_types": list(self.source_error_types),
            "generator": self.generator,
            "review_status": self.review_status,
            "gold": self.gold,
            "provenance": dict(self.provenance),
        }
        if self.segments:
            payload["segments"] = [
                {"segment_id": segment.segment_id, "speaker": segment.speaker, "text": segment.text}
                for segment in self.segments
            ]
        return payload


@dataclass(frozen=True, slots=True)
class ReviewedCandidate:
    """Human-reviewed candidate kept outside official corpora."""

    candidate_id: str
    text: str
    language: str
    gold: tuple[GoldMention, ...]
    reviewer: str
    review_status: str = "APPROVED_FOR_CORPUS"
    review_notes: str = ""


class ClinicalLanguageGenerator(Protocol):
    provider: str

    def generate(self, seed: FailureSeed, ordinal: int) -> str:
        """Return one new candidate sentence for a historical failure signal."""


class DeterministicClinicalLanguageGenerator:
    """Auditable fallback generator used until an optional model is reviewed."""

    provider = "deterministic-clinical-language-simulator"

    _TEMPLATES: dict[str, tuple[str, ...]] = {
        "MULTI_MENTION_COLLISION": (
            "Nega dor no joelho esquerdo, mas passou a relatar formigamento na mão direita.",
            "Refere queimação no pé direito e dormência nova na perna esquerda ao caminhar.",
            "Sem dor no ombro direito, porém percebe fraqueza na perna esquerda ao subir escadas.",
            "A queimação ficou no pé esquerdo e a dormência apareceu na mão direita.",
            "Nega enjoo, mas relata cólica no lado esquerdo e tontura ao levantar.",
            "Não sente pressão no peito; refere dor no braço direito desde ontem.",
            "A dor abdominal ficou à direita e a sensibilidade surgiu no flanco esquerdo.",
            "Sem ardor ao urinar, mas com urgência urinária e dor lombar à esquerda.",
        ),
        "DOSE_ATTACHMENT": (
            "Tomava losartana 25 mg pela manhã e passou para 50 mg depois do jantar.",
            "Usava metformina 500 mg no almoço e agora toma 850 mg no jantar.",
            "Ficou com atenolol 25 mg de manhã e aumentou para 50 mg à noite.",
            "A dose de sertralina era 50 mg antes de dormir e virou 75 mg pela manhã.",
            "Tomava ibuprofeno 200 mg se dor e passou a usar 400 mg a cada oito horas.",
            "Reduziu a prednisona de 20 mg para 10 mg depois do café.",
            "Usava amlodipino 5 mg à noite e mudou para 10 mg pela manhã.",
            "A levotiroxina passou de 75 mcg em jejum para 88 mcg antes do café.",
        ),
        "TEMPORAL_SCOPE": (
            "Teve dor antiga no ombro, mas hoje relata dormência no braço direito.",
            "A cirurgia foi há anos; atualmente sente peso na perna esquerda.",
            "Já tratou uma pneumonia na infância e agora apresenta tosse seca.",
            "A queda aconteceu no mês passado, mas a dor no quadril começou hoje.",
            "História de enxaqueca antiga; neste momento refere visão borrada.",
            "Teve febre ontem, porém está sem febre e com calafrios agora.",
            "A lesão no tornozelo foi tratada no passado; hoje há inchaço no pé.",
            "Relata bronquite na infância e chiado recorrente nesta semana.",
        ),
        "NEGATION_SCOPE": (
            "Nega dor no peito, porém refere falta de ar ao esforço.",
            "Sem febre hoje, mas começou tosse seca durante a noite.",
            "Não relata vômitos, mas mantém náusea desde cedo.",
            "Nega formigamento na mão, embora tenha fraqueza no braço.",
            "Sem sangramento, mas refere cólica forte no abdome.",
            "Diz que não tem tontura e que sente apenas desequilíbrio ao andar.",
            "Não sente azia, embora apresente dor epigástrica depois das refeições.",
            "Nega febre e calafrios, mas começou a sentir mal-estar hoje.",
        ),
        "FAMILY_EXPERIENCER_SCOPE": (
            "A mãe teve diabetes, mas o paciente nega sintomas atuais.",
            "O irmão relata asma antiga e a paciente não refere chiado.",
            "O pai conviveu com hipertensão, enquanto a paciente nega pressão alta.",
            "A avó sofreu um AVC, mas o paciente não apresenta fraqueza hoje.",
            "A irmã teve alergia a penicilina; o paciente não relata reação ao antibiótico.",
            "A filha conta que a mãe teve câncer, sem que o paciente tenha esse diagnóstico.",
            "O avô teve insuficiência cardíaca, enquanto a paciente não refere inchaço.",
            "A tia apresentou epilepsia, mas o paciente nega crises convulsivas.",
        ),
        "LATERALITY_ATTACHMENT": (
            "A dor permanece no joelho esquerdo e a fraqueza surgiu na mão direita.",
            "Queixa de formigamento no braço direito e dor nova no pé esquerdo.",
            "A pressão incomoda o ouvido esquerdo, enquanto o zumbido aparece no direito.",
            "Refere rigidez no quadril direito e sensibilidade na panturrilha esquerda.",
            "O inchaço está no tornozelo esquerdo e a coceira na mão direita.",
            "Sente peso na perna direita, mas a queimação fica no pé esquerdo.",
            "A dormência ocupa o lado direito do rosto e a dor está na perna esquerda.",
            "Refere dor no punho esquerdo e tremor na mão direita ao escrever.",
        ),
        "STATUS_CONFLICT": (
            "Suspendeu o remédio há uma semana e voltou a usá-lo ontem.",
            "Parou a medicação no mês passado, mas retomou a dose habitual hoje.",
            "Interrompeu o comprimido por três dias e reiniciou ao perceber a pressão alta.",
            "Deixou de tomar o remédio durante a viagem, mas recomeçou na segunda-feira.",
            "A medicação foi suspensa no inverno e voltou a ser usada nesta semana.",
            "Parou o tratamento por conta própria e depois retomou conforme orientação.",
            "Suspendeu as gotas por alguns dias e reiniciou o uso ontem à noite.",
            "Interrompeu a terapia no feriado e retomou o esquema habitual no retorno.",
        ),
        "ATTRIBUTE_MISBOUND": (
            "Possível pneumonia à direita, sem confirmação, e nega falta de ar.",
            "A hipótese é alergia à dipirona, mas não apresenta urticária.",
            "Talvez seja sinusite, porém não há confirmação e a paciente nega febre.",
            "Suspeita de fratura no punho esquerdo, sem imagem conclusiva até agora.",
            "Pode ser refluxo, mas o paciente não confirma azia neste momento.",
            "Provável crise de asma, embora não relate chiado atualmente.",
            "Talvez seja uma infecção, mas os exames ainda não confirmaram a hipótese.",
            "A hipótese de tendinite é possível, sem confirmação clínica até o momento.",
        ),
    }

    def generate(self, seed: FailureSeed, ordinal: int) -> str:
        options = self._TEMPLATES.get(seed.error_types[0], self._TEMPLATES["ATTRIBUTE_MISBOUND"])
        index = (ordinal + sum(ord(char) for char in seed.source_case_id)) % len(options)
        return options[index]


def load_failure_seeds(
    corpus_paths: Sequence[Path],
    taxonomy_paths: Sequence[Path],
    historical_manifest_path: Path | None = None,
) -> tuple[FailureSeed, ...]:
    """Load current taxonomy signals plus explicitly labelled initial runs."""
    cases_by_corpus: dict[str, tuple[BenchmarkCase, ...]] = {
        path.stem: tuple(load_corpus(path)) for path in corpus_paths
    }
    seeds: list[FailureSeed] = []
    for taxonomy_path in taxonomy_paths:
        payload = json.loads(taxonomy_path.read_text(encoding="utf-8"))
        corpus_name = str(payload.get("corpus", taxonomy_path.stem))
        case_map = {case.case_id: case for case in cases_by_corpus.get(corpus_name, ())}
        report = payload.get("report", {}).get("composition", {})
        for classification in report.get("case_classifications", []):
            error_types = tuple(classification.get("error_types", ()))
            if not error_types:
                continue
            case = case_map.get(classification.get("case_id"))
            if case:
                seeds.append(FailureSeed(corpus_name, case.case_id, error_types, case.text))

    if historical_manifest_path and historical_manifest_path.exists():
        manifest = json.loads(historical_manifest_path.read_text(encoding="utf-8"))
        for corpus_name, summary in manifest.get("corpora", {}).items():
            cases = cases_by_corpus.get(corpus_name, ())
            if not cases:
                continue
            for ordinal, error_type in enumerate(summary.get("error_types", ())):
                case = cases[ordinal % len(cases)]
                seeds.append(
                    FailureSeed(
                        corpus_name,
                        case.case_id,
                        (error_type,),
                        case.text,
                        history_status="initial-run-summary",
                    )
                )
    return tuple(seeds)


class ClinicalLanguageSimulator:
    """Generate disjoint candidates without mutating the official corpora."""

    def __init__(self, generator: ClinicalLanguageGenerator | None = None) -> None:
        self._generator = generator or DeterministicClinicalLanguageGenerator()

    def generate(
        self,
        seeds: Sequence[FailureSeed],
        official_cases: Sequence[BenchmarkCase],
        *,
        per_error_type: int = 1,
        limit: int | None = None,
        excluded_texts: Sequence[str] = (),
        candidate_id_start: int = 1,
    ) -> tuple[CandidateCase, ...]:
        official_texts = {case.text for case in official_cases}
        candidates: list[CandidateCase] = []
        seen_texts = set(official_texts) | set(excluded_texts)
        seen_signatures: set[str] = set()
        ordered_seeds = sorted(seeds, key=lambda seed: (seed.error_types, seed.source_case_id))
        for seed in ordered_seeds:
            for ordinal in range(per_error_type):
                text = self._generator.generate(seed, ordinal)
                signature = hashlib.sha256(text.encode("utf-8")).hexdigest()
                if text in seen_texts or signature in seen_signatures:
                    continue
                seen_texts.add(text)
                seen_signatures.add(signature)
                candidate_id = f"sim-v6-{candidate_id_start + len(candidates):04d}"
                candidates.append(
                    CandidateCase(
                        candidate_id=candidate_id,
                        text=text,
                        language="pt-BR",
                        source_case_ids=(seed.source_case_id,),
                        source_error_types=seed.error_types,
                        generator=self._generator.provider,
                        provenance={
                            "source_corpus": seed.source_corpus,
                            "history_status": seed.history_status,
                            "source_text_sha256": hashlib.sha256(seed.source_text.encode("utf-8")).hexdigest(),
                            "candidate_text_sha256": signature,
                            "official_corpus_mutation": False,
                        },
                    )
                )
                if limit is not None and len(candidates) >= limit:
                    return tuple(candidates)
        return tuple(candidates)


def approve_candidate(
    candidate: CandidateCase,
    gold: Sequence[GoldMention],
    *,
    reviewer: str,
    notes: str = "",
) -> ReviewedCandidate:
    """Require a named human reviewer before a candidate can become gold."""
    if candidate.review_status != "PENDING_REVIEW":
        raise ValueError("only pending candidates can be approved")
    if not reviewer.strip():
        raise ValueError("reviewer is required")
    if not gold:
        raise ValueError("approved candidates require at least one gold mention")
    for item in gold:
        if not item.segment_ids:
            raise ValueError(f"gold segment ownership is required for {item.surface}")
        if "concept" not in item.attribute_provenance:
            raise ValueError(f"gold concept provenance is required for {item.surface}")
    return ReviewedCandidate(
        candidate_id=candidate.candidate_id,
        text=candidate.text,
        language=candidate.language,
        gold=tuple(gold),
        reviewer=reviewer.strip(),
        review_notes=notes,
    )


def reviewed_candidate_to_case(
    candidate: CandidateCase,
    gold: Sequence[GoldMention],
    *,
    reviewer: str,
    notes: str = "",
    segment_id: str | None = None,
) -> BenchmarkCase:
    """Materialize one approved candidate as a provenance-complete case.

    This is deliberately an explicit human-review operation.  It is not used
    by candidate generation and it never writes to the official V6 corpus.
    """
    reviewed = approve_candidate(candidate, gold, reviewer=reviewer, notes=notes)
    candidate_segment_ids = {segment.segment_id for segment in candidate.segments}
    source_segment_id = segment_id or (
        next(iter(candidate_segment_ids)) if len(candidate_segment_ids) == 1 else None
    )
    normalized_gold: list[GoldMention] = []
    for item in reviewed.gold:
        if candidate.segments:
            if not item.segment_ids or not set(item.segment_ids).issubset(candidate_segment_ids):
                raise ValueError(f"gold segment ownership is invalid for {candidate.candidate_id}")
        else:
            source_segment_id = source_segment_id or f"{candidate.candidate_id}:segment-01"
            if tuple(item.segment_ids) != (source_segment_id,):
                raise ValueError(f"gold segment ownership must use {source_segment_id}")
        if "concept" not in item.attribute_provenance:
            raise ValueError(f"gold concept provenance is required for {item.surface}")
        valid_sources = candidate_segment_ids or {source_segment_id}
        if not set(item.attribute_provenance["concept"]).issubset(valid_sources):
            raise ValueError(f"gold concept provenance is invalid for {candidate.candidate_id}")
        if any(not sources or not set(sources).issubset(valid_sources) for sources in item.attribute_provenance.values()):
            raise ValueError(f"gold attribute provenance is invalid for {candidate.candidate_id}")
        if any(not sources or not set(sources).issubset(valid_sources) for sources in item.relation_provenance.values()):
            raise ValueError(f"gold relation provenance is invalid for {candidate.candidate_id}")
        mention_span(candidate.text, item.surface, item.occurrence)
        normalized_gold.append(item)
    return BenchmarkCase(
        case_id=candidate.candidate_id,
        text=candidate.text,
        language=candidate.language,
        source="simulator-approved",
        gold=tuple(normalized_gold),
        segments=candidate.segments or (ConversationSegment(source_segment_id, "unknown", candidate.text),),
    )


def write_candidates(path: Path, candidates: Sequence[CandidateCase]) -> None:
    """Write review candidates only; this is not an official corpus writer."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(candidate.to_dict(), ensure_ascii=False) + "\n" for candidate in candidates),
        encoding="utf-8",
    )


def default_error_types() -> tuple[str, ...]:
    """Expose the taxonomy vocabulary to future provider adapters."""
    return ERROR_TYPES
