// REF-011: employee provenance graph as a light constellation.
// Graph interaction/visual design adapted from vectorize-io/hindsight control-plane constellation (Apache-2.0).
// Recolored to the Caldera palette (DESIGN.md). Deterministic seeded layout, vanilla canvas,
// no dependency, no ambient animation loop: redraw on hover/selection/pan/zoom only.
"use strict";
const $ = (s) => document.querySelector(s);
const canvas = $("#graph"), ctx = canvas.getContext("2d");
// Node color encodes type (constellation dots): Ember center, Obsidian evidence, outlined Sulfur competency, warm-gray rater.
const NODE_COLORS = {employee:"#fc5000", evidence:"#070607", competency:"#f5f28e", rater:"#77746e"};
const NODE_RADIUS = {employee:11, evidence:5, competency:6.5, rater:5};
// Stored link types stay warm neutrals/subtle Sulfur; response relations are the single Plasma standout.
const LINK_COLORS = {"has-evidence":"#77746e", "competency":"#514f4a", "rated-by":"#a3a09a"};
const RESPONSE_COLOR = "#524ae9";
const BG = "#f7f6f2", INK = "#070607", MUTED = "#514f4a", HUD = "#514f4a";
const NODE_FONT = '12px "DM Sans", system-ui, sans-serif';
const EVIDENCE_FONT = '12px "DM Sans", system-ui, sans-serif';
const MONO = '10px ui-monospace, "SF Mono", Consolas, monospace';

let graph, labelsOn = true, requestId = 0, selectedId, focusIdx = -1;
let nodes = [], links = [], nodeIndex = new Map(), neighborIds = new Set();
let wx, wy, sx, sy, layoutDone = false;
const params = new URLSearchParams(location.search);
$("#employee").value = params.get("employee") || "emp-004";
$("#actor").value = $("#employee").value;
if (["research", "runtime"].includes(params.get("source"))) $("#source").value = params.get("source");

// Camera + interaction state; world layout is frozen after seeding (Hindsight constellation behavior).
const S = {W:0, H:0, dpr:1, zoom:1, fit:1, panX:0, panY:0, mouseX:-1, mouseY:-1, hover:-1,
           down:false, dragged:false, downX:0, downY:0, labelsShown:0};

function hashStr(s) { let h = 0; for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0; return h; }

// Deterministic seeded layout: Hindsight-style hash-ring init around a pinned employee center,
// fixed 300-iteration repulsion/spring settle (no d3), then frozen. Same data -> same picture.
function seededLayout() {
  const n = nodes.length;
  wx = new Float64Array(n); wy = new Float64Array(n);
  const pin = new Uint8Array(n);
  const base = Math.max(Math.sqrt(n) * 70, 140);
  nodes.forEach((nd, i) => {
    if (nd.type === "employee") { pin[i] = 1; return; }
    const seed = Math.abs(hashStr(nd.id));
    const angle = (i / n) * Math.PI * 2 + ((seed % 100) / 100) * 0.6;
    const radius = base * 0.35 + ((seed % 1000) / 1000) * base * 0.75;
    wx[i] = Math.cos(angle) * radius; wy[i] = Math.sin(angle) * radius;
  });
  nodeIndex = new Map(nodes.map((nd, i) => [nd.id, i]));
  const springs = links.map(l => [nodeIndex.get(l.source), nodeIndex.get(l.target)])
    .filter(([a, b]) => a !== undefined && b !== undefined);
  const K = 95, L = 135;
  for (let it = 0; it < 300; it++) {
    const fx = new Float64Array(n), fy = new Float64Array(n);
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
      let dx = wx[i] - wx[j], dy = wy[i] - wy[j];
      const d2 = dx * dx + dy * dy;
      if (!d2 || d2 > 4 * K * K) continue;
      const d = Math.sqrt(d2), f = (K * K) / d * 0.5;
      dx /= d; dy /= d;
      fx[i] += dx * f; fy[i] += dy * f; fx[j] -= dx * f; fy[j] -= dy * f;
    }
    for (const [a, b] of springs) {
      const dx = wx[b] - wx[a], dy = wy[b] - wy[a], d = Math.hypot(dx, dy) || 1, f = (d - L) / d * 0.06;
      fx[a] += dx * f; fy[a] += dy * f; fx[b] -= dx * f; fy[b] -= dy * f;
    }
    const cool = 6 * (1 - it / 300) + 0.4;
    for (let i = 0; i < n; i++) {
      if (pin[i]) continue;
      fx[i] -= wx[i] * 0.008; fy[i] -= wy[i] * 0.008; // gentle gravity keeps the field centered
      wx[i] += Math.max(-cool, Math.min(cool, fx[i]));
      wy[i] += Math.max(-cool, Math.min(cool, fy[i]));
    }
  }
  // Widen constellation to match landscape stage and leave room for under-node IDs.
  for (let i = 0; i < n; i++) wx[i] *= 1.7;
  sx = new Float64Array(n); sy = new Float64Array(n);
  S.fit = fitZoom();
  S.zoom = S.fit; S.panX = S.panY = 0;
}

