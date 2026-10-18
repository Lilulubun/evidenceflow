/* KerjaKita AI demo UI. Vanilla JS, no build, no dependencies, no secret storage. */
"use strict";

const $ = (sel) => document.querySelector(sel);
const EMP = "emp-004";
let chatSession = null;
function chatRender(events) { const stream = $("#chat-stream"); stream.replaceChildren(...events.map(e => { const p=document.createElement('p'); p.className=`chat-event ${e.type}`; p.textContent=(e.progress ? `[${e.progress}] ` : '') + (e.text || (e.preview ? 'Evidence preview ready.' : '')); if (e.type === 'citation') { (e.evidence || []).forEach(r => { const c=document.createElement('div'); c.className='claim'; c.textContent=`${r.id} · ${r.rater_role} · ${r.quarter} · ${r.competency}: “${r.quote}”`; p.append(c); }); } return p; })); const last=events[events.length-1]; const chatDone = last && ['evidence_created'].includes(last.type); $("#chat-form").hidden=!chatSession || chatDone; if (last && last.type === 'confirmation_required') { const b=document.createElement('button'); b.className='primary'; b.textContent='Confirm and save evidence'; b.onclick=async()=>{const r=await api('POST','/api/chat/confirm',{sessionId:chatSession}); chatRender(r.body.events || []);}; stream.append(b); } }
async function startChat(kind = 'contribution') { const r=await api('POST','/api/chat/session',{actor:actor(), kind}); chatSession=r.body.sessionId; chatRender(r.body.events || []); $("#chat-input").focus(); }
$("#chat-add").onclick=()=>startChat('contribution'); $("#chat-feedback").onclick=()=>startChat('feedback'); $("#chat-checkin").onclick=()=>startChat('checkin');
$("#chat-form").onsubmit=async(e)=>{e.preventDefault(); const input=$("#chat-input"); const r=await api('POST','/api/chat/message',{sessionId:chatSession,message:input.value}); input.value=''; chatRender(r.body.events || []); input.focus();};

function actor() { return { id: $("#actor-id").value.trim() || "demo", role: $("#role").value }; }

async function api(method, path, payload) {
  const loading = document.createElement('p');
  loading.className = 'meta'; loading.setAttribute('role', 'status'); loading.textContent = 'Loading evidence…';
  if (path !== '/health') $('#app').prepend(loading);
  try {
    const response = await fetch(path, {
      method,
      headers: payload === undefined ? {} : { "Content-Type": "application/json" },
      body: payload === undefined ? undefined : JSON.stringify(payload),
    });
    const body = await response.json();
    return { status: response.status, body };
  } catch (error) {
    $('#app').replaceChildren(card('Workspace unavailable', '<p>Request failed. Check server connection, then choose a workspace action to retry.</p>'));
    throw error;
  } finally { loading.remove(); }
}

function card(title, html) {
  const section = document.createElement("div");
  section.className = "card";
  section.innerHTML = `<h2>${title}</h2>${html}`;
  section.querySelectorAll('table').forEach(table => {
    const scroll = document.createElement('div'); scroll.className = 'table-scroll'; scroll.tabIndex = 0; scroll.setAttribute('role', 'region'); scroll.setAttribute('aria-label', `${title} table, scroll horizontally if needed`);
    table.replaceWith(scroll); scroll.append(table);
  });
  return section;
}

function field(label, id, value = "", type = "text", autocomplete = "off") {
  return `<label class="field">${label}<input id="${id}" type="${type}" autocomplete="${autocomplete}" value="${value}"></label>`;
}

/* ---------- AI mode banner (REF-003: mock/live/degraded visibility) ---------- */
async function refreshBanner() {
  const { body } = await api("GET", "/health");
  const el = $("#ai-banner");
  const state = body.aiState ? body.aiState.state : body.mode;  // fallback: older health payload
  const detail = state === "degraded" && body.aiState.detail ? ` · ${body.aiState.detail}` : "";
  el.textContent = `AI mode: ${state}${detail}`;
  el.className = `banner ${state}`;
}
setInterval(refreshBanner, 5000);

