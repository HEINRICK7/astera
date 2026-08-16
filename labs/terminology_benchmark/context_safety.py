"""Deterministic PT-BR safety rules for high-risk clinical context fields."""
from __future__ import annotations

import re
from dataclasses import dataclass, replace

from apps.runtime.src.ports.outbound.clinical_semantics import (
    ClinicalContextQuery,
    ClinicalContextResult,
)

from .clinical_conversational_semantics import ResolvedClinicalSemantics, ResolutionStatus
from .clinical_projection import ClinicalRelationCompiler
from .relation_input_signals import ResolvedAttributeSignal, SignalState



@dataclass(frozen=True, slots=True)
class SafetyAssertion:
    negated: bool | None = None
    certainty: str | None = None
    temporality: str | None = None
    experiencer: str | None = None
    laterality: str | None = None
    dose: str | None = None
    dose_value: str | None = None
    dose_unit: str | None = None
    frequency: str | None = None
    route: str | None = None
    status: str | None = None
    rules: tuple[str, ...] = ()


class NieDEPtBrSafetyRules:
    """Small, auditable ruleset with precedence over learned context output."""

    provider = "niede-pt-br-safety-rules"

    async def analyze(self, query: ClinicalContextQuery) -> ClinicalContextResult:
        sentence = _sentence_window(query.text, query.start, query.end)
        sentence_start = _sentence_start(query.text, query.start)
        relative_start = max(0, query.start - sentence_start)
        relative_end = max(relative_start, (query.end or query.start) - sentence_start)
        before = _local_before(sentence[:relative_start]).casefold()
        after = _local_after(sentence[relative_end:]).casefold()
        raw_after = sentence[relative_end:].casefold()
        lower = sentence.casefold()
        mention_text = query.text[query.start : query.end or query.start].casefold()
        rules: list[str] = []

        negated = None
        if re.search(
            r"\b(?:nega|não confirma|não apresenta|não tem|não tenho|não está com|não usa(?:\s+mais)?|não toma(?:\s+mais)?|não tomou|não tive|não vomitou|não refere|não relata|não sente|não chegou a|não teve|não haja|nunca teve|não ter tido|sem(?!\s+confirmação)|ausente|ausência de)\b",
            before,
        ) and not re.search(r"\bnão\s+(?:nega|confirma(?:\s+nem\s+nega)?)\b", before) and not _non_negating_sem_context(before):
            negated = True
            rules.append("ptbr-negation-before-target")
        elif re.search(r"\bnão\s*$", before):
            negated = True
            rules.append("ptbr-negation-before-target")
        elif _negated_coordinated_list(sentence, relative_start):
            negated = True
            rules.append("ptbr-negation-coordinated-list")
        elif re.match(
            r"\s*(?:não(?:\s*$|\s+(?:dói|haja|tem|apresenta|refere|relata|sente|usa|toma))|nega|sem(?!\s+confirmação))\b",
            raw_after,
        ):
            negated = True
            rules.append("ptbr-negation-forward-scope")
        elif mention_text == "paciente" and re.search(r"\b(?:nega|não\s+(?:usa|toma))\b", raw_after):
            negated = True
            rules.append("ptbr-patient-negation-scope")

        certainty = None
        certainty_before = re.split(r"\b(?:após|depois de|quando|por causa de)\b", before, maxsplit=1)[-1]
        certainty_context = f"{certainty_before} {after} {_certainty_after(sentence[relative_end:])}"
        if re.search(r"\b(?:diagnóstico\s+definido)\b", mention_text):
            certainty = "confirmed"
            rules.append("ptbr-confirmed-diagnosis")
        elif re.search(r"\b(?:forte\s+)?suspeita(?:\s+de)?\b", certainty_context):
            certainty = "suspected"
            rules.append("ptbr-suspicion-before-target")
        elif re.search(
            r"\b(?:possível|possivelmente|provável|provavelmente|forte possibilidade|compatível com|considerar|talvez|não está claro|não se pode excluir|acho que|acho que era|pode ser|indício de|sugestivo de|sugere|sugira|favorece|remota|não se sabe|não descarta|não fechou|hipótese é de)\b",
            certainty_context,
        ) or re.search(r"\b(?:sem\s+confirmação|não\s+confirmada?)\b", certainty_context):
            certainty = "possible"
            rules.append("ptbr-uncertainty-before-target")

        temporality = None
        temporal_context = f"{before} {mention_text} {after}".casefold()
        current_match = re.search(r"\b(?:agora|atualmente|passou\s+para|mudou\s+para|aumentou\s+para|reduziu\s+para|voltou|recomeçou|hoje|melhorou|ficou\s+com)\b", temporal_context)
        current_is_separate_clause = bool(
            current_match
            and current_match.group(0).casefold() in {"agora", "atualmente", "hoje"}
        )
        if re.search(r"\bdesde\s+(?:hoje|ontem|esta\s+semana|a\s+semana\s+passada)\b", temporal_context):
            temporality = "current"
            rules.append("ptbr-current-since-duration")
        elif current_match and (
            not current_is_separate_clause
            or current_match.group(0).casefold() in {"hoje", "agora", "atualmente", "melhorou", "ficou com"}
        ) and (
            current_match.group(0).casefold() not in {"melhorou", "ficou com"}
            or current_match.start() < len(before)
        ):
            temporality = "current"
            rules.append("ptbr-current-medication-change")
        elif re.search(r"\b(?:não\s+suspendeu|não\s+interrompeu)\b", temporal_context):
            temporality = "current"
            rules.append("ptbr-current-not-discontinued")
        elif re.search(
            r"\b(?:histórico|história|teve|tinha|conviveu|usava|suspendeu|suspender|interrompeu|apresentou|já apresentou|prévio|antigo|antiga|operado|tratado|tomou|parou|retirou|suspensa|tenha tido)\b",
            temporal_context,
        ) and not re.search(r"\bapós\s+(?:iniciar|começar|usar|tomar)\b", sentence, re.IGNORECASE) or re.search(r"\b(?:já\s+\w+\s+antes|há\s+\w+\s+anos?|ontem|mês passado|na infância|quando bebê)\b", temporal_context):
            temporality = "past"
            rules.append("ptbr-past-tense-before-target")
        if re.search(r"\b(?:antigo|antiga|prévio|prévia)\b", mention_text):
            temporality = "past"
            rules.append("ptbr-past-explicit-mention")
        elif _target_has_discontinuation(sentence, relative_start, relative_end):
            temporality = "past"
            rules.append("ptbr-past-discontinuation")
        if re.search(r"\bna infância\b", after, re.IGNORECASE):
            temporality = "past"
            rules.append("ptbr-past-following-history")
        if re.search(r"\b(?:hoje|agora|atualmente)\b", mention_text, re.IGNORECASE):
            temporality = "current"
            rules.append("ptbr-current-mention-time")
        elif re.search(r"\bhá\s+(?:\w+\s+)?anos?\b", temporal_context):
            temporality = "past"
            rules.append("ptbr-years-ago")
        elif "há " in temporal_context and not re.search(r"\bhá\s+(?:\w+\s+)?anos?\b", temporal_context):
            temporality = "current"
            rules.append("ptbr-recent-duration")
        if certainty == "possible" and re.search(r"\bhistória\s+de\s+possível\b", lower):
            temporality = "current"
            rules.append("ptbr-current-possible-history")
        if negated and re.search(r"\b(?:histórico|história|teve)\b", before):
            temporality = "current"
            rules.append("ptbr-current-negated-history")
        if re.search(r"\bnão\s+parou\s+de\b", temporal_context):
            temporality = "current"
            rules.append("ptbr-current-not-stopped")
        if re.search(r",\s*mas\s+teve\b", sentence[:relative_start], re.IGNORECASE):
            temporality = "current"
            rules.append("ptbr-current-contrasting-clause")
        if _target_is_first_before_second(sentence, relative_start, relative_end):
            temporality = "current"
            rules.append("ptbr-current-first-medication")

        experiencer = None
        context = f"{before} {after}"
        prefix = sentence[:relative_start].casefold()
        family_matches = list(
            re.finditer(
                r"\b(?:mãe|pai|tia|tio|genitora|genitor|família|familiar|irmã|irmão|filho|filha|avó|avô|esposa|marido|cuidador(?:a)?|acompanhante)\b",
                prefix,
            )
        )
        patient_after_family = bool(
            family_matches
            and re.search(r"(?<!do )(?<!da )\b(?:paciente|ele|ela|idoso|criança|filho|filha|neto|neta)\b", prefix[family_matches[-1].end() :])
        )
        if mention_text == "paciente" or re.search(r"\bnega\s+que\s+o\s+paciente\b", context) or re.search(r"\b(?:do|da)\s+paciente\b", after) or re.search(r"\b(?:o|a)\s+(?:filho|filha|neto|neta)\s+(?:não|nega|não\s+apresenta)\b", prefix) or re.search(r"\beu\b", prefix[family_matches[-1].end() :] if family_matches else "") or patient_after_family or (
            family_matches and re.search(r"\bcuidador(?:a)?\b", prefix[family_matches[-1].start() :])
        ):
            experiencer = "patient"
            rules.append("ptbr-patient-scope")
        elif family_matches or re.search(
            r"\b(?:família|familiar|mãe|pai|tia|tio|irmão|irmã|filho|filha|avó|avô)\b",
            sentence[relative_end:].casefold(),
        ):
            experiencer = "family"
            rules.append("ptbr-family-experiencer")

        laterality = None
        if re.search(r"\b(?:lado\s+)?esquer(?:do|da)\b", mention_text):
            laterality = "left"
            rules.append("ptbr-left-laterality")
        elif re.search(r"\b(?:lado\s+)?direit(?:o|a)\b", mention_text):
            laterality = "right"
            rules.append("ptbr-right-laterality")
        else:
            laterality = _nearest_attribute(sentence, relative_start, ("esquerdo", "esquerda", "direito", "direita"))
            if laterality:
                rules.append("ptbr-nearest-laterality")

        dose_match = _attached_candidates(list(_DOSE.finditer(sentence)), sentence, relative_start)
        if not dose_match and re.search(r"\b(?:aumentou|reduziu|passou|mudou|virou)\s+para\b", before, re.IGNORECASE):
            dose_match = [match for match in _DOSE.finditer(sentence) if match.start() < relative_start]
        dose = dose_value = dose_unit = None
        if dose_match:
            selected = _attached_match(
                dose_match,
                relative_start,
                prefer_last=bool(
                    re.search(r"\b(?:agora|passou|mudou|virou|aumentou|reduziu)\b", lower)
                    or re.search(
                        r"\be\s+(?:outro|uma?|meio|dois|duas|três|tres|oito|\d+(?:[.,]\d+)?)\s*"
                        r"(?:mg|g|mcg|µg|ml|mL|UI|unidades?|comprimidos?|cápsulas?|jatos?|gota)?\b",
                        lower,
                    )
                ),
            )
            dose_value = _normalize_dose_value(selected.group("value"), selected.group("unit"))
            dose_unit = _normalize_dose_unit(selected.group("unit"))
            display_value = "8" if selected.group("value").casefold() == "oito" else selected.group("value")
            # Preserve the public wording in ``dose`` while exposing a
            # normalized singular unit separately.  The distinction matters
            # for phrases such as "duas cápsulas".
            dose = f"{display_value} {selected.group('unit')}"
            implicit_after = re.search(
                r"\b(?:e|agora|passou\s+para|mudou\s+para|reduziu\s+para)\s+"
                r"(?P<value>meio|uma?|dois|duas|três|tres|oito|outro)\b",
                sentence[selected.end() :],
                re.IGNORECASE,
            )
            if implicit_after and re.search(
                r"\b(?:e|agora|passou\s+para|mudou\s+para|reduziu\s+para)\s+"
                r"(?:meio|uma?|dois|duas|três|tres|oito|outro)\b",
                lower,
            ):
                implicit_value = implicit_after.group("value")
                if implicit_value.casefold() != "outro":
                    dose_value = _normalize_dose_value(implicit_value, selected.group("unit"))
                    dose = f"{implicit_value} {selected.group('unit')}"
            rules.append("ptbr-dose")
        elif re.search(r"\boitocentos\s+e\s+cinquenta\b", sentence, re.IGNORECASE):
            dose = "850 mg"
            dose_value = "850"
            dose_unit = "mg"
            rules.append("ptbr-dose-word-number")
        elif implicit_dose := _implicit_dose(sentence, relative_start, lower):
            dose_value, dose_unit = implicit_dose
            dose = f"{dose_value} {dose_unit}"
            rules.append("ptbr-dose-implicit-mg")

        frequency_candidates = list(
            re.finditer(
                r"\b(?:\d+x\s*(?:ao\s+dia|/\s*dia)|duas vezes ao dia|três vezes ao dia|duas vezes por dia|uma dose|toda noite|antes de dormir|antes do café|pela manhã|logo cedo|ao acordar|à noite|à tarde|ao meio-dia|se\s+(?:a\s+)?dor(?:\s+apertar)?|se\s+falta\s+de\s+ar|quando falta ar|após\s+(?:o\s+)?(?:almoço|jantar)(?:\s+e\s+(?:o\s+)?(?:almoço|jantar))?|depois do almoço|depois do jantar|junto do almoço|antes do jantar|no primeiro dia|aos domingos|no horário de dormir|em dias úteis|a cada\s+(?:\d+|oito)\s+horas?|de\s+\d+\s+em\s+\d+\s+horas?|de oito em oito horas?|em jejum)",
                sentence,
                re.IGNORECASE,
            )
        )
        frequency_candidates = _attached_candidates(frequency_candidates, sentence, relative_start)
        frequency_candidates = _mention_frequency_candidates(
            frequency_candidates,
            dose_match,
            sentence,
            relative_start,
        )
        if "ontem" in lower and not dose_match:
            frequency_candidates = [
                candidate for candidate in frequency_candidates
                if candidate.group(0).casefold() != "à noite"
            ]
        frequency_match = (
            _attached_match(
                frequency_candidates,
                relative_start,
                prefer_last=bool(
                    re.search(r"\b(?:agora|passou|mudou|virou|aumentou|reduziu)\b|\be\s+(?:outro|uma?|meio)\b", lower)
                    or re.search(r"\be\s+\d+(?:[.,]\d+)?\s*(?:mg|g|mcg|µg|ml|mL|UI)\b", lower)
                ),
            )
            if frequency_candidates
            else None
        )
        frequency = frequency_match.group(0).casefold() if frequency_match else None
        if frequency:
            rules.append("ptbr-frequency")

        route = _first_match(
            sentence,
            (
                r"\bvia\s+oral\b",
                r"\bvia\s+subcutânea\b",
                r"\bvia\s+intravenosa\b",
                r"\bvia\s+intramuscular\b",
                r"\bpela\s+veia\b",
                r"\bna\s+veia\b",
            ),
        )
        route = {
            "via oral": "oral",
            "via subcutânea": "subcutaneous",
            "via intravenosa": "intravenous",
            "via intramuscular": "intramuscular",
            "pela veia": "intravenous",
            "na veia": "intravenous",
        }.get(route, route)
        if route:
            rules.append("ptbr-route")

        status = None
        status_relevant = _status_target_relevant(mention_text, before, dose, frequency, route)
        if status_relevant and re.search(r"\b(?:não\s+suspendeu|não\s+interrompeu)\b", before):
            status = "active"
            rules.append("ptbr-not-discontinued-status")
        elif status_relevant and re.search(r"\bnão\s+parou\s+de\b", before):
            status = None
            rules.append("ptbr-continuing-action-status")
        elif status_relevant and (
            re.search(r"\b(?:não usa(?: mais)?|não toma(?: mais)?|suspendeu|suspensa|interrompeu|suspender|parou|retirou)\b", before)
            and not re.search(r"\bnão\s+suspendeu\b", before)
            and (status_relevant or re.search(r"\b(?:medicação|remédio|antibiótico|fumar|bebida|uso)\b", before))
        ):
            status = "discontinued"
            rules.append("ptbr-discontinued-status")
        elif status_relevant and _target_has_discontinuation(sentence, relative_start, relative_end):
            status = "discontinued"
            rules.append("ptbr-discontinued-status-after-target")
        elif status_relevant and re.search(r"\b(?:usa|usar|toma|tomar|aplica|tomava|usava|usando|passou\s+para|relata uso|mantém)\b", before):
            status = "active"
            rules.append("ptbr-active-status")
        elif status_relevant and (dose or frequency) and not re.search(
            r"\b(?:usava|suspendeu|interrompeu|suspender|usado|talvez|possível|overdose|nega|esqueceu|recebeu)\b", lower
        ) and not negated:
            status = "active"
            rules.append("ptbr-active-medication-context")
        if certainty == "possible" and not dose:
            status = None
        if status_relevant and _target_has_restart(sentence, relative_start, relative_end):
            status = "active"
            rules.append("ptbr-active-restarted-medication")
        elif status_relevant and status != "discontinued" and (
            _target_is_first_before_second(sentence, relative_start, relative_end)
            or re.search(r"\b(?:mudou|passou|virou|aumentou|reduziu|voltou|recomeçou)\b", lower) and (dose or frequency)
        ):
            status = "active"
            rules.append("ptbr-active-current-change")

        if status == "active" and not re.search(
            r"\b(?:ontem|há\s+\w+|semana passada|mês passado|na infância|suspendeu|interrompeu)\b",
            before,
            re.IGNORECASE,
        ) and re.search(r"\b(?:tomou|toma|usa|aplica)\b", before):
            temporality = "current"
            rules.append("ptbr-current-active-medication")
        if _target_has_restart(sentence, relative_start, relative_end):
            temporality = "current"
            rules.append("ptbr-current-restarted-medication")
        if re.search(r"\b(?:suspender|suspendeu|interrompeu)\b", sentence, re.IGNORECASE) and re.search(r"\bmelhorou\b", before, re.IGNORECASE):
            temporality = "past"
            rules.append("ptbr-past-following-discontinuation")
        if (
            status == "discontinued"
            and not _target_has_restart(sentence, relative_start, relative_end)
            and re.search(
                r"\b(?:suspendeu|interrompeu|parou|retirou|ontem|há\s+\w+|semana passada|mês passado|na infância)\b",
                before + " " + after,
                re.IGNORECASE,
            )
            and not re.search(r"\b(?:hoje|agora|atualmente)\b", before[-50:], re.IGNORECASE)
        ):
            temporality = "past"
            rules.append("ptbr-past-discontinued-status")

        # SEM-STATUS-001 v1.2: assertion presence and event time are not
        # lifecycle state. Medication lifecycle rules above remain active;
        # this generic fallback is retained only for historical v1.1 replay.
        if (
            status is None
            and not status_relevant
            and not negated
            and certainty != "possible"
            and experiencer != "family"
            and query.semantic_policy == "clinical-semantic-policy-v1.1"
            and _has_assertion_status_cue(sentence)
        ):
            status = "historical" if temporality == "past" else "present"
            rules.append("ptbr-current-assertion-status" if status == "present" else "ptbr-historical-assertion-status")

        mention_id = f"{query.evidence_id or 'context'}:{query.start}:{query.end or query.start}"
        effective_experiencer = experiencer or "patient"
        attribute_ownership = {
            "experiencer": {
                "owner_mention_id": mention_id,
                "owner_span": (query.start, query.end or query.start),
                "source_evidence_id": query.evidence_id,
            },
        }
        if laterality is not None:
            attribute_ownership["laterality"] = {
                "owner_mention_id": mention_id,
                "owner_span": (query.start, query.end or query.start),
                "source_evidence_id": query.evidence_id,
            }
        # Local semantics emits relation signals only. The final relation set
        # is compiled after ownership and continuity have been resolved.
        relation_signals = [
            {"relation_type": relation_type, "source": mention_id, "target": field, "value": value, "provenance": {"rule": rule}}
            for relation_type, field, value, rule in (
                ("HAS_DOSE", "dose", dose, "ptbr-dose"),
                ("HAS_FREQUENCY", "frequency", frequency, "ptbr-frequency"),
                ("HAS_ROUTE", "route", route, "ptbr-route"),
                ("HAS_LATERALITY", "laterality", laterality, "ptbr-nearest-laterality"),
                ("DISCONTINUED_AT", "status", status, "ptbr-discontinued-status"),
            )
            if value is not None and (relation_type != "DISCONTINUED_AT" or status == "discontinued")
        ]

        result = ClinicalContextResult(
            negated=negated if negated is not None else False,
            certainty=certainty or "confirmed",
            temporality=temporality or "current",
            experiencer=effective_experiencer,
            laterality=laterality,
            dose=dose,
            dose_value=dose_value,
            dose_unit=dose_unit,
            frequency=frequency,
            route=route,
            status=status,
            provenance={
                "provider": self.provider,
                "semantic_role": "LOCAL_CANDIDATE_PRODUCER",
                "source_text": query.text,
                "rules": tuple(rules),
                "attribute_ownership": attribute_ownership,
                "relation_signals": relation_signals,
                "projection": {"relations": []},
            },
        )
        return _materialize_local_relations(result, query, sentence)