function fitZoom() {
  // Fit axis bounds independently: use available width, reserve room for under-node labels.
  const maxX = Math.max(1, ...Array.from(wx, Math.abs));
  const maxY = Math.max(1, ...Array.from(wy, Math.abs));
  return Math.min(2, Math.max(0.1, (S.W - 110) / (2 * maxX)), Math.max(0.1, (S.H - 120) / (2 * maxY)));
}

function setLabels(visible) {
  labelsOn = visible;
  $("#labels").setAttribute("aria-pressed", String(visible));
  $("#labels").textContent = visible ? "Hide labels" : "Show labels";
  draw();
}

function inspectorLines(node) {
  const lines = [`${node.type}`, `id: ${node.id}`];
  for (const [key, value] of Object.entries(node)) {
    if (!["id", "type", "label"].includes(key)) lines.push(`${key}: ${value}`);
  }
  const related = graph.links.filter(l => l.source === node.id || l.target === node.id);
  neighborIds = new Set(related.flatMap(l => [l.source, l.target]));
  lines.push("", "Stored / provenance links:", ...related.map(l => `${l.source} · ${l.type} · ${l.target}`));
  return lines;
}

function select(node) {
  selectedId = node.id;
  focusIdx = nodeIndex.get(node.id);
  $("#detail-title").textContent = node.label;
  $("#detail").textContent = inspectorLines(node).join("\n");
  document.querySelectorAll("#node-list button").forEach(button =>
    button.setAttribute("aria-pressed", String(button.dataset.nodeId === node.id)));
  draw();
}

