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
python3 scripts/render.py project-map.json
```

Open:

```
.project-map/index.html
```

The renderer has no external Python dependencies.

## Files

```text
.
├── AGENTS.md
├── project-map.json
├── project-map.schema.json
├── docs/
│   └── spec-v1.md
├── examples/
│   └── project-map.json
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

## License

License will be added before the first tagged release.