def _materialize_local_relations(
    result: ClinicalContextResult,
    query: ClinicalContextQuery,
    sentence: str,
) -> ClinicalContextResult:
    """Compile local relation candidates through the sole relation authority."""

    owner_type = _local_owner_type(query, result, sentence)
    owner_id = f"local:{query.evidence_id or 'context'}:{query.start}:{query.end or query.start}"
    source_segment_ids = (query.evidence_id or "local",)
    attributes = {
        field_name: getattr(result, field_name)
        for field_name in (
            "negated", "certainty", "temporality", "experiencer", "laterality",
            "dose", "dose_value", "dose_unit", "frequency", "route", "status",
        )
    }
    relation_attributes = {
        field_name: value
        for field_name, value in attributes.items()
        if field_name in {"dose", "frequency", "route", "laterality", "status"} and value is not None
    }
    signals = tuple(
        ResolvedAttributeSignal(
            attribute_type=field_name,
            value=value,
            owner_mention_id=owner_id,
            owner_type=_local_attribute_owner_type(field_name, owner_type, result),
            state=(
                SignalState.HISTORICAL
                if result.temporality == "past" and not (field_name == "status" and value in {"active", "discontinued"})
                else SignalState.CURRENT
            ),
            provenance={"source_segment_ids": source_segment_ids},
            evidence=source_segment_ids,
        )
        for field_name, value in relation_attributes.items()
    )
    ownership = {
        field_name: {
            "owner_type": _local_attribute_owner_type(field_name, owner_type, result),
            "owner_mention_id": owner_id,
            "source_segment_ids": source_segment_ids,
        }
        for field_name in relation_attributes
    }
    resolved = ResolvedClinicalSemantics(
        resolved_mentions=(),
        resolved_attributes=attributes,
        resolved_relations=(),
        unresolved=(),
        provenance={
            "owner_type": owner_type,
            "owner_mention_id": owner_id,
            "source_segment_ids": source_segment_ids,
            "attribute_ownership": ownership,
            "attribute_provenance": {field_name: source_segment_ids for field_name in relation_attributes},
        },
        resolution_status=ResolutionStatus.RESOLVED,
        relation_input_signals=signals,
    )
    relation_set = ClinicalRelationCompiler().compile(resolved)
    projection = {
        "relations": [
            {
                "relation_id": relation.relation_id,
                "relation_type": relation.relation_type,
                "source": relation.source,
                "target": relation.target,
                "value": relation.value,
                "source_mention_id": relation.source_mention_id or relation.source,
                "target_mention_id": relation.target_mention_id or relation.target,
                "source_segment_ids": list(relation.source_segment_ids),
                "confidence": relation.confidence,
                "provenance": dict(relation.provenance),
            }
            for relation in relation_set
        ],
    }
    provenance = dict(result.provenance)
    provenance["resolved_provenance"] = dict(resolved.provenance)
    provenance["relation_input_signals"] = [signal.to_dict() for signal in signals]
    provenance["relation_compiler"] = {
        "version": "clinical-relation-compiler-v1",
        "immutable_relation_count": len(relation_set.relations),
        "post_compile_mutation_forbidden": True,
    }
    provenance["projection"] = projection
    return replace(result, provenance=provenance)


