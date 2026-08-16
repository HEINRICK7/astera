"""Dependency-free tests for the experimental terminology/context harness."""
from __future__ import annotations

import asyncio
from dataclasses import replace
import unittest

from labs.terminology_benchmark.adapters import DeterministicBaselineAdapter
from labs.terminology_benchmark.asset_registry import load_registry
from labs.terminology_benchmark.context_adapters import DeterministicContextAdapter
from labs.terminology_benchmark.context_harness import evaluate as evaluate_context
from labs.terminology_benchmark.context_rules import RULES_PATH, load_context_rules
from labs.terminology_benchmark.context_safety import NieDEPtBrSafetyRules
from labs.terminology_benchmark.corpus import (
    CONTEXT_HARDENING_CORPUS_PATH,
    CONTEXT_VALIDATION_V3_PATH,
    CONTEXT_VALIDATION_V4_PATH,
    CONTEXT_VALIDATION_V5_PATH,
    CONTEXT_VALIDATION_V6_DRAFT_PATH,
    load_corpus,
    mention_span,
)
from labs.terminology_benchmark.harness import run
from labs.terminology_benchmark.models import GoldMention
from labs.terminology_benchmark.simulator import (
    ClinicalLanguageSimulator,
    FailureSeed,
    approve_candidate,
    load_failure_seeds,
    reviewed_candidate_to_case,
)
from labs.terminology_benchmark.review_queue import build_review_packet
from labs.terminology_benchmark.v6_corpus import V6AssemblyBlocked, assert_official_v6_ready, validate_v6_draft
from labs.terminology_benchmark.v6_harness import evaluate_v6
from apps.runtime.src.ports.outbound.clinical_semantics import (
    ClinicalContextPort,
    TerminologyPort,
)


