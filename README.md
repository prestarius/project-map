# Project Map

**Project Map** is a vendor-neutral, evidence-based visual read model for software projects.

It turns repository state, architecture, delivery progress, tests, CI and acceptance evidence into a single interactive map that can be maintained by humans or coding agents.

## Why

Project boards answer *what someone says is happening*.

Project Map aims to answer:

- what exists;
- what is planned;
- how parts relate;
- what is blocked;
- what is actually verified;
- why a feature is considered done.

The core rule is simple:

> **Status must be supported by evidence.**

Code existing in the repository is not enough to call something done.

## Interactive map

The generated HTML is a real project graph, not a static report.

Current interaction model:

- pan the canvas;
- zoom with mouse wheel or controls;
- drag nodes;
- filter by Product / Architecture / Delivery views;
- search nodes;
- click a node to inspect evidence and relationships;
- visualize progress and status directly on the graph.

The output is still a single standalone HTML file with no runtime dependencies.

## Status model

- ⚪ `planned`
- 🟡 `in_progress`
- 🔵 `needs_review`
- 🔴 `blocked`
- 🟢 `done`

A node should only become `done` when every required evidence check passes.

Typical evidence:

- implementation
- tests
- CI
- documentation
- acceptance criteria

## Views

The same graph can be projected through different views:

- **Product** — what are we building?
- **Architecture** — how is it built?
- **Delivery** — where are we now?

## Quick start

Clone the repository and copy the example:

```bash
cp examples/project-map.json project-map.json
python -m project_map validate
python -m project_map render
```

Open:

```
.project-map/index.html
```

The CLI and renderer have no external Python dependencies.

## CLI

Project Map now has a small vendor-neutral CLI:

```bash
python -m project_map validate
python -m project_map render
python -m project_map collect
python -m project_map update
```

- `validate` checks the Project Map core contract.
- `render` generates the standalone interactive HTML.
- `collect` runs declared deterministic evidence collectors and updates status/progress.
- `update` collects evidence and renders in one command.

You can point it at another file or repository root:

```bash
python -m project_map --map docs/project-map.json --root . update
```

### Evidence collectors

Evidence can remain manual, or declare an optional collector:

```json
"tests": {
  "required": true,
  "state": "unknown",
  "collector": {
    "type": "command",
    "command": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
  }
}
```

Initial collectors:

- `path_exists`
- `command`
- `git_clean`
- `github_actions`

Collectors are explicit and deterministic: they gather evidence; they do not guess whether code is semantically complete.

### Provenance

Evidence can now carry clickable provenance to the exact commit or GitHub Actions run that produced it. Nodes can also contain general links to PRs, source files, ADRs, issues, or dashboards. The interactive inspector renders both kinds of links.

The GitHub Actions collector uses standard `GITHUB_*` environment variables. It captures commit/run URLs automatically, but it will not claim a successful check unless a conclusion is explicitly supplied.

## Files

```text
.
├── AGENTS.md
├── project-map.json
├── project-map.schema.json
├── project_map/
│   ├── cli.py
│   ├── evidence.py
│   ├── github.py
│   └── validation.py
├── docs/
│   └── spec-v1.md
├── examples/
│   └── project-map.json
├── tests/
│   └── test_render.py
└── scripts/
    └── render.py
```

## Agentic development loop

Before substantial work:

1. inspect the current map;
2. identify affected nodes;
3. update scope/status if needed.

After implementation:

1. inspect changed files;
2. inspect or run tests;
3. inspect CI;
4. verify acceptance criteria;
5. update evidence;
6. derive status from evidence;
7. regenerate the HTML.

See [AGENTS.md](AGENTS.md) for shared instructions and [docs/spec-v1.md](docs/spec-v1.md) for the v1 format.

## Claude Code / Codex / Kiro / Copilot

Project Map is intentionally tool-agnostic.

Agents should consume the same:

- `AGENTS.md`
- `project-map.json`
- `docs/spec-v1.md`

Tool-specific adapters or skills can be added later without changing the canonical data model.

## Current state

This repository dogfoods Project Map: its own implementation status lives in [project-map.json](project-map.json).

## Roadmap

Near-term:

- GitLab CI provenance adapter;
- richer evidence collectors;
- PR discovery and issue links;
- tool-specific skills and adapters;
- improved graph layout and persistence.

## License

License will be added before the first tagged release.