// --- Draw: full-bleed light constellation, DPR-aware, redrawn on interaction only ---
function draw() {
  const {W, H, dpr, zoom, panX, panY} = S;
  if (!W) return;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, W, H);
  if (!nodes.length) return;
  const cx = W / 2 + panX, cy = H / 2 + panY, margin = 60;
  const visible = new Uint8Array(nodes.length);
  for (let i = 0; i < nodes.length; i++) {
    sx[i] = cx + wx[i] * zoom; sy[i] = cy + wy[i] * zoom;
    visible[i] = sx[i] > -margin && sx[i] < W + margin && sy[i] > -margin && sy[i] < H + margin ? 1 : 0;
  }
  // Hover hit test: nearest node inside its reach (Hindsight hover).
  if (S.mouseX >= 0 && !S.down) {
    let best = -1, bestDist = Infinity;
    for (let i = 0; i < nodes.length; i++) {
      if (!visible[i]) continue;
      const d = Math.hypot(S.mouseX - sx[i], S.mouseY - sy[i]);
      if (d < Math.max(14, NODE_RADIUS[nodes[i].type] * Math.min(zoom, 2) + 8) && d < bestDist) { bestDist = d; best = i; }
    }
    if (best !== S.hover) { S.hover = best; canvas.style.cursor = best >= 0 ? "pointer" : "default"; }
  } else if (S.mouseX < 0 && S.hover >= 0) S.hover = -1;

  const focus = S.hover >= 0 ? S.hover : focusIdx >= 0 ? focusIdx : nodeIndex.get(selectedId) ?? -1;
  const focusLinks = new Set(), bright = new Set();
  if (focus >= 0) {
    links.forEach((l, li) => {
      if (l.source === nodes[focus].id || l.target === nodes[focus].id) {
        focusLinks.add(li);
        bright.add(nodeIndex.get(l.source)); bright.add(nodeIndex.get(l.target));
      }
    });
  }

  // Links: faint neutral web; focus links brighten; stored response relations stay Plasma-visible.
  links.forEach((l, li) => {
    const a = nodeIndex.get(l.source), b = nodeIndex.get(l.target);
    if (!visible[a] && !visible[b]) return;
    const isResponse = !LINK_COLORS[l.type];
    const isFocus = focusLinks.has(li);
    if (focus >= 0 && !isFocus && !isResponse) return;
    const ax = sx[a], ay = sy[a], bx = sx[b], by = sy[b];
    const midX = (ax + bx) / 2 + (by - ay) * 0.08, midY = (ay + by) / 2 - (bx - ax) * 0.08;
    ctx.strokeStyle = isResponse ? RESPONSE_COLOR : LINK_COLORS[l.type];
    ctx.globalAlpha = isFocus ? 0.8 : isResponse ? (focus >= 0 ? 0.35 : 0.6) : 0.27;
    ctx.lineWidth = isFocus ? 1.5 : isResponse ? 1.25 : 0.75;
    ctx.beginPath();
    ctx.moveTo(ax, ay);
    ctx.quadraticCurveTo(midX, midY, bx, by);
    ctx.stroke();
  });
  ctx.globalAlpha = 1;

  // Nodes: dots with a subtle static glow (Hindsight signature); hover/selection brightens, rest recede.
  const drawOrder = [];
  for (let i = 0; i < nodes.length; i++) if (visible[i] && i !== focus) drawOrder.push(i);
  if (focus >= 0 && visible[focus]) drawOrder.push(focus);
  for (const i of drawOrder) {
    const nd = nodes[i], isFocus = i === focus;
    const isBright = isFocus || bright.has(i);
    const r = Math.max(3, NODE_RADIUS[nd.type] * Math.min(zoom, 2));
    let alpha = nd.type === "employee" ? 1 : nd.type === "competency" ? 0.95 : 0.8;
    if (focus >= 0 && !isBright) alpha = 0.14;
    ctx.beginPath();
    ctx.arc(sx[i], sy[i], r, 0, Math.PI * 2);
    ctx.fillStyle = NODE_COLORS[nd.type];
    ctx.globalAlpha = alpha;
    ctx.shadowColor = NODE_COLORS[nd.type];
    ctx.shadowBlur = isFocus ? 22 : nd.type === "employee" ? 12 : isBright ? 8 : 0;
    ctx.fill();
    ctx.shadowBlur = 0;
    if (nd.type === "competency" || nd.type === "employee") {
      ctx.strokeStyle = INK; ctx.lineWidth = 1; ctx.stroke();
    }
    if (nd.id === selectedId) {
      ctx.strokeStyle = INK; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(sx[i], sy[i], r + 4, 0, Math.PI * 2); ctx.stroke();
    }
    ctx.globalAlpha = 1;
    if (focusIdx === i) { // keyboard focus ring
      ctx.setLineDash([3, 3]);
      ctx.strokeStyle = INK;
      ctx.globalAlpha = 0.9;
      ctx.beginPath();
      ctx.arc(sx[i], sy[i], r + 6, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha = 1;
    }
  }

  // Labels under nodes: collision-aware deconfliction grid (Hindsight), evidence hidden by the global toggle only.
  const used = [];
  const canPlace = (x, y, w, h) => !used.some(b => x < b.x + b.w + 4 && x + w + 4 > b.x && y < b.y + b.h + 3 && y + h + 3 > b.y);
  const claim = (x, y, w, h) => used.push({x,y,w,h});
  const priority = {employee: 0, competency: 1, rater: 2, evidence: 3};
  const order = drawOrder.slice().sort((a, b) => priority[nodes[a].type] - priority[nodes[b].type]);
  S.labelsShown = 0;
  for (const i of order) {
    const nd = nodes[i];
    const isEvidence = nd.type === "evidence";
    if (isEvidence && !labelsOn) continue;
    const isFocus = i === focus, isBright = bright.has(i);
    const r = Math.max(3, NODE_RADIUS[nd.type] * Math.min(zoom, 2));
    const label = nd.label.length > 42 ? nd.label.slice(0, 42) + "…" : nd.label;
    ctx.font = isEvidence ? EVIDENCE_FONT : NODE_FONT;
    const lw = ctx.measureText(label).width, lh = 13;
    const lx = Math.max(4, Math.min(W - lw - 4, sx[i] - lw / 2));
    let ly = sy[i] + r + 4;
    // Keep labels under dots; try lower rows rather than overlapping or silently hiding IDs.
    for (let row = 0; row < 30 && !canPlace(lx, ly, lw, lh); row++) ly += 16;
    if (ly + lh > H - 25 || lx + lw > W) continue;
    claim(lx, ly, lw, lh);
    if (ly > sy[i] + r + 5) {
      ctx.strokeStyle = "#b9b7b2"; ctx.lineWidth = 0.5;
      ctx.beginPath(); ctx.moveTo(sx[i], sy[i] + r); ctx.lineTo(lx + lw / 2, ly - 2); ctx.stroke();
    }
    ctx.textAlign = "center";
    ctx.globalAlpha = 1;
    ctx.fillStyle = isFocus ? INK : MUTED;
    ctx.strokeStyle = BG; ctx.lineWidth = 3; ctx.lineJoin = "round";
    ctx.strokeText(label, lx + lw / 2, ly + 10);
    ctx.fillText(label, lx + lw / 2, ly + 10);
    ctx.globalAlpha = 1;
    S.labelsShown++;
  }

  // HUD stats (Hindsight footer habit, Caldera muted tone).
  ctx.font = MONO;
  ctx.fillStyle = HUD;
  ctx.textAlign = "left";
  const stats = `${nodes.length} nodes · ${drawOrder.length} visible · ${S.labelsShown} labels`;
  ctx.fillText(stats, 12, H - (W < 360 ? 24 : 10));
  ctx.fillText(`zoom ${zoom.toFixed(2)}`, W < 360 ? 12 : W - 72, H - 10);
}

