import json
import tempfile
import unittest
from pathlib import Path

from scripts.render import render


class RenderTests(unittest.TestCase):
    def test_example_renders_expected_project_and_nodes(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        output = render(data)

        self.assertIn("Example Agentic Project", output)
        self.assertIn("Daily Planning", output)
        self.assertIn("Relationships", output)
        self.assertIn("data-view='architecture'", output)

    def test_dogfood_map_uses_supported_statuses(self):
        data = json.loads(Path("project-map.json").read_text(encoding="utf-8"))
        allowed = {"planned", "in_progress", "needs_review", "blocked", "done"}

        for node in data["nodes"]:
            self.assertIn(node["status"], allowed)


if __name__ == "__main__":
    unittest.main()
