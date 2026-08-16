"""HTTP Encounter adapter."""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from packages.auth_sdk import AuthenticationError, AuthorizationError
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort, EncounterRepositoryPort


class CreateEncounterRequest(BaseModel):
    workspace_id: str
    patient_id: str


class PatientConsentRequest(BaseModel):
    accepted: bool


class PatientEquipmentRequest(BaseModel):
    camera_ready: bool
    microphone_ready: bool


def create_encounter_router(
    *,
    directory: EncounterRepositoryPort,
    auth_service: AuthenticationPort,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/encounters", tags=["Encounter"])
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

    @router.post("")
    async def create_encounter(
        request: CreateEncounterRequest,
        principal=Depends(principal_from),
    ) -> JSONResponse:
        try:
            encounter = directory.create(
                principal,
                workspace_id=request.workspace_id,
                patient_id=request.patient_id,
            )
        except AuthorizationError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        return JSONResponse(content={"success": True, "data": encounter.to_dict()})

    @router.get("")
    async def list_encounters(principal=Depends(principal_from)) -> JSONResponse:
        encounters = sorted(
            directory.list_for(principal),
            key=lambda item: item.started_at or item.ended_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        return JSONResponse(content={"success": True, "data": [item.to_dict() for item in encounters]})

    # Development invite-link surface. The encounter id is the link secret;
    # production hardening belongs to a later Journey and does not change the
    # existing ConsultationSession or provider boundaries.
    @router.get("/{encounter_id}/patient-journey")
    async def read_patient_journey(encounter_id: str) -> JSONResponse:
        try:
            encounter = directory.get_public(encounter_id)
        except KeyError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="encounter not found") from exc
        return JSONResponse(content={"success": True, "data": encounter.to_dict()})

    @router.post("/{encounter_id}/patient-join")
    async def patient_join(encounter_id: str) -> JSONResponse:
        try:
            encounter = directory.patient_join(encounter_id)
        except KeyError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="encounter not found") from exc
        return JSONResponse(content={"success": True, "data": encounter.to_dict()})

    @router.post("/{encounter_id}/patient-consent")
    async def patient_consent(encounter_id: str, request: PatientConsentRequest) -> JSONResponse:
        try:
            encounter = directory.patient_consent(encounter_id, accepted=request.accepted)
        except KeyError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="encounter not found") from exc
        return JSONResponse(content={"success": True, "data": encounter.to_dict()})

    @router.post("/{encounter_id}/patient-equipment")
    async def patient_equipment(encounter_id: str, request: PatientEquipmentRequest) -> JSONResponse:
        try:
            encounter = directory.patient_equipment(
                encounter_id,
                camera_ready=request.camera_ready,
                microphone_ready=request.microphone_ready,
            )
        except KeyError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="encounter not found") from exc
        return JSONResponse(content={"success": True, "data": encounter.to_dict()})

    @router.post("/{encounter_id}/start")
    async def start_encounter(encounter_id: str, principal=Depends(principal_from)) -> JSONResponse:
        try:
            encounter = directory.start(principal, encounter_id)
        except AuthorizationError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        return JSONResponse(content={"success": True, "data": encounter.to_dict()})

    @router.post("/{encounter_id}/complete")
    async def complete_encounter(encounter_id: str, principal=Depends(principal_from)) -> JSONResponse:
        try:
            encounter = directory.complete(principal, encounter_id)
        except AuthorizationError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        return JSONResponse(content={"success": True, "data": encounter.to_dict()})

    return router