/* ---------- Capture flows (quick replies → form → confirmation card) ---------- */
const FLOWS = {
  contribution: {
    label: "Add contribution",
    fields: [["employeeId", "Employee ID", EMP], ["period", "Period (Q4-2026)", "Q4-2026"], ["competency", "Competency", "collaboration"],
             ["situation", "Situation", ""], ["action", "Personal action", ""], ["result", "Result / impact", ""], ["verifier", "Verifier", ""]],
  },
  feedback: {
    label: "Give feedback",
    fields: [["employeeId", "Employee ID", EMP], ["period", "Period", "Q4-2026"], ["competency", "Competency", "collaboration"],
             ["behavior", "Observed behavior", ""], ["impact", "Impact", ""],
             ["feedbackType", "Type (recognition/coaching/concern)", "coaching"], ["visibility", "Visibility", "employee_manager_hr"]],
  },
  checkin: {
    label: "Start check-in",
    fields: [["employeeId", "Employee ID", EMP], ["period", "Period", "Q4-2026"], ["competency", "Competency", "adaptability"],
             ["progress", "Progress", ""], ["obstacle", "Obstacle", ""], ["support", "Support", ""],
             ["owner", "Owner ID", ""], ["dueDate", "Due date (YYYY-MM-DD)", ""], ["successEvidence", "Success evidence", ""]],
  },
};

function showQuickReplies() {
  const wrap = card("Capture evidence", `<p class="muted">Structured evidence is created only after you confirm the card below.</p><div class="quick-replies">${Object.entries(FLOWS).map(([kind, flow]) => `<button data-kind="${kind}">${flow.label}</button>`).join("")}</div>`);
  wrap.querySelectorAll("button[data-kind]").forEach((btn) => { btn.onclick = () => showForm(btn.dataset.kind); });
  $("#app").replaceChildren(wrap);
}

function showForm(kind) {
  const flow = FLOWS[kind];
  const form = card(flow.label, flow.fields.map(([id, label, value]) => field(label, `f-${id}`, value)).join("") +
    `<button class="primary" id="f-submit">Review draft</button> <span id="f-msg" class="muted"></span>
     <div id="f-hints" class="muted"></div>`);
  form.querySelector("#f-submit").onclick = async () => {
    const payload = {};
    flow.fields.forEach(([id]) => { payload[id] = form.querySelector(`#f-${id}`).value.trim(); });
    const msg = form.querySelector("#f-msg");
    let hintText = "";
    // REF-005: advisory rubric hints; shown as suggestions, never block submission.
    if (kind === "feedback") {
      const { body: hints } = await api("POST", "/api/feedback/hints", payload);
      if (hints.hints && hints.hints.length) {
        hintText = `suggestions (advisory, mode ${hints.mode}): <ul>${hints.hints.map((h) => `<li>${h}</li>`).join("")}</ul>You can still submit.`;
      } else if (hints.missing && hints.missing.length === 0) {
        hintText = "Rubric looks good (advisory).";
      }
    }
    const { status, body } = await api("POST", `/api/conversations/${kind}/draft`, { actor: actor(), payload });
    if (body.state === "needs_clarification") {
      msg.textContent = `Missing: ${body.missing.join(", ")} · nothing stored.`;
      return;
    }
    if (status !== 201) { msg.textContent = body.reason || "Rejected."; return; }
    showConfirmation(kind, body.draftId, body.preview, hintText);
  };
  $("#app").replaceChildren(form);
}

function showConfirmation(kind, draftId, preview, hintText = "") {
  const rows = Object.entries(preview).map(([key, value]) => `<tr><th>${key}</th><td>${String(value)}</td></tr>`).join("");
  // REF-005: hints travel with the draft onto the confirmation card; still advisory.
  const view = card("Confirm before saving", `${hintText ? `<div id="c-hints" class="muted">${hintText}</div>` : ""}<table>${rows}</table><p class="muted">Evidence becomes immutable once confirmed.</p>
    <button class="primary" id="c-yes">Confirm & save</button> <button id="c-no">Discard</button>`);
  view.querySelector("#c-yes").onclick = async () => {
    const { body } = await api("POST", "/api/conversations/x/confirm", { actor: actor(), draftId });
    if (body.state === "confirmed") { showEvidenceChip(body.evidence); }
    else { view.querySelector("h2").textContent = `Rejected: ${body.reason}`; }
  };
  view.querySelector("#c-no").onclick = showQuickReplies;
  $("#app").replaceChildren(view);
}

