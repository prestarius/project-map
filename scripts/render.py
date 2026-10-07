#!/usr/bin/env python3
"""Render project-map.json into a standalone interactive HTML graph."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

STATUS = {
    "planned": ("⚪", "Planned", "#9aa4af"),
    "in_progress": ("🟡", "In progress", "#eab308"),
    "needs_review": ("🔵", "Needs review", "#3b82f6"),
    "blocked": ("🔴", "Blocked", "#ef4444"),
    "done": ("🟢", "Done", "#22c55e"),
}

def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""))

def render(data: dict) -> str:
    project = data.get("project", {})
    views = data.get("views", [])
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    graph_data = json.dumps(
        {
            "nodes": nodes,
            "edges": edges,
            "status": {
                key: {"icon": value[0], "label": value[1], "color": value[2]}
                for key, value in STATUS.items()
            },
        },
        ensure_ascii=False,
    ).replace("</", "<\/")

    view_buttons = ["<button class='view-btn active' data-view='all'>All</button>"] + [
        f"<button class='view-btn' data-view='{esc(v.get('id'))}'>{esc(v.get('name'))}</button>"
        for v in views
    ]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(project.get('name', 'Project Map'))}</title>
<style>
:root {{ color-scheme:dark; --bg:#090b0f; --panel:#11151b; --panel2:#171c24; --line:#28313c; --text:#f1f5f9; --muted:#8b98a8; --accent:#60a5fa; }}
* {{ box-sizing:border-box }}
html,body {{ width:100%;height:100%;margin:0;overflow:hidden;background:var(--bg);color:var(--text);font:14px/1.4 Inter,ui-sans-serif,system-ui,sans-serif }}
button,input {{ font:inherit }}
.app {{ height:100%;display:grid;grid-template-rows:auto 1fr }}
.topbar {{ display:flex;align-items:center;gap:18px;padding:16px 20px;border-bottom:1px solid var(--line);background:rgba(9,11,15,.96);z-index:10 }}
.brand {{ min-width:260px }}
.brand .eyebrow {{ color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.12em }}
.brand h1 {{ font-size:18px;margin:2px 0 0 }}
.controls {{ display:flex;gap:8px;align-items:center;flex-wrap:wrap;flex:1 }}
button {{ border:1px solid var(--line);background:var(--panel);color:var(--text);padding:8px 11px;border-radius:9px;cursor:pointer }}
button:hover {{ border-color:#3a4654 }}
button.active {{ border-color:var(--accent);box-shadow:0 0 0 1px var(--accent) inset }}
.search {{ margin-left:auto;min-width:220px;background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:9px;padding:8px 11px;outline:none }}
.workspace {{ display:grid;grid-template-columns:1fr 360px;min-height:0 }}
.canvas-wrap {{ position:relative;overflow:hidden;background:
  radial-gradient(circle at 20% 20%, rgba(59,130,246,.08), transparent 30%),
  linear-gradient(rgba(255,255,255,.018) 1px,transparent 1px),
  linear-gradient(90deg,rgba(255,255,255,.018) 1px,transparent 1px);
  background-size:auto,32px 32px,32px 32px;
}}
svg {{ width:100%;height:100%;display:block;cursor:grab }}
svg.dragging {{ cursor:grabbing }}
.edge {{ stroke:#536171;stroke-width:1.6;opacity:.55;vector-effect:non-scaling-stroke }}
.edge.blocks {{ stroke:#ef4444;stroke-dasharray:7 5 }}
.node rect {{ fill:#121821;stroke:#334155;stroke-width:1.5;rx:14;ry:14;filter:drop-shadow(0 10px 22px rgba(0,0,0,.28)) }}
.node:hover rect,.node.selected rect {{ stroke:#93c5fd;stroke-width:2 }}
.node.dim {{ opacity:.12 }}
.node.hidden {{ display:none }}
.edge.dim {{ opacity:.05 }}
.node-title {{ fill:var(--text);font-weight:700;font-size:14px;pointer-events:none }}
.node-summary {{ fill:#9eabb9;font-size:11px;pointer-events:none }}
.node-status {{ font-size:15px;pointer-events:none }}
.node-progress-bg {{ fill:#25303c }}
.node-progress {{ pointer-events:none }}
.inspector {{ border-left:1px solid var(--line);background:var(--panel);padding:20px;overflow:auto }}
.empty {{ color:var(--muted);padding-top:30vh;text-align:center }}
.inspector h2 {{ margin:0 0 6px;font-size:20px }}
.meta {{ color:var(--muted);font-size:12px;margin-bottom:18px }}
.summary {{ color:#cbd5e1;margin-bottom:22px }}
.section-title {{ font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin:20px 0 8px }}
.evidence {{ border:1px solid var(--line);border-radius:10px;overflow:hidden }}
.ev {{ display:grid;grid-template-columns:90px 70px 1fr;gap:8px;padding:9px 10px;border-top:1px solid var(--line);font-size:12px }}
.ev:first-child {{ border-top:0 }}
.ev .name {{ font-weight:600 }}
.pass {{ color:#4ade80 }} .fail {{ color:#f87171 }} .unknown {{ color:#facc15 }} .not_applicable {{ color:var(--muted) }}
.legend {{ position:absolute;left:16px;bottom:16px;background:rgba(17,21,27,.92);border:1px solid var(--line);border-radius:12px;padding:10px 12px;display:flex;gap:12px;flex-wrap:wrap;max-width:620px }}
.legend span {{ color:var(--muted);font-size:11px }}
.zoom-controls {{ position:absolute;right:16px;bottom:16px;display:flex;flex-direction:column;gap:6px }}
.zoom-controls button {{ width:38px;height:38px;padding:0;font-size:18px }}
@media(max-width:900px) {{ .workspace {{ grid-template-columns:1fr }} .inspector {{ display:none }} .brand {{ min-width:0 }} .search {{ min-width:150px }} }}
</style>
</head>
<body>
<div class="app">
  <div class="topbar">
    <div class="brand">
      <div class="eyebrow">Project Map v{esc(data.get('version', ''))}</div>
      <h1>{esc(project.get('name', 'Project Map'))}</h1>
    </div>
    <div class="controls">
      {''.join(view_buttons)}
      <button id="fit">Fit</button>
      <input id="search" class="search" placeholder="Search nodes…" />
    </div>
  </div>
  <div class="workspace">
    <div class="canvas-wrap">
      <svg id="graph" aria-label="Interactive project graph">
        <g id="viewport">
          <g id="edges"></g>
          <g id="nodes"></g>
        </g>
      </svg>
      <div class="legend">
        <span>🟢 Done</span><span>🟡 In progress</span><span>🔵 Needs review</span><span>🔴 Blocked</span><span>⚪ Planned</span>
        <span>Drag nodes · wheel to zoom · drag background to pan</span>
      </div>
      <div class="zoom-controls"><button id="zin">+</button><button id="zout">−</button></div>
    </div>
    <aside id="inspector" class="inspector"><div class="empty">Select a node to inspect its evidence.</div></aside>
  </div>
</div>
<script>
const DATA={graph_data};
const svg=document.getElementById('graph'), viewport=document.getElementById('viewport');
const nodesLayer=document.getElementById('nodes'), edgesLayer=document.getElementById('edges');
const inspector=document.getElementById('inspector'), search=document.getElementById('search');
let view='all', selected=null, scale=1, tx=0, ty=0, panning=false, panStart=null, draggingNode=null;

const nodeMap=new Map();
const cols=Math.max(2,Math.ceil(Math.sqrt(DATA.nodes.length)));
DATA.nodes.forEach((n,i)=>{{ n.x=120+(i%cols)*270; n.y=100+Math.floor(i/cols)*180; nodeMap.set(n.id,n); }});

function el(name,attrs={{}}) {{ const e=document.createElementNS('http://www.w3.org/2000/svg',name); Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v)); return e; }}
function short(s,n=40) {{ s=s||''; return s.length>n?s.slice(0,n-1)+'…':s; }}
function statusOf(n) {{ return DATA.status[n.status]||{{icon:'❔',label:n.status||'Unknown',color:'#64748b'}}; }}

function draw() {{
  edgesLayer.innerHTML=''; nodesLayer.innerHTML='';
  DATA.edges.forEach((e,idx)=>{{
    const a=nodeMap.get(e.from), b=nodeMap.get(e.to); if(!a||!b)return;
    const line=el('line',{{class:'edge '+(e.type==='blocks'?'blocks':''),'data-edge':idx}});
    line.dataset.from=e.from; line.dataset.to=e.to; edgesLayer.appendChild(line);
  }});
  DATA.nodes.forEach(n=>{{
    const st=statusOf(n), g=el('g',{{class:'node','data-id':n.id}});
    g.innerHTML=`
      <rect width="220" height="112"></rect>
      <text x="16" y="27" class="node-status">${st.icon}</text>
      <text x="44" y="27" class="node-title">${escapeHtml(short(n.title,28))}</text>
      <text x="16" y="52" class="node-summary">${escapeHtml(short(n.summary,34))}</text>
      <rect x="16" y="78" width="188" height="7" rx="4" class="node-progress-bg"></rect>
      <rect x="16" y="78" width="${1.88*(n.progress||0)}" height="7" rx="4" class="node-progress" fill="${st.color}"></rect>
      <text x="16" y="101" class="node-summary">${st.label} · ${n.progress||0}%</text>`;
    g.addEventListener('pointerdown',ev=>{{ev.stopPropagation();draggingNode={{n,ox:ev.clientX,oy:ev.clientY,sx:n.x,sy:n.y}};svg.setPointerCapture(ev.pointerId);}});
    g.addEventListener('click',ev=>{{ev.stopPropagation();selectNode(n.id);}});
    nodesLayer.appendChild(g);
  }});
  updatePositions(); applyFilters();
}}

function updatePositions() {{
  [...nodesLayer.children].forEach(g=>{{const n=nodeMap.get(g.dataset.id);g.setAttribute('transform',`translate(${n.x},${n.y})`);}});
  [...edgesLayer.children].forEach(line=>{{const a=nodeMap.get(line.dataset.from),b=nodeMap.get(line.dataset.to);
    line.setAttribute('x1',a.x+110);line.setAttribute('y1',a.y+56);line.setAttribute('x2',b.x+110);line.setAttribute('y2',b.y+56);}});
}}

function applyTransform() {{ viewport.setAttribute('transform',`translate(${tx} ${ty}) scale(${scale})`); }}
function visible(n) {{ return view==='all'||(n.views||[]).includes(view); }}
function applyFilters() {{
  const q=search.value.trim().toLowerCase();
  [...nodesLayer.children].forEach(g=>{{const n=nodeMap.get(g.dataset.id), okView=visible(n), okSearch=!q||(n.title||'').toLowerCase().includes(q)||(n.summary||'').toLowerCase().includes(q)||(n.id||'').toLowerCase().includes(q);
    g.classList.toggle('hidden',!okView);g.classList.toggle('dim',okView&&!okSearch);}});
  [...edgesLayer.children].forEach(line=>{{const a=nodeMap.get(line.dataset.from),b=nodeMap.get(line.dataset.to); const ok=visible(a)&&visible(b);line.classList.toggle('dim',!ok||q.length>0);}});
}}

function selectNode(id) {{
  selected=id; [...nodesLayer.children].forEach(g=>g.classList.toggle('selected',g.dataset.id===id));
  const n=nodeMap.get(id), st=statusOf(n);
  const ev=Object.entries(n.evidence||{{}}).map(([name,x])=>`<div class="ev"><div class="name">${escapeHtml(name)}</div><div class="${escapeHtml(x.state||'unknown')}">${escapeHtml(x.state||'unknown')}</div><div>${escapeHtml(x.detail||'')}</div></div>`).join('');
  const rel=DATA.edges.filter(e=>e.from===id||e.to===id).map(e=>`<div class="ev"><div class="name">${escapeHtml(e.type)}</div><div>→</div><div>${escapeHtml(e.from===id?e.to:e.from)}</div></div>`).join('');
  inspector.innerHTML=`<h2>${st.icon} ${escapeHtml(n.title)}</h2><div class="meta">${escapeHtml(n.id)} · ${st.label} · ${n.progress||0}%</div><div class="summary">${escapeHtml(n.summary||'')}</div>
  <div class="section-title">Evidence</div><div class="evidence">${ev||'<div class="ev"><div>No evidence recorded.</div></div>'}</div>
  <div class="section-title">Relationships</div><div class="evidence">${rel||'<div class="ev"><div>No relationships.</div></div>'}</div>`;
}}

function escapeHtml(s) {{ return String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[c])); }}

svg.addEventListener('pointerdown',ev=>{{if(ev.target===svg||ev.target===viewport){{panning=true;panStart={{x:ev.clientX,y:ev.clientY,tx,ty}};svg.classList.add('dragging');svg.setPointerCapture(ev.pointerId);}}}});
svg.addEventListener('pointermove',ev=>{{
  if(draggingNode){{const dx=(ev.clientX-draggingNode.ox)/scale,dy=(ev.clientY-draggingNode.oy)/scale;draggingNode.n.x=draggingNode.sx+dx;draggingNode.n.y=draggingNode.sy+dy;updatePositions();}}
  else if(panning){{tx=panStart.tx+(ev.clientX-panStart.x);ty=panStart.ty+(ev.clientY-panStart.y);applyTransform();}}
}});
svg.addEventListener('pointerup',()=>{{draggingNode=null;panning=false;svg.classList.remove('dragging');}});
svg.addEventListener('wheel',ev=>{{ev.preventDefault();const factor=ev.deltaY<0?1.12:.89;scale=Math.min(2.5,Math.max(.35,scale*factor));applyTransform();}},{{passive:false}});

document.querySelectorAll('.view-btn').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('.view-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');view=b.dataset.view;applyFilters();}}));
search.addEventListener('input',applyFilters);
document.getElementById('zin').onclick=()=>{{scale=Math.min(2.5,scale*1.2);applyTransform();}};
document.getElementById('zout').onclick=()=>{{scale=Math.max(.35,scale/1.2);applyTransform();}};
document.getElementById('fit').onclick=()=>{{scale=1;tx=40;ty=40;applyTransform();}};

draw(); tx=40;ty=40;applyTransform();
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
