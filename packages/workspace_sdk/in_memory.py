"""Development workspace directory behind the future persistent adapter."""
from __future__ import annotations

from packages.auth_sdk import Principal

from .models import Workspace


class InMemoryWorkspaceRepository:
    """Development adapter for workspace membership records."""

    def __init__(self) -> None:
        self._workspaces: dict[str, Workspace] = {}

    def register(self, workspace: Workspace) -> None:
        self._workspaces[workspace.workspace_id] = workspace

    def list_for(self, principal: Principal) -> tuple[Workspace, ...]:
        return tuple(
            workspace
            for workspace in self._workspaces.values()
            if workspace.organization_id == principal.organization_id
            and workspace.workspace_id in principal.workspace_ids
        )

    def get(self, workspace_id: str) -> Workspace | None:
        return self._workspaces.get(workspace_id)


# Compatibility name for callers migrating from the original directory API.
WorkspaceDirectory = InMemoryWorkspaceRepository
