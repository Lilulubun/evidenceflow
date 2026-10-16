# Caldera UI refinement / REF-009

## Scope and purpose
Applied user-authored `DESIGN.md` to workspace, employee graph and server-rendered validation results. Existing stdlib server, vanilla JS and graph API remain. No dependency/framework, installer, global preference, plugin or agent-entry change.

Anti-slop applied in DURING mode (explicit session choice). Core/UI/human/mobile upstream texts fetched by explicit user request into `research/anti-slop/`; read fully in paginated parts. Upstream: https://github.com/miqdadbadjuber/anti-slop . Installer workflow intentionally not run. These files are task-local reference snapshots, not an installed global skill.

Design read: evidence workspace for employees/managers/HR, Caldera warm industrial/editorial. ENERGY 3 / RHYTHM 2 / MOTION 1.

## Decision reasons
- Pumice canvas and Limestone surfaces preserve warm Caldera identity while separating working regions without shadows.
- Ember identifies primary submission and graph selection; Obsidian text on Ember avoids low-contrast white text.
- Sulfur tags communicate actual status/selection, not fictional live status.
- One compact Plasma halftone per page carries requested signature without stealing evidence space; never used on controls.
- Anton condensed headings give industrial/editorial structure. DM Sans 500 keeps dense workflow labels legible.
- Graph/inspector split prioritizes evidence selection and source verification; narrow layout stacks them, with same-data keyboard node list.
- Evidence labels show for small graphs; dense graphs reveal selected/hovered/focused evidence label, avoiding permanent label collision. Node list always includes every returned node.
- Circle/diamond/square/ring encode real node types without color-only semantics. Bold lines indicate selected-node connections; actual link type remains in inspector.
- Rounded rectangle surfaces (40px) differ from pill controls and square status tags. 16px gaps and reduced mobile padding avoid marketing-scale emptiness.
- Wide workspace tables use labeled, keyboard-focusable horizontal regions rather than squeezing 6 columns into unreadable fragments.
- No illustration, avatars, decorative icon library, shadow, glow, animation loop, fabricated metrics or inferred graph links.

## Font attribution
`static/anton-latin.woff2`: Anton Regular, Google Fonts CDN v27. `static/anton-OFL.txt` is accompanying SIL Open Font License.
`static/dm-sans-500-latin.woff2`: DM Sans 500, Google Fonts CDN v17. `static/dm-sans-OFL.txt` is accompanying SIL Open Font License.
License sources: https://github.com/google/fonts/tree/main/ofl/anton and https://github.com/google/fonts/tree/main/ofl/dmsans . Self-hosted Latin subsets, no runtime external request. Other scripts use system fallback. Requested proprietary PP Neue Corp Compact unavailable; Anton is disclosed substitute, not a claimed PP asset.

## Verified evidence
Exact command output and browser records: `docs/caldera_ui_checks.txt`.
- Required Python checks and both JS syntax checks exit 0. TKT3 12/12.
- Original `runtime_state.json` and `runtime_ai_settings.json` SHA-256 unchanged during regression; isolated profile scratch state/settings used.
- Real browser graph: research 24 evidence / 37 nodes / 72 links; Q4 collaboration filter 3 / 7 / 9. Keyboard Enter selection updates original quote inspector. Node list selection, source/quarter/competency/role/actor/employee controls, denied scope, empty runtime, zoom in/out/reset and pointer pan exercised.
- Real browser workspace: incomplete draft clarification; contribution draft/discard/retry/confirm; check-in confirm; peer feedback hints/confirm; employee disputed response confirm; manager cited draft/edit/remove/rating; unresolved response finalization gate; acknowledgment/finalize; HR finalized audit; settings save and unconfigured connection-test feedback. Settings browser storage empty. API regression verifies masked key and no secret echo without typing secrets into browser.
- Summary Edit handler exercised with native prompt return stubbed in browser; visible claim text and remove-index maintenance verified. Native OS/browser prompt itself not visually assessed.
- `/tkt3`: actual 12/12 output, trajectory expands, real fixture/input/output text retained.
- Widths 320/768/1280: graph, workspace, populated review and validation page have no document horizontal overflow. Six-column review table remains 640px within 248px scroll region at 320px, 14px table type.
- Visible keyboard focus on skip link and SVG node verified; SVG node Enter selected. No captured error/unhandled-rejection events on final graph/workspace pages. Full assistive technology audit not performed.
- Screenshot inspection found source-option truncation and hidden labels on small graphs; fixed both and recaptured. Final screenshot inspection: no blocking desktop overlap/clipping; mobile graph dense but readable inspector/list. List intentionally internally scrollable; final partially visible row is not lost content.

