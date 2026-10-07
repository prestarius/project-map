# Project Map

> **A vendor-neutral, evidence-based visual map of a software project — built for humans and coding agents.**

Project Map turns repository state, architecture, delivery progress, tests, CI, documentation, and acceptance evidence into a single interactive project dashboard.

It is intentionally simple:

- the **repository remains the source of truth**;
- `project-map.json` is a transparent read model;
- status is backed by **evidence**, not agent guesswork;
- the UI is generated as a **single standalone HTML file**;
- the core runtime has **zero external Python dependencies**;
- Claude Code, Codex, Kiro, Copilot, CI, and humans can all use the same format.

---

## Why Project Map?

Project boards usually tell you what someone *says* is happening.

Project Map aims to show what can actually be supported by the project:

- what exists;
- what is planned;
- what is currently being implemented;
- how components depend on one another;
- what is blocked;
- what has been verified;
- why something is considered done;
- where the evidence came from.

The core rule is:

> **Status must be supported by evidence.**

The existence of code alone is never sufficient to mark work as done.

---

## What it looks like

Project Map now opens into a dashboard-first **Project Cockpit**, with the full dependency graph available as a dedicated Graph mode.

- milestone rail derived from top-level groups;
- project-part cards with strong status treatment;
- next actionable item;
- needs-attention panel for blocked/review work;
- evidence health summary;
- Cockpit / Graph mode switching;
- status summary chips;
- Product / Architecture / Delivery views;
- searchable project graph;
- draggable nodes;
- persistent layout;
- groups and bounded-context swimlanes;
- nested and collapsible groups;
- high-level Overview mode;
- cross-group relationship aggregation;
- drill-down from overview to implementation detail;
- curved directional dependency edges;
- dependency-path highlighting;
- evidence inspection;
- commit / PR / CI provenance links;
- progress and verification status.

Cockpit is a renderer projection over the same canonical `project-map.json`; it does not introduce a second source of truth.

The generated output is still just:

```text
.project-map/index.html
```

No web server, framework, Node.js runtime, or database is required.

---

# Quick start

## Requirements

Project Map is tested in CI with **Python 3.12**.

There are currently no external Python package dependencies.

Check your Python version:

```bash
python --version
```

On systems where Python is exposed as `python3`, use `python3` in the commands below.

## 1. Clone the repository

```bash
git clone https://github.com/prestarius/project-map.git
cd project-map
```

## 2. Validate the map

```bash
python -m project_map validate
```

Expected result:

```text
OK: project-map.json
```

## 3. Render the UI

```bash
python -m project_map render
```

This generates:

```text
.project-map/index.html
```

## 4. Open it

You can open the generated HTML directly in a browser.

### macOS

```bash
open .project-map/index.html
```

### Linux

```bash
xdg-open .project-map/index.html
```

### Windows

```powershell
start .project-map/index.html
```

That is enough to run Project Map locally.

---

# Try the curated self-demo

The repository includes a curated sample based on **Project Map itself**. It is intentionally smaller than the full dogfood map, with a layout that is easy to understand immediately.

```bash
python -m project_map \
  --map examples/project-map-self-demo.json \
  render \
  -o .project-map/self-demo.html
```

Open it:

### macOS

```bash
open .project-map/self-demo.html
```

### Linux

```bash
xdg-open .project-map/self-demo.html
```

### Windows

```powershell
start .project-map/self-demo.html
```

There is also a smaller generic example in `examples/project-map.json`.

---

# CLI

Project Map exposes four core commands.

## Validate

Validate the Project Map contract:

```bash
python -m project_map validate
```

Use another map:

```bash
python -m project_map --map path/to/project-map.json validate
```

---

## Render

Generate the interactive standalone HTML:

```bash
python -m project_map render
```

Custom output:

```bash
python -m project_map render -o build/project-map.html
```

---

## Collect

Run explicitly configured evidence collectors and update the map:

```bash
python -m project_map collect
```

Check whether committed evidence is stale without writing changes:

```bash
python -m project_map collect --check
```

Exit code `2` means the collected evidence differs from the committed map.

> Evidence collection is intentionally explicit. A `command` collector may execute project-defined tests or commands, so agents should not run collectors silently.

---

## Update

Collect evidence and render in one step:

```bash
python -m project_map update
```

Custom repository root and map:

