"""A2UI Cognitive Presentation Protocol projection for Clinical Objects."""
from __future__ import annotations

from typing import Any

from .presentation_composer import ClinicalObject, PresentationModel


class ClinicalA2UIProjector:
    """Turn the clinical presentation model into stable A2UI deltas.

    The projector owns protocol state, while the composer owns clinical
    meaning.  This keeps the Workbench as a renderer instead of a second
    clinical state machine.
    """

    _COMPONENTS = {
        "clinical_problem": "ClinicalProblemCard",
        "clinical_history": "ClinicalHistoryCard",
        "medication_profile": "MedicationProfileCard",
        "allergy_profile": "AllergyProfileCard",
        "clinical_hypothesis": "HypothesisCard",
        "clinical_question": "QuestionCard",
        "investigation": "InvestigationCard",
        "clinical_summary": "ClinicalSummaryCard",
        "soap_progress": "SOAPProgressCard",
    }

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._workspace_state: dict[str, Any] | None = None

    def project(self, presentation: PresentationModel) -> tuple[dict[str, Any], ...]:
        operations: list[dict[str, Any]] = []
        operations.extend(self._workspace_delta(presentation.workspace_state))

        current_ids = {item.object_id for item in presentation.objects}
        for object_id in sorted((set(self._nodes) - current_ids) - {"knowledge-timeline"}):
            operations.append({"op": "archive", "id": object_id})
            self._nodes.pop(object_id, None)

        for item in presentation.objects:
            component, props = self._object_payload(item)
            previous = self._nodes.get(item.object_id)
            if previous is None:
                operations.append({
                    "op": "create",
                    "id": item.object_id,
                    "component": component,
                    "props": props,
                    "target": {"title": item.title, "object_type": item.object_type},
                })
            else:
                changed = {key: value for key, value in props.items() if previous.get("props", {}).get(key) != value}
                if changed:
                    operation = {"op": "patch", "id": item.object_id, "patch": changed}
                    operation["target"] = {"title": props.get("title", previous.get("props", {}).get("title", item.title)), "object_type": item.object_type}
                    operation["diff"] = {
                        key: {
                            "from": previous.get("props", {}).get(key),
                            "to": value,
                        }
                        for key, value in changed.items()
                    }
                    if previous.get("component") != component:
                        operation["component"] = component
                    operations.append(operation)
            self._nodes[item.object_id] = {"component": component, "props": props}

        timeline_props = {"entries": [dict(entry) for entry in presentation.timeline]}
        previous_timeline = self._nodes.get("knowledge-timeline")
        if previous_timeline is None:
            operations.append({
                "op": "create",
                "id": "knowledge-timeline",
                "component": "TimelineCard",
                "props": timeline_props,
                "target": {"title": "Linha do tempo clínica", "object_type": "clinical_timeline"},
            })
        elif previous_timeline.get("props") != timeline_props:
            previous_entries = previous_timeline.get("props", {}).get("entries", [])
            operations.append({
                "op": "patch",
                "id": "knowledge-timeline",
                "patch": timeline_props,
                "target": {"title": "Linha do tempo clínica", "object_type": "clinical_timeline"},
                "diff": {"entries": {"from": previous_entries, "to": timeline_props["entries"]}},
            })
        self._nodes["knowledge-timeline"] = {"component": "TimelineCard", "props": timeline_props}
        return tuple(operations)

    def transition(self, lifecycle: str) -> tuple[dict[str, Any], ...]:
        return self._workspace_delta({"lifecycle": lifecycle})

    def validate(self) -> tuple[dict[str, Any], ...]:
        return self._workspace_delta({"validation": "completed"})

    def archive(self) -> tuple[dict[str, Any], ...]:
        return self._workspace_delta({"lifecycle": "archived"})

    def transcript(
        self,
        *,
        text: str,
        partial: str = "",
        final_segments: tuple[dict[str, Any], ...] = (),
    ) -> tuple[dict[str, Any], ...]:
        """Project speech progress without waiting for a clinical object."""
        return self._workspace_delta({
            "schema": "astera.clinical-workspace-state/v1",
            "transcript": {
                "text": text,
                "partial": partial,
                "final_segments": [dict(segment) for segment in final_segments],
            },
        })

    def _workspace_delta(self, state: dict[str, Any]) -> tuple[dict[str, Any], ...]:
        if self._workspace_state is None:
            self._workspace_state = dict(state)
            return ({"op": "state", "id": "clinical-workspace-state", "state": dict(state)},)
        changed = {key: value for key, value in state.items() if self._workspace_state.get(key) != value}
        if not changed:
            return ()
        self._workspace_state = {**self._workspace_state, **changed}
        return ({"op": "patch", "id": "clinical-workspace-state", "patch": changed},)

    def _object_payload(self, item: ClinicalObject) -> tuple[str, dict[str, Any]]:
        return self._COMPONENTS.get(item.object_type, "ObservationCard"), item.to_dict()