Screenshots: `docs/screenshots/caldera_graph_desktop.png`, `caldera_graph_mobile.png`, `caldera_workspace_desktop.png`.

## Anti-slop delivery gate
Evidence per item, task scope only. PASS means inspected sources and executed paths below, not certification of every device or assistive technology.

### Hard gate
- R-02 PASS: newly authored UI strings use periods/colon/middle dot, no em dash.
- R-03 PASS: 320/768/1280 document-width checks; contained wide table; responsive graph inspector and filters.
- R-17 PASS: displayed counts come from API graph and TKT3 results, no invented KPI cards.
- R-18 PASS: no testimonials or invented avatars added.
- R-23 PASS: explicit Caldera direction; existing navigation destinations; CSS signature explicitly requested; no new illustration/logo asset.
- R-24 PASS: workspace, graph and validation routes loaded in real browser.
- R-25 PASS: WCAG formula ratios recorded in check log for all active text/surface/control pairings. Text uses Obsidian or dark neutral, never white on Ember.
- R-26 PASS: existing workflow controls and graph controls exercised, results recorded element by element above and in JSON log. Prompt return stub disclosed.
- R-27 PASS: graph loading/empty/denied text; workspace request loading/error; review/respond empty messages. No data-dependent decorative skeleton.
- R-28 PASS: no FAQ added.
- R-32 PASS: native controls, skip link, visible outlines, SVG Enter selection and native details; node list supplies full keyboard alternative.
- R-33 PASS: direct source edits only; no rewriting script or patch script shipped.
- R-34 PASS: one explicitly requested light theme; no broken toggle shipped.
- R-35 PASS: app run on fresh isolated server; command, browser control and screenshot evidence recorded. No claim of physical mobile keyboard testing.
- R-36 PASS: synthetic/demo limits retained, no compliance/performance/customer claim added.
- R-37 PASS: user Caldera direction transcribed before implementation; dials declared.
- R-38 PASS: actual existing synthetic evidence remains explicitly labeled synthetic; no plausible fabricated activity added.

### Purpose gate
- R-01 PASS: palette from user direction; no generic gradient.
- R-04 PASS: node geometric marks encode actual types; no decorative icon library.
- R-06 PASS: Anton industrial headings / DM Sans readable workflow reason above; no large monospace heading.
- R-07 PASS: compact halftone carries explicit Caldera signature, not full-page grid.
- R-08 PASS: no decorative arrow appended to CTAs.
- R-09 PASS: tags show actual demo/mode/provenance/selection state.
- R-10 PASS: no glass/backdrop blur.
- R-12 PASS: zero shadows.
- R-13 PASS: zero glow.
- R-14 PASS: form, graph and inspector serve distinct content, not feature-card grid.
- R-19 PASS: MOTION 1, hover/focus/state feedback only, no looping animation.
- R-22 PASS: no generic illustration.

### Liveliness
- Dials PASS: ENERGY 3 / RHYTHM 2 / MOTION 1 declared and visible.
- Consistency PASS: condensed structural headings, compact controls, graph/inspector composition.
- Focal point PASS: evidence work surface, not KPI cards or marketing hero.
- Whitespace PASS: meaningful group gaps, reduced mobile padding, no full-height hero.
- Accent PASS: Ember primary action/selection only; Sulfur functional; Plasma signature only.
- Motif PASS: condensed type, warm flat canvas, dotted dividers, pill actions.
- Design read PASS: declared before source edits.

### Craftsmanship and quality locks
- C-1 PASS: major choices have one-line reasons above.
- C-2 PASS: functional paths recorded, no placeholder button added.
- C-3 PASS: every region belongs to evidence workflow or validation.
- C-4 PASS: tested narrow/tablet/desktop, loading/empty/error, keyboard selection; physical device/AT limits disclosed.
- C-5 PASS: only existing labeled synthetic sources and executed test results.
- R-05 PASS: no template marketing or generic dashboard shell.
- R-11 PASS: rectangle surfaces, pill controls, square tags, distinct graph shapes.
- R-15 PASS: action-specific capture/review/confirm/finalize controls retained.
- R-16 PASS: no new AI marketing buzzwords.
- R-20 PASS: user Caldera palette/type/shape identity across pages.
- R-21 PASS: fixed light appearance is explicit user brand direction.
- R-29 PASS: neutral base plus Ember action, Sulfur functional tag, single Plasma surface.
- R-30 PASS: not clone of external product.
- R-31 PASS: color/layout/type/spacing/surface/shape reasons recorded.

