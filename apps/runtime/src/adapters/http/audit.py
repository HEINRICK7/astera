"""HTTP adapter for tenant-scoped audit records."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from packages.audit_sdk import AuditPort
from packages.auth_sdk import AuthenticationError, AuthorizationError
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort


def create_audit_router(*, audit_log: AuditPort, auth_service: AuthenticationPort) -> APIRouter:
    """Create the protected audit query route."""
    router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])
    bearer = HTTPBearer(auto_error=False)

    async def principal_from(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    ):
        if credentials is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required")
        try:
            principal = auth_service.authenticate(credentials.credentials)
            auth_service.require_permission(principal, "audit:read")
            return principal
        except AuthenticationError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        except AuthorizationError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    @router.get("", summary="Read organization audit trail")
    async def list_audit(
        action: str | None = Query(default=None, min_length=1),
        limit: int = Query(default=100, ge=1, le=500),
        principal=Depends(principal_from),
    ) -> JSONResponse:
        entries = audit_log.list_for_organization(
            principal.organization_id,
            limit=limit,
            action=action,
        )
        return JSONResponse(
            content={"success": True, "data": [entry.to_dict() for entry in entries]}
        )

    return router
