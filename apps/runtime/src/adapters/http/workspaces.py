"""HTTP Workspace adapter."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse

from packages.auth_sdk import AuthenticationError
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort, WorkspaceRepositoryPort


def create_workspace_router(
    *,
    directory: WorkspaceRepositoryPort,
    auth_service: AuthenticationPort,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/workspaces", tags=["Workspace"])
    bearer = HTTPBearer(auto_error=False)

    @router.get("")
    async def list_workspaces(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    ) -> JSONResponse:
        if credentials is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
        try:
            principal = auth_service.authenticate(credentials.credentials)
        except AuthenticationError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        return JSONResponse(
            content={
                "success": True,
                "data": [workspace.to_dict() for workspace in directory.list_for(principal)],
            }
        )

    return router
