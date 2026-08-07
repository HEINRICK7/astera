"""
Astera Kernel — Context Manager.

The ContextManager maintains the organizational and clinical context
for every active session in the platform.

Hierarchy:
    Organization
    └── Workspace
        └── Encounter
            └── Patient
                └── Session

At Phase C, this is intentionally a minimal scaffold.
It is built NOW because:
    - The ADK will depend on it from Day 1 of Phase D
    - Every Plugin receives a ContextScope on invocation
    - Multi-tenancy is baked in from the start — not retrofitted later

When Speech, Vision, OCR, and Medical NLP arrive, they receive:
    invoke(audio, context=ContextScope(organization_id=..., patient_id=..., encounter_id=...))

The plugin never needs to worry about multi-tenancy because the Kernel
enforces it through the ContextScope.
"""
from __future__ import annotations

import logging
from typing import Any

from apps.runtime.src.domain.entities import ContextScope

logger = logging.getLogger("astera.kernel.context")


class ContextManager:
    """
    Manages the lifecycle of all active ContextScopes in the Kernel.

    Responsibilities:
        - Create and destroy ContextScopes
        - Maintain an in-memory index of active sessions
        - Provide context lookup by session_id, encounter_id, etc.

    Phase C scope:
        - In-memory only (no persistence)
        - System context always available
        - API to create/destroy contexts

    Phase D+ extensions:
        - Persist contexts to Redis (session TTL)
        - Publish context events to EventBus
        - Context-based routing to Capabilities
    """

    def __init__(self) -> None:
        # session_id → ContextScope
        self._sessions: dict[str, ContextScope] = {}
        # Pre-create the system context
        self._system_context = ContextScope.system()
        logger.info("ContextManager initialized")

    # ── System Context ────────────────────────────────────────────────────────

    @property
    def system_context(self) -> ContextScope:
        """The system-level context. Always available. No clinical data."""
        return self._system_context

    # ── Session Lifecycle ─────────────────────────────────────────────────────

    def create_session(
        self,
        organization_id: str,
        workspace_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ContextScope:
        """
        Create a new session context for an authenticated user.

        Args:
            organization_id: The tenant organization.
            workspace_id: The workspace within the organization.
            user_id: The authenticated user initiating the session.
            metadata: Arbitrary session metadata.

        Returns:
            A new ContextScope with a unique session_id.
        """
        ctx = ContextScope(
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            metadata=metadata or {},
        )
        self._sessions[ctx.session_id] = ctx

        logger.info(
            "Session created",
            extra={
                "session_id": ctx.session_id,
                "organization_id": organization_id,
                "workspace_id": workspace_id,
            },
        )

        return ctx

    def start_encounter(
        self,
        session_id: str,
        encounter_id: str,
        patient_id: str,
    ) -> ContextScope:
        """
        Attach an Encounter and Patient to an existing session.

        This transitions the session from workspace context to clinical context.
        After this call, the session is_clinical() == True.
        """
        ctx = self._get_or_raise(session_id)
        ctx.encounter_id = encounter_id
        ctx.patient_id = patient_id

        logger.info(
            "Encounter started",
            extra={
                "session_id": session_id,
                "encounter_id": encounter_id,
                "patient_id": patient_id,
            },
        )

        return ctx

    def end_session(self, session_id: str) -> None:
        """
        Terminate a session and remove it from the active index.

        Called when the user logs out or the session expires.
        """
        ctx = self._sessions.pop(session_id, None)
        if ctx:
            logger.info("Session ended", extra={"session_id": session_id})
        else:
            logger.warning("Attempted to end unknown session", extra={"session_id": session_id})

    # ── Query ─────────────────────────────────────────────────────────────────

    def get_session(self, session_id: str) -> ContextScope | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[ContextScope]:
        return list(self._sessions.values())

    def active_session_count(self) -> int:
        return len(self._sessions)

    def active_clinical_session_count(self) -> int:
        return sum(1 for ctx in self._sessions.values() if ctx.is_clinical())

    # ── Introspection ─────────────────────────────────────────────────────────

    def summary(self) -> dict[str, Any]:
        return {
            "active_sessions": self.active_session_count(),
            "active_clinical_sessions": self.active_clinical_session_count(),
        }

    # ── Private ───────────────────────────────────────────────────────────────

    def _get_or_raise(self, session_id: str) -> ContextScope:
        ctx = self._sessions.get(session_id)
        if ctx is None:
            from apps.runtime.src.domain.exceptions import AsteraError
            raise AsteraError(
                f"Session '{session_id}' not found.",
                code="SESSION_NOT_FOUND",
            )
        return ctx