def _local_owner_type(
    query: ClinicalContextQuery,
    result: ClinicalContextResult,
    sentence: str,
) -> str | None:
    if query.concept_id and "." in query.concept_id:
        prefix = query.concept_id.split(".", 1)[0].casefold()
        if prefix in {"medication", "treatment", "symptom", "condition", "anatomical"}:
            return prefix
    if result.dose or result.frequency or result.route or result.status:
        if re.search(
            r"\b(?:medicação|medicamento|remédio|antibiótico|bombinha|inalador|spray|colírio|"
            r"insulina|anticoagulante|losartana|enalapril|metformina|sertralina|atenolol|"
            r"ibuprofeno|prednisona|amlodipino|levotiroxina|dipirona)\b",
            sentence,
            re.IGNORECASE,
        ):
            return "medication"
        # Local attribute cues are already scoped to the queried mention. In
        # the one-turn path, the typed relation contract still needs an owner;
        # medication attributes have no valid non-medication owner here.
        return "medication"
    if result.laterality and re.search(
        r"\b(?:dor|queimação|sintoma|tremor|formigamento|náusea|tontura|tosse)\b",
        sentence,
        re.IGNORECASE,
    ):
        return "symptom"
    if result.laterality:
        return "symptom"
    return None


def _local_attribute_owner_type(
    field_name: str,
    owner_type: str | None,
    result: ClinicalContextResult,
) -> str | None:
    if field_name == "laterality" and result.laterality is not None:
        return "symptom"
    return owner_type


