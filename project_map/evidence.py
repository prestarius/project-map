"""Deterministic evidence collection and status derivation."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from project_map.github import provenance_from_github

PASS = "pass"
FAIL = "fail"
UNKNOWN = "unknown"
NOT_APPLICABLE = "not_applicable"


def collect_evidence(evidence: dict[str, Any], root: Path) -> dict[str, Any]:
    """Return an evidence entry updated from its optional collector definition."""
    result = dict(evidence)
    collector = evidence.get("collector")
    if not collector:
        return result

    kind = collector.get("type")
    try:
        if kind == "path_exists":
            path = root / collector["path"]
            exists = path.exists()
            result["state"] = PASS if exists else FAIL
            result["detail"] = f"{collector['path']} {'exists' if exists else 'missing'}"
        elif kind == "command":
            command = collector.get("command")
            if not isinstance(command, list) or not command:
                raise ValueError("command collector requires a non-empty command array")
            completed = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=int(collector.get("timeoutSeconds", 120)),
                check=False,
            )
            result["state"] = PASS if completed.returncode == 0 else FAIL
            output = (completed.stdout or completed.stderr or "").strip().splitlines()
            suffix = output[-1] if output else f"exit {completed.returncode}"
            result["detail"] = f"{' '.join(command)} — {suffix}"[:500]
        elif kind == "github_actions":
            conclusion = collector.get("conclusion") or os.environ.get("PROJECT_MAP_GITHUB_CONCLUSION")
            result["provenance"] = provenance_from_github()
            if conclusion == "success":
                result["state"] = PASS
                result["detail"] = "GitHub Actions conclusion: success"
            elif conclusion in {"failure", "cancelled", "timed_out"}:
                result["state"] = FAIL
                result["detail"] = f"GitHub Actions conclusion: {conclusion}"
            else:
                result["state"] = UNKNOWN
                result["detail"] = "GitHub Actions context captured; conclusion not provided"
        elif kind == "git_clean":
            completed = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            if completed.returncode != 0:
                result["state"] = UNKNOWN
                result["detail"] = (completed.stderr or "git status failed").strip()[:500]
            else:
                clean = not completed.stdout.strip()
                result["state"] = PASS if clean else FAIL
                result["detail"] = "working tree clean" if clean else "working tree has uncommitted changes"
        else:
            result["state"] = UNKNOWN
            result["detail"] = f"unknown collector type: {kind}"
    except (OSError, KeyError, subprocess.TimeoutExpired, ValueError) as exc:
        result["state"] = UNKNOWN
        result["detail"] = str(exc)[:500]

    return result


def derive_status(node: dict[str, Any]) -> str:
    """Derive node status from evidence without overriding an explicit blocker."""
    if node.get("status") == "blocked":
        return "blocked"

    evidence = node.get("evidence", {})
    required = [item for item in evidence.values() if item.get("required", False)]

    if not required:
        return "in_progress" if int(node.get("progress", 0)) > 0 else "planned"

    states = [item.get("state", UNKNOWN) for item in required]
    if all(state in (PASS, NOT_APPLICABLE) for state in states):
        return "done"
    if FAIL in states:
        return "needs_review"

    implementation = evidence.get("implementation", {})
    if implementation.get("state") == PASS:
        return "needs_review"

    return "in_progress" if int(node.get("progress", 0)) > 0 else "planned"


def derive_progress(node: dict[str, Any]) -> int:
    """Estimate progress from required evidence when available."""
    required = [item for item in node.get("evidence", {}).values() if item.get("required", False)]
    if not required:
        return int(node.get("progress", 0))

    passed = sum(1 for item in required if item.get("state") in (PASS, NOT_APPLICABLE))
    return round((passed / len(required)) * 100)
