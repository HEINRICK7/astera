from __future__ import annotations

import asyncio

from apps.runtime.src.ports.outbound.clinical_semantics import ClinicalContextQuery
from labs.terminology_benchmark.relation_input_signals import (
    RelationInputContractReport,
    ResolvedAttributeSignal,
    ResolvedTransitionSignal,
    SignalState,
    SignalStatus,
)
from labs.terminology_benchmark.context_safety import NieDEPtBrSafetyRules
from labs.terminology_benchmark.cross_segment_context import CrossSegmentContextAdapter
from labs.terminology_benchmark.models import BenchmarkCase, ConversationSegment


def _source(*segments: str) -> dict[str, object]:
    return {"source_segment_ids": segments}


def test_relation_attribute_requires_typed_owner_and_provenance() -> None:
    ready = ResolvedAttributeSignal(
        attribute_type="dose",
        value="100 mg",
        owner_mention_id="m-medication",
        owner_type="medication",
        state=SignalState.CURRENT,
        provenance=_source("answer"),
    )
    missing_owner = ResolvedAttributeSignal(
        attribute_type="dose",
        value="100 mg",
        owner_mention_id=None,
        owner_type=None,
        state=SignalState.CURRENT,
        provenance=_source("answer"),
    )
    assert ready.relation_ready
    assert ready.status is SignalStatus.RESOLVED
    assert not missing_owner.relation_ready
    assert missing_owner.status is SignalStatus.UNRESOLVED_OWNER


def test_historical_attribute_does_not_become_current() -> None:
    signal = ResolvedAttributeSignal(
        attribute_type="dose",
        value="50 mg",
        owner_mention_id="m-medication",
        owner_type="medication",
        state=SignalState.HISTORICAL,
        provenance=_source("history"),
    )
    assert signal.relation_ready
    assert signal.state is SignalState.HISTORICAL


def test_transition_requires_distinct_from_and_to_values() -> None:
    valid = ResolvedTransitionSignal(
        attribute_type="dose",
        owner_mention_id="m-medication",
        owner_type="medication",
        previous_value="50 mg",
        current_value="100 mg",
        transition_type="CHANGED_FROM",
        temporal_anchor="yesterday",
        provenance=_source("change"),
        state=SignalState.CURRENT,
    )
    ambiguous = ResolvedTransitionSignal(
        attribute_type="dose",
        owner_mention_id="m-medication",
        owner_type="medication",
        previous_value="50 mg",
        current_value="50 mg",
        transition_type="CHANGED_FROM",
        temporal_anchor=None,
        provenance=_source("change"),
        state=SignalState.CURRENT,
    )
    assert valid.relation_ready
    assert ambiguous.status is SignalStatus.AMBIGUOUS
    assert not ambiguous.relation_ready


def test_missing_owner_does_not_create_transition() -> None:
    signal = ResolvedTransitionSignal(
        attribute_type="frequency",
        owner_mention_id=None,
        owner_type=None,
        previous_value="à noite",
        current_value="pela manhã",
        transition_type="CHANGED_FROM",
        temporal_anchor=None,
        provenance=_source("change"),
        state=SignalState.CURRENT,
    )
    assert signal.status is SignalStatus.UNRESOLVED_OWNER
    assert not signal.relation_ready


def test_contract_gate_reports_complete_and_blocking_inputs() -> None:
    report = RelationInputContractReport(
        attribute_signals=(ResolvedAttributeSignal(
            attribute_type="laterality",
            value="left",
            owner_mention_id="m-symptom",
            owner_type="symptom",
            state=SignalState.CURRENT,
            provenance=_source("symptom"),
        ),),
        transition_signals=(ResolvedTransitionSignal(
            attribute_type="dose",
            owner_mention_id=None,
            owner_type=None,
            previous_value="20 mg",
            current_value="10 mg",
            transition_type="CHANGED_FROM",
            temporal_anchor=None,
            provenance=_source("change"),
            state=SignalState.CURRENT,
        ),),
    )
    assert report.owner_completeness == 0.5
    assert report.state_completeness == 1.0
    assert report.transition_validity == 0.0
    assert report.provenance_completeness == 1.0
    assert report.has_blocking_signal


def test_cross_segment_boundary_persists_contract_before_compiler() -> None:
    text = "Mantenho losartana 20 mg pela manhã."
    case = BenchmarkCase(
        case_id="c2-contract-integration",
        text=text,
        language="pt-BR",
        gold=(),
        segments=(ConversationSegment("c2-segment", "patient", text),),
    )
    start = text.index("losartana")
    result = asyncio.run(CrossSegmentContextAdapter(
        NieDEPtBrSafetyRules(), (case,)
    ).analyze(ClinicalContextQuery(
        text=text,
        start=start,
        end=start + len("losartana"),
        evidence_id=case.case_id,
    )))
    contract = result.provenance["resolved_provenance"]["relation_input_contract"]
    assert contract["relation_input_owner_completeness"] == 1.0
    assert contract["relation_input_state_completeness"] == 1.0
    assert contract["transition_contract_validity"] == 1.0
    assert contract["relation_input_provenance"] == 1.0