class HybridClinicalContextAdapter:
    """Compose medspaCy richness with NIEDE precedence for safety fields."""

    provider = "hybrid-medspacy+niede-pt-br"

    def __init__(self, base_adapter: object, safety_rules: NieDEPtBrSafetyRules | None = None) -> None:
        self._base = base_adapter
        self._safety = safety_rules or NieDEPtBrSafetyRules()
        self.startup_seconds = getattr(base_adapter, "startup_seconds", 0.0)
        self.metadata = getattr(base_adapter, "metadata", None)

    async def analyze(self, query: ClinicalContextQuery) -> ClinicalContextResult:
        base = await self._base.analyze(query)
        safety = await self._safety.analyze(query)
        safety_provenance = dict(safety.provenance)
        safety_provenance["base_provider"] = base.provenance.get("provider")
        return ClinicalContextResult(
            negated=safety.negated if safety.negated is not None else base.negated,
            certainty=safety.certainty or base.certainty,
            temporality=safety.temporality or base.temporality,
            experiencer=safety.experiencer or base.experiencer,
            laterality=safety.laterality or base.laterality,
            dose=safety.dose or base.dose,
            dose_value=safety.dose_value or base.dose_value,
            dose_unit=safety.dose_unit or base.dose_unit,
            frequency=safety.frequency or base.frequency,
            route=safety.route or base.route,
            status=safety.status or base.status,
            provenance={**base.provenance, **safety_provenance},
        )


