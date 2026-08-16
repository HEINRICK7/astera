"""HTTP patient timeline adapter."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse

from packages.auth_sdk import AuthenticationError
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort, TimelineRepositoryPort


def create_timeline_router(
    *,
    directory: TimelineRepositoryPort,
    auth_service: AuthenticationPort,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patients", tags=["Timeline"])
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

    @router.get("/{patient_id}/timeline")
    async def list_timeline(patient_id: str, principal=Depends(principal_from)) -> JSONResponse:
        return JSONResponse(
            content={
                "success": True,
                "data": [event.to_dict() for event in directory.list_for(principal, patient_id)],
            }
        )

    return router
