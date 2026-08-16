"""
TaskIntent — declarative request from ADK or API to the TaskOrchestrator.

WHY a frozen dataclass (not a dict or function args):
    Intent is a value object. It carries intent, not instructions.
    The Orchestrator decides HOW to fulfil it.
    Immutability guarantees the intent is not modified during execution.
    Named fields make the code self-documenting.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from apps.runtime.src.domain.entities.context_scope import ContextScope
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from apps.runtime.src.domain.value_objects.selection_criteria import SelectionCriteria


@dataclass(frozen=True)
class TaskIntent:
    """
    A request from the ADK (or API) to the TaskOrchestrator.

    The caller declares WHAT they need and the constraints.
    The Orchestrator decides WHO handles it.
    The caller NEVER names a Provider or Plugin.

    Example:
        intent = TaskIntent(
            capability_type=CapabilityType.SPEECH_TRANSCRIPTION,
            payload=audio_bytes,
            context=context_scope,
            criteria=SelectionCriteria(language="pt-BR", requires_streaming=True),
        )
    """

    capability_type: CapabilityType
    payload: object                                # audio bytes, image, text, dict…
    context: ContextScope
    criteria: SelectionCriteria = field(default_factory=SelectionCriteria)
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex)