## Limits
Local synthetic provenance, not live Hindsight; demo actor controls are not production authentication. No physical mobile keyboard, screen-reader session or axe run. 200% root-text reflow checked in browser; not full browser/OS zoom certification. Dense mobile SVG remains overview; zoom controls and readable complete node list are deliberate fallback. No production security claim. No unrelated API/governance changes. Existing claim-edit visual update and remove-index defect fixed because browser review needs edits to reflect what will save.

## REF-011 Hindsight constellation addendum (supersedes earlier graph styling)
- User correction: graph area stays light Limestone `#f7f6f2`; only nodes/links adopt Hindsight constellation design. Shell, inspector, filters and node list remain light. Earlier zero-glow/monochrome-graph rules are superseded for this graph only.
- Vanilla DPR-aware canvas replaces SVG. Deterministic ID-hash seed plus fixed 300-step force settle, pinned employee center, frozen layout; no dependency or perpetual animation. Nodes: Ember employee, Obsidian evidence, outlined Sulfur competency, warm-gray rater. Stored link types use distinct neutral tones; response links alone use Plasma. Static glow and hover/selection highlight follow upstream interaction direction.
- Attribution in `static/graph.js`: vectorize-io/hindsight control-plane constellation, Apache-2.0; studied commit `9a499b1759084a86598eff8af30ed59f7354e76c`. Adaptation omits React/Pretext, ambient drift/pulse, inferred links and upstream data model. Not live Hindsight.
- Labels default on, placed below dots with bounding-box collision checks and displaced-label leader lines. Global evidence-label toggle retained (`aria-pressed`). Desktop 37/37 labels visible; mobile 320 overview deconflicts to 19/37 labels, full list preserves every node. Zoom/list are deliberate dense-view fallbacks. Labels use dark neutral text on Limestone; Sulfur/Ember dots have dark outlines. No blanket WCAG certification for faint contextual links or dimmed unrelated dots.
- Browser :8167: research 24 evidence/37 nodes/72 links; filtered Q4 collaboration 3/7/9. Toggle 37→13→37, hover, click quote inspector, Enter/Space selection, zoom buttons/wheel, drag pan/reset, deterministic layout repeat, DPR=2 backing store, no captured error events. Widths 320/768/1280 have no document horizontal overflow. Screenshots vision-checked: light card contained, no blocking graph clipping; center remains dense at overview scale (some node-label association ambiguity).
- Screenshots: `docs/screenshots/graph_constellation_desktop.png`, `docs/screenshots/graph_constellation_mobile.png`. Synthetic source and demo-auth caveats unchanged. No physical device/screen-reader audit.

## REF-010 graph readability addendum
- Labels: all evidence IDs visible by default at any count; hover no longer hides anything; new global `#labels` toolbar toggle ("Hide labels"/"Show labels", honest `aria-pressed`) hides only evidence labels; non-evidence labels stay for orientation. Evidence labels gain leader ticks, side anchoring toward outside, and two staggered rows; rater/competency labels flip below the node in the upper half to avoid the evidence label band.
- Calm canvas: default edges `#b9b7b2` 1px; selection darkens stored links to `#54524d` 1.5px and fades unrelated nodes to opacity .55 (labels never disappear). Node fills softened to Pumice/Limestone/`#514f4a` outlines; employee stays Obsidian solid, rater an outline ring; shapes kept but smaller (22px square with 4px radius, 26px diamond, 10–18px circles); Ember `#fc5000` marks selection only.
- Legibility: node labels 14px DM Sans with surface halo (evidence IDs 12px caption style), selected label 15px bold; inspector "Node details" heading reduced to 22px; page h1 on graph page tamed to clamp(1.75rem,3vw,2.25rem) so the canvas dominates; inspector no longer leaks layout fields (`angle:`, `row:`).
- Invariants: same deterministic rings, no force layout, no new dependency, no new accent hues; inspector keeps exact quotes/dates/raters and stored links only; filters, keyboard selection, zoom/pan/reset, node-list fallback, scope/visibility rules unchanged.
- Evidence: `docs/screenshots/graph_readability_desktop.png` (1280, 24 evidence), `graph_readability_mobile.png` (320). Desktop vision pass after fixes: no collisions, calm spokes, no debug text, no clipping. Mobile pass: no horizontal overflow; labels small at native 320 by design, toggle/zoom/list are the disclosed fallbacks.
