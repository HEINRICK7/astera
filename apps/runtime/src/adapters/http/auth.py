"""HTTP authentication adapter."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from packages.auth_sdk import AuthenticationError, LoginCredentials
from apps.runtime.src.ports.outbound.persistence import AuthenticationPort


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def create_auth_router(auth_service: AuthenticationPort) -> APIRouter:
    router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

    @router.post("/login")
    async def login(request: LoginRequest) -> JSONResponse:
        try:
            tokens = auth_service.login(LoginCredentials(request.email, request.password))
        except (AuthenticationError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        return JSONResponse(content={"success": True, "data": tokens.to_dict()})

    @router.post("/refresh")
    async def refresh(request: RefreshRequest) -> JSONResponse:
        try:
            tokens = auth_service.refresh(request.refresh_token)
        except AuthenticationError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        return JSONResponse(content={"success": True, "data": tokens.to_dict()})

    return router