```bash
python -m project_map \
  --map docs/project-map.json \
  --root . \
  update
```

---

# Status model

Project Map uses five intentionally small states:

| Status | Meaning |
|---|---|
| ⚪ `planned` | Work has not started |
| 🟡 `in_progress` | Implementation is underway |
| 🔵 `needs_review` | Implementation exists, but verification is incomplete or failed |
| 🔴 `blocked` | Progress is prevented by an explicit dependency or problem |
| 🟢 `done` | All required evidence passes |

A typical node should move toward `done` through evidence, not intuition.

---

# Evidence model

A node may define evidence such as:

```json
{
  "evidence": {
    "implementation": {
      "required": true,
      "state": "pass",
      "detail": "src/payment/service.py"
    },
    "tests": {
      "required": true,
      "state": "pass",
      "detail": "unit and integration tests pass"
    },
    "ci": {
      "required": true,
      "state": "pass",
      "detail": "GitHub Actions"
    }
  }
}
```

Allowed evidence states:

- `pass`
- `fail`
- `unknown`
- `not_applicable`

If required verification is unknown, the feature should not silently become `done`.

---

# Evidence collectors

Evidence may be maintained manually or collected deterministically.

Current collectors:

| Collector | Purpose |
|---|---|
| `path_exists` | Verify that a declared path exists |
| `command` | Run a command and use its exit code as evidence |
| `git_clean` | Verify that the Git working tree is clean |
| `github_actions` | Attach GitHub commit / run provenance |

Example:

```json
{
  "tests": {
    "required": true,
    "state": "unknown",
    "collector": {
      "type": "command",
      "command": [
        "python",
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-v"
      ],
      "timeoutSeconds": 120
    }
  }
}
```

Collectors gather facts. They do not infer semantic completion from source code.

---

# GitHub provenance

Project Map can attach clickable provenance to evidence.

For example:

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

The GitHub Actions collector captures context from standard `GITHUB_*` variables.

It does **not** claim that CI passed merely because it is running inside GitHub Actions. A successful conclusion must be explicit.

---

# Project structure

```text
.
├── AGENTS.md
├── README.md
├── project-map.json
├── project-map.schema.json
│
├── project_map/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── evidence.py
│   ├── github.py
│   └── validation.py
│
├── scripts/
│   └── render.py
│
├── docs/
│   └── spec-v1.md
│
├── examples/
│   ├── project-map.json
│   └── project-map-self-demo.json
│
├── tests/
│   ├── test_cli.py
│   ├── test_evidence.py
│   ├── test_github.py
│   ├── test_render.py
│   ├── test_render_js.py
│   └── test_validation.py
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

# Canonical Project Map

The canonical project map is a human-readable JSON document.

Minimal shape:

```json
{
  "version": "1.0",
  "project": {
    "id": "my-project",
    "name": "My Project"
  },
  "views": [],
  "nodes": [],
  "edges": []
}
```

For the full contract see:

- [Project Map v1 specification](docs/spec-v1.md)
- [JSON Schema](project-map.schema.json)

---

# Views

The same canonical graph can be projected through different perspectives.

The default views are:

### Product

**What are we building?**

Useful for product capabilities, features, milestones, and user-facing scope.

### Architecture

**How is it built?**

Useful for services, components, contracts, boundaries, and dependencies.

### Delivery

**Where are we now?**

Useful for implementation state, verification, blockers, and CI evidence.

A node may belong to one or more views.

---

# Groups and bounded contexts

Large maps do not have to remain flat.

Define optional groups:

```json
{
  "groups": [
    {
      "id": "checkout",
      "name": "Checkout"
    },
    {
      "id": "platform",
      "name": "Platform"
    }
  ]
}
```

Assign a node:

```json
{
  "id": "payments-api",
  "title": "Payments API",
  "groupId": "checkout"
}
```

Groups can also be nested:

```json
{
  "id": "runtime",
  "name": "Runtime & Tooling",
  "parentGroupId": "core"
}
```

The UI supports:

- swimlanes;
- nested boundaries;
- collapse / expand;
- group filtering;
- aggregated group status.

---

# Overview mode

For larger systems, switch to **Overview**.

Overview derives a high-level architecture from the canonical graph:

- top-level groups become summary cards;
- status is aggregated from descendant nodes;
- node counts are displayed;
- relationships crossing top-level groups are aggregated;
- aggregated edges show the number of underlying relationships.

Click a group to drill back into detail.

Click an aggregated relationship to inspect the concrete canonical edges behind it.

Overview is only a renderer projection. It does not introduce a second source of truth.

---

# Layout

Nodes may have persistent coordinates:

```json
{
  "layout": {
    "x": 420,
    "y": 180,
    "pinned": true
  }
}
```

Without explicit coordinates, Project Map generates a deterministic dependency-oriented fallback layout.

You can also:

1. drag nodes in the UI;
2. click **Save layout**;
3. download `project-map.layout.json`;
4. copy the resulting `layout` fields into the canonical `project-map.json`;
5. commit the layout to Git.

---

# Agentic development workflow

Project Map is designed to sit inside an agentic SDLC loop.

Before implementation:

1. inspect the current map;
2. identify affected nodes;
3. update planned / in-progress scope where appropriate.

After implementation:

1. inspect changed files;
2. run or inspect tests;
3. inspect CI;
4. verify acceptance criteria;
5. update evidence;
6. derive status from evidence;
7. regenerate the UI;
8. review and merge.

Conceptually:

```text
brainstorm
   ↓
