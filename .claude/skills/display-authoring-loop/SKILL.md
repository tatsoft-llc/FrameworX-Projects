---
name: display-authoring-loop
description: >-
  Author and self-review a FrameworX Display via a two-iteration correctness + composition loop against this
  project's own solution in Solutions/. Drives the write → check-schema → render/screenshot →
  verify-live-bindings cycle: compose the Display (including the compose-time OnResize + lock decisions), then
  a correctness pass (get_screenshot + the resolved display tree) catches wrong-control-choice and
  invisible-in-JSON render defects, then a composition pass catches alignment and rhythm. Catches the defects
  that pass write-time validation but fail what the operator actually sees, before you hand the Display back.
  Use when building or converting a Display. Trigger phrases include "build this Display", "author this
  screen", "convert this mockup and build the Display", "implement this UI", "draw this in FrameworX".
license: Apache-2.0
metadata:
  author: Marc Taccolini
---

# Display Authoring Loop: Two-Iteration Self-Review

## Why this exists

A successful write confirms the JSON parsed and the config persisted. It does NOT confirm the rendered Display
matches intent. Three failure modes pass write-time validation and still fail the operator's eye:

**Mode A, wrong control choice.** You reach for shape primitives (Rectangle + Label + a click handler) where
the platform-canonical idiom is a composite, a Button, DataGrid, ComboBox, FlowPanel, ToggleSwitch, or a
Symbol. The JSON validates, the runtime executes, the result looks hand-rolled. Caught only by reading the
resolved control hierarchy back and comparing it against the recognition map's intent.

**Mode B, alignment math wrong.** Coordinates that don't line up: text not centered over its button, labels
drifting off grid, a header and its content panel not edge-aligned. The JSON looks right; the post-layout
resolved bounds disagree. Caught by a geometry diff against the resolved tree.

**Mode C, invisible-in-JSON render defects.** A property can be JSON-valid, round-trip faithfully through a
read-back, and still render wrong because an empty or default value triggers a default-seeding path on the
control. The classic tell: an interactive control whose label resolves to the platform's literal default text
("Button", "Label") instead of the string you intended. These are invisible in the JSON. Caught only by
querying the post-render resolved tree, not by a screenshot too small to read.

This skill drives the two-iteration loop that catches all three after the initial write.

## Before the loop: confirm the verification surface

The loop needs two reads against the live Designer canvas. Confirm both work for a Display before you start:

- **A legible live render**: `get_screenshot(element=<DisplayName>, max_width=1200, format='png')`. For a
  Display this must come from the live editor canvas, not a stored thumbnail. A stored thumbnail is pre-render
  and too small for Mode C; if that's all you can get, surface the gap and stop. Do NOT run the loop on a
  degraded toolset.
- **The resolved scene**: the per-element type, name, post-layout bounds, raw vs resolved label, whether the
  label is dynamically bound, and fill / foreground colors. Use the Designer's display-tree read (or
  `browse_object_model` / `get_objects` for the resolved control hierarchy). If you can't read the resolved
  tree, you can't catch Mode C. Surface the gap and stop.

If you're unsure which call returns the resolved Display tree on the installed product, check `search_docs`
before improvising.

## When this skill triggers

Fire when you're about to author a full FrameworX Display in this project's solution under `Solutions/`.
Trigger phrases: "build this Display", "author this screen", "convert this mockup and build the Display",
"implement this UI", "draw this in FrameworX".

Do NOT fire for:

- Tag, Device, Alarm, Dataset, Script, Report, or Symbol authoring. A successful write is sufficient
  confirmation for these per the workspace default in `CLAUDE.md` ("read it back").
- A focused single-property edit on one existing control: the verification surface is narrower than a full
  Display build; just read that one property back.
- Reads, queries, or exports with no write.

This is real-Display authoring on the customer's solution, not a sandbox (`CLAUDE.md` → "The target is YOUR
solution"). For a genuinely disposable experiment, copy first and target a scratch location under `AISessions/`.

## The loop

