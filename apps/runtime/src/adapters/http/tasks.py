"""Versioned API adapter for declarative Runtime task execution."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from apps.runtime.src.application.orchestrator.task_intent import TaskIntent
from apps.runtime.src.domain.entities.context_scope import ContextScope
from apps.runtime.src.domain.value_objects.capability_type import CapabilityType
from apps.runtime.src.ports.inbound import TaskExecutionPort


class ExecuteTaskRequest(BaseModel):
    """Public request contract for one capability execution."""

    capability_type: CapabilityType = CapabilityType.PLATFORM_ECHO
    payload: Any = None
    organization_id: str = Field(default="system", min_length=1)
    workspace_id: str | None = None
    encounter_id: str | None = None
    patient_id: str | None = None
    request_id: str | None = None


def create_task_router(kernel: TaskExecutionPort) -> APIRouter:
    """Create the versioned task routes for one Kernel instance."""

    router = APIRouter(prefix="/api/v1", tags=["Runtime"])

    @router.post(
        "/tasks",
        summary="Execute a Runtime capability",
        response_description="Standard Astera API response envelope",
    )
    async def execute_task(request: ExecuteTaskRequest) -> JSONResponse:
        context = ContextScope(
            organization_id=request.organization_id,
            workspace_id=request.workspace_id,
            encounter_id=request.encounter_id,
            patient_id=request.patient_id,
        )
        intent_data = {
            "capability_type": request.capability_type,
            "payload": request.payload,
            "context": context,
        }
        if request.request_id:
            intent_data["request_id"] = request.request_id
        try:
            result = await kernel.execute_task(TaskIntent(**intent_data))
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"success": False, "error": {"message": str(exc)}},
            ) from exc

        body = {
            "success": result.success,
            "data": result.to_event_payload() if result.success else None,
            "error": None if result.success else {
                "message": result.error,
                "code": "TASK_FAILED",
            },
            "meta": {"request_id": result.request_id},
            "trace_id": result.request_id,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        }
        return JSONResponse(content=body)

    return router
