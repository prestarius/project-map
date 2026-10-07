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
    groups = data.get("groups", [])

    graph_data = json.dumps(
        {
            "nodes": nodes,
            "edges": edges,
            "groups": groups,
            "status": {
                key: {"icon": value[0], "label": value[1], "color": value[2]}
                for key, value in STATUS.items()
            },
        },
        ensure_ascii=False,
    ).replace("</", r"<\\/")

    view_buttons = ["<button class='view-btn active' data-view='all'>All</button>"] + [
        f"<button class='view-btn' data-view='{esc(v.get('id'))}'>{esc(v.get('name'))}</button>"
        for v in views
    ]
    group_options = ["<option value='all'>All groups</option>"] + [
        f"<option value='{esc(g.get('id'))}'>{esc(g.get('name'))}</option>"
        for g in groups
    ]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(project.get('name', 'Project Map'))}</title>
<style>
:root {{ color-scheme:dark; --bg:#07090d; --panel:rgba(15,20,28,.84); --panel2:rgba(21,28,38,.9); --line:rgba(148,163,184,.16); --text:#f8fafc; --muted:#8fa0b3; --accent:#7dd3fc; --accent2:#818cf8; --shadow:0 24px 80px rgba(0,0,0,.35); }}
* {{ box-sizing:border-box }}
html,body {{ width:100%;height:100%;margin:0;overflow:hidden;background:radial-gradient(circle at 12% -10%,rgba(56,189,248,.12),transparent 32%),radial-gradient(circle at 88% 0%,rgba(129,140,248,.10),transparent 30%),linear-gradient(180deg,#080b11 0%,#06080c 100%);color:var(--text);font:14px/1.45 Inter,ui-sans-serif,system-ui,sans-serif }}
button,input {{ font:inherit }}
.app {{ height:100%;display:grid;grid-template-rows:auto auto 1fr }}
.topbar {{ display:flex;align-items:center;gap:22px;padding:18px 22px 14px;border-bottom:1px solid var(--line);background:rgba(8,11,17,.74);backdrop-filter:blur(18px);z-index:10;box-shadow:0 10px 40px rgba(0,0,0,.12) }}
.brand {{ min-width:260px }}
.brand .eyebrow {{ color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.12em }}
.brand h1 {{ font-size:20px;margin:3px 0 0;letter-spacing:-.02em }}
.controls {{ display:flex;gap:8px;align-items:center;flex-wrap:wrap;flex:1 }}
button {{ border:1px solid var(--line);background:linear-gradient(180deg,rgba(30,41,59,.72),rgba(15,23,42,.72));color:var(--text);padding:8px 12px;border-radius:10px;cursor:pointer;transition:.18s ease;box-shadow:inset 0 1px rgba(255,255,255,.03) }}
button:hover {{ border-color:rgba(125,211,252,.38);transform:translateY(-1px);box-shadow:0 8px 24px rgba(0,0,0,.18) }}
button.active {{ border-color:rgba(125,211,252,.7);background:linear-gradient(180deg,rgba(14,116,144,.28),rgba(30,64,175,.24));box-shadow:0 0 0 1px rgba(125,211,252,.18) inset,0 0 26px rgba(56,189,248,.10) }}
.search {{ margin-left:auto;min-width:220px;background:rgba(15,23,42,.66);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:8px 11px;outline:none;backdrop-filter:blur(12px) }}
.statsbar {{ display:flex;align-items:center;gap:10px;padding:10px 22px;border-bottom:1px solid var(--line);background:rgba(8,11,17,.58);backdrop-filter:blur(14px);z-index:9 }}
.stat-chip {{ display:inline-flex;align-items:center;gap:7px;padding:6px 9px;border:1px solid var(--line);border-radius:999px;background:rgba(15,23,42,.56);color:#cbd5e1;font-size:12px }}
.stat-dot {{ width:7px;height:7px;border-radius:50%;box-shadow:0 0 14px currentColor }}
.breadcrumbs {{ position:absolute;left:18px;top:18px;z-index:5;display:flex;gap:6px;align-items:center;padding:7px 10px;border:1px solid var(--line);border-radius:11px;background:rgba(10,15,22,.68);backdrop-filter:blur(14px);box-shadow:var(--shadow);font-size:12px;color:#cbd5e1 }}
.breadcrumbs .sep {{ color:#475569 }}
.workspace {{ display:grid;grid-template-columns:1fr 380px;min-height:0 }}
.canvas-wrap {{ position:relative;overflow:hidden;background:
  radial-gradient(circle at 20% 20%, rgba(59,130,246,.08), transparent 30%),
  linear-gradient(rgba(255,255,255,.018) 1px,transparent 1px),
  linear-gradient(90deg,rgba(255,255,255,.018) 1px,transparent 1px);
  background-size:auto,32px 32px,32px 32px;
}}
svg {{ width:100%;height:100%;display:block;cursor:grab }}
svg.dragging {{ cursor:grabbing }}
.group-box {{ fill:#0f141b;stroke:#263241;stroke-width:1.4;stroke-dasharray:8 6;rx:18;ry:18 }}
.group-title {{ fill:#64748b;font-size:12px;font-weight:700;letter-spacing:.08em;cursor:pointer }}
.overview-group rect {{ fill:url(#overviewGradient);stroke:#475569;stroke-width:1.6;rx:20;ry:20;filter:drop-shadow(0 18px 40px rgba(0,0,0,.28));transition:.18s ease }}
.overview-group:hover rect {{ stroke:#7dd3fc;filter:drop-shadow(0 20px 44px rgba(0,0,0,.34)) drop-shadow(0 0 18px rgba(56,189,248,.12)) }}
.overview-group {{ cursor:pointer }}
.overview-group text {{ fill:#e2e8f0;pointer-events:none }}
.overview-edge {{ stroke:#64748b;stroke-width:2.2;opacity:.7;vector-effect:non-scaling-stroke;cursor:pointer }}
.overview-edge-label {{ fill:#94a3b8;font-size:11px;cursor:pointer }}
.edge {{ fill:none;stroke:#5f7187;stroke-width:1.7;opacity:.52;vector-effect:non-scaling-stroke;transition:.18s ease }}
.edge.connected {{ stroke:#7dd3fc;stroke-width:2.5;opacity:.96;filter:drop-shadow(0 0 6px rgba(56,189,248,.26)) }}
.edge.blocks {{ stroke:#ef4444;stroke-dasharray:7 5 }}
.node rect.card {{ fill:url(#nodeGradient);stroke:rgba(148,163,184,.24);stroke-width:1.2;rx:16;ry:16;filter:drop-shadow(0 14px 30px rgba(0,0,0,.28));transition:.18s ease }}
.node .accent {{ rx:3;ry:3 }}
.node:hover rect.card,.node.selected rect.card {{ stroke:#7dd3fc;stroke-width:1.8;filter:drop-shadow(0 18px 36px rgba(0,0,0,.34)) drop-shadow(0 0 14px rgba(56,189,248,.12)) }}
.node {{ transition:opacity .18s ease }}
.node.dim {{ opacity:.12 }}
.node.hidden {{ display:none }}
.edge.dim {{ opacity:.05 }}
.node-title {{ fill:var(--text);font-weight:700;font-size:14px;pointer-events:none }}
.node-summary {{ fill:#9eabb9;font-size:11px;pointer-events:none }}
.node-status {{ font-size:15px;pointer-events:none }}
.node-progress-bg {{ fill:#25303c }}
.node-progress {{ pointer-events:none }}
.inspector {{ border-left:1px solid var(--line);background:linear-gradient(180deg,rgba(15,20,28,.92),rgba(10,14,20,.94));padding:22px;overflow:auto;backdrop-filter:blur(20px);box-shadow:-20px 0 60px rgba(0,0,0,.16) }}
.empty {{ color:var(--muted);padding-top:30vh;text-align:center }}
.inspector h2 {{ margin:0 0 6px;font-size:20px }}
.meta {{ color:var(--muted);font-size:12px;margin-bottom:18px }}
.summary {{ color:#cbd5e1;margin-bottom:22px }}
.section-title {{ font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em;margin:20px 0 8px }}
.evidence {{ border:1px solid var(--line);border-radius:12px;overflow:hidden;background:rgba(15,23,42,.42);box-shadow:inset 0 1px rgba(255,255,255,.02) }}
.ev {{ display:grid;grid-template-columns:90px 70px 1fr;gap:8px;padding:9px 10px;border-top:1px solid var(--line);font-size:12px }}
.ev:first-child {{ border-top:0 }}
.ev .name {{ font-weight:600 }}
.pass {{ color:#4ade80 }} .fail {{ color:#f87171 }} .unknown {{ color:#facc15 }} .not_applicable {{ color:var(--muted) }}\n.link-list {{ display:flex;flex-wrap:wrap;gap:7px }} .link-list a {{ color:#bfdbfe;text-decoration:none;border:1px solid #334155;background:#0f172a;padding:6px 8px;border-radius:8px;font-size:12px }} .link-list a:hover {{ border-color:#60a5fa }}
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
      <button id="overview">Overview</button>
      <button id="save-layout">Save layout</button>
      <select id="group-filter" class="search" style="margin-left:0;min-width:180px">{''.join(group_options)}</select>
      <input id="search" class="search" placeholder="Search nodes…" />
    </div>
  </div>
  <div id="statsbar" class="statsbar"></div>
  <div class="workspace">
    <div class="canvas-wrap">
      <div id="breadcrumbs" class="breadcrumbs"><span>Project</span><span class="sep">/</span><span>All nodes</span></div>
      <svg id="graph" aria-label="Interactive project graph">
        <defs><linearGradient id="nodeGradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#151d29"/><stop offset="100%" stop-color="#0d131c"/></linearGradient><linearGradient id="overviewGradient" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#182334"/><stop offset="100%" stop-color="#0e1622"/></linearGradient><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#64748b"/></marker><marker id="arrow-active" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#7dd3fc"/></marker></defs>
        <g id="viewport">
          <g id="groups"></g>
          <g id="overview-edges"></g>
          <g id="overview-groups"></g>
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
const nodesLayer=document.getElementById('nodes'), edgesLayer=document.getElementById('edges'), groupsLayer=document.getElementById('groups'), overviewGroupsLayer=document.getElementById('overview-groups'), overviewEdgesLayer=document.getElementById('overview-edges');
const inspector=document.getElementById('inspector'), search=document.getElementById('search'), groupFilter=document.getElementById('group-filter'), statsbar=document.getElementById('statsbar'), breadcrumbs=document.getElementById('breadcrumbs');
groupFilter.value='all';
let view='all', group='all', overview=false, selected=null, scale=1, tx=0, ty=0, panning=false, panStart=null, draggingNode=null;
const collapsedGroups=new Set(DATA.groups.filter(g=>g.collapsed).map(g=>g.id));

const nodeMap=new Map();

function renderStats() {{
  const order=['done','in_progress','needs_review','blocked','planned'];
  statsbar.innerHTML=order.map(status=>{{
    const st=DATA.status[status], count=DATA.nodes.filter(n=>n.status===status).length;
    return '<span class="stat-chip"><span class="stat-dot" style="color:'+st.color+';background:'+st.color+'"></span><strong>'+count+'</strong> '+escapeHtml(st.label)+'</span>';
  }}).join('')+'<span class="stat-chip"><strong>'+DATA.nodes.length+'</strong> total</span>';
}}

function renderBreadcrumbs() {{
  if(overview) {{ breadcrumbs.innerHTML='<span>Overview</span>'; return; }}
  if(group!=='all') {{
    const g=DATA.groups.find(x=>x.id===group);
    breadcrumbs.innerHTML='<span>Overview</span><span class="sep">/</span><span>'+escapeHtml(g?g.name:group)+'</span>';
    return;
  }}
  breadcrumbs.innerHTML='<span>Project</span><span class="sep">/</span><span>All nodes</span>';
}}

function computeLevels() {{
  const incoming=new Map(DATA.nodes.map(n=>[n.id,0]));
  DATA.edges.forEach(e=>{{ if(incoming.has(e.to)) incoming.set(e.to,(incoming.get(e.to)||0)+1); }});
  const level=new Map();
  const queue=[...DATA.nodes.filter(n=>(incoming.get(n.id)||0)===0).map(n=>n.id)];
  queue.forEach(id=>level.set(id,0));
  while(queue.length) {{
    const id=queue.shift(), base=level.get(id)||0;
    DATA.edges.filter(e=>e.from===id).forEach(e=>{{
      if(!level.has(e.to) || level.get(e.to)<base+1) level.set(e.to,base+1);
      incoming.set(e.to,(incoming.get(e.to)||1)-1);
      if((incoming.get(e.to)||0)===0) queue.push(e.to);
    }});
  }}
  DATA.nodes.forEach(n=>{{ if(!level.has(n.id)) level.set(n.id,0); }});
  return level;
}}

const levels=computeLevels();
const buckets=new Map();
DATA.nodes.forEach(n=>{{
  if(n.layout && Number.isFinite(n.layout.x) && Number.isFinite(n.layout.y)) {{
    n.x=n.layout.x; n.y=n.layout.y;
  }} else {{
    const l=levels.get(n.id)||0;
    if(!buckets.has(l)) buckets.set(l,[]);
    const row=buckets.get(l).length;
    buckets.get(l).push(n.id);
    n.x=100+l*300;
    n.y=90+row*170;
  }}
  nodeMap.set(n.id,n);
}});

function el(name,attrs={{}}) {{ const e=document.createElementNS('http://www.w3.org/2000/svg',name); Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v)); return e; }}
function short(s,n=40) {{ s=s||''; return s.length>n?s.slice(0,n-1)+'…':s; }}
function statusOf(n) {{ return DATA.status[n.status]||{{icon:'❔',label:n.status||'Unknown',color:'#64748b'}}; }}

function descendantGroupIds(groupId) {{
  const out=new Set([groupId]);
  let changed=true;
  while(changed) {{
    changed=false;
    DATA.groups.forEach(g=>{{
      if(g.parentGroupId && out.has(g.parentGroupId) && !out.has(g.id)) {{ out.add(g.id); changed=true; }}
    }});
  }}
  return out;
}}

function groupMembers(groupId) {{
  const ids=descendantGroupIds(groupId);
  return DATA.nodes.filter(n=>ids.has(n.groupId));
}}

function groupStatus(groupId) {{
  const members=groupMembers(groupId);
  if(!members.length) return DATA.status.planned;
  const order=['blocked','needs_review','in_progress','planned','done'];
  const status=order.find(s=>members.some(n=>n.status===s))||'planned';
  return DATA.status[status]||DATA.status.planned;
}}

function rootGroupId(groupId) {{
  if(!groupId) return null;
  let current=groupId, root=null;
  const seen=new Set();
  while(current && !seen.has(current)) {{
    seen.add(current);
    const g=DATA.groups.find(x=>x.id===current);
    if(!g) break;
    root=current;
    current=g.parentGroupId;
  }}
  return root;
}}

function rootGroups() {{ return DATA.groups.filter(g=>!g.parentGroupId); }}

function groupCenter(groupId) {{
  const members=groupMembers(groupId);
  if(!members.length) return {{x:0,y:0}};
  const xs=members.map(n=>n.x+110), ys=members.map(n=>n.y+56);
  return {{x:xs.reduce((a,b)=>a+b,0)/xs.length,y:ys.reduce((a,b)=>a+b,0)/ys.length}};
}}

function aggregatedGroupEdges() {{
  const agg=new Map();
  DATA.edges.forEach(e=>{{
    const a=nodeMap.get(e.from), b=nodeMap.get(e.to);
    if(!a||!b) return;
    const from=rootGroupId(a.groupId), to=rootGroupId(b.groupId);
    if(!from||!to||from===to) return;
    const key=from+'→'+to;
    const item=agg.get(key)||{{from:from,to:to,count:0}};
    item.count+=1; agg.set(key,item);
  }});
  return [...agg.values()];
}}

function underlyingRelations(fromGroup,toGroup) {{
  return DATA.edges.filter(e=>{{
    const a=nodeMap.get(e.from), b=nodeMap.get(e.to);
    return a&&b&&rootGroupId(a.groupId)===fromGroup&&rootGroupId(b.groupId)===toGroup;
  }});
}}

function drillIntoGroup(groupId) {{
  overview=false;
  document.getElementById('overview').classList.remove('active');
  group=groupId;
  groupFilter.value=groupId;
  descendantGroupIds(groupId).forEach(id=>collapsedGroups.delete(id));
  drawGroups(); applyFilters(); renderBreadcrumbs();
  const g=DATA.groups.find(x=>x.id===groupId);
  const members=groupMembers(groupId);
  const st=groupStatus(groupId);
  inspector.innerHTML='<h2>'+st.icon+' '+escapeHtml(g?g.name:groupId)+'</h2><div class="meta">'+members.length+' nodes · '+escapeHtml(st.label)+'</div><div class="summary">'+escapeHtml((g&&g.description)||'')+'</div><div class="section-title">Drill-down</div><div class="evidence"><div class="ev"><div class="name">Scope</div><div>group</div><div>'+escapeHtml(groupId)+'</div></div></div>';
}}

function inspectOverviewEdge(fromGroup,toGroup) {{
  const rels=underlyingRelations(fromGroup,toGroup);
  const from=DATA.groups.find(g=>g.id===fromGroup), to=DATA.groups.find(g=>g.id===toGroup);
  const rows=rels.map(e=>'<div class="ev"><div class="name">'+escapeHtml(e.type)+'</div><div>→</div><div>'+escapeHtml(e.from)+' → '+escapeHtml(e.to)+'</div></div>').join('');
  inspector.innerHTML='<h2>Cross-group relationships</h2><div class="meta">'+escapeHtml(from?from.name:fromGroup)+' → '+escapeHtml(to?to.name:toGroup)+' · '+rels.length+' total</div><div class="section-title">Underlying edges</div><div class="evidence">'+(rows||'<div class="ev"><div>No relationships.</div></div>')+'</div>';
}}

function drawOverview() {{
  overviewGroupsLayer.innerHTML=''; overviewEdgesLayer.innerHTML='';
  const centers=new Map();
  rootGroups().forEach(g=>{{
    const c=groupCenter(g.id); centers.set(g.id,c);
    const st=groupStatus(g.id), members=groupMembers(g.id);
    const box=el('g',{{class:'overview-group','data-overview-group':g.id}});
    box.setAttribute('transform','translate('+(c.x-110)+','+(c.y-56)+')');
    box.innerHTML='<rect width="220" height="112"></rect><text x="16" y="30" font-size="16" font-weight="700">'+st.icon+' '+escapeHtml(g.name)+'</text><text x="16" y="56" font-size="12">'+members.length+' nodes</text><text x="16" y="82" font-size="12">'+st.label+'</text>';
    box.addEventListener('click',()=>drillIntoGroup(g.id));
    overviewGroupsLayer.appendChild(box);
  }});
  aggregatedGroupEdges().forEach((e,i)=>{{
    const a=centers.get(e.from), b=centers.get(e.to); if(!a||!b)return;
    const line=el('line',{{class:'overview-edge','data-overview-edge':i,x1:a.x,y1:a.y,x2:b.x,y2:b.y}});
    line.addEventListener('click',ev=>{{ev.stopPropagation();inspectOverviewEdge(e.from,e.to);}});
    overviewEdgesLayer.appendChild(line);
    const label=el('text',{{class:'overview-edge-label',x:(a.x+b.x)/2,y:(a.y+b.y)/2-6}});
    label.textContent=e.count+' relation'+(e.count===1?'':'s');
    label.addEventListener('click',ev=>{{ev.stopPropagation();inspectOverviewEdge(e.from,e.to);}});
    overviewEdgesLayer.appendChild(label);
  }});
}}

function drawGroups() {{
  groupsLayer.innerHTML='';
  DATA.groups.forEach(g=>{{
    const members=groupMembers(g.id);
    if(!members.length)return;
    const xs=members.map(n=>n.x), ys=members.map(n=>n.y);
    const minX=(g.layout&&Number.isFinite(g.layout.x))?g.layout.x:Math.min(...xs)-35;
    const minY=(g.layout&&Number.isFinite(g.layout.y))?g.layout.y:Math.min(...ys)-45;
    const width=(g.layout&&Number.isFinite(g.layout.width))?g.layout.width:(Math.max(...xs)-minX+255);
    const height=(g.layout&&Number.isFinite(g.layout.height))?g.layout.height:(Math.max(...ys)-minY+155);
    const box=el('rect',{{class:'group-box',x:minX,y:minY,width,height,'data-group':g.id}});
    const title=el('text',{{class:'group-title',x:minX+14,y:minY+23,'data-group-title':g.id}});
    const st=groupStatus(g.id);
    title.textContent=(collapsedGroups.has(g.id)?'▸ ':'▾ ')+st.icon+' '+g.name;
    title.addEventListener('click',ev=>{{
      ev.stopPropagation();
      if(collapsedGroups.has(g.id)) collapsedGroups.delete(g.id); else collapsedGroups.add(g.id);
      drawGroups(); applyFilters();
    }});
    groupsLayer.appendChild(box);groupsLayer.appendChild(title);
  }});
}}

function draw() {{
  groupsLayer.innerHTML=''; edgesLayer.innerHTML=''; nodesLayer.innerHTML='';
  DATA.edges.forEach((e,idx)=>{{
    const a=nodeMap.get(e.from), b=nodeMap.get(e.to); if(!a||!b)return;
    const line=el('path',{{class:'edge '+(e.type==='blocks'?'blocks':''),'data-edge':idx,'marker-end':'url(#arrow)'}});
    line.dataset.from=e.from; line.dataset.to=e.to; edgesLayer.appendChild(line);
  }});
  DATA.nodes.forEach(n=>{{
    const st=statusOf(n), g=el('g',{{class:'node','data-id':n.id}});
    g.innerHTML=`
      <rect class="card" width="220" height="112"></rect>
      <rect class="accent" x="0" y="14" width="4" height="84" fill="${{st.color}}"></rect>
      <circle cx="22" cy="24" r="5" fill="${{st.color}}"></circle>
      <text x="36" y="29" class="node-title">${{escapeHtml(short(n.title,28))}}</text>
      <text x="16" y="52" class="node-summary">${{escapeHtml(short(n.summary,34))}}</text>
      <rect x="16" y="78" width="188" height="7" rx="4" class="node-progress-bg"></rect>
      <rect x="16" y="78" width="${{1.88*(n.progress||0)}}" height="7" rx="4" class="node-progress" fill="${{st.color}}"></rect>
      <text x="16" y="101" class="node-summary">${{st.label}} · ${{n.progress||0}}%</text>`;
    g.addEventListener('pointerdown',ev=>{{ev.stopPropagation();draggingNode={{n,ox:ev.clientX,oy:ev.clientY,sx:n.x,sy:n.y}};svg.setPointerCapture(ev.pointerId);}});
    g.addEventListener('click',ev=>{{ev.stopPropagation();selectNode(n.id);}});
    nodesLayer.appendChild(g);
  }});
  updatePositions(); drawGroups(); applyFilters();
}}

function updatePositions() {{
  [...nodesLayer.children].forEach(g=>{{const n=nodeMap.get(g.dataset.id);g.setAttribute('transform',`translate(${{n.x}},${{n.y}})`);}});
  [...edgesLayer.children].forEach(line=>{{const a=nodeMap.get(line.dataset.from),b=nodeMap.get(line.dataset.to);
    const x1=a.x+220,y1=a.y+56,x2=b.x,y2=b.y+56,dx=Math.max(70,Math.abs(x2-x1)*.45);
    line.setAttribute('d','M '+x1+' '+y1+' C '+(x1+dx)+' '+y1+', '+(x2-dx)+' '+y2+', '+x2+' '+y2);}});
}}

function applyTransform() {{ viewport.setAttribute('transform',`translate(${{tx}} ${{ty}}) scale(${{scale}})`); }}
function hiddenByCollapse(n) {{
  if(!n.groupId) return false;
  let current=n.groupId;
  const seen=new Set();
  while(current && !seen.has(current)) {{
    if(collapsedGroups.has(current)) return true;
    seen.add(current);
    const g=DATA.groups.find(x=>x.id===current);
    current=g&&g.parentGroupId;
  }}
  return false;
}}

function visible(n) {{
  const viewOk=view==='all'||(n.views||[]).includes(view);
  const selectedGroups=group==='all'?null:descendantGroupIds(group);
  const groupOk=!selectedGroups||selectedGroups.has(n.groupId);
  return viewOk&&groupOk&&!hiddenByCollapse(n);
}}
function applyFilters() {{
  nodesLayer.style.display=overview?'none':'';
  edgesLayer.style.display=overview?'none':'';
  groupsLayer.style.display=overview?'none':'';
  overviewGroupsLayer.style.display=overview?'':'none';
  overviewEdgesLayer.style.display=overview?'':'none';
  const q=search.value.trim().toLowerCase();
  [...nodesLayer.children].forEach(g=>{{const n=nodeMap.get(g.dataset.id), okView=visible(n), okSearch=!q||(n.title||'').toLowerCase().includes(q)||(n.summary||'').toLowerCase().includes(q)||(n.id||'').toLowerCase().includes(q);
    g.classList.toggle('hidden',!okView);g.classList.toggle('dim',okView&&!okSearch);}});
  [...edgesLayer.children].forEach(line=>{{const a=nodeMap.get(line.dataset.from),b=nodeMap.get(line.dataset.to); const ok=visible(a)&&visible(b);line.classList.toggle('dim',!ok||q.length>0);}});
  [...groupsLayer.children].forEach(item=>{{
    const gid=item.dataset.group||item.dataset.groupTitle;
    const selectedGroups=group==='all'?null:descendantGroupIds(group);
    item.style.display=(!selectedGroups||selectedGroups.has(gid))?'':'none';
  }});
}}

function selectNode(id) {{
  selected=id; [...nodesLayer.children].forEach(g=>g.classList.toggle('selected',g.dataset.id===id));
  [...edgesLayer.children].forEach(line=>{{const hit=line.dataset.from===id||line.dataset.to===id;line.classList.toggle('connected',hit);line.setAttribute('marker-end',hit?'url(#arrow-active)':'url(#arrow)');}});
  const n=nodeMap.get(id), st=statusOf(n);
  const ev=Object.entries(n.evidence||{{}}).map(([name,x])=>{{
    const prov=(x.provenance||[]).map(p=>`<a href="${{escapeAttr(p.url)}}" target="_blank" rel="noreferrer">${{escapeHtml(p.label||p.kind||'source')}}</a>`).join('');
    const provHtml=prov?`<div class="link-list" style="margin-top:6px">${{prov}}</div>`:'';
    return `<div class="ev"><div class="name">${{escapeHtml(name)}}</div><div class="${{escapeHtml(x.state||'unknown')}}">${{escapeHtml(x.state||'unknown')}}</div><div>${{escapeHtml(x.detail||'')}}${{provHtml}}</div></div>`;
  }}).join('');
  const rel=DATA.edges.filter(e=>e.from===id||e.to===id).map(e=>`<div class="ev"><div class="name">${{escapeHtml(e.type)}}</div><div>→</div><div>${{escapeHtml(e.from===id?e.to:e.from)}}</div></div>`).join('');
  const links=(n.links||[]).map(link=>`<a href="${{escapeAttr(link.url)}}" target="_blank" rel="noreferrer">${{escapeHtml(link.label||link.kind||'link')}}</a>`).join('');
  inspector.innerHTML=`<h2>${{st.icon}} ${{escapeHtml(n.title)}}</h2><div class="meta">${{escapeHtml(n.id)}} · ${{st.label}} · ${{n.progress||0}}%</div><div class="summary">${{escapeHtml(n.summary||'')}}</div>
  <div class="section-title">Evidence</div><div class="evidence">${{ev||'<div class="ev"><div>No evidence recorded.</div></div>'}}</div>
  ${{links?`<div class="section-title">Links</div><div class="link-list">${{links}}</div>`:''}}
  <div class="section-title">Relationships</div><div class="evidence">${{rel||'<div class="ev"><div>No relationships.</div></div>'}}</div>`;
}}

function escapeHtml(s) {{ return String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}}[c])); }}
function escapeAttr(s) {{ return escapeHtml(String(s??'')); }}

svg.addEventListener('pointerdown',ev=>{{if(ev.target===svg||ev.target===viewport){{panning=true;panStart={{x:ev.clientX,y:ev.clientY,tx,ty}};svg.classList.add('dragging');svg.setPointerCapture(ev.pointerId);}}}});
svg.addEventListener('pointermove',ev=>{{
  if(draggingNode){{const dx=(ev.clientX-draggingNode.ox)/scale,dy=(ev.clientY-draggingNode.oy)/scale;draggingNode.n.x=draggingNode.sx+dx;draggingNode.n.y=draggingNode.sy+dy;updatePositions();}}
  else if(panning){{tx=panStart.tx+(ev.clientX-panStart.x);ty=panStart.ty+(ev.clientY-panStart.y);applyTransform();}}
}});
svg.addEventListener('pointerup',()=>{{draggingNode=null;panning=false;svg.classList.remove('dragging');}});
svg.addEventListener('wheel',ev=>{{ev.preventDefault();const factor=ev.deltaY<0?1.12:.89;scale=Math.min(2.5,Math.max(.35,scale*factor));applyTransform();}},{{passive:false}});

document.querySelectorAll('.view-btn').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('.view-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');view=b.dataset.view;applyFilters();}}));
search.addEventListener('input',applyFilters);
groupFilter.addEventListener('change',()=>{{group=groupFilter.value;applyFilters();renderBreadcrumbs();}});
document.getElementById('zin').onclick=()=>{{scale=Math.min(2.5,scale*1.2);applyTransform();}};
document.getElementById('zout').onclick=()=>{{scale=Math.max(.35,scale/1.2);applyTransform();}};
document.getElementById('fit').onclick=()=>{{scale=1;tx=40;ty=40;applyTransform();}};
document.getElementById('overview').onclick=()=>{{overview=!overview;document.getElementById('overview').classList.toggle('active',overview);drawOverview();applyFilters();renderBreadcrumbs();}};
document.getElementById('save-layout').onclick=()=>{{
  const out=JSON.parse(JSON.stringify(DATA));
  out.nodes=out.nodes.map(n=>{{
    const copy={{...n}};
    copy.layout={{x:Math.round(n.x),y:Math.round(n.y),pinned:true}};
    delete copy.x; delete copy.y;
    return copy;
  }});
  delete out.status;
  const blob=new Blob([JSON.stringify(out,null,2)+'\\\\n'],{{type:'application/json'}});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='project-map.layout.json';
  a.click();
  URL.revokeObjectURL(a.href);
}};

function initialize() {{
  try {{
    draw();
    drawOverview();
    renderStats();
    renderBreadcrumbs();
    tx=40;ty=40;applyTransform();applyFilters();
  }} catch (error) {{
    console.error('Project Map renderer failed', error);
    inspector.innerHTML='<h2>Renderer error</h2><div class="summary">'+escapeHtml(error&&error.message?error.message:String(error))+'</div><div class="meta">Open the browser console for the stack trace.</div>';
    statsbar.innerHTML='<span class="stat-chip"><strong>Renderer failed</strong></span>';
  }}
}}
initialize();
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
