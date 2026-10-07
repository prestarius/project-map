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

    def test_renderer_supports_persistent_layout(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        data["nodes"][0]["layout"] = {"x": 321, "y": 654, "pinned": True}

        output = render(data)

        self.assertIn("n.layout.x", output)
        self.assertIn("computeLevels", output)
        self.assertIn('id="save-layout"', output)
        self.assertIn("project-map.layout.json", output)

    def test_renderer_supports_groups_and_swimlanes(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        data["groups"] = [{"id": "core", "name": "Core"}]
        data["nodes"][0]["groupId"] = "core"

        output = render(data)

        self.assertIn('id="groups"', output)
        self.assertIn('id="group-filter"', output)
        self.assertIn("drawGroups", output)
        self.assertIn("Core", output)

    def test_renderer_supports_collapsible_nested_groups(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        data["groups"] = [
            {"id": "parent", "name": "Parent", "collapsed": True},
            {"id": "child", "name": "Child", "parentGroupId": "parent"},
        ]
        data["nodes"][0]["groupId"] = "child"

        output = render(data)

        self.assertIn("collapsedGroups", output)
        self.assertIn("descendantGroupIds", output)
        self.assertIn("groupStatus", output)
        self.assertIn("parentGroupId", output)

    def test_renderer_supports_overview_and_aggregated_edges(self):
        data = json.loads(Path("project-map.json").read_text(encoding="utf-8"))

        output = render(data)

        self.assertIn('id="overview"', output)
        self.assertIn('id="overview-groups"', output)
        self.assertIn('id="overview-edges"', output)
        self.assertIn("aggregatedGroupEdges", output)
        self.assertIn("rootGroupId", output)
        self.assertIn("drawOverview", output)

    def test_renderer_supports_overview_drilldown(self):
        data = json.loads(Path("project-map.json").read_text(encoding="utf-8"))

        output = render(data)

        self.assertIn("drillIntoGroup", output)
        self.assertIn("inspectOverviewEdge", output)
        self.assertIn("underlyingRelations", output)
        self.assertIn("box.addEventListener('click'", output)

    def test_renderer_contains_polished_demo_ui(self):
        data = json.loads(Path("project-map.json").read_text(encoding="utf-8"))
        output = render(data)

        self.assertIn('id="statsbar"', output)
        self.assertIn('id="breadcrumbs"', output)
        self.assertIn("nodeGradient", output)
        self.assertIn("overviewGradient", output)
        self.assertIn("marker id=\"arrow\"", output)
        self.assertIn("renderStats", output)
        self.assertIn("renderBreadcrumbs", output)
        self.assertIn("edge connected", output.replace(".", " "))

    def test_dogfood_map_uses_supported_statuses(self):
        data = json.loads(Path("project-map.json").read_text(encoding="utf-8"))
        allowed = {"planned", "in_progress", "needs_review", "blocked", "done"}

        for node in data["nodes"]:
            self.assertIn(node["status"], allowed)


if __name__ == "__main__":
    unittest.main()