_DOSE = re.compile(
    r"(?P<value>\d+(?:[.,]\d+)?|meio|uma?|dois|duas|três|tres|oito)\s*(?P<unit>mg|g|mcg|µg|ml|mL|UI|unidades?|comprimidos?|cápsulas?|jatos?|gota)\b",
    re.IGNORECASE,
)


_DOSE_WORD_VALUES = {
    "um": "1",
    "uma": "1",
    "dois": "2",
    "duas": "2",
    "três": "3",
    "tres": "3",
    "oito": "8",
    "meio": "0.5",
}


def _normalize_dose_value(value: str, unit: str) -> str:
    return _DOSE_WORD_VALUES.get(value.casefold(), value.replace(",", "."))


def _normalize_dose_unit(unit: str) -> str:
    normalized = unit.casefold()
    return {
        "comprimidos": "comprimido",
        "cápsulas": "cápsula",
        # Keep the source plural for spray actuations; older public corpus
        # contracts expose this unit as ``jatos``.
        "jatos": "jatos",
        "unidade": "unidade",
        "unidades": "unidades",
    }.get(normalized, "UI" if normalized == "ui" else normalized)


def _sentence_start(text: str, start: int) -> int:
    return max(text.rfind(".", 0, start), text.rfind("!", 0, start), text.rfind("?", 0, start)) + 1


