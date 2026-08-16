"""HTTP adapter for Disaster Recovery readiness."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from packages.auth_sdk import AuthenticationError, AuthorizationError
from packages.disaster_recovery_sdk import RecoveryPort
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort


def create_recovery_router(*, recovery: RecoveryPort, auth_service: AuthenticationPort) -> APIRouter:
    router = APIRouter(prefix="/api/v1/disaster-recovery", tags=["Disaster Recovery"])
    bearer = HTTPBearer(auto_error=False)

    async def principal_from(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    ):
        if credentials is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
        try:
            principal = auth_service.authenticate(credentials.credentials)
            auth_service.require_permission(principal, "recovery:read")
            return principal
        except AuthenticationError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        except AuthorizationError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    @router.get("/status", summary="Read Disaster Recovery readiness")
    async def recovery_status(principal=Depends(principal_from)) -> JSONResponse:
        del principal
        return JSONResponse(content={"success": True, "data": recovery.status().to_dict()})

    return router