// --- Camera controls: buttons + wheel zoom, drag pan, reset to fit ---
function zoomBy(amount) { S.zoom = Math.max(0.15, Math.min(5, S.zoom * amount)); draw(); }
$("#zoom-in").onclick = () => zoomBy(1.2);
$("#zoom-out").onclick = () => zoomBy(1 / 1.2);
$("#reset").onclick = () => { S.zoom = S.fit; S.panX = S.panY = 0; draw(); };
$("#labels").onclick = () => setLabels(!labelsOn);
canvas.addEventListener("wheel", (e) => { e.preventDefault(); zoomBy(e.deltaY < 0 ? 1.1 : 1 / 1.1); }, {passive: false});
canvas.addEventListener("pointerdown", (e) => {
  const rect = canvas.getBoundingClientRect();
  S.mouseX = e.clientX - rect.left; S.mouseY = e.clientY - rect.top; draw();
  S.down = true; S.dragged = false; S.downX = e.clientX; S.downY = e.clientY;
  canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener("pointermove", (e) => {
  const rect = canvas.getBoundingClientRect();
  if (S.down) {
    const dx = e.clientX - S.downX, dy = e.clientY - S.downY;
    if (S.dragged || Math.hypot(dx, dy) > 3) {
      S.dragged = true;
      S.panX += dx; S.panY += dy;
      S.downX = e.clientX; S.downY = e.clientY;
      canvas.style.cursor = "grabbing";
      draw();
    }
    return;
  }
  S.mouseX = e.clientX - rect.left; S.mouseY = e.clientY - rect.top;
  draw();
});
canvas.addEventListener("pointerup", (e) => {
  if (S.down && !S.dragged && S.hover >= 0) select(nodes[S.hover]);
  S.down = false; S.dragged = false;
  canvas.style.cursor = S.hover >= 0 ? "pointer" : "default";
});
canvas.addEventListener("pointercancel", () => { S.down = false; S.dragged = false; });
canvas.addEventListener("pointerleave", () => { S.mouseX = S.mouseY = -1; S.hover = -1; draw(); });
canvas.addEventListener("focus", () => { if (nodes.length && focusIdx < 0) { focusIdx = 0; draw(); } });
canvas.addEventListener("blur", () => { focusIdx = -1; draw(); });
canvas.addEventListener("keydown", (e) => {
  if (!nodes.length) return;
  const ids = nodes.map(n => n.id).sort();
  if (["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft"].includes(e.key)) {
    e.preventDefault();
    const current = focusIdx >= 0 ? ids.indexOf(nodes[focusIdx].id) : -1;
    const step = e.key === "ArrowDown" || e.key === "ArrowRight" ? 1 : -1;
    focusIdx = nodeIndex.get(ids[Math.max(0, Math.min(ids.length - 1, (current < 0 ? 0 : current + step)))]);
    draw();
  } else if ((e.key === "Enter" || e.key === " ") && focusIdx >= 0) {
    e.preventDefault();
    select(nodes[focusIdx]);
  }
});

// --- DPR-aware resize; ResizeObserver catches container reflow, not just window resizes ---
function resize() {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  S.dpr = dpr; S.W = rect.width; S.H = rect.height;
  canvas.width = Math.max(1, Math.round(rect.width * dpr));
  canvas.height = Math.max(1, Math.round(rect.height * dpr));
  if (layoutDone) {
    S.fit = fitZoom();
    S.zoom = S.fit; S.panX = S.panY = 0;
  }
  draw();
}
window.addEventListener("resize", resize);
new ResizeObserver(resize).observe(canvas);
resize();

function render() {
  $("#node-list").replaceChildren();
  nodes = graph.nodes; links = graph.links;
  seededLayout();
  layoutDone = true;
  nodes.forEach(node => {
    const button = document.createElement("button");
    button.textContent = `${node.type}: ${node.label}`;
    button.dataset.nodeId = node.id;
    button.onclick = () => select(node);
    $("#node-list").append(button);
  });
  $("#reset").click();
  selectedId = undefined; focusIdx = -1; draw();
}
function options(id, values, label) {
  const picker = $(id), previous = picker.value;
  picker.replaceChildren(new Option(label, ""), ...values.map(v => new Option(v, v)));
  picker.value = values.includes(previous) ? previous : "";
}
async function load(e) {
  if (e) e.preventDefault();
  const current = ++requestId;
  layoutDone = false; nodes = []; links = []; selectedId = undefined; focusIdx = -1; neighborIds = new Set();
  S.hover = -1; S.mouseX = S.mouseY = -1; S.down = false;
  $("#node-list").replaceChildren();
  $("#detail").textContent = "Load a graph, then select a node to inspect quote, date and rater.";
  $("#detail-title").textContent = "Nothing selected";
  draw();
  $("#status").textContent = "Loading scoped evidence…";
  const payload = {employeeId: $("#employee").value, source: $("#source").value, actor: {id: $("#actor").value, role: $("#role").value}, quarter: $("#quarter").value, competency: $("#competency").value};
  try {
    const response = await fetch("/api/graph", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
    const data = await response.json();
    if (current !== requestId) return;
    if (!response.ok) throw new Error(data.error || "Graph request failed");
    graph = data;
    options("#quarter", data.filters.quarters, "All quarters");
    options("#competency", data.filters.competencies, "All competencies");
    $("#status").textContent = data.evidenceCount ? `${data.employeeId} · ${data.source} · ${data.evidenceCount} evidence · ${data.nodes.length} nodes · ${data.links.length} links` : "No visible evidence matches this employee/source/filter. Change filters or confirm runtime evidence first.";
    render();
    $("#detail").textContent = "Select a node to inspect its original quote, date, rater and stored links.";
    history.replaceState(null, "", `/graph?${new URLSearchParams({employee: payload.employeeId, source: payload.source})}`);
  } catch (error) { if (current === requestId) $("#status").textContent = `Cannot load graph: ${error.message}. Check source, actor and employee; retry Load graph.`; }
}
$("#filters").onsubmit = load;
$("#role").onchange = () => { $("#actor").value = ({employee: $("#employee").value, peer: "peer-001", manager: "manager-001", hr: "hr-001"})[$("#role").value]; load(); };
for (const id of ["#source", "#quarter", "#competency"]) $(id).onchange = load;
if ($("#source").value) load();