function showEvidenceChip(evidence) {
  const data = evidence.data;
  const chips = `<span class="chip ${data.rater_role}">${data.rater_role}</span><span class="chip">${data.period || ""}</span><span class="chip">${data.competency || ""}</span>`;
  const quote = data.result || data.impact || data.progress || "";
  const view = card("Evidence created", `<code>${evidence.id}</code> ${chips}<p>“${quote}”</p>
    <p class="muted">Saved by ${evidence.created_by.role} <code>${evidence.created_by.id}</code> at ${evidence.created_at}</p>
    <button onclick="showQuickReplies()">Back</button>`);
  $("#app").replaceChildren(view);
}

/* ---------- Manager review ---------- */
async function showReview() {
  const { body: view } = await api("POST", "/api/review/view", { employeeId: EMP });
  const rows = view.evidence.map((row) => {
    const conflict = view.conflicting.some((c) => c.id === row.id);
    return `<tr><td><code>${row.id}</code></td><td><span class="chip ${row.raterRole}">${row.raterRole}</span></td>
      <td>${row.period || ""}</td><td>${row.competency || ""}</td><td>${row.quote}</td>
      <td>${conflict ? '<span class="chip conflict">conflict</span>' : ""}</td></tr>`;
  }).join("");
  const missing = view.missingCompetencies.map((c) => `<span class="pill warn">${c}</span>`).join(" ") || '<span class="pill ok">none</span>';
  const screen = card(`Manager review · ${EMP}`,
    `<p>Rater roles: ${view.raterRoles.map((r) => `<span class="chip ${r}">${r}</span>`).join("")} · Missing competencies: ${missing}</p>
     <table><tr><th>ID</th><th>Role</th><th>Period</th><th>Competency</th><th>Quote</th><th></th></tr>${rows}</table>
     <button class="primary" id="r-draft">Draft cited summary</button> <span id="r-msg"></span>`);
    const title = document.createElement('p'); title.className = 'muted'; title.textContent = 'No confirmed evidence yet. Use Capture to add and confirm evidence.';
    if (!view.evidence.length) screen.append(title);
  screen.querySelector("#r-draft").onclick = () => showSummaryDraft(screen);
  $("#app").replaceChildren(screen);
}

async function showSummaryDraft(reviewCard) {
  const { body } = await api("POST", "/api/review/summary-draft", { employeeId: EMP });
  const claims = body.claims.map((claim, i) =>
    `<div class="claim"><div>${claim.text}</div><div class="src">cite: <code>${claim.evidenceId}</code> “${claim.quote}”</div>
     <button data-i="${i}" class="c-edit">Edit</button> <button data-i="${i}" class="c-del">Remove</button></div>`).join("");
  const draftCard = card(`AI-assisted summary (${body.mode} mode)`,
    `<p class="muted">${body.notice} AI state: ${body.aiState?.state ?? "unknown"}.</p>${claims}
     ${field("Manager rating", "r-rating", "meets")}${field("Rationale", "r-rationale", "")}
     <button class="primary" id="r-record">Record provisional rating</button> <span id="r-msg2" class="muted"></span>`);
  draftCard.querySelectorAll(".c-edit").forEach((btn) => { btn.onclick = () => {
    const i = Number(btn.dataset.i);
    const text = prompt("Edit claim text (citation stays linked):", body.claims[i].text);
    if (text !== null) { body.claims[i].text = text; btn.closest('.claim').firstElementChild.textContent = text; }
  }; });
  draftCard.querySelectorAll(".c-del").forEach((btn) => { btn.onclick = () => {
    body.claims.splice(Number(btn.dataset.i), 1);
    btn.closest(".claim").remove();
    draftCard.querySelectorAll('.claim').forEach((claim, i) => claim.querySelectorAll('button').forEach(button => { button.dataset.i = i; }));
  }; });
  draftCard.querySelector("#r-record").onclick = async () => {
    const { status, body: result } = await api("POST", "/api/review/rating", {
      actor: actor(), employeeId: EMP, summary: body.claims,
      rationale: draftCard.querySelector("#r-rationale").value, rating: draftCard.querySelector("#r-rating").value });
    const msg = draftCard.querySelector("#r-msg2");
    msg.textContent = result.state === "recorded" ? `Recorded (citation coverage: ${result.citation.coverage}%, ${result.citation.citationCount} cited claims)` : `Rejected: ${result.reason}`;
    if (result.state === "recorded") showFinalize();
  };
  $("#app").append(draftCard);
}

