# Project Map v1 Specification

Project Map is a vendor-neutral read model of a software project. It visualizes what exists, what is planned, how parts relate, and why a status is trusted.

## Principles

1. **Repository and delivery systems are sources of truth.** The map is generated state, not a planning database.
2. **Evidence over inference.** Agents must not mark work `done` because code merely exists.
3. **Vendor neutral.** Claude Code, Codex, Kiro, Copilot, humans, or CI can all produce the same format.
4. **Progressive detail.** A project can start with a handful of nodes and later add architecture, delivery, tests, docs, and links.
5. **Human-readable JSON.** The canonical representation is `project-map.json`.

## Status model

Allowed statuses:

- `planned`
- `in_progress`
- `needs_review`
- `blocked`
- `done`

Recommended display:

- ⚪ planned
- 🟡 in progress
- 🔵 needs review
- 🔴 blocked
- 🟢 done

## Evidence-based completion

A node should be `done` only when all required evidence checks pass.

Typical checks:

- implementation exists
- tests pass
- CI passes
- documentation is updated
- acceptance criteria are satisfied

A node with implementation present but failing or missing verification should be `needs_review` or `in_progress`, not `done`.

## Top-level shape

```json
{
  "version": "1.0",
  "project": {},
  "views": [],
  "nodes": [],
  "edges": []
}
```

### project

Required:

- `id`
- `name`

Optional:

- `description`
- `repository`
- `updatedAt`

### views

Defines logical projections of the same graph.

Recommended views:

- `product`
- `architecture`
- `delivery`

Each node can belong to one or more views.

### nodes

Each node requires:

- `id`
- `title`
- `status`
- `views`

Optional:

- `summary`
- `progress` from 0 to 100
- `parentId`
- `evidence`
- `links`
- `tags`

### evidence

```json
{
  "implementation": { "required": true, "state": "pass", "detail": "src/..." },
  "tests":          { "required": true, "state": "pass", "detail": "42 tests" },
  "ci":             { "required": true, "state": "pass", "detail": "GitHub Actions" },
  "docs":           { "required": false, "state": "pass" },
  "acceptance":     { "required": true, "state": "pass" }
}
```

Allowed evidence states:

- `pass`
- `fail`
- `unknown`
- `not_applicable`

### evidence collectors

Evidence entries may optionally declare a deterministic collector. Collectors are executed only when the user explicitly runs the CLI.

```json
{
  "tests": {
    "required": true,
    "state": "unknown",
    "collector": {
      "type": "command",
      "command": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
      "timeoutSeconds": 120
    }
  }
}
```

Supported v1 collectors:

- `path_exists` — pass when a declared repository path exists;
- `command` — pass when a declared command exits with code 0;
- `git_clean` — pass when the Git working tree has no uncommitted changes;
- `github_actions` — attaches commit/run provenance from standard GitHub Actions environment variables. It changes evidence state only when a conclusion is explicitly supplied via the collector or `PROJECT_MAP_GITHUB_CONCLUSION`.

Collectors are intentionally simple and deterministic. They must not infer semantic completion from code content.

### edges

Edges make dependencies explicit.

```json
{
  "from": "api",
  "to": "domain",
  "type": "depends_on"
}
```

Recommended edge types:

- `depends_on`
- `contains`
- `implements`
- `blocks`
- `relates_to`

## Agent behavior

An agent updating the map should:

1. inspect repository state;
2. inspect tests and CI evidence where available;
3. inspect relevant docs / acceptance criteria;
4. update only nodes whose evidence can be supported;
5. prefer `unknown` over guessing;
6. never downgrade failed evidence to `pass` based on code inspection alone;
7. preserve manually curated titles, summaries, grouping, and links unless clearly obsolete.

## Generated artifact

The recommended output is:

```
.project-map/
  project-map.json
  index.html
```

Projects may git-ignore `.project-map/index.html` while keeping `project-map.json` committed, or ignore the entire directory and generate both files on demand. The repository should state its chosen policy explicitly.


### provenance

Evidence may carry clickable provenance:

```json
{
  "ci": {
    "required": true,
    "state": "pass",
    "detail": "GitHub Actions conclusion: success",
    "provenance": [
      {
        "kind": "commit",
        "label": "Commit abc1234",
        "url": "https://github.com/org/repo/commit/abc1234",
        "ref": "abc1234"
      },
      {
        "kind": "ci_run",
        "label": "Actions run 12345",
        "url": "https://github.com/org/repo/actions/runs/12345",
        "ref": "12345"
      }
    ]
  }
}
```

Nodes may also expose general `links` for source files, pull requests, ADRs, issues, dashboards, or other supporting resources. Provenance is evidence-specific; node links are navigational context.
