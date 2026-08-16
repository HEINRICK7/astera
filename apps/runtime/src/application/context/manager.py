"""
ContextManager — manages the lifecycle of ContextScopes.

WHY exists in Phase C:
    Every plugin invocation receives a ContextScope.
    The ADK depends on it from Day 1 of Phase D.
    Multi-tenancy is baked in from the start — not retrofitted later.

Hierarchy enforced:
    Organization → Workspace → Encounter → Patient → Session
"""
from __future__ import annotations

import logging
from typing import Any

from apps.runtime.src.domain.entities.context_scope import ContextScope
from apps.runtime.src.domain.exceptions.context_not_found import ContextNotFoundError

logger = logging.getLogger("astera.context_manager")


class ContextManager:
    """
    Manages the lifecycle of all active ContextScopes.

    Phase C: in-memory only.
    Phase D+: persist to Redis, publish events to EventBus, TTL-based expiry.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ContextScope] = {}
        logger.info("ContextManager initialized")

    @property
    def system_context(self) -> ContextScope:
        """System-level context. Always available. No clinical data."""
        return ContextScope(organization_id="system")

    def create_session(
        self,
        organization_id: str,
        workspace_id: str | None = None,
        patient_id: str | None = None,
    ) -> ContextScope:
        """Create and track a new session context."""
        ctx = ContextScope(
            organization_id=organization_id,
            workspace_id=workspace_id,
            patient_id=patient_id,
        )
        ctx.session_id = ctx.id
        self._sessions[ctx.id] = ctx
        logger.info("Session created", extra={
            "session_id":      ctx.id,
            "organization_id": organization_id,
        })
        return ctx

    def start_encounter(
        self,
        session_id: str,
        encounter_id: str,
        patient_id: str,
    ) -> ContextScope:
        """Attach an Encounter and Patient to an existing session."""
        ctx = self._get_or_raise(session_id)
        ctx.encounter_id = encounter_id
        ctx.patient_id   = patient_id
        logger.info("Encounter started", extra={
            "session_id":   session_id,
            "encounter_id": encounter_id,
        })
        return ctx

    def end_session(self, session_id: str) -> None:
        ctx = self._sessions.pop(session_id, None)
        if ctx:
            logger.info("Session ended", extra={"session_id": session_id})
        else:
            logger.warning("Unknown session", extra={"session_id": session_id})

    def get_session(self, session_id: str) -> ContextScope | None:
        return self._sessions.get(session_id)

    def active_count(self) -> int:
        return len(self._sessions)

    def clinical_count(self) -> int:
        return sum(1 for ctx in self._sessions.values() if ctx.is_clinical())

    def summary(self) -> dict[str, Any]:
        return {
            "active_sessions":          self.active_count(),
            "active_clinical_sessions": self.clinical_count(),
        }

    def _get_or_raise(self, session_id: str) -> ContextScope:
        ctx = self._sessions.get(session_id)
        if ctx is None:
            raise ContextNotFoundError(session_id)
        return ctx