### Before Iteration 0: recognition

When an SVG mockup is the input, call `svg-to-fx-display` first. It produces the recognition map (region → FX
control + key properties + verification path). Hand that map into Iteration 0.

When the user gives prose intent or an existing recognition map (no SVG), use the supplied map directly. Don't
invoke `svg-to-fx-display` for prose-only inputs.

### Iteration 0: initial write

Apply the recognition map to compose the Display JSON. **Set the Display's `OnResize` mode and the per-element
locks now**: they are compose-time correctness decisions, not an audit-time patch (see "Responsive authoring"
below). Write it. A successful write is required to continue; on failure, surface the validation error and
stop: the loop does not self-heal a write failure.

### Iteration 1: correctness pass

Fetch both artifacts in parallel: the legible live render (`get_screenshot`) and the resolved display tree.

Critique against the **correctness checklist**:

1. **Mode A, control class per region.** For each region in the map, does the resolved tree show the
   platform-canonical control? A region mapped to a Button that resolves to Rectangle + Label + click handler
   is a Mode A miss. Fix: replace the hand-rolled construct with the canonical composite.

2. **Mode C, resolved label legibility.** For every interactive control carrying a label link, does the
   resolved label equal the intended user-facing string? A blank label link resolving to the platform default
   literal is the canonical miss; the inverse is a static label where a tag binding was intended.

3. **Mode C, resolved colors.** For each element with a deliberate theme intent (brand-primary, panel-bg,
   accent), do the resolved fill / foreground colors fall in the theme palette? Hard-coded hex bleed-through is
   a Mode C miss, prefer theme defaults (omit the color) per the Context Package's theme guidance.

4. **Mode B (gross), bounds sanity.** For each pair placed in a structural relationship (header above content,
   sidebar beside main, button row inside a toolbar), does the resolved tree preserve it? No unintended overlap,
   no off-canvas elements.

5. **Visibility.** For each element the mockup or prose showed, is it present in the resolved tree at the
   expected place? An element that the write accepted but the resolved tree does not carry is a Mode C miss.

6. **Responsive round-trip.** Confirm the compose-time `OnResize` value and the intended lock flags survived
   the write (read them back on the row / resolved tree). A docked Header that lost `LockedHeight`, or a data
   control that lost `IsWidthAlign`+`IsHeightAlign`, is a correctness miss, not a cosmetic one.

Emit a delta list: one entry per finding, `{ element_path, miss_class, observed, intended }`. Apply the fixes.
If the delta list is empty, note "Iteration 1: no findings" and proceed to Iteration 2 without writing.

### Iteration 2: composition pass

Re-fetch the render + resolved tree against the post-Iteration-1 state (not the Iteration-0 state, fixes may
have moved bounds).

Critique against the **composition checklist**:

1. **Mode B fine-grain, alignment math.** For each visually-aligned cluster the map declared (button row,
   filter bar, column headers, card grid), do the resolved bounds align on the relevant axis within tolerance?
   Default tolerance: ±4 px for aligned clusters; ±2 px for edge-snapped elements.

2. **Mode B fine-grain, vertical rhythm and grid.** Are paragraph-level vertical gaps consistent? Are columns
   of equal-weight items the same width? Are panel paddings uniform across sibling panels?

3. **Composition, density.** Does the rendered Display feel appropriately dense for its kind? Advisory, flag
   obvious outliers; skip if uncertain.

4. **Composition, idiom.** Does it read as platform-native? Advisory. Flag a region that looks hand-built
   despite each individual control being correct.

Items 1 and 2 are mechanically actionable from the resolved tree and enforce in full. Items 3 and 4 are
advisory judgment calls. Emit a final delta list; apply fixes.

### Iteration 3: OnResize + responsive-lock audit (read-only, single pass)

A distinct responsive-correctness check, not a third cosmetic pass. Read-only: it reports and recommends; it
does not iterate and it never drives a resize. Fires on any Display you authored or converted this session, plus
a one-shot solution-wide sweep if you touched more than one Display.

