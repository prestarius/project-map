import unittest

from project_map.github import github_context, provenance_from_github


class GitHubContextTests(unittest.TestCase):
    def test_context_builds_commit_and_run_urls(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_SERVER_URL": "https://github.com",
            "GITHUB_REPOSITORY": "prestarius/project-map",
            "GITHUB_SHA": "abcdef1234567890",
            "GITHUB_RUN_ID": "12345",
            "GITHUB_REF_NAME": "feat/example",
            "GITHUB_EVENT_NAME": "pull_request",
        }

        context = github_context(env)

        self.assertEqual("github", context["provider"])
        self.assertEqual(
            "https://github.com/prestarius/project-map/commit/abcdef1234567890",
            context["commit"]["url"],
        )
        self.assertEqual(
            "https://github.com/prestarius/project-map/actions/runs/12345",
            context["run"]["url"],
        )

    def test_provenance_is_empty_outside_actions(self):
        self.assertEqual([], provenance_from_github({}))


if __name__ == "__main__":
    unittest.main()
