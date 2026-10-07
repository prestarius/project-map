"""Dependency-free validation for the Project Map v1 core contract."""

from __future__ import annotations

from typing import Any

STATUSES = {"planned", "in_progress", "needs_review", "blocked", "done"}
EVIDENCE_STATES = {"pass", "fail", "unknown", "not_applicable"}
EDGE_TYPES = {"depends_on", "contains", "implements", "blocks", "relates_to"}


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if data.get("version") != "1.0":
        errors.append("version must be '1.0'")

    project = data.get("project")
    if not isinstance(project, dict) or not project.get("id") or not project.get("name"):
        errors.append("project.id and project.name are required")

    views = data.get("views", [])
    view_ids = {v.get("id") for v in views if isinstance(v, dict)}
    if len(view_ids) != len(views):
        errors.append("view ids must be present and unique")

    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        errors.append("nodes must be an array")
        nodes = []

    node_ids: set[str] = set()
    for index, node in enumerate(nodes):
        prefix = f"nodes[{index}]"
        node_id = node.get("id")
        if not node_id:
            errors.append(f"{prefix}.id is required")
        elif node_id in node_ids:
            errors.append(f"duplicate node id: {node_id}")
        else:
            node_ids.add(node_id)

        if not node.get("title"):
            errors.append(f"{prefix}.title is required")
        if node.get("status") not in STATUSES:
            errors.append(f"{prefix}.status is invalid")
        if not isinstance(node.get("views"), list):
            errors.append(f"{prefix}.views must be an array")
        else:
            unknown_views = set(node["views"]) - view_ids
            if unknown_views:
                errors.append(f"{prefix}.views references unknown views: {sorted(unknown_views)}")

        progress = node.get("progress", 0)
        if not isinstance(progress, int) or not 0 <= progress <= 100:
            errors.append(f"{prefix}.progress must be an integer from 0 to 100")

        for name, evidence in node.get("evidence", {}).items():
            if evidence.get("state") not in EVIDENCE_STATES:
                errors.append(f"{prefix}.evidence.{name}.state is invalid")
            collector = evidence.get("collector")
            if collector is not None and not isinstance(collector, dict):
                errors.append(f"{prefix}.evidence.{name}.collector must be an object")

    for index, edge in enumerate(data.get("edges", [])):
        prefix = f"edges[{index}]"
        if edge.get("from") not in node_ids:
            errors.append(f"{prefix}.from references unknown node: {edge.get('from')}")
        if edge.get("to") not in node_ids:
            errors.append(f"{prefix}.to references unknown node: {edge.get('to')}")
        if edge.get("type") not in EDGE_TYPES:
            errors.append(f"{prefix}.type is invalid")

    return errors
