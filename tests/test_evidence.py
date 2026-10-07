import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