**Read cheaply:**
- **OnResize across all displays:** one `get_objects(table_type='DisplaysList', detail='summary')` read, a
  row listing with key fields. `OnResize` stores as an int enum (`0=StretchFill 1=StretchUniform 2=Responsive
  3=NoAction 4=ResizeChildren`); the listing also carries `PanelType`, `Size`, and **`Category`**. If your
  build's summary projection omits `OnResize`, fall back to `detail='full'` per display, scoped to the
  Responsive-Canvas candidates only (the audit already restricts lock checks to those).
- **Element locks:** one `get_objects(detail='full')` per **Responsive Canvas** display only (Dashboards reflow
  by grid → skip). Full-reads can't be batched (multiple names return `[{},{}]`). One display per call.

**Check, in order:**
1. **OnResize matches what the display IS** (the decision tree in "Responsive authoring" below /
   `KnowledgeBase/Conventions/Display-Authoring.md`): dominant-control Canvas → Responsive (+W/H on that
   control); P&ID/mimic → StretchUniform; viewer/text → ResizeChildren; KPI/Dashboard → Responsive (grid
   reflow, no element locks); docked band → Responsive+LockedHeight; docked rail → Responsive+LockedWidth;
   popup/dialog/fixed form → NoAction; full-bleed art → StretchFill. Report each as
   CORRECT / DEFENSIBLE-DIVERGENCE / DEFECT, never "fix" a documented defensible preference.
2. **Element locks (Responsive Canvas only)** vs the per-role rule (prominent grid/chart → W+H; band/row → W;
   bottom input row → Top+W; right-edge control → Left; nav icons / small top-left → none), applying the
   axis-pinning override (LockedHeight ⇒ no Top/Height lock; LockedWidth ⇒ no Left/Width lock).
3. **Name the ambiguous wide/spanning element** (e.g. an AssetName title): IsWidthAlign vs IsLeftAlign vs none
   all behave differently past native width; surface it, don't silently pick.
4. **Check the breakpoint model before recommending any lock.** If the hosting Layout *swaps* displays at
   discrete widths (region `Page`/`Mobile`/`MobileLandscape` refs to different displays: read
   `DisplaysLayouts_*`), each renders near native and zero-lock is CORRECT. Only a *fluidly-widening* region
   needs element locks.
5. **Grid-fills-next-to-a-fixed-pane = a DOCKED region, never a Canvas sibling.** Element locks anchor to the
   element's CONTAINER, never to a sibling: there is no element-to-element anchor. So a list page where a grid
   should fill *up to* a fixed detail rail does NOT work as two siblings on one Canvas: the grid has no fixed
   right boundary and a gap opens (an observed failure on a real list page). Correct structure: dock the rail
   as a Layout Menu/SubMenu region (`LockedWidth`) with the grid in the **Content** region
   (`IsWidthAlign`+`IsHeightAlign` fills to it), the Asset Monitor "Area + MenuTree" pattern, or a Dashboard
   2-col (`Columns:["*","<fixed>"]`). Flag any Responsive Canvas that puts a filling grid beside a fixed-width
   *sibling* pane as this anti-pattern (see Display-Authoring → "Responsive list + detail"). `IsWidthAlign`
   FILLS the container (not proportional pixel-scale), confirmed by the shipped Asset Monitor "Area" grid.

**Write-wall pre-filter (do this BEFORE proposing any lock edit):** from the same DisplaysList listing, only
`Category = MCP` displays accept `write_objects`; on the rest the call returns "Only Description can be
updated". Do NOT recommend a lock change you cannot apply. Mark non-writable targets "Designer-UI only."

