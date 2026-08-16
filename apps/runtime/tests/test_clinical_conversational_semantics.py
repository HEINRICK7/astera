"""Synthetic engineering tests for clinical conversational semantics."""
from __future__ import annotations

import unittest
import asyncio

from labs.terminology_benchmark.clinical_conversational_semantics import (
    AmbiguityPolicy,
    AttributeEvidence,
    ClinicalAttributeCandidate,
    ClinicalAttributeAttachmentResolver,
    ClinicalReferenceResolver,
    ClinicalRelationResolver,
    ContextLifetimePolicy,
    ContextMention,
    ConversationalSemanticsTrace,
    CrossSegmentContextState,
    AuthorityDecisionMetrics,
    AuthoritativeProjectionWriter,
    ResolvedClinicalSemantics,
    ResolutionStatus,
    QuestionContext,
    SegmentContext,
    ShortAnswerResolver,
)
from labs.terminology_benchmark.context_safety import NieDEPtBrSafetyRules
from labs.terminology_benchmark.cross_segment_context import CrossSegmentContextAdapter
from labs.terminology_benchmark.models import BenchmarkCase, ConversationSegment
from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery


def mention(
    name: str,
    entity_type: str,
    turn: int,
    *,
    speaker: str = "patient",
    experiencer: str = "patient",
    status: str | None = None,
    attributes: tuple[str, ...] = (),
) -> ContextMention:
    return ContextMention(
        mention_id=name,
        concept_id=f"{entity_type}.{name}",
        entity_type=entity_type,
        surface=name,
        speaker=speaker,
        experiencer=experiencer,
        segment_id=f"seg-{turn}",
        turn_index=turn,
        status=status,
        recency=turn,
        attributes={key: True for key in attributes},
        source_segment_ids=(f"seg-{turn}",),
    )