async function showFinalize() {
  const finalizeCard = card("Finalize",
    `<p class="muted">Finalization requires rationale; unresolved responses require explicit acknowledgment.</p>
     ${field("Final rationale", "fin-rationale", "")}
     <label class="field"><input type="checkbox" id="fin-ack"> Acknowledge unresolved responses</label>
     <button class="primary" id="fin-go">Finalize as manager</button> <span id="fin-msg"></span>`);
  finalizeCard.querySelector("#fin-go").onclick = async () => {
    const { status, body } = await api("POST", "/api/review/finalize", {
      actor: actor(), employeeId: EMP, rationale: finalizeCard.querySelector("#fin-rationale").value,
      acknowledgeUnresolved: finalizeCard.querySelector("#fin-ack").checked });
    const msg = finalizeCard.querySelector("#fin-msg");
    if (body.state === "finalized") { msg.textContent = "Review finalized."; }
    else { msg.textContent = `Rejected: ${body.reason}`; }
  };
  $("#app").append(finalizeCard);
}

/* ---------- Employee response flow ---------- */
async function showRespond() {
  const { body: view } = await api("POST", "/api/review/view", { employeeId: EMP });
  const others = view.evidence.filter((row) => row.raterRole !== "self");
  const pick = card("Respond to evidence (employee)",
    `<table><tr><th>ID</th><th>Role</th><th>Quote</th><th></th></tr>
     ${others.map((row) => `<tr><td><code>${row.id}</code></td><td>${row.raterRole}</td><td>${row.quote}</td>
       <td><button data-id="${row.id}">Respond</button></td></tr>`).join("")}</table>`);
  if (!others.length) pick.append(Object.assign(document.createElement('p'), {textContent:'No evidence from other raters yet. Confirm peer feedback first, then return here.'}));
  pick.querySelectorAll("button[data-id]").forEach((btn) => { btn.onclick = () => responseForm(btn.dataset.id); });
  $("#app").replaceChildren(pick);
}

function responseForm(evidenceId) {
  const form = card(`Respond to ${evidenceId}`,
    field("Response", "p-response") +
    `<label class="field">Relationship
      <select id="p-rel"><option value="clarified">clarified</option><option value="superseded">superseded</option><option value="disputed">disputed</option></select></label>` +
    field("Source", "p-source") +
    `<button class="primary" id="p-go">Draft response</button> <span id="p-msg" class="muted"></span>`);
  form.querySelector("#p-go").onclick = async () => {
    const { body } = await api("POST", "/api/responses/draft", { actor: actor(), payload: {
      originalEvidenceId: evidenceId, response: form.querySelector("#p-response").value,
      relationship: form.querySelector("#p-rel").value, source: form.querySelector("#p-source").value } });
    if (body.state !== "ready_for_confirmation") { form.querySelector("#p-msg").textContent = body.reason || "Needs clarification."; return; }
    const confirmCard = card("Confirm response",
      `<table><tr><th>Original</th><td><code>${evidenceId}</code> (stays unchanged)</td></tr>
       <tr><th>Response</th><td>${body.preview.response}</td></tr><tr><th>Relationship</th><td>${body.preview.relationship}</td></tr></table>
       <button class="primary" id="p-yes">Confirm</button>`);
    confirmCard.querySelector("#p-yes").onclick = async () => {
      const { body: done } = await api("POST", "/api/conversations/x/confirm", { actor: actor(), draftId: body.draftId });
      confirmCard.querySelector("h2").textContent = done.state === "confirmed" ? `Response linked: ${done.evidence.id}` : `Rejected: ${done.reason}`;
    };
    $("#app").append(confirmCard);
  };
  $("#app").replaceChildren(form);
}

