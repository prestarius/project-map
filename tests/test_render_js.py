import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.render import render


class RenderedJavaScriptTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "node is required for generated JavaScript syntax check")
    def test_generated_javascript_has_valid_syntax(self):
        data = json.loads(Path("examples/project-map-self-demo.json").read_text(encoding="utf-8"))
        output = render(data)
        match = re.search(r"<script>(.*?)</script>", output, re.DOTALL)
        self.assertIsNotNone(match, "rendered HTML must contain a script block")

        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "project-map-rendered.js"
            script.write_text(match.group(1), encoding="utf-8")
            completed = subprocess.run(
                ["node", "--check", str(script)],
                capture_output=True,
                text=True,
            )

        self.assertEqual(
            0,
            completed.returncode,
            msg=completed.stderr or completed.stdout,
        )


if __name__ == "__main__":
    unittest.main()