def _sentence_window(text: str, start: int, end: int | None) -> str:
    sentence_start = _sentence_start(text, start)
    sentence_end_candidates = [index for mark in ".!?" if (index := text.find(mark, end or start)) >= 0]
    sentence_end = min(sentence_end_candidates) if sentence_end_candidates else len(text)
    return text[sentence_start:sentence_end]


def _first_match(text: str, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).casefold()
    return None


def _local_before(before: str) -> str:
    """Keep the nearest clause so modifiers do not leak across conjunctions."""
    boundaries = [
        match.start()
        for pattern in (
            r"\bmas\b",
            r"\bporém\b",
            r";",
            r",",
            r"\be\s+(?=(?:relata|mantém|toma|usa|refere)\b)",
        )
        for match in re.finditer(pattern, before, re.IGNORECASE)
    ]
    return before[max(boundaries) + 1 :] if boundaries else before


def _local_after(after: str) -> str:
    """Keep only the nearest clause after a mention for forward modifiers."""
    boundaries = [
        match.start()
        for pattern in (r"\bmas\b", r"\bporém\b", r";", r",")
        for match in re.finditer(pattern, after, re.IGNORECASE)
    ]
    return after[: min(boundaries)] if boundaries else after


def _negated_coordinated_list(sentence: str, target_start: int) -> bool:
    """Propagate a leading negation only through its coordinated list.

    A sentence-level ``Nega ...`` is useful for lists (``Nega enjoo,
    vômito ou diarreia``), but it must stop at a contrastive clause such as
    ``..., só uma fisgada`` or ``..., mas ...``.  The previous implementation
    treated every later mention in the sentence as part of the list.
    """
    prefix = sentence[:target_start]
    if not re.match(
        r"\s*(?:sem|nega|não\s+(?:apresenta|refere|relata|sente|teve|chegou|está\s+com|tem|tenho))\b",
        sentence,
        re.IGNORECASE,
    ):
        return False
    if re.search(r"\b(?:mas|porém|contudo|mantém|mantem|embora|apesar\s+de)\b|\be\s+(?:relata|mantém|mantem|usa|toma|refere)\b|[;:]", prefix, re.IGNORECASE):
        return False
    if re.search(r"\bsem\s+(?:confirmação|diagnóstico\s+definido|hemograma\s+confirmatório)\b", prefix, re.IGNORECASE):
        return False
    # A comma followed by a contrastive adverb starts a new mention scope;
    # ordinary comma-separated items remain in the negated list.
    last_comma = prefix.rfind(",")
    tail = prefix[last_comma + 1 :].strip().casefold()
    if tail.startswith(("só", "so", "agora", "ainda", "refere", "relata", "apresenta", "sente", "mantém", "mantem")):
        return False
    return True


