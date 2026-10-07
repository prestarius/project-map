import json
import tempfile
import unittest
from pathlib import Path

from project_map.cli import main, update_map


class CliTests(unittest.TestCase):
    def test_validate_command_accepts_example(self):
        self.assertEqual(0, main(["--map", "examples/project-map.json", "validate"]))

    def test_update_map_collects_and_derives_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "implemented.txt").write_text("yes", encoding="utf-8")
            data = {
                "version": "1.0",
                "project": {"id": "x", "name": "X"},
                "views": [{"id": "delivery", "name": "Delivery"}],
                "nodes": [{
                    "id": "feature",
                    "title": "Feature",
                    "status": "in_progress",
                    "progress": 10,
                    "views": ["delivery"],
                    "evidence": {
                        "implementation": {
                            "required": True,
                            "state": "unknown",
                            "collector": {"type": "path_exists", "path": "implemented.txt"}
                        }
                    }
                }],
                "edges": []
            }

            updated = update_map(data, root)

            self.assertEqual("pass", updated["nodes"][0]["evidence"]["implementation"]["state"])
            self.assertEqual("done", updated["nodes"][0]["status"])
            self.assertEqual(100, updated["nodes"][0]["progress"])


if __name__ == "__main__":
    unittest.main()
