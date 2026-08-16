"""Declarative clinical workspace view builder."""
from __future__ import annotations

from packages.a2ui_sdk import A2UIDocument, A2UINode
from packages.auth_sdk import Principal
from packages.encounter_sdk import Encounter
from packages.patient_sdk import Patient
from packages.timeline_sdk import TimelineEvent
from apps.runtime.src.application.dashboard import DashboardService


class A2UIService:
    """Build a renderer-neutral workspace document from the dashboard port."""

    def __init__(self, dashboard: DashboardService) -> None:
        self._dashboard = dashboard

    def workspace_view(self, principal: Principal) -> A2UIDocument:
        snapshot = self._dashboard.snapshot(principal)
        root = A2UINode(
            node_id="workspace-root",
            component="ClinicalWorkspace",
            props={"organization_id": snapshot.organization_id},
            children=("workspace-header", "workspace-metrics"),
        )
        header = A2UINode(
            node_id="workspace-header",
            component="WorkspaceHeader",
            props={"title": "Astera Workspace", "workspace_ids": list(snapshot.workspace_ids)},
        )
        metrics = A2UINode(
            node_id="workspace-metrics",
            component="MetricGrid",
            props=snapshot.to_dict(),
        )
        return A2UIDocument(
            view_id="clinical-workspace",
            version="1",
            root_id=root.node_id,
            nodes=(root, header, metrics),
        )

    def consultation_view(
        self,
        *,
        patient: Patient,
        encounter: Encounter,
        timeline: tuple[TimelineEvent, ...],
        result: dict[str, object] | None = None,
    ) -> A2UIDocument:
        root = A2UINode(
            node_id="consultation-root",
            component="ClinicalConsultation",
            props={"encounter_id": encounter.encounter_id},
            children=("patient-card", "encounter-card", "timeline-panel", "stream-panel", "representation-panel"),
        )
        patient_card = A2UINode(
            node_id="patient-card",
            component="PatientCard",
            props=patient.to_dict(),
        )
        encounter_card = A2UINode(
            node_id="encounter-card",
            component="EncounterStatus",
            props=encounter.to_dict(),
        )
        timeline_panel = A2UINode(
            node_id="timeline-panel",
            component="TimelinePanel",
            props={"events": [event.to_dict() for event in timeline]},
        )
        stream_panel = A2UINode(
            node_id="stream-panel",
            component="AudioStream",
            props={"stream_id": encounter.encounter_id, "status": "ready"},
        )
        result = result or {}
        representations = result.get("representations") if isinstance(result.get("representations"), dict) else {}
        representation_items = representations.get("representations") if isinstance(representations, dict) else []
        rendered = {
            str(item.get("format")): item.get("content")
            for item in representation_items
            if isinstance(item, dict) and item.get("format")
        } if isinstance(representation_items, list) else {}

        def result_value(name: str, *aliases: str) -> object | None:
            for candidate in (name, *aliases):
                if result.get(candidate) is not None:
                    return result.get(candidate)
                if rendered.get(candidate) is not None:
                    return rendered.get(candidate)
            return None

        available_formats = [name for name in ("soap", "fhir", "summary") if result_value(name) is not None]
        representation_panel = A2UINode(
            node_id="representation-panel",
            component="RepresentationPanel",
            props={
                "formats": available_formats or ["soap", "fhir", "summary"],
                "status": "completed" if available_formats else "pending",
                "transcript": result_value("transcript"),
                "clinical_facts": result_value("clinical_facts", "facts", "evidence"),
                "clinical_context": result_value("clinical_context", "context", "understanding"),
                "reasoning": result_value("reasoning", "correlations"),
                "knowledge": result_value("knowledge", "knowledge_evidence"),
                "soap": result_value("soap"),
                "fhir": result_value("fhir"),
                "summary": result_value("summary"),
                "persistence": result_value("persistence"),
            },
        )
        return A2UIDocument(
            view_id="clinical-consultation",
            version="1",
            root_id=root.node_id,
            nodes=(root, patient_card, encounter_card, timeline_panel, stream_panel, representation_panel),
        )