class ClinicalConversationalSemanticsTests(unittest.TestCase):
    def setUp(self) -> None:
        segments = tuple(
            SegmentContext(f"seg-{index}", "clinician" if index == 0 else "patient", index, text)
            for index, text in enumerate(("medication review", "symptom review", "follow-up"))
        )
        self.state = CrossSegmentContextState.derive(
            segments,
            (
                mention("med-a", "medication", 0, attributes=("dose",)),
                mention("med-b", "medication", 1, attributes=("frequency",)),
                mention("pain", "symptom", 1, attributes=("laterality",)),
                mention("mother", "condition", 0, experiencer="family", speaker="clinician"),
            ),
        )

    def test_state_keeps_multiple_entities_by_type(self) -> None:
        self.assertEqual(tuple(item.mention_id for item in self.state.medication_context), ("med-a", "med-b"))
        self.assertEqual(tuple(item.mention_id for item in self.state.symptom_context), ("pain",))
        self.assertEqual(tuple(item.mention_id for item in self.state.condition_context), ("mother",))

    def test_reference_resolution_prefers_compatible_nearest_entity_after_speaker_change(self) -> None:
        result = ClinicalReferenceResolver().resolve(
            state=self.state,
            target_turn_index=2,
            target_speaker="patient",
            entity_type="medication",
            attribute_names=("frequency",),
        )
        self.assertEqual(result.status, ResolutionStatus.RESOLVED)
        self.assertEqual(result.selected.mention_id, "med-b")
        self.assertTrue(result.candidates[0].score > result.candidates[1].score)

    def test_family_experiencer_does_not_become_patient(self) -> None:
        result = ClinicalReferenceResolver().resolve(
            state=self.state,
            target_turn_index=1,
            target_speaker="patient",
            entity_type="condition",
            experiencer="family",
        )
        self.assertEqual(result.status, ResolutionStatus.RESOLVED)
        self.assertEqual(result.selected.mention_id, "mother")

    def test_topic_change_invalidates_old_context_without_explicit_reference(self) -> None:
        result = ClinicalReferenceResolver(
            lifetime_policy=ContextLifetimePolicy(),
        ).resolve(
            state=self.state,
            target_turn_index=2,
            target_speaker="patient",
            entity_type="medication",
            topic_changed=True,
        )
        self.assertEqual(result.status, ResolutionStatus.UNRESOLVED)

    def test_ambiguity_is_preserved_instead_of_forcing_selection(self) -> None:
        ambiguous_state = CrossSegmentContextState.derive(
            self.state.segments,
            (mention("a", "medication", 0), mention("b", "medication", 0)),
        )
        result = ClinicalReferenceResolver(
            ambiguity_policy=AmbiguityPolicy(tie_margin=0.5),
        ).resolve(
            state=ambiguous_state,
            target_turn_index=1,
            target_speaker="patient",
            entity_type="medication",
        )
        self.assertEqual(result.status, ResolutionStatus.AMBIGUOUS)
        self.assertIsNone(result.selected)
        self.assertEqual(len(result.candidates), 2)

    def test_attribute_attachment_has_field_level_provenance_and_owner(self) -> None:
        target = self.state.medication_context[0]
        attachments = ClinicalAttributeAttachmentResolver().attach(
            target=target,
            evidence=(
                AttributeEvidence("dose", "850 mg", ("seg-2",), ("medication",)),
                AttributeEvidence("laterality", "right", ("seg-2",), ("symptom",)),
            ),
        )
        self.assertEqual(attachments[0].status, ResolutionStatus.RESOLVED)
        self.assertEqual(attachments[0].provenance, ("seg-2",))
        self.assertEqual(attachments[1].status, ResolutionStatus.UNRESOLVED)

    def test_relation_resolver_projects_attributes_and_transition(self) -> None:
        target = self.state.medication_context[0]
        attachments = ClinicalAttributeAttachmentResolver().attach(
            target=target,
            evidence=(AttributeEvidence("dose", "850 mg", ("seg-2",), ("medication",)),),
        )
        relations = ClinicalRelationResolver().resolve(
            source=target,
            attachments=attachments,
            changed_from=(AttributeEvidence("dose", "500 mg", ("seg-1",), ("medication",)),),
        )
        self.assertEqual([item.relation_type for item in relations], ["HAS_DOSE", "CHANGED_FROM"])
        self.assertEqual(relations[0].provenance["source_segment_ids"], ("seg-2",))

    def test_trace_is_serializable_without_phrases_or_phi_logging(self) -> None:
        trace = ConversationalSemanticsTrace(
            input_segment="seg-2",
            candidate_mentions=("med-a", "med-b"),
            candidate_scores={"med-a": 0.91, "med-b": 0.34},
            selected_antecedent="med-a",
            ambiguity_status=ResolutionStatus.RESOLVED,
        )
        payload = trace.to_dict()
        self.assertEqual(payload["ambiguity_status"], "RESOLVED")
        self.assertNotIn("source_text", payload)

    def test_small_deterministic_invariant_matrix_preserves_single_attribute_owner(self) -> None:
        attachment_resolver = ClinicalAttributeAttachmentResolver()
        for owner_type in ("medication", "symptom", "condition"):
            owner = mention(f"owner-{owner_type}", owner_type, 0)
            other = mention("other", "medication" if owner_type != "medication" else "symptom", 1)
            evidence = (
                AttributeEvidence("dose", "10 mg", ("seg-1",), ("medication",)),
                AttributeEvidence("laterality", "left", ("seg-1",), ("symptom",)),
                AttributeEvidence("negated", True, ("seg-1",), ("symptom",)),
            )
            owner_attachments = attachment_resolver.attach(target=owner, evidence=evidence)
            other_attachments = attachment_resolver.attach(target=other, evidence=evidence)
            for left, right in zip(owner_attachments, other_attachments):
                self.assertFalse(
                    left.status is ResolutionStatus.RESOLVED
                    and right.status is ResolutionStatus.RESOLVED
                    and left.attribute.name == right.attribute.name
                )

    def test_provenance_points_to_known_segments_and_state_does_not_change_input(self) -> None:
        original_segments = self.state.segments
        result = ClinicalAttributeAttachmentResolver().attach(
            target=self.state.medication_context[0],
            evidence=(AttributeEvidence("dose", "10 mg", ("seg-2",), ("medication",)),),
        )[0]
        known = {segment.segment_id for segment in original_segments}
        self.assertTrue(set(result.provenance).issubset(known))
        self.assertEqual(original_segments, self.state.segments)

    def test_authoritative_writer_prevents_post_resolution_overwrite(self) -> None:
        from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextResult

        local = ClinicalContextResult(
            dose="10 mg",
            dose_value="10",
            dose_unit="mg",
            status="active",
            provenance={"semantic_role": "LOCAL_CANDIDATE_PRODUCER"},
        )
        resolved = ResolvedClinicalSemantics(
            resolved_mentions=(),
            resolved_attributes={
                "negated": False,
                "certainty": "confirmed",
                "temporality": "current",
                "experiencer": "patient",
                "laterality": None,
                "dose": "20 mg",
                "dose_value": "20",
                "dose_unit": "mg",
                "frequency": None,
                "route": None,
                "status": "active",
            },
            resolved_relations=(),
            unresolved=(),
            provenance={"dose": ("seg-2",)},
        )
        metrics = AuthorityDecisionMetrics()
        result = AuthoritativeProjectionWriter(metrics).materialize(
            local_candidate=local,
            resolved=resolved,
        )
        self.assertEqual(result.dose, "20 mg")
        self.assertTrue(result.provenance["authoritative_resolution"])
        self.assertEqual(metrics.resolver_decisions_overwritten, 2)
        self.assertEqual(metrics.legacy_fallback_count, 0)

    def test_all_resolved_attributes_and_relation_survive_projection(self) -> None:
        from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextResult
        from labs.terminology_benchmark.clinical_projection import ClinicalRelation

        local = ClinicalContextResult(provenance={"semantic_role": "LOCAL_CANDIDATE_PRODUCER"})
        relation = ClinicalRelation(
            relation_type="HAS_DOSE",
            source="med-a",
            target="dose",
            value="850 mg",
            provenance={"source_segment_ids": ("answer-1",)},
            relation_id="med-a:HAS_DOSE:dose",
            source_mention_id="med-a",
            target_mention_id="med-a",
            source_segment_ids=("answer-1",),
        )
        resolved_values = {
            "negated": True,
            "certainty": "probable",
            "temporality": "past",
            "experiencer": "family",
            "laterality": "left",
            "dose": "850 mg",
            "dose_value": "850",
            "dose_unit": "mg",
            "frequency": "à noite",
            "route": "oral",
            "status": "discontinued",
        }
        result = AuthoritativeProjectionWriter().materialize(
            local_candidate=local,
            resolved=ResolvedClinicalSemantics(
                resolved_mentions=(),
                resolved_attributes=resolved_values,
                resolved_relations=(relation,),
                unresolved=(),
                provenance={"source_segment_ids": ("answer-1",)},
            ),
        )
        for field, expected in resolved_values.items():
            self.assertEqual(getattr(result, field), expected, field)
        self.assertEqual(
            result.provenance["projection"]["relations"][0]["relation_type"],
            "HAS_DOSE",
        )
        self.assertEqual(
            result.provenance["projection"]["relations"][0]["source_segment_ids"],
            ["answer-1"],
        )

    def test_unresolved_and_ambiguous_are_materialized_without_forcing_resolution(self) -> None:
        from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextResult

        local = ClinicalContextResult(provenance={"semantic_role": "LOCAL_CANDIDATE_PRODUCER"})
        for status in (ResolutionStatus.UNRESOLVED, ResolutionStatus.AMBIGUOUS):
            result = AuthoritativeProjectionWriter().materialize(
                local_candidate=local,
                resolved=ResolvedClinicalSemantics(
                    resolved_mentions=(),
                    resolved_attributes={field: getattr(local, field) for field in (
                        "negated", "certainty", "temporality", "experiencer", "laterality",
                        "dose", "dose_value", "dose_unit", "frequency", "route", "status",
                    )},
                    resolved_relations=(),
                    unresolved=("medication",),
                    provenance={},
                    resolution_status=status,
                ),
            )
            self.assertEqual(result.provenance["resolution_status"], status.value)
            self.assertFalse(result.provenance.get("ambiguous_forced_resolution", False))

    def test_cross_segment_facade_returns_only_projection_writer_output(self) -> None:
        case = BenchmarkCase(
            case_id="engineering-authority-case",
            text="Ainda usa losartana?\nParei na semana passada.",
            language="pt-BR",
            gold=(),
            segments=(
                ConversationSegment("authority-1", "clinician", "Ainda usa losartana?"),
                ConversationSegment("authority-2", "patient", "Parei na semana passada."),
            ),
        )
        adapter = CrossSegmentContextAdapter(NieDEPtBrSafetyRules(), (case,))
        result = asyncio.run(adapter.analyze(ClinicalContextQuery(
            text=case.text,
            start=11,
            end=20,
            evidence_id=case.case_id,
        )))
        self.assertEqual(result.provenance["semantic_role"], "PROJECTION_WRITER")
        self.assertTrue(result.provenance["authoritative_resolution"])
        self.assertEqual(adapter.authority_metrics()["legacy_fallback_count"], 0)

    def test_short_answers_require_question_context_and_keep_origin(self) -> None:
        question = QuestionContext.from_segment(
            SegmentContext("q", "clinician", 0, "Qual a dose do remédio?")
        )
        candidates = ShortAnswerResolver.resolve(
            "850 mg",
            question=question,
            segment_id="a",
            owner_ids=("med-a",),
        )
        self.assertEqual({item.name for item in candidates}, {"dose", "dose_value", "dose_unit"})
        self.assertEqual(candidates[0].candidate_owner_ids, ("med-a",))
        self.assertEqual(candidates[0].originating_rule, "short-answer:dose")
        self.assertEqual(ShortAnswerResolver.resolve("850 mg", question=None, segment_id="a"), ())

    def test_short_answer_status_laterality_and_experiencer_are_typed(self) -> None:
        status_question = QuestionContext.from_segment(
            SegmentContext("q1", "clinician", 0, "Ainda usa o tratamento?")
        )
        lateral_question = QuestionContext.from_segment(
            SegmentContext("q2", "clinician", 1, "Qual lado dói?")
        )
        person_question = QuestionContext.from_segment(
            SegmentContext("q3", "clinician", 2, "Quem teve esse diagnóstico?")
        )
        self.assertEqual(
            {item.name for item in ShortAnswerResolver.resolve("Parei", question=status_question, segment_id="a")},
            {"status", "temporality"},
        )
        lateral = ShortAnswerResolver.resolve("Do lado esquerdo", question=lateral_question, segment_id="a")
        self.assertEqual(lateral[0].value, "left")
        person = ShortAnswerResolver.resolve("Minha irmã", question=person_question, segment_id="a")
        self.assertEqual(person[0].name, "experiencer")

    def test_typed_attribute_candidate_cannot_cross_owner_type_or_explicit_owner(self) -> None:
        target = self.state.symptom_context[0]
        candidate = ClinicalAttributeCandidate(
            name="dose",
            value="850 mg",
            source_segment_ids=("seg-2",),
            candidate_owner_ids=("med-a",),
            candidate_id="answer:dose",
            originating_rule="test",
        )
        attachment = ClinicalAttributeAttachmentResolver().attach(target=target, evidence=(candidate,))[0]
        self.assertEqual(attachment.status, ResolutionStatus.UNRESOLVED)
        self.assertIn("med-a", attachment.candidates)

    def test_type_a_scope_repairs_preserve_explicit_local_semantics(self) -> None:
        async def analyze(text: str, surface: str):
            start = text.index(surface)
            return await NieDEPtBrSafetyRules().analyze(
                ClinicalContextQuery(text=text, start=start, end=start + len(surface))
            )

        text = "Nega enjoo, mas relata cólica no lado esquerdo."
        result = asyncio.run(analyze(text, "cólica"))
        self.assertFalse(result.negated)
        self.assertEqual(result.laterality, "left")

        text = "A tia apresentou epilepsia, mas o paciente nega crises convulsivas."
        result = asyncio.run(analyze(text, "epilepsia"))
        self.assertEqual(result.experiencer, "family")
        self.assertEqual(result.temporality, "past")

        text = "A dose de sertralina era 50 mg antes de dormir e virou 75 mg pela manhã."
        result = asyncio.run(analyze(text, "sertralina"))
        self.assertEqual(result.dose, "75 mg")
        self.assertEqual(result.frequency, "pela manhã")

    def test_v5_1_attribute_ownership_keeps_each_laterality_with_its_mention(self) -> None:
        cases = (
            ("A dor permanece no joelho esquerdo e a fraqueza surgiu na mão direita.", "fraqueza", "right"),
            ("Nega dor no joelho esquerdo, mas passou a relatar formigamento na mão direita.", "formigamento", "right"),
            ("Teve dor antiga no ombro, mas hoje relata dormência no braço direito.", "dormência", "right"),
            ("A dormência ocupa o lado direito do rosto e a dor está na perna esquerda.", "dor", "left"),
            ("A pressão incomoda o ouvido esquerdo, enquanto o zumbido aparece no direito.", "zumbido", "right"),
            ("Refere rigidez no quadril direito e sensibilidade na panturrilha esquerda.", "sensibilidade", "left"),
            ("A queimação ficou no pé esquerdo e a dormência apareceu na mão direita.", "dormência", "right"),
            ("A dor abdominal ficou à direita e a sensibilidade surgiu no flanco esquerdo.", "sensibilidade", "left"),
        )

        async def analyze(text: str, surface: str):
            # ``dor`` is also the prefix of ``dormência`` in one fixture; the
            # benchmark span for that case is the second occurrence.
            start = text.rindex(surface) if surface == "dor" else text.index(surface)
            return await NieDEPtBrSafetyRules().analyze(
                ClinicalContextQuery(text=text, start=start, end=start + len(surface))
            )

        for text, surface, expected in cases:
            result = asyncio.run(analyze(text, surface))
            self.assertEqual(result.laterality, expected, text)

    def test_v5_1_attribute_ownership_keeps_family_experiencer_on_its_mention(self) -> None:
        text = "A tia apresentou epilepsia, mas o paciente nega crises convulsivas."
        surface = "epilepsia"
        start = text.index(surface)
        result = asyncio.run(NieDEPtBrSafetyRules().analyze(
            ClinicalContextQuery(text=text, start=start, end=start + len(surface))
        ))
        self.assertEqual(result.experiencer, "family")
        ownership = result.provenance["attribute_ownership"]["experiencer"]
        self.assertEqual(ownership["owner_span"], (start, start + len(surface)))

    def test_v5_1_attribute_ownership_is_not_shared_between_laterality_mentions(self) -> None:
        text = "A dor permanece no joelho esquerdo e a fraqueza surgiu na mão direita."
        first_start = text.index("dor")
        second_start = text.index("fraqueza")
        rules = NieDEPtBrSafetyRules()
        first = asyncio.run(rules.analyze(ClinicalContextQuery(
            text=text, start=first_start, end=first_start + len("dor")
        )))
        second = asyncio.run(rules.analyze(ClinicalContextQuery(
            text=text, start=second_start, end=second_start + len("fraqueza")
        )))
        first_owner = first.provenance["attribute_ownership"]["laterality"]["owner_mention_id"]
        second_owner = second.provenance["attribute_ownership"]["laterality"]["owner_mention_id"]
        self.assertNotEqual(first_owner, second_owner)
        self.assertEqual(first.laterality, "left")
        self.assertEqual(second.laterality, "right")

    def test_short_answer_state_does_not_leak_medication_status_to_sibling_symptom(self) -> None:
        case = BenchmarkCase(
            case_id="type-a-owner-scope",
            text="Médico: Ainda está tomando losartana?\nPaciente: Não, parei semana passada e não tive tontura.",
            language="pt-BR",
            gold=(),
            segments=(
                ConversationSegment("q", "clinician", "Ainda está tomando losartana?"),
                ConversationSegment("a", "patient", "Não, parei semana passada e não tive tontura."),
            ),
        )
        start = case.text.index("tontura")
        result = asyncio.run(CrossSegmentContextAdapter(
            NieDEPtBrSafetyRules(), (case,)
        ).analyze(ClinicalContextQuery(
            text=case.text,
            start=start,
            end=start + len("tontura"),
            evidence_id=case.case_id,
        )))
        self.assertIsNone(result.status)
        self.assertEqual(result.temporality, "current")
        self.assertTrue(result.negated)

    def test_v5_2_transition_ownership_selects_current_dose_and_frequency(self) -> None:
        cases = (
            (
                "A dose de sertralina era 50 mg antes de dormir e virou 75 mg pela manhã.",
                "sertralina",
                "75 mg",
                "pela manhã",
                {("CHANGED_FROM", "dose", "50 mg"), ("CHANGED_FROM", "frequency", "antes de dormir")},
            ),
            (
                "Tomava ibuprofeno 200 mg se dor e passou a usar 400 mg a cada oito horas.",
                "ibuprofeno",
                "400 mg",
                "a cada oito horas",
                {("CHANGED_FROM", "dose", "200 mg"), ("CHANGED_FROM", "frequency", "se dor")},
            ),
            (
                "A levotiroxina passou de 75 mcg em jejum para 88 mcg antes do café.",
                "levotiroxina",
                "88 mcg",
                "antes do café",
                {("CHANGED_FROM", "dose", "75 mcg"), ("CHANGED_FROM", "frequency", "em jejum")},
            ),
        )

        for text, surface, expected_dose, expected_frequency, expected_transitions in cases:
            case = BenchmarkCase(
                case_id=f"v5-2-{surface}",
                text=text,
                language="pt-BR",
                gold=(),
                segments=(ConversationSegment("transition", "patient", text),),
            )
            start = text.index(surface)
            result = asyncio.run(CrossSegmentContextAdapter(
                NieDEPtBrSafetyRules(), (case,)
            ).analyze(ClinicalContextQuery(
                text=text,
                start=start,
                end=start + len(surface),
                evidence_id=case.case_id,
            )))
            self.assertEqual(result.dose, expected_dose, text)
            self.assertEqual(result.frequency, expected_frequency, text)
            self.assertEqual(
                result.provenance["resolved_provenance"]["transition_attribute_ownership"]["dose"]["current"],
                expected_dose,
                text,
            )
            transitions = {
                (item["relation_type"], item["target"], item["value"])
                for item in result.provenance["projection"]["relations"]
                if item["relation_type"] == "CHANGED_FROM"
            }
            self.assertTrue(expected_transitions.issubset(transitions), text)

    def test_v5_3_status_tracks_current_historical_and_negated_assertions(self) -> None:
        cases = (
            ("A dor permanece no joelho esquerdo.", "dor", "present"),
            ("Teve dor antiga no ombro.", "dor", "historical"),
            ("Nega dor no joelho esquerdo.", "dor", None),
        )
        for text, surface, expected in cases:
            start = text.index(surface)
            result = asyncio.run(NieDEPtBrSafetyRules().analyze(
                ClinicalContextQuery(
                    text=text,
                    start=start,
                    end=start + len(surface),
                    semantic_policy="clinical-semantic-policy-v1.1",
                )
            ))
            self.assertEqual(result.status, expected, text)

    def test_v6_status_policy_uses_null_without_explicit_lifecycle(self) -> None:
        cases = (
            ("Refere dor no braço.", "dor", None),
            ("Teve uma queda mês passado.", "queda", None),
            ("Fez cirurgia há anos.", "cirurgia", None),
            ("A mãe teve câncer.", "mãe", None),
            ("Usa losartana 50 mg.", "losartana", "active"),
            ("Parou losartana ontem.", "losartana", "discontinued"),
        )
        for text, surface, expected in cases:
            start = text.index(surface)
            result = asyncio.run(NieDEPtBrSafetyRules().analyze(
                ClinicalContextQuery(
                    text=text,
                    start=start,
                    end=start + len(surface),
                    semantic_policy="clinical-semantic-policy-v1.2",
                )
            ))
            self.assertEqual(result.status, expected, text)
            if expected is None:
                self.assertNotIn("ptbr-current-assertion-status", result.provenance["rules"])
                self.assertNotIn("ptbr-historical-assertion-status", result.provenance["rules"])

    def test_v5_4_negation_scope_stops_at_contrastive_assertion(self) -> None:
        cases = (
            ("Diz que não vomitou mas teve enjoo e uma azia forte hoje.", "vomitou", True),
            ("Diz que não vomitou mas teve enjoo e uma azia forte hoje.", "enjoo", False),
            ("Sem tontura, só fraqueza e visão meio turva hoje.", "fraqueza", False),
            ("Nega palpitação, refere cansaço e peso no peito hoje.", "cansaço", False),
            ("Nega palpitação, refere cansaço e peso no peito hoje.", "peso no peito", False),
        )
        for text, surface, expected in cases:
            start = text.index(surface)
            result = asyncio.run(NieDEPtBrSafetyRules().analyze(
                ClinicalContextQuery(
                    text=text,
                    start=start,
                    end=start + len(surface),
                    semantic_policy="clinical-semantic-policy-v1.1",
                )
            ))
            self.assertEqual(result.negated, expected, f"{text} [{surface}]")

    def test_v5_5_temporality_belongs_to_event_not_following_mention(self) -> None:
        cases = (
            (
                "Teve cirurgia no ombro há anos, mas hoje sente dormência no braço.",
                "cirurgia no ombro",
                "past",
            ),
            (
                "Teve cirurgia no ombro há anos, mas hoje sente dormência no braço.",
                "dormência no braço",
                "current",
            ),
            (
                "O pai conviveu com hipertensão, enquanto a paciente nega pressão alta.",
                "hipertensão",
                "past",
            ),
            (
                "O pai conviveu com hipertensão, enquanto a paciente nega pressão alta.",
                "pressão alta",
                "current",
            ),
        )
        for text, surface, expected in cases:
            start = text.index(surface)
            result = asyncio.run(NieDEPtBrSafetyRules().analyze(
                ClinicalContextQuery(
                    text=text,
                    start=start,
                    end=start + len(surface),
                    semantic_policy="clinical-semantic-policy-v1.1",
                )
            ))
            self.assertEqual(result.temporality, expected, f"{text} [{surface}]")

    def test_v5_6_cross_segment_discontinuation_emits_relation(self) -> None:
        cases = (
            ("Médico: Continua usando losartana?\nPaciente: Não, parei na semana passada.", "losartana"),
            ("Médico: Você ainda usa enalapril?\nPaciente: Parei no mês passado.", "enalapril"),
            ("Médico: Ainda está tomando losartana?\nPaciente: Não, parei semana passada e não tive tontura.", "losartana"),
        )
        for text, surface in cases:
            case = BenchmarkCase(
                case_id=f"v5-6-{surface}-{len(text)}",
                text=text,
                language="pt-BR",
                gold=(),
                segments=tuple(
                    ConversationSegment(f"seg-{index}", speaker, segment_text)
                    for index, (speaker, segment_text) in enumerate(
                        (line.split(": ", 1) for line in text.splitlines())
                    )
                ),
            )
            start = text.index(surface)
            result = asyncio.run(CrossSegmentContextAdapter(
                NieDEPtBrSafetyRules(), (case,)
            ).analyze(ClinicalContextQuery(
                text=text,
                start=start,
                end=start + len(surface),
                evidence_id=case.case_id,
                semantic_policy="clinical-semantic-policy-v1.1",
            )))
            self.assertEqual(result.status, "discontinued", text)
            relations = {
                (item["relation_type"], item["target"], item["value"])
                for item in result.provenance["projection"]["relations"]
            }
            self.assertIn(("DISCONTINUED_AT", "status", "discontinued"), relations, text)
            discontinuations = [
                item
                for item in result.provenance["projection"]["relations"]
                if item["relation_type"] == "DISCONTINUED_AT"
            ]
            self.assertEqual(len(discontinuations), 1, text)
            self.assertEqual(
                discontinuations[0]["source_mention_id"],
                discontinuations[0]["source"],
                text,
            )

    def test_post_holdout_cross_segment_laterality_materializes_relation(self) -> None:
        text = "Médico: A queimação voltou?\nPaciente: Está apenas na perna direita agora."
        case = BenchmarkCase(
            case_id="post-repair-engineering-laterality",
            text=text,
            language="pt-BR",
            gold=(),
            segments=(
                ConversationSegment("post-lat-q", "clinician", "A queimação voltou?"),
                ConversationSegment("post-lat-a", "patient", "Está apenas na perna direita agora."),
            ),
        )
        start = text.index("queimação")
        result = asyncio.run(CrossSegmentContextAdapter(
            NieDEPtBrSafetyRules(), (case,)
        ).analyze(ClinicalContextQuery(
            text=text,
            start=start,
            end=start + len("queimação"),
            evidence_id=case.case_id,
            semantic_policy="clinical-semantic-policy-v1.2",
        )))
        self.assertEqual(result.laterality, "right")
        relation = next(
            item for item in result.provenance["projection"]["relations"]
            if item["relation_type"] == "HAS_LATERALITY"
        )
        self.assertEqual(relation["value"], "right")
        self.assertEqual(relation["source_segment_ids"], ["post-lat-a"])

    def test_post_holdout_cross_segment_dose_materializes_relation(self) -> None:
        text = "Médico: Qual dose da sertralina?\nPaciente: Passei para 75 mg hoje."
        case = BenchmarkCase(
            case_id="post-repair-engineering-dose",
            text=text,
            language="pt-BR",
            gold=(),
            segments=(
                ConversationSegment("post-dose-q", "clinician", "Qual dose da sertralina?"),
                ConversationSegment("post-dose-a", "patient", "Passei para 75 mg hoje."),
            ),
        )
        start = text.index("sertralina")
        result = asyncio.run(CrossSegmentContextAdapter(
            NieDEPtBrSafetyRules(), (case,)
        ).analyze(ClinicalContextQuery(
            text=text,
            start=start,
            end=start + len("sertralina"),
            evidence_id=case.case_id,
            semantic_policy="clinical-semantic-policy-v1.2",
        )))
        self.assertEqual(result.dose, "75 mg")
        relation = next(
            item for item in result.provenance["projection"]["relations"]
            if item["relation_type"] == "HAS_DOSE"
        )
        self.assertEqual(relation["value"], "75 mg")
        self.assertEqual(relation["source_segment_ids"], ["post-dose-a"])

    def test_post_holdout_event_time_isolated_from_current_medication_state(self) -> None:
        text = "Médico: Como está a dose do atenolol?\nPaciente: Aumentei para 50 mg ontem."
        case = BenchmarkCase(
            case_id="post-repair-engineering-temporality",
            text=text,
            language="pt-BR",
            gold=(),
            segments=(
                ConversationSegment("post-time-q", "clinician", "Como está a dose do atenolol?"),
                ConversationSegment("post-time-a", "patient", "Aumentei para 50 mg ontem."),
            ),
        )
        start = text.index("atenolol")
        result = asyncio.run(CrossSegmentContextAdapter(
            NieDEPtBrSafetyRules(), (case,)
        ).analyze(ClinicalContextQuery(
            text=text,
            start=start,
            end=start + len("atenolol"),
            evidence_id=case.case_id,
            semantic_policy="clinical-semantic-policy-v1.2",
        )))
        self.assertEqual(result.temporality, "current")
        self.assertEqual(result.provenance["event_temporality"]["value"], "past")
        self.assertEqual(result.provenance["event_temporality"]["owner"], "dose_change_event")

    def test_post_holdout_provenance_contract_uses_full_conversation_scope(self) -> None:
        text = "Médico: Qual dose da sertralina?\nPaciente: Passei para 75 mg hoje."
        case = BenchmarkCase(
            case_id="post-repair-engineering-provenance",
            text=text,
            language="pt-BR",
            gold=(),
            segments=(
                ConversationSegment("post-prov-q", "clinician", "Qual dose da sertralina?"),
                ConversationSegment("post-prov-a", "patient", "Passei para 75 mg hoje."),
            ),
        )
        start = text.index("sertralina")
        result = asyncio.run(CrossSegmentContextAdapter(
            NieDEPtBrSafetyRules(), (case,)
        ).analyze(ClinicalContextQuery(
            text=text,
            start=start,
            end=start + len("sertralina"),
            evidence_id=case.case_id,
            semantic_policy="clinical-semantic-policy-v1.2",
        )))
        self.assertEqual(result.provenance["source_text"], text)
        self.assertEqual(result.provenance["source_scope"], "conversation")
        self.assertEqual(result.provenance["target_segment_id"], "post-prov-q")


if __name__ == "__main__":
    unittest.main()
