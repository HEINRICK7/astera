"""Governance checks for benchmark provider code and data assets."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


APPROVED_FOR_BENCHMARK = "APPROVED_FOR_BENCHMARK"
APPROVED_FOR_PRODUCTION = "APPROVED_FOR_PRODUCTION"
RESEARCH_ONLY = "RESEARCH_ONLY"
BLOCKED = "BLOCKED"
PENDING_REVIEW = "PENDING_REVIEW"


@dataclass(frozen=True, slots=True)
class AssetRecord:
    asset_id: str
    provider: str
    code_license: str
    asset_type: str
    asset_source: str
    asset_version: str
    vocabulary: str
    vocabulary_version: str
    model_license: str
    data_license: str
    commercial_use: bool | None
    redistribution_allowed: bool | None
    territory: str
    approved_for: tuple[str, ...]
    checksum: str | None
    download_origin: str
    approval_status: str

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AssetRecord":
        required = {
            "asset_id", "provider", "code_license", "asset_type", "asset_source",
            "asset_version", "vocabulary", "vocabulary_version", "model_license",
            "data_license", "commercial_use", "redistribution_allowed", "territory",
            "approved_for", "checksum", "download_origin", "approval_status",
        }
        missing = required - payload.keys()
        if missing:
            raise ValueError(f"Asset record missing fields: {sorted(missing)}")
        return cls(
            asset_id=str(payload["asset_id"]),
            provider=str(payload["provider"]),
            code_license=str(payload["code_license"]),
            asset_type=str(payload["asset_type"]),
            asset_source=str(payload["asset_source"]),
            asset_version=str(payload["asset_version"]),
            vocabulary=str(payload["vocabulary"]),
            vocabulary_version=str(payload["vocabulary_version"]),
            model_license=str(payload["model_license"]),
            data_license=str(payload["data_license"]),
            commercial_use=payload["commercial_use"],
            redistribution_allowed=payload["redistribution_allowed"],
            territory=str(payload["territory"]),
            approved_for=tuple(str(item) for item in payload["approved_for"]),
            checksum=payload["checksum"],
            download_origin=str(payload["download_origin"]),
            approval_status=str(payload["approval_status"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "provider": self.provider,
            "code_license": self.code_license,
            "asset_type": self.asset_type,
            "asset_source": self.asset_source,
            "asset_version": self.asset_version,
            "vocabulary": self.vocabulary,
            "vocabulary_version": self.vocabulary_version,
            "model_license": self.model_license,
            "data_license": self.data_license,
            "commercial_use": self.commercial_use,
            "redistribution_allowed": self.redistribution_allowed,
            "territory": self.territory,
            "approved_for": list(self.approved_for),
            "checksum": self.checksum,
            "download_origin": self.download_origin,
            "approval_status": self.approval_status,
        }


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    provider: str
    purpose: str
    allowed: bool
    status: str
    reasons: tuple[str, ...]
    assets: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "purpose": self.purpose,
            "allowed": self.allowed,
            "status": self.status,
            "reasons": list(self.reasons),
            "assets": list(self.assets),
        }


class AssetRegistry:
    def __init__(self, records: Iterable[AssetRecord]) -> None:
        self._records = tuple(records)

    def records_for(self, provider: str) -> tuple[AssetRecord, ...]:
        return tuple(record for record in self._records if record.provider == provider)

    def authorize(self, provider: str, purpose: str) -> AuthorizationDecision:
        records = self.records_for(provider)
        reasons: list[str] = []
        if not records:
            reasons.append("provider has no registered assets")
        for record in records:
            if record.approval_status == BLOCKED:
                reasons.append(f"{record.asset_id}: BLOCKED")
            elif record.approval_status == PENDING_REVIEW:
                reasons.append(f"{record.asset_id}: PENDING_REVIEW")
            elif record.approval_status == RESEARCH_ONLY and purpose != "research":
                reasons.append(f"{record.asset_id}: RESEARCH_ONLY")
            if purpose not in record.approved_for:
                reasons.append(f"{record.asset_id}: not approved for {purpose}")
            if record.checksum is None and record.asset_type not in {"code", "runtime"}:
                reasons.append(f"{record.asset_id}: checksum missing")
        allowed = not reasons
        return AuthorizationDecision(
            provider=provider,
            purpose=purpose,
            allowed=allowed,
            status=APPROVED_FOR_BENCHMARK if allowed else BLOCKED,
            reasons=tuple(reasons),
            assets=tuple(record.asset_id for record in records),
        )

    def verify_path(self, asset_id: str, path: Path) -> bool:
        record = next((item for item in self._records if item.asset_id == asset_id), None)
        if record is None or record.checksum in {None, "not_applicable"}:
            return False
        return _sha256(path) == record.checksum


def load_registry(path: Path | None = None) -> AssetRegistry:
    registry_path = path or Path(__file__).with_name("data") / "provider_asset_registry.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    records = tuple(AssetRecord.from_dict(item) for item in payload["assets"])
    return AssetRegistry(records)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