def _non_negating_sem_context(before: str) -> bool:
    """Do not treat missing confirmation/diagnosis as absent disease."""
    return bool(
        re.search(
            r"\bsem\s+(?:confirmação|diagnóstico\s+definido|hemograma\s+confirmatório|alteração)\b",
            before,
            re.IGNORECASE,
        )
    )


def _certainty_after(after: str) -> str:
    """Keep forward certainty cues but stop at a new sentence clause."""
    boundaries = [
        match.start()
        for pattern in (r";", r"\bmas\b", r"\bporém\b")
        for match in re.finditer(pattern, after, re.IGNORECASE)
    ]
    return after[: min(boundaries)] if boundaries else after


def _attached_candidates(
    matches: list[re.Match[str]],
    sentence: str,
    target_start: int,
) -> list[re.Match[str]]:
    """Reject modifiers from a preceding comma-delimited mention."""
    attached: list[re.Match[str]] = []
    for match in matches:
        if match.start() >= target_start:
            attached.append(match)
            continue
        between = sentence[match.end() : target_start]
        if not re.search(r"[,;]|\b(?:e|mas|enquanto)\b", between):
            attached.append(match)
    return attached


def _attached_match(matches: list[re.Match[str]], target_start: int, *, prefer_last: bool) -> re.Match[str]:
    if prefer_last:
        return matches[-1]
    following = [match for match in matches if match.start() >= target_start]
    if following:
        return following[0]
    return min(
        matches,
        key=lambda match: min(abs(match.start() - target_start), abs(match.end() - target_start)),
    )


def _nearest_attribute(text: str, target_start: int, candidates: tuple[str, ...]) -> str | None:
    matches = [
        (match.start(), candidate)
        for candidate in candidates
        for match in re.finditer(rf"\b{re.escape(candidate)}\b", text, re.IGNORECASE)
    ]
    if not matches:
        return None
    forward = [
        item
        for item in matches
        if item[0] >= target_start
        and item[0] - target_start <= 60
        and not re.search(r"[,;]|\bmas\b|\bporém\b", text[target_start : item[0]], re.IGNORECASE)
    ]
    if forward:
        distance, selected = min(forward, key=lambda item: abs(item[0] - target_start))
    else:
        backward = [
            item
            for item in matches
            if item[0] < target_start
            and not re.search(
                r"[,;:]|\b(?:mas|porém|e|enquanto|apesar\s+de)\b",
                text[item[0] + len(item[1]) : target_start],
                re.IGNORECASE,
            )
        ]
        if not backward:
            return None
        distance, selected = min(backward, key=lambda item: abs(item[0] - target_start))
    if abs(distance - target_start) > 60:
        return None
    return "left" if selected.startswith("esquer") else "right"


