"""HTTP adapter for protected enterprise observability snapshots."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from packages.auth_sdk import AuthenticationError, AuthorizationError
from packages.observability_sdk import OperationalObservabilityPort
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort


def create_observability_router(
    *,
    observability: OperationalObservabilityPort,
    auth_service: AuthenticationPort,
) -> APIRouter:
    """Create the operator-facing telemetry route."""
    router = APIRouter(prefix="/api/v1/observability", tags=["Observability"])
    bearer = HTTPBearer(auto_error=False)

    async def principal_from(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    ):
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="authentication required",
            )
        try:
            principal = auth_service.authenticate(credentials.credentials)
            auth_service.require_permission(principal, "observability:read")
            return principal
        except AuthenticationError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        except AuthorizationError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    @router.get("", summary="Read operational observability snapshot")
    async def snapshot(principal=Depends(principal_from)) -> JSONResponse:
        del principal
        return JSONResponse(content={"success": True, "data": observability.snapshot().to_dict()})

    return router
