"""HTTP adapter for LGPD consent and data-subject workflows."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from packages.auth_sdk import AuthenticationError, AuthorizationError
from packages.privacy_sdk import ConsentRecord, DataSubjectRequest, PrivacyPort
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort


class ConsentRequest(BaseModel):
    subject_id: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    policy_version: str = Field(min_length=1)
    granted: bool


class DataSubjectRequestBody(BaseModel):
    subject_id: str = Field(min_length=1)
    request_type: str = Field(pattern="^(access|rectification|erasure|portability)$")


def create_privacy_router(*, privacy: PrivacyPort, auth_service: AuthenticationPort) -> APIRouter:
    router = APIRouter(prefix="/api/v1/privacy", tags=["LGPD"])
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

    def require(principal, permission: str) -> None:
        try:
            auth_service.require_permission(principal, permission)
        except AuthorizationError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    @router.post("/consents")
    async def record_consent(body: ConsentRequest, principal=Depends(principal_from)) -> JSONResponse:
        require(principal, "privacy:write")
        consent = ConsentRecord.create(
            organization_id=principal.organization_id,
            subject_id=body.subject_id,
            purpose=body.purpose,
            policy_version=body.policy_version,
            granted=body.granted,
        )
        privacy.record_consent(consent)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"success": True, "data": consent.to_dict()})

    @router.post("/requests")
    async def create_request(body: DataSubjectRequestBody, principal=Depends(principal_from)) -> JSONResponse:
        require(principal, "privacy:write")
        request = DataSubjectRequest.create(
            organization_id=principal.organization_id,
            subject_id=body.subject_id,
            request_type=body.request_type,
        )
        privacy.request(request)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"success": True, "data": request.to_dict()})

    @router.get("/requests")
    async def list_requests(
        subject_id: str | None = None,
        principal=Depends(principal_from),
    ) -> JSONResponse:
        require(principal, "privacy:read")
        requests = privacy.list_requests(principal.organization_id, subject_id)
        return JSONResponse(content={"success": True, "data": [item.to_dict() for item in requests]})

    @router.get("/consents/{subject_id}")
    async def list_consents(subject_id: str, principal=Depends(principal_from)) -> JSONResponse:
        require(principal, "privacy:read")
        consents = privacy.list_consents(principal.organization_id, subject_id)
        return JSONResponse(content={"success": True, "data": [item.to_dict() for item in consents]})

    return router