**Hard limit, this pass must NOT claim lock-correctness:** it runs against the native-size Designer canvas, and
driving the client to a second window size is outside this pass, so reflow at non-native sizes is UNVERIFIABLE
here. Report locks as PRESENT / ABSENT and heuristic-consistent. Never "verified correct." An absent lock is
ambiguous (intentional vs never-authored: state it, don't infer). Do not assert a sibling's locks transfer "by
analogy." WebView2-hosted controls (TKnowledgeGraph) come back blank in the WPF screenshot, blank ≠ broken:
don't judge those from this pass.

**Close line:** OnResize verdict per touched display · locks present/absent per Responsive-Canvas element ·
which targets are MCP-writable vs Designer-UI-only · explicit "runtime resize NOT verified. Locks
static-consistent only."

### Exit criterion: fixed two-pass cap (+ the read-only audit)

The "no third pass" rule below bounds the **cosmetic composition loop** only; Iteration 3 (read-only OnResize +
lock audit) is a separate responsive-correctness report and always runs once. After Iteration 2 applies its
fixes, the loop ends unconditionally. Hand the Display back with a one-line
summary: "Iteration 1: N findings fixed. Iteration 2: M findings fixed." If both passes found nothing, say so
explicitly, "Iteration 1: clean. Iteration 2: clean." Do NOT run a third pass; the fixed cap prevents
unbounded drift on cosmetic noise.

## Responsive authoring: set OnResize + the six locks at compose time

A Display that renders correctly at design size still fails when the window resizes unless its `OnResize` mode
and per-element locks are set deliberately at compose time (Iteration 0). This is a correctness decision, not a
cosmetic one: set it when you write the Display, then confirm it survived the round-trip in Iteration 1
(checklist item 6). House conventions: `KnowledgeBase/Conventions/Display-Authoring.md`.

`OnResize` is a Display-level enum: `StretchFill=0`, `StretchUniform=1`, `Responsive=2`, `NoAction=3`,
`ResizeChildren=4`.

### OnResize decision tree: by Display role

| Display role | `OnResize` | Element locks (see below) |
|---|---|---|
| **Canvas with a prominent data control** (DataGrid / TrendChart / AlarmViewer) | `Responsive` | `IsWidthAlign`+`IsHeightAlign` on that control; band/row element → `IsWidthAlign` only; bottom-pinned input row → `IsTopAlign`+`IsWidthAlign`; right-edge control → `IsLeftAlign`; small top-left labels / nav icons → no locks |
| **Process diagram / drawing** (P&ID, equipment layout) | `StretchUniform` | none |
| **Viewer / text-led page** (everything scales together) | `ResizeChildren` | none |
| **KPI / Dashboard** | `Responsive` | none, the grid reflows; no element locks |
| **Header / Footer / Menu** (docked region) | `Responsive` + display lock | `LockedHeight` (Header/Footer) or `LockedWidth` (Menu), see the docked rule below |
| **Popup / Dialog / Form** | `NoAction` | none |
| **Full-bleed background / decorative art** | `StretchFill` | none |

### The six locks: written as flat JSON properties, never raw XAML

There are six locks at two levels. **Always write them as flat JSON properties on the element or display
object; never emit raw attached-property XAML**: the platform's import/export translates the flat JSON to the
underlying property. All six are honored only when the Display's `OnResize=Responsive`.

**Element level, four booleans:** `IsLeftAlign`, `IsTopAlign`, `IsWidthAlign`, `IsHeightAlign`.

- `IsWidthAlign` / `IsHeightAlign`: **STRETCH** the element with the container.
- `IsLeftAlign` / `IsTopAlign`: **MOVE** the element to track the container's right / bottom edge.

Per-element lock by role (inside a `Responsive` Canvas):

| Element role | Locks |
|---|---|
| Prominent data control (DataGrid / TrendChart / AlarmViewer / tree) | `IsWidthAlign` + `IsHeightAlign` |
| Full-width band / row panel | `IsWidthAlign` |
| Bottom-pinned input row | `IsTopAlign` + `IsWidthAlign` |
| Right-edge control | `IsLeftAlign` |
| Small top-left label / nav icon | none |

**Display level, two booleans:** `LockedWidth`, `LockedHeight` (peers of `OnResize` on the display row). They
pin a **docked** region to native pixels under `Responsive`: `LockedHeight` pins a docked Header/Footer band
height; `LockedWidth` pins a docked Menu/SubMenu rail width.

### Docked Header / Footer / Menu rule

A docked Header or Footer is `Responsive` + `LockedHeight`; a docked Menu/SubMenu rail is `Responsive` +
`LockedWidth`. **Match the Header's native `Width` to the Layout `Width`** so the band does not horizontally
compress.

> Precision note: a layout that reads "Header set to Stretch (spans full width)" means the **region's**
> `HorizontalAlign=Stretch`, NOT `OnResize=StretchUniform`. Two different knobs: do not conflate them.

### Standard composition shapes

- **Home / landing page** = a Dashboard: `Responsive` + grid Star columns + a splitter + **two
  `ChildDisplays`**, with **no element locks** (the grid does the responsive work). The shipped Asset Monitor
  Demo's Home page is the worked example.
- **Mobile Canvas split**: when a Canvas page must also render on mobile, split it into two child displays,
  each its own Canvas. Do not try to make one Canvas serve both form factors.

## What this skill does NOT do

- **Does not override the workspace write default.** Tags, Devices, Alarms, Datasets, Scripts, Reports, and
  Symbols stay on the default. A successful write, read back, is sufficient. The two-iteration loop fires only
  for Display authoring.
- **Does not run against runtime screenshots.** Both iterations target the Designer canvas. Runtime visual
  verification, and confirming the Display's bindings carry live values with good quality once the solution
  runs, is a separate commissioning step, not this loop.
- **Does not author the recognition map.** That's `svg-to-fx-display`'s job. This skill receives the map and
  drives the write + review cycle.
- **Does not decide layout architecture.** Canvas vs Dashboard, cell sizing, panel type: those belong to the
  recognition map or to the user's explicit direction.
- **Does not run for minor edits.** A targeted single-property fix on an existing Display does not trigger the
  loop. The loop is for full-Display authoring runs where a recognition map drives the initial write.

## Anti-patterns

- **Skipping Iteration 1 because the screenshot looks right.** The screenshot is low-information for Mode C. The
  resolved display tree is the authoritative surface for label-link and color correctness. Always run both reads
  in parallel each iteration.
- **Running Iteration 2 against the Iteration-0 tree.** Iteration 2 critiques the post-Iteration-1 state. A
  stale tree mixes already-fixed and not-yet-fixed findings.
- **Running a third iteration.** The fixed two-pass cap is a deliberate scope brake. Residual geometry noise
  after Iteration 2 goes into the hand-back summary, not into another loop.
- **Treating a stored thumbnail as acceptable.** Stored thumbnails are pre-render and too small for Mode C. If
  the render comes back as a stored thumbnail for a Display, the live-render surface isn't available. Surface
  the gap, do NOT continue.
- **Bypassing `svg-to-fx-display` and writing from raw SVG shape primitives.** Writing rects → Rectangles
  directly without recognition produces Mode A misses at scale. Recognition is the gate.
- **Deferring OnResize to "later".** A Display authored with the default OnResize and zero locks reads as
  "never decided" to every later audit. Decide at Iteration 0; record a deliberate zero-lock choice in the
  project's `Decisions/`.

## Composition with other skills

- **`svg-to-fx-display`**: call first for any mockup-driven build. Produces the recognition map this skill
  consumes. Don't bypass recognition and write directly from SVG primitives.
- **`ground-first`**: call before this skill on any session that hasn't bootstrapped. The Context Package is
  required to interpret the resolved tree (theme tokens, canonical control behaviors, list→detail patterns),
  and grounding in the project's prior Displays + `KnowledgeBase/` conventions keeps a new Display consistent
  with the ones already built.
- **`premise-check`**: when a region asks for a pattern with no native equivalent on the platform, the
  right move is to re-question the design intent, not to invent a workaround.
- **`KnowledgeBase/Conventions/Display-Authoring.md`**: the house Display conventions (OnResize by display
  type, symbol source-order, the empty-LabelLink literal-text gotcha, color discipline). Read it before
  composing; it is where Mode A / Mode C defaults come from.
