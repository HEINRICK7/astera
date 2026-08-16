"""HTTP projection for the real-time clinical review workspace."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from packages.auth_sdk import AuthenticationError, AuthorizationError
from apps.runtime.src.ports.outbound.persistence import (
    AuthenticationPort,
    EncounterRepositoryPort,
    ReviewRepositoryPort,
)


def create_clinical_review_router(
    *,
    encounters: EncounterRepositoryPort,
    review_store: ReviewRepositoryPort,
    auth_service: AuthenticationPort,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/clinical-review", tags=["Clinical Review"])
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

    @router.get("/encounters")
    async def list_reviews(principal=Depends(principal_from)) -> JSONResponse:
        result = []
        for encounter in encounters.list_for(principal):
            review = review_store.get(encounter.encounter_id)
            result.append({
                "encounter": encounter.to_dict(),
                "review": review,
            })
        result.sort(
            key=lambda item: item["encounter"].get("started_at")
            or item["encounter"].get("ended_at")
            or "",
            reverse=True,
        )
        return JSONResponse(content={"success": True, "data": result})

    @router.get("/encounters/{encounter_id}")
    async def read_review(encounter_id: str, principal=Depends(principal_from)) -> JSONResponse:
        try:
            encounter = encounters.get(principal, encounter_id)
        except (KeyError, AuthorizationError) as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="encounter not found") from exc
        review = review_store.get(encounter_id)
        return JSONResponse(content={
            "success": True,
            "data": {
                "encounter": encounter.to_dict(),
                "review": review,
            },
        })

    return router