class TerminologyBenchmarkTests(unittest.TestCase):
    def test_pt_br_corpus_is_versioned_and_all_gold_spans_exist(self) -> None:
        corpus = load_corpus()
        self.assertEqual(len(corpus), 10)
        for case in corpus:
            for gold in case.gold:
                start, end = mention_span(case.text, gold.surface)
                self.assertEqual(case.text[start:end].casefold(), gold.surface.casefold())

    def test_deterministic_baseline_runs_only_in_harness(self) -> None:
        adapter = DeterministicBaselineAdapter()
        self.assertIsInstance(adapter, TerminologyPort)
        report = run(adapter)
        self.assertEqual(report.provider.provider, "deterministic-baseline")
        self.assertEqual(report.cases, 10)
        self.assertEqual(report.concept_stability, 1.0)
        self.assertEqual(report.provenance_completeness, 1.0)
        self.assertFalse(report.hard_gate_passed)

    def test_context_track_is_separate_from_entity_linking(self) -> None:
        result = asyncio.run(evaluate_context(DeterministicContextAdapter()))
        self.assertEqual(result["provider"], "deterministic-context-baseline")
        self.assertIn("attribute_accuracy", result)
        self.assertEqual(result["attribute_accuracy"]["provenance"], 1.0)

    def test_niede_context_rules_are_versioned_and_context_adapter_is_provider_neutral(self) -> None:
        rules = load_context_rules()
        self.assertEqual(rules["rule_set"], "niede-pt-br-context-v1")
        self.assertEqual(rules["language"], "pt-BR")
        self.assertIsInstance(DeterministicContextAdapter(), ClinicalContextPort)

    def test_asset_registry_blocks_unreviewed_terminology_and_verifies_context_rules(self) -> None:
        registry = load_registry()
        terminology = registry.authorize("quickumls", "benchmark")
        self.assertFalse(terminology.allowed)
        self.assertIn("PENDING_REVIEW", " ".join(terminology.reasons))

        context = registry.authorize("medspacy", "benchmark")
        self.assertTrue(context.allowed)
        self.assertTrue(
            registry.verify_path(
                "niede-pt-br-context-rules-v1",
                RULES_PATH,
            )
        )

    def test_pt_br_hardening_rules_pass_lab_gate_on_focus_corpus(self) -> None:
        cases = load_corpus(CONTEXT_HARDENING_CORPUS_PATH)
        self.assertEqual(len(cases), 21)
        result = asyncio.run(evaluate_context(NieDEPtBrSafetyRules(), cases))
        self.assertTrue(result["hard_gate_passed"])

    def test_v3_adversarial_corpus_measures_mention_exact_match(self) -> None:
        cases = load_corpus(CONTEXT_VALIDATION_V3_PATH)
        self.assertEqual(len(cases), 80)
        result = asyncio.run(evaluate_context(NieDEPtBrSafetyRules(), cases))
        self.assertEqual(result["attribute_accuracy"]["mention_exact_match"], 1.0)
        self.assertTrue(result["hard_gate_passed"])

    def test_v4_is_unseen_and_has_compositional_hard_gate_metrics(self) -> None:
        v3 = load_corpus(CONTEXT_VALIDATION_V3_PATH)
        v4 = load_corpus(CONTEXT_VALIDATION_V4_PATH)
        self.assertEqual(len(v4), 100)
        self.assertTrue({case.text for case in v3}.isdisjoint({case.text for case in v4}))
        result = asyncio.run(
            evaluate_context(
                NieDEPtBrSafetyRules(),
                v4,
                enforce_composition_gate=True,
            )
        )
        metrics = result["attribute_accuracy"]
        self.assertIn("relation_exact_match", metrics)
        self.assertIn("scope_accuracy", metrics)
        self.assertIn("cross_mention_isolation", metrics)

    def test_v5_is_unseen_generalization_corpus(self) -> None:
        v3 = load_corpus(CONTEXT_VALIDATION_V3_PATH)
        v4 = load_corpus(CONTEXT_VALIDATION_V4_PATH)
        v5 = load_corpus(CONTEXT_VALIDATION_V5_PATH)
        self.assertEqual(len(v5), 120)
        self.assertTrue({case.text for case in v5}.isdisjoint({case.text for case in v3}))
        self.assertTrue({case.text for case in v5}.isdisjoint({case.text for case in v4}))
        result = asyncio.run(
            evaluate_context(
                NieDEPtBrSafetyRules(),
                v5,
                enforce_composition_gate=True,
                composition_thresholds={
                    "relation_exact_match": 0.95,
                    "scope_accuracy": 0.97,
                    "cross_mention_isolation": 0.95,
                },
            )
        )
        metrics = result["attribute_accuracy"]
        self.assertEqual(metrics["mention_exact_match"], 1.0)
        self.assertEqual(metrics["relation_exact_match"], 1.0)
        self.assertEqual(metrics["scope_accuracy"], 1.0)
        self.assertEqual(metrics["cross_mention_isolation"], 1.0)
        self.assertTrue(result["hard_gate_passed"])

    def test_clinical_language_simulator_generates_review_only_disjoint_candidates(self) -> None:
        corpora = (
            CONTEXT_VALIDATION_V3_PATH,
            CONTEXT_VALIDATION_V4_PATH,
            CONTEXT_VALIDATION_V5_PATH,
        )
        taxonomies = tuple(
            CONTEXT_VALIDATION_V3_PATH.parent.parent
            / "results"
            / f"context-taxonomy-v{version}-2026-08-15.json"
            for version in (3, 4, 5)
        )
        manifest = CONTEXT_VALIDATION_V5_PATH.parent / "historical_failure_manifest.json"
        seeds = load_failure_seeds(corpora, taxonomies, manifest)
        official = tuple(case for path in corpora for case in load_corpus(path))
        candidates = ClinicalLanguageSimulator().generate(seeds, official, limit=12)

        self.assertEqual(len(candidates), 12)
        self.assertTrue({candidate.text for candidate in candidates}.isdisjoint({case.text for case in official}))
        self.assertTrue(all(candidate.review_status == "PENDING_REVIEW" for candidate in candidates))
        self.assertTrue(all(candidate.gold is None for candidate in candidates))
        self.assertTrue(all(candidate.provenance["official_corpus_mutation"] is False for candidate in candidates))

    def test_candidate_requires_named_human_review_before_gold(self) -> None:
        candidate = ClinicalLanguageSimulator().generate(
            seeds=(FailureSeed("synthetic", "synthetic-001", ("NEGATION_SCOPE",), "texto histórico"),),
            official_cases=(),
        )[0]
        with self.assertRaises(ValueError):
            approve_candidate(candidate, (), reviewer="")
        reviewed = approve_candidate(
            candidate,
            (GoldMention(
                surface="dor",
                concept_id="symptom.pain",
                segment_ids=("candidate-segment",),
                attribute_provenance={"concept": ("candidate-segment",)},
            ),),
            reviewer="reviewer@example.org",
        )
        self.assertEqual(reviewed.review_status, "APPROVED_FOR_CORPUS")

    def test_v6_review_queue_is_read_only_and_keeps_gold_pending(self) -> None:
        candidate = ClinicalLanguageSimulator().generate(
            seeds=(FailureSeed("synthetic", "synthetic-001", ("NEGATION_SCOPE",), "texto histórico"),),
            official_cases=(),
        )[0]
        packet = build_review_packet((candidate.to_dict(),))
        self.assertEqual(packet[0]["review_status"], "PENDING_REVIEW")
        self.assertIsNone(packet[0]["mentions"])
        self.assertIsNone(packet[0]["relations"])
        self.assertFalse(packet[0]["provenance"]["official_corpus_mutation"])

    def test_v6_draft_has_independent_realistic_and_conversational_cases(self) -> None:
        cases = load_corpus(CONTEXT_VALIDATION_V6_DRAFT_PATH)
        report = validate_v6_draft(cases)
        self.assertEqual(report["cases"], 105)
        self.assertEqual(report["mentions"], 255)
        self.assertEqual(report["sources"], {"independent": 60, "realistic": 45})
        self.assertEqual(sum(bool(case.segments) for case in cases), 15)

    def test_v6_cross_segment_gold_preserves_attribute_and_relation_provenance(self) -> None:
        cases = load_corpus(CONTEXT_VALIDATION_V6_DRAFT_PATH)
        case = next(case for case in cases if case.case_id == "v6-c-001-1")
        medication = case.gold[0]
        self.assertEqual(medication.attribute_provenance["concept"], ("seg_01_0_01",))
        self.assertEqual(medication.attribute_provenance["status"], ("seg_01_0_02",))
        self.assertEqual(medication.relation_provenance["status"], ("seg_01_0_02",))
        self.assertEqual(medication.relation_provenance["temporality"], ("seg_01_0_02",))

    def test_v6_rejects_conversational_gold_without_provenance(self) -> None:
        cases = list(load_corpus(CONTEXT_VALIDATION_V6_DRAFT_PATH))
        case_index = next(index for index, case in enumerate(cases) if case.segments)
        case = cases[case_index]
        cases[case_index] = replace(
            case,
            gold=(replace(case.gold[0], attribute_provenance={}, relation_provenance={}), *case.gold[1:]),
        )
        with self.assertRaises(V6AssemblyBlocked):
            validate_v6_draft(cases)

    def test_v6_assembler_blocks_until_simulator_gold_is_human_approved(self) -> None:
        cases = load_corpus(CONTEXT_VALIDATION_V6_DRAFT_PATH)
        with self.assertRaises(V6AssemblyBlocked):
            assert_official_v6_ready(cases, ())

    def test_reviewed_simulator_case_requires_explicit_segment_provenance(self) -> None:
        candidate = ClinicalLanguageSimulator().generate(
            seeds=(FailureSeed("synthetic", "synthetic-001", ("NEGATION_SCOPE",), "texto histórico"),),
            official_cases=(),
        )[0]
        segment_id = f"{candidate.candidate_id}:segment-01"
        gold = GoldMention(
            surface="febre",
            concept_id="symptom.fever",
            segment_ids=(segment_id,),
            attribute_provenance={"concept": (segment_id,)},
        )
        case = reviewed_candidate_to_case(candidate, (gold,), reviewer="reviewer@example.org")
        self.assertEqual(case.source, "simulator-approved")
        self.assertEqual(case.gold[0].segment_ids, (segment_id,))
        self.assertEqual(case.segments[0].segment_id, segment_id)

    def test_v6_harness_exposes_cross_segment_and_speaker_metrics(self) -> None:
        cases = load_corpus(CONTEXT_VALIDATION_V6_DRAFT_PATH)
        result = asyncio.run(evaluate_v6(NieDEPtBrSafetyRules(), cases))
        self.assertIn("cross_segment_resolution", result["v6_metrics"])
        self.assertIn("speaker_attribution", result["v6_metrics"])
        self.assertIn("cross_segment_resolution", result["hard_gate_thresholds"])
