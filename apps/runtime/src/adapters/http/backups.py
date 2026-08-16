"""HTTP adapter for backup manifests."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from packages.auth_sdk import AuthenticationError, AuthorizationError
from packages.backup_sdk import BackupPort
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort


def create_backup_router(*, backups: BackupPort, auth_service: AuthenticationPort) -> APIRouter:
    router = APIRouter(prefix="/api/v1/backups", tags=["Backups"])
    bearer = HTTPBearer(auto_error=False)

    async def principal_from(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    ):
        if credentials is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
        try:
            principal = auth_service.authenticate(credentials.credentials)
            auth_service.require_permission(principal, "backup:read")
            return principal
        except AuthenticationError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        except AuthorizationError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    @router.get("", summary="List verified backup manifests")
    async def list_backups(principal=Depends(principal_from)) -> JSONResponse:
        del principal
        return JSONResponse(
            content={"success": True, "data": [item.to_dict() for item in backups.list_backups()]}
        )

    return router
