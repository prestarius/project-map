"""Project Map command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from project_map.evidence import collect_evidence, derive_progress, derive_status
from project_map.validation import validate


def load_map(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_map(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd_validate(args: argparse.Namespace) -> int:
    data = load_map(Path(args.map))
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {args.map}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    from scripts.render import render

    source = Path(args.map)
    target = Path(args.output)
    errors = validate(load_map(source))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(load_map(source)), encoding="utf-8")
    print(f"Rendered {target}")
    return 0


def update_map(data: dict[str, Any], root: Path) -> dict[str, Any]:
    for node in data.get("nodes", []):
        evidence = node.get("evidence", {})
        node["evidence"] = {
            name: collect_evidence(item, root)
            for name, item in evidence.items()
        }
        node["status"] = derive_status(node)
        node["progress"] = derive_progress(node)
    return data


def cmd_collect(args: argparse.Namespace) -> int:
    path = Path(args.map)
    data = load_map(path)
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    before = json.dumps(data, sort_keys=True)
    updated = update_map(data, Path(args.root).resolve())
    if args.check:
        after = json.dumps(updated, sort_keys=True)
        if before != after:
            print("Evidence is stale.")
            return 2
        print("Evidence is current.")
        return 0

    save_map(path, updated)
    print(f"Updated evidence in {path}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    collect_args = argparse.Namespace(map=args.map, root=args.root, check=False)
    result = cmd_collect(collect_args)
    if result:
        return result
    render_args = argparse.Namespace(map=args.map, output=args.output)
    return cmd_render(render_args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="project-map")
    parser.add_argument("--map", default="project-map.json", help="Path to project-map.json")
    parser.add_argument("--root", default=".", help="Repository root for evidence collectors")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate", help="Validate the Project Map core contract")

    render_parser = sub.add_parser("render", help="Render standalone interactive HTML")
    render_parser.add_argument("-o", "--output", default=".project-map/index.html")

    collect_parser = sub.add_parser("collect", help="Run configured evidence collectors")
    collect_parser.add_argument("--check", action="store_true", help="Fail when collected evidence differs")

    update_parser = sub.add_parser("update", help="Collect evidence and render the map")
    update_parser.add_argument("-o", "--output", default=".project-map/index.html")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    commands = {
        "validate": cmd_validate,
        "render": cmd_render,
        "collect": cmd_collect,
        "update": cmd_update,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
