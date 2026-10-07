import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from project_map.evidence import collect_evidence, derive_progress, derive_status


class EvidenceTests(unittest.TestCase):
    def test_path_exists_collector(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "feature.txt").write_text("ok", encoding="utf-8")
            evidence = {
                "required": True,
                "state": "unknown",
                "collector": {"type": "path_exists", "path": "feature.txt"},
            }

            result = collect_evidence(evidence, root)

            self.assertEqual("pass", result["state"])

    def test_command_collector_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            result = collect_evidence(
                {
                    "required": True,
                    "state": "unknown",
                    "collector": {
                        "type": "command",
                        "command": ["python", "-c", "raise SystemExit(3)"],
                    },
                },
                Path(directory),
            )
            self.assertEqual("fail", result["state"])

    def test_done_requires_all_required_evidence(self):
        node = {
            "status": "in_progress",
            "progress": 30,
            "evidence": {
                "implementation": {"required": True, "state": "pass"},
                "tests": {"required": True, "state": "pass"},
            },
        }
        self.assertEqual("done", derive_status(node))
        self.assertEqual(100, derive_progress(node))

    def test_unknown_verification_becomes_needs_review(self):
        node = {
            "status": "in_progress",
            "progress": 50,
            "evidence": {
                "implementation": {"required": True, "state": "pass"},
                "ci": {"required": True, "state": "unknown"},
            },
        }
        self.assertEqual("needs_review", derive_status(node))

    def test_github_actions_collector_attaches_provenance_without_guessing(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_SERVER_URL": "https://github.com",
            "GITHUB_REPOSITORY": "prestarius/project-map",
            "GITHUB_SHA": "abcdef1234567890",
            "GITHUB_RUN_ID": "98765",
        }
        with patch.dict(os.environ, env, clear=True):
            result = collect_evidence(
                {
                    "required": True,
                    "state": "unknown",
                    "collector": {"type": "github_actions"},
                },
                Path("."),
            )

        self.assertEqual("unknown", result["state"])
        self.assertEqual(2, len(result["provenance"]))

    def test_github_actions_collector_accepts_explicit_success(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": "prestarius/project-map",
            "GITHUB_SHA": "abcdef1234567890",
            "PROJECT_MAP_GITHUB_CONCLUSION": "success",
        }
        with patch.dict(os.environ, env, clear=True):
            result = collect_evidence(
                {
                    "required": True,
                    "state": "unknown",
                    "collector": {"type": "github_actions"},
                },
                Path("."),
            )

        self.assertEqual("pass", result["state"])


if __name__ == "__main__":
    unittest.main()
