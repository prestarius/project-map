import json
import unittest
from pathlib import Path

from project_map.validation import validate


class ValidationTests(unittest.TestCase):
    def test_example_is_valid(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        self.assertEqual([], validate(data))

    def test_unknown_edge_node_is_rejected(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        data["edges"].append({"from": "missing", "to": "domain", "type": "depends_on"})
        self.assertTrue(any("unknown node" in error for error in validate(data)))

    def test_unknown_group_reference_is_rejected(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        data["groups"] = [{"id": "known", "name": "Known"}]
        data["nodes"][0]["groupId"] = "missing"

        self.assertTrue(any("unknown group" in error for error in validate(data)))

    def test_unknown_parent_group_is_rejected(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        data["groups"] = [{"id": "child", "name": "Child", "parentGroupId": "missing"}]
        self.assertTrue(any("parentGroupId references unknown group" in error for error in validate(data)))

    def test_group_cycle_is_rejected(self):
        data = json.loads(Path("examples/project-map.json").read_text(encoding="utf-8"))
        data["groups"] = [
            {"id": "a", "name": "A", "parentGroupId": "b"},
            {"id": "b", "name": "B", "parentGroupId": "a"},
        ]
        self.assertTrue(any("hierarchy contains a cycle" in error for error in validate(data)))


if __name__ == "__main__":
    unittest.main()
