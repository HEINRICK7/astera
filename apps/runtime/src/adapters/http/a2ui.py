"""HTTP A2UI adapter."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse

from packages.auth_sdk import AuthenticationError, AuthorizationError
from apps.runtime.src.application.a2ui import A2UIService
from apps.runtime.src.ports.outbound.persistence import (
    AuthenticationPort,
    EncounterRepositoryPort,
    PatientRepositoryPort,
    TimelineRepositoryPort,
)


def create_a2ui_router(
    *,
    service: A2UIService,
    auth_service: AuthenticationPort,
    encounters: EncounterRepositoryPort,
    patients: PatientRepositoryPort,
    timeline: TimelineRepositoryPort,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/a2ui", tags=["A2UI"])
    bearer = HTTPBearer(auto_error=False)

    async def principal_from(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    ):
        if credentials is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
        try:
            return auth_service.authenticate(credentials.credentials)
        except AuthenticationError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    @router.get("/workspace")
    async def workspace_view(principal=Depends(principal_from)) -> JSONResponse:
        return JSONResponse(content={"success": True, "data": service.workspace_view(principal).to_dict()})

    @router.get("/encounters/{encounter_id}")
    async def consultation_view(encounter_id: str, principal=Depends(principal_from)) -> JSONResponse:
        try:
            encounter = encounters.get(principal, encounter_id)
        except (KeyError, AuthorizationError) as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="encounter not found") from exc
        patient = patients.get(principal, encounter.patient_id)
        if patient is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="patient not found")
        events = timeline.list_for(principal, patient.patient_id)
        document = service.consultation_view(patient=patient, encounter=encounter, timeline=events, result=None)
        return JSONResponse(content={"success": True, "data": document.to_dict()})

    return router
