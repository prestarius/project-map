import json
import unittest
from pathlib import Path

from scripts.render import render


class RenderTests(unittest.TestCase):
    def test_example_renders_interactive_graph_ui(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        output = render(data)

        self.assertIn("Example Agentic Project", output)
        self.assertIn('aria-label="Interactive project graph"', output)
        self.assertIn('id="inspector"', output)
        self.assertIn('id="search"', output)
        self.assertIn('id="zin"', output)
        self.assertIn("data-view=\'architecture\'", output)
        self.assertIn("Daily Planning", output)

    def test_renderer_embeds_graph_data_and_relationships(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        output = render(data)

        self.assertIn('"depends_on"', output)
        self.assertIn('"nodes"', output)
        self.assertIn('"edges"', output)

    def test_renderer_contains_provenance_and_node_link_support(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        data["nodes"][0]["links"] = [{"label": "PR #1", "url": "https://github.com/example/repo/pull/1"}]
        data["nodes"][0]["evidence"]["implementation"]["provenance"] = [
            {"kind": "commit", "label": "Commit abc1234", "url": "https://github.com/example/repo/commit/abc1234"}
        ]

        output = render(data)

        self.assertIn("Commit abc1234", output)
        self.assertIn("PR #1", output)
        self.assertIn("link-list", output)

    def test_dogfood_map_uses_supported_statuses(self):
        data = json.loads(Path("project-map.json").read_text(encoding="utf-8"))
        allowed = {"planned", "in_progress", "needs_review", "blocked", "done"}

        for node in data["nodes"]:
            self.assertIn(node["status"], allowed)


if __name__ == "__main__":
    unittest.main()
