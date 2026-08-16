"""HTTP Dashboard adapter."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse

from packages.auth_sdk import AuthenticationError
from apps.runtime.src.application.dashboard import DashboardService
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort


def create_dashboard_router(*, service: DashboardService, auth_service: AuthenticationPort) -> APIRouter:
    router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])
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

    @router.get("")
    async def dashboard(principal=Depends(principal_from)) -> JSONResponse:
        return JSONResponse(content={"success": True, "data": service.snapshot(principal).to_dict()})

    return router
