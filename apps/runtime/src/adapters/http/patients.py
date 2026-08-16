"""HTTP Patient adapter."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from packages.auth_sdk import AuthenticationError
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort, PatientRepositoryPort


class CreatePatientRequest(BaseModel):
    full_name: str


def create_patient_router(
    *,
    directory: PatientRepositoryPort,
    auth_service: AuthenticationPort,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patients", tags=["Patient"])
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
    async def create_patient(
        request: CreatePatientRequest,
        principal=Depends(principal_from),
    ) -> JSONResponse:
        patient = directory.create(principal, full_name=request.full_name)
        return JSONResponse(content={"success": True, "data": patient.to_dict()})

    @router.get("")
    async def list_patients(principal=Depends(principal_from)) -> JSONResponse:
        return JSONResponse(
            content={
                "success": True,
                "data": [patient.to_dict() for patient in directory.list_for(principal)],
            }
        )

    return router
