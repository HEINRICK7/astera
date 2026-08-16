"""Immutable A2UI document contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class A2UINode:
    node_id: str
    component: str
    props: Mapping[str, Any] = field(default_factory=dict)
    children: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.node_id.strip() or not self.component.strip():
            raise ValueError("A2UI node identity must not be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "component": self.component,
            "props": dict(self.props),
            "children": list(self.children),
        }


@dataclass(frozen=True, slots=True)
class A2UIDocument:
    view_id: str
    version: str
    root_id: str
    nodes: tuple[A2UINode, ...]

    def __post_init__(self) -> None:
        if not self.view_id.strip() or not self.version.strip() or not self.root_id.strip():
            raise ValueError("A2UI document identity must not be empty")
        node_ids = {node.node_id for node in self.nodes}
        if self.root_id not in node_ids:
            raise ValueError("root_id must reference a document node")

    def to_dict(self) -> dict[str, Any]:
        return {
            "view_id": self.view_id,
            "version": self.version,
            "root_id": self.root_id,
            "nodes": [node.to_dict() for node in self.nodes],
        }
