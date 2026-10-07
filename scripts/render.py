#!/usr/bin/env python3
"""Render project-map.json into a standalone HTML dashboard."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

STATUS = {
    "planned": ("⚪", "Planned"),
    "in_progress": ("🟡", "In progress"),
    "needs_review": ("🔵", "Needs review"),
    "blocked": ("🔴", "Blocked"),
    "done": ("🟢", "Done"),
}

def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""))

def render(data: dict) -> str:
    project = data.get("project", {})
    views = data.get("views", [])
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    node_cards = []
    for node in nodes:
        evidence_rows = []
        for name, ev in node.get("evidence", {}).items():
            evidence_rows.append(
                f"<tr><td>{esc(name)}</td><td>{esc(ev.get('state', 'unknown'))}</td>"
                f"<td>{esc(ev.get('detail', ''))}</td></tr>"
            )
        evidence_html = (
            "<table><thead><tr><th>Evidence</th><th>State</th><th>Detail</th></tr></thead><tbody>"
            + "".join(evidence_rows)
            + "</tbody></table>"
            if evidence_rows else "<p class='muted'>No evidence recorded.</p>"
        )
        icon, label = STATUS.get(node.get("status"), ("❔", node.get("status", "unknown")))
        views_attr = " ".join(node.get("views", []))
        node_cards.append(f"""
        <article class="card" data-views="{esc(views_attr)}">
          <header><span class="status">{icon}</span><div><h3>{esc(node.get('title'))}</h3><span class="pill">{esc(label)}</span></div></header>
          <p>{esc(node.get('summary', ''))}</p>
          <div class="progress"><span style="width:{int(node.get('progress', 0))}%"></span></div>
          <div class="progress-label">{int(node.get('progress', 0))}%</div>
          <details><summary>Evidence</summary>{evidence_html}</details>
        </article>
        """)

    edge_items = "".join(
        f"<li><code>{esc(e.get('from'))}</code> → <code>{esc(e.get('to'))}</code> <span class='muted'>({esc(e.get('type'))})</span></li>"
        for e in edges
    )

    view_buttons = ["<button class='active' data-view='all'>All</button>"] + [
        f"<button data-view='{esc(v.get('id'))}'>{esc(v.get('name'))}</button>" for v in views
    ]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(project.get('name', 'Project Map'))}</title>
<style>
:root {{ color-scheme: dark; --bg:#0b0d10; --panel:#14181d; --line:#2a3138; --text:#eef2f6; --muted:#8f9aa6; }}
* {{ box-sizing:border-box }} body {{ margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,sans-serif }}
main {{ max-width:1180px;margin:auto;padding:36px 20px 64px }} h1 {{ margin:0;font-size:34px }} .muted {{ color:var(--muted) }}
.toolbar {{ display:flex;gap:8px;flex-wrap:wrap;margin:24px 0 }} button {{ border:1px solid var(--line);background:var(--panel);color:var(--text);padding:8px 12px;border-radius:10px;cursor:pointer }} button.active {{ outline:2px solid #6aa7ff }}
.grid {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px }}
.card {{ background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px }}
.card header {{ display:flex;gap:12px;align-items:flex-start }} .card h3 {{ margin:0 0 6px }} .status {{ font-size:24px }}
.pill {{ font-size:12px;color:var(--muted) }} .progress {{ height:8px;background:#222831;border-radius:999px;overflow:hidden;margin-top:14px }} .progress span {{ display:block;height:100%;background:#6aa7ff }} .progress-label {{ font-size:12px;color:var(--muted);margin-top:4px }}
details {{ margin-top:14px }} table {{ width:100%;border-collapse:collapse;margin-top:10px;font-size:13px }} th,td {{ text-align:left;padding:7px;border-top:1px solid var(--line);vertical-align:top }}
section {{ margin-top:34px }} code {{ color:#b7d7ff }} .hidden {{ display:none }}
</style>
</head>
<body>
<main>
  <p class="muted">Project Map v{esc(data.get('version', ''))}</p>
  <h1>{esc(project.get('name', 'Project Map'))}</h1>
  <p>{esc(project.get('description', ''))}</p>
  <div class="toolbar">{''.join(view_buttons)}</div>
  <div class="grid">{''.join(node_cards)}</div>
  <section>
    <h2>Relationships</h2>
    <ul>{edge_items or "<li class='muted'>No relationships recorded.</li>"}</ul>
  </section>
</main>
<script>
const buttons=[...document.querySelectorAll('button[data-view]')];
const cards=[...document.querySelectorAll('.card')];
buttons.forEach(b=>b.addEventListener('click',()=>{{
  buttons.forEach(x=>x.classList.remove('active')); b.classList.add('active');
  const view=b.dataset.view;
  cards.forEach(c=>c.classList.toggle('hidden', view!=='all' && !c.dataset.views.split(' ').includes(view)));
}}));
</script>
</body>
</html>"""

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", default="project-map.json")
    parser.add_argument("-o", "--output", default=".project-map/index.html")
    args = parser.parse_args()

    source = Path(args.input)
    target = Path(args.output)
    data = json.loads(source.read_text(encoding="utf-8"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(data), encoding="utf-8")
    print(f"Rendered {target}")

if __name__ == "__main__":
    main()