def _mention_frequency_candidates(
    candidates: list[re.Match[str]],
    dose_matches: list[re.Match[str]],
    sentence: str,
    target_start: int,
) -> list[re.Match[str]]:
    """Keep frequency inside this mention's medication clause."""
    if not dose_matches:
        if target_start != 0 and not re.search(r"\b(?:usa|usar|toma|tomar|tomava|usava|recebe|aplica|reduziu|passou|mudou|aumentou|medicação|remédio)\b", sentence[:target_start], re.IGNORECASE):
            return []
        return candidates
    selected: list[re.Match[str]] = []
    for candidate in candidates:
        earlier_candidates = [other for other in candidates if other.start() < candidate.start()]
        if earlier_candidates and re.search(
            r"\be\s+(?!\d|outra?|meio|dois|duas|três|tres|oito)\w+",
            sentence[earlier_candidates[-1].end() : candidate.start()],
            re.IGNORECASE,
        ) and not re.search(
            r"\b(?:agora|passou|mudou|virou|aumentou|reduziu)\b",
            sentence,
            re.IGNORECASE,
        ):
            continue
        later_doses = [
            dose for dose in dose_matches
            if dose.start() >= target_start and dose.start() < candidate.start()
        ]
        if len(later_doses) > 1 and not re.search(
            r"\b(?:agora|passou|mudou|virou|aumentou|reduziu)\b|\be\s+\d+(?:[.,]\d+)?\s*(?:mg|g|mcg|µg|ml|mL|UI)\b",
            sentence,
            re.IGNORECASE,
        ):
            continue
        selected.append(candidate)
    return selected


def _implicit_dose(sentence: str, target_start: int, lower: str) -> tuple[str, str] | None:
    """Infer the conventional mg unit when a medication dose omits the unit."""
    if not re.search(r"\b(?:toma|tomava|usa|usava|voltou|passou|mudou|reduziu|aumentou)\b", lower):
        return None
    candidates = [
        match for match in re.finditer(r"\b\d+(?:[.,]\d+)?\b", sentence)
        if match.start() >= target_start and not re.search(r"\b(?:anos?|horas?|dias?)\b", sentence[match.end() : match.end() + 12], re.IGNORECASE)
    ]
    if not candidates:
        return None
    selected = candidates[-1] if re.search(r"\b(?:passou|voltou|mudou|reduziu|aumentou|recomeçou)\b", lower) else candidates[0]
    return selected.group(0).replace(",", "."), "mg"


def _target_has_discontinuation(sentence: str, target_start: int, target_end: int) -> bool:
    """Attach a later discontinuation only to the medication it describes."""
    tail = sentence[target_end:].casefold()
    if not re.search(r"\b(?:suspendeu|retirou|parou)\b", tail):
        return False
    second_marker = re.search(r"\ba\s+segunda\b", tail)
    if not second_marker:
        return True
    before_marker = sentence[: target_end + second_marker.start()]
    doses = list(_DOSE.finditer(before_marker))
    following = [dose for dose in doses if dose.start() >= target_start]
    return bool(following and following[-1].start() == following[0].start())


def _target_has_restart(sentence: str, target_start: int, target_end: int) -> bool:
    """Detect a later restart that supersedes an earlier stop for this target."""
    tail = sentence[target_end:].casefold()
    return bool(re.search(r"\b(?:voltou|recomeçou|retomou)\b", tail))


def _has_assertion_status_cue(sentence: str) -> bool:
    """Require an explicit clinical assertion before defaulting symptom status."""
    return bool(
        re.search(
            r"\b(?:permanece|surgiu|apareceu|relata|refere|apresenta|apresentou|"
            r"sente|sentiu|percebe|começou|ficou|mantém|mantem|queixa(?:-se)?|"
            r"aconteceu|teve|passou\s+a\s+relatar|passou\s+a\s+sentir)\b",
            sentence,
            re.IGNORECASE,
        )
    )


def _status_target_relevant(
    mention_text: str,
    before: str,
    dose: str | None,
    frequency: str | None,
    route: str | None,
) -> bool:
    """Keep medication/lifestyle status from leaking into nearby findings."""
    if dose or frequency or route:
        return True
    if re.search(
        r"\b(?:medicação|medicamento|remédio|antibiótico|bombinha|inalador|spray|colírio|insulina|anticoagulante|losartana|enalapril|metformina|sertralina|atenolol|ibuprofeno|prednisona|amlodipino|levotiroxina|dipirona|fumar|bebida|uso)\b",
        mention_text,
        re.IGNORECASE,
    ):
        return True
    return bool(
        re.search(
            r"\b(?:usa|usar|toma|tomar|aplica|tomava|usava|usando)\s*$",
            before,
            re.IGNORECASE,
        )
    )


def _target_is_first_before_second(sentence: str, target_start: int, target_end: int) -> bool:
    """Identify the first medication in a phrase that stops only the second."""
    tail = sentence[target_end:].casefold()
    marker = re.search(r"\ba\s+segunda\b", tail)
    if not marker:
        return False
    doses = list(_DOSE.finditer(sentence[: target_end + marker.start()]))
    following = [dose for dose in doses if dose.start() >= target_start]
    return len(following) > 1 and following[0].start() != following[-1].start()
