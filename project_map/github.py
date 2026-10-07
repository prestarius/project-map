"""GitHub provenance helpers using standard GitHub Actions environment variables."""

from __future__ import annotations

import os
from typing import Mapping, Any


def github_context(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = os.environ if env is None else env
    if env.get("GITHUB_ACTIONS") != "true":
        return {}

    server = env.get("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    repository = env.get("GITHUB_REPOSITORY")
    sha = env.get("GITHUB_SHA")
    run_id = env.get("GITHUB_RUN_ID")
    ref_name = env.get("GITHUB_HEAD_REF") or env.get("GITHUB_REF_NAME")
    event_name = env.get("GITHUB_EVENT_NAME")

    context: dict[str, Any] = {
        "provider": "github",
        "event": event_name,
        "ref": ref_name,
    }

    if repository:
        context["repository"] = repository
        context["repositoryUrl"] = f"{server}/{repository}"
        if sha:
            context["commit"] = {
                "sha": sha,
                "url": f"{server}/{repository}/commit/{sha}",
                "label": sha[:7],
            }
        if run_id:
            context["run"] = {
                "id": run_id,
                "url": f"{server}/{repository}/actions/runs/{run_id}",
                "label": f"Actions run {run_id}",
            }

    return {k: v for k, v in context.items() if v not in (None, "")}


def provenance_from_github(env: Mapping[str, str] | None = None) -> list[dict[str, str]]:
    context = github_context(env)
    items: list[dict[str, str]] = []

    commit = context.get("commit")
    if commit:
        items.append({
            "kind": "commit",
            "url": commit["url"],
            "label": f"Commit {commit['label']}",
            "ref": commit["sha"],
        })

    run = context.get("run")
    if run:
        items.append({
            "kind": "ci_run",
            "url": run["url"],
            "label": run["label"],
            "ref": run["id"],
        })

    return items