/* ---------- HR audit ---------- */
async function showAudit() {
  const { status, body } = await api("POST", "/api/hr/audit", { actor: actor(), employeeId: EMP });
  if (body.state !== "ok") {
    $("#app").replaceChildren(card("HR audit", `<p class="pill bad">${body.reason}</p><p class="muted">Switch role to HR.</p>`));
    return;
  }
  const review = body.review || {};
  const history = (review.rating_history || []).map((entry) =>
    `<tr><td>${entry.stage}</td><td>${entry.before ?? "not set"}</td><td>${entry.after}</td><td>${entry.actor.id}</td><td>${entry.timestamp}</td><td>${entry.reason}</td></tr>`).join("");
  const screen = card(`HR audit · ${EMP}`,
    `<p><span class="pill ${review.finalized ? "ok" : "warn"}">${review.finalized ? "finalized" : "not finalized"}</span>
      evidence=${body.evidence.length} relations=${body.relations.length} events=${body.events.length}</p>
     <h2>Rating history (append-only)</h2>
     <table><tr><th>Stage</th><th>Before</th><th>After</th><th>Actor</th><th>Timestamp</th><th>Reason</th></tr>${history}</table>
     <h2>Relations</h2>
     <table><tr><th>Original</th><th>Response</th><th>Type</th></tr>
     ${body.relations.map((r) => `<tr><td><code>${r.original_evidence_id}</code></td><td><code>${r.response_evidence_id}</code></td><td>${r.relationship}</td></tr>`).join("")}</table>`);
  $("#app").replaceChildren(screen);
}

/* ---------- Settings (masked key, server-side only) ---------- */
async function showSettings() {
  const { body } = await api("GET", "/api/settings");
  const screen = card("AI settings (server-side, key masked)",
    `<p class="muted">The API key is stored server-side (file mode 0600) and every response shows only ${body.apiKey || "(unset)"}.
     It never enters browser storage or this page.</p>
     ${field("Base URL", "s-base", body.baseUrl || "")}${field("Chat model", "s-chat", body.chatModel || "")}
     ${field("API key (masked echo keeps stored key)", "s-key", body.apiKey || "", "password", "new-password")}
     <label class="field">Enabled <select id="s-enabled"><option value="false">false (mock)</option><option value="true">true</option></select></label>
     <button class="primary" id="s-save">Save</button> <button id="s-test">Test connection</button> <button id="s-models">Discover models</button> <span id="s-msg" class="muted"></span>`);
  screen.querySelector("#s-enabled").value = String(body.enabled === true);
  screen.querySelector("#s-save").onclick = async () => {
    const payload = { baseUrl: screen.querySelector("#s-base").value, chatModel: screen.querySelector("#s-chat").value,
                      apiKey: screen.querySelector("#s-key").value, enabled: screen.querySelector("#s-enabled").value === "true" };
    const { body: result } = await api("POST", "/api/settings", payload);
    screen.querySelector("#s-msg").textContent = result.state === "saved" ? "Saved (key masked server-side)." : `Rejected: ${result.reason}`;
    refreshBanner();
  };
  screen.querySelector("#s-test").onclick = async () => {
    const { body: result } = await api("POST", "/api/ai/test", {});
    screen.querySelector("#s-msg").textContent = result.ok ? `OK (${result.model})` : `Not reachable: ${result.reason}`;
  };
  screen.querySelector("#s-models").onclick = async () => {
    const { body: result } = await api("POST", "/api/ai/models", {});
    screen.querySelector("#s-msg").textContent = result.ok ? (result.models.length ? `Models: ${result.models.join(", ")}` : "No models returned.") : `Discovery failed: ${result.reason}`;
  };
  $("#app").replaceChildren(screen);
}

/* ---------- Screens per role ---------- */
const DEFAULT_IDS = { employee: "emp-004", peer: "peer-001", manager: "manager-001", hr: "hr-001" };
const SCREENS = {
  employee: [["Capture", showQuickReplies], ["Respond to evidence", showRespond], ["Review (view)", showReview]],
  peer: [["Capture", showQuickReplies]],
  manager: [["Review emp-004", showReview]],
  hr: [["Audit emp-004", showAudit]],
};

function renderActions() {
  const wrap = $("#screen-actions");
  wrap.replaceChildren(...SCREENS[$("#role").value].map(([label, fn]) => {
    const btn = document.createElement("button");
    btn.textContent = label;
    btn.onclick = fn;
    return btn;
  }));
  const settingsBtn = document.createElement("button");
  settingsBtn.textContent = "AI settings";
  settingsBtn.onclick = showSettings;
  wrap.append(settingsBtn);
}

$("#role").onchange = () => {
  // Demo default: switching role switches to that role's demo actor, so provenance stays honest.
  $("#actor-id").value = DEFAULT_IDS[$("#role").value];
  renderActions(); showQuickReplies();
};
refreshBanner();
renderActions();
showQuickReplies();
