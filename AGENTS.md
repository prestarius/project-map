# Agent Instructions

This repository defines Project Map, a vendor-neutral visual read model for software projects.

## When updating a Project Map

- Treat repository state, tests, CI, documentation, and explicit acceptance criteria as evidence.
- Never mark a node `done` because implementation code merely exists.
- Prefer `unknown` evidence over inference.
- Preserve human-authored summaries and grouping unless they are demonstrably obsolete.
- Keep the JSON valid and conformant with `docs/spec-v1.md`.

## Recommended agent loop

Before a substantial implementation run:

1. inspect the current map;
2. identify affected nodes;
3. update planned/in-progress state if scope changed.

After implementation:

1. inspect changed files;
2. run or inspect tests;
3. inspect CI where available;
4. verify acceptance criteria;
5. update evidence;
6. derive the node status from that evidence;
7. regenerate the HTML view.

## Status guidance

- `planned`: work has not started.
- `in_progress`: implementation is actively underway.
- `needs_review`: implementation exists but verification is incomplete or failed.
- `blocked`: progress is prevented by an explicit dependency/problem.
- `done`: all required evidence checks pass.

These rules apply equally to Claude Code, Codex, Kiro, Copilot, and human contributors.