Project Map
   ↓
implementation
   ↓
tests / CI / acceptance
   ↓
evidence update
   ↓
Project Map
   ↓
review / merge
```

The intended principle is:

> **The agent proposes state. The validator proves state.**

---

# Coding agents

Project Map is deliberately tool-agnostic.

The same repository contract can be consumed by:

- Claude Code;
- OpenAI Codex;
- AWS Kiro;
- GitHub Copilot;
- other coding agents;
- humans.

Agents should start with:

- [AGENTS.md](AGENTS.md)
- [project-map.json](project-map.json)
- [docs/spec-v1.md](docs/spec-v1.md)

Tool-specific skills and adapters may be layered on top later without changing the canonical model.

---

# CI

The repository dogfoods Project Map in GitHub Actions.

Current CI:

1. validates `project-map.json`;
2. runs the Python test suite;
3. renders the generic example map;
4. renders the curated Project Map self-demo;
5. renders the repository's own dogfood map;
6. syntax-checks the generated JavaScript when Node.js is available;
7. smoke-tests GitHub provenance collection.

Run the same core checks locally:

```bash
python -m project_map validate
python -m unittest discover -s tests -v
python -m project_map render
```

---

# Using Project Map in another repository

A minimal adoption path is:

1. copy `project_map/` and `scripts/render.py`, or package the tool once distribution is available;
2. create a `project-map.json`;
3. optionally reference `project-map.schema.json`;
4. add `AGENTS.md` guidance;
5. add deterministic evidence collectors;
6. render locally or in CI.

For now, Project Map is still under active development and is dogfooded directly from this repository.

---

# Design principles

Project Map should remain:

- **evidence-based** — facts before inference;
- **vendor-neutral** — no dependency on one coding agent;
- **repository-first** — no parallel planning database;
- **human-readable** — JSON that can be reviewed in a PR;
- **deterministic where possible** — collectors over guesses;
- **progressively adoptable** — small projects can stay small;
- **portable** — standalone HTML output;
- **low-dependency** — the core currently uses only Python's standard library.

---

# Current state

This repository uses Project Map to track Project Map itself.

See:

- [project-map.json](project-map.json)
- [Project Map v1 specification](docs/spec-v1.md)
- [Agent instructions](AGENTS.md)

---

# Roadmap

Near-term ideas:

- GitLab CI provenance adapter;
- richer deterministic evidence collectors;
- PR and issue discovery;
- tool-specific agent skills / adapters;
- keyboard navigation;
- URL state and shareable deep links;
- minimap / orientation aid;
- packaging and easier installation;
- release automation.

The roadmap should remain driven by the same rule as the product itself: add capabilities only when they improve the project read model without creating another source of truth.

---

# Contributing

Project Map is currently evolving quickly.

Before contributing:

```bash
python -m project_map validate
python -m unittest discover -s tests -v
python -m project_map render
```

Keep changes:

- evidence-based;
- vendor-neutral;
- dependency-light;
- backwards-compatible where practical;
- documented in the README / specification when behavior changes.

More detailed contributor guidance will be added before the first tagged release.

---

# License

A license will be added before the first tagged release.
