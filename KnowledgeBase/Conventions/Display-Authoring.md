# Convention: Display / HMI authoring

House rules for authoring FrameworX Displays. Pairs with the `display-authoring-loop` skill (which enforces a
correctness + composition self-review) and the `svg-to-fx-display` recognition map.

## OnResize by display type

Pick `OnResize` by what the Display *is*, the responsive-design rule governs, not a blanket "stretch":

| Display kind | OnResize | Element locks (Responsive only) |
|---|---|---|
| Canvas with a prominent element that should resize (DataGrid / TrendChart / AlarmViewer) | **`Responsive`** | set `IsWidthAlign` + `IsHeightAlign` on that element |
| Process diagram / P&ID (equipment must keep proportions) | **`StretchUniform`**, non-uniform stretch distorts vessels | n/a |
| Viewer / text-led page (everything scales together) | **`ResizeChildren`** | n/a |
| KPI / dashboard | **`Responsive`** | cells reflow via the grid; no element locks |
| Header / Footer / Menu (docked in a Layout) | **`Responsive`** + `LockedHeight` (Header/Footer) or `LockedWidth` (Menu) | match the Header's native Width to the Layout Width so it isn't compressed |
| Fixed-pixel popup / dialog / form / chat panel | **`NoAction`** | n/a |
| Full-bleed background / decorative art | `StretchFill` | n/a |

A docked Header/Footer/Menu is **`Responsive` + the matching `Locked*` flag, not `NoAction`**. `LockedHeight` /
`LockedWidth` pin the docked band/rail to its native pixel size while `Responsive` still lets the contents
reflow. (`OnResize` has five valid values: `StretchFill`, `StretchUniform`, `Responsive`, `NoAction`,
`ResizeChildren`.)

### The six resize locks: flat properties, never raw XAML

Two levels, all authored as **flat JSON properties** (the import/export translates them, do not hand-write the
attached-property XAML):

- **Element** (honored only when the Display is `Responsive`): `IsWidthAlign` / `IsHeightAlign` = **stretch** the
  element with the container; `IsLeftAlign` / `IsTopAlign` = **move** it to track the container's right / bottom
  edge. By role: prominent grid/chart → Width + Height; band/row → Width only; bottom input row → Top + Width;
  right-edge control → Left; small top-left labels / nav icons → none.
- **Display** (peers of `OnResize` on the display row): `LockedWidth` pins a docked Menu/SubMenu rail width;
  `LockedHeight` pins a docked Header/Footer band height.

A Layout region's "Header set to Stretch" is the **region** `HorizontalAlign=Stretch`. A different knob from
`OnResize=StretchUniform`; don't conflate them.

### Verified mechanics & interaction cost (observed 2026-06-07)

What the Designer-MCP write path does to an **existing** Canvas Display, confirmed against the persisted
solution storage rather than against the write response:

- **`OnResize` (row field) DOES persist** on a Canvas `write_objects` update, verified
  `StretchUniform → Responsive` in the stored `DisplaysList` row. Responsive fixes are landable via the MCP.
- **Element locks DO round-trip** in the Elements body. Author `IsWidthAlign` / `IsHeightAlign` /
  `IsLeftAlign` / `IsTopAlign` as flat props on the element; they read back unchanged (confirmed on a DataGrid +
  16 side-pane TextBlocks).
- **Set `Description` in the Designer UI, not over MCP.** The "Canvas display updated" fast-path carries the
  body + `OnResize`; the row's `Description` does not come along with it (verified in one call: OnResize
  changed, Description stayed stale). This is **specific to `Description`**, not all row fields, and it is the
  same for both MCP paths: neither `write_objects` nor a workspace import lands it. So author the Description
  in the Designer UI, and **confirm `Description` by reading the row back and comparing**, not from the write
  response. (The DatasetsQueries body write has the same shape. See the read-back rule in
  `Patterns/MCP-Schema-Field-Gotchas.md`.)

Why display edits burn interactions, and how to spend fewer:
1. **Document objects are full-replacement.** Adding ONE lock = re-send the entire Elements array (a list page
   is ~24-30 elements). There is no per-element patch. Keep the last full read so you can re-emit with the one
   change instead of re-reading.
2. **Audit cheaply, don't dump.** For a display-level `OnResize` sweep across all displays, use one
   `get_objects(table_type='DisplaysList', detail='summary')` read, a row listing with key fields. If your
   build's summary projection omits `OnResize`, fall back to `detail='full'` per display, scoped to the
   Responsive-Canvas candidates only (the audit already restricts lock checks to those).
   `get_objects detail='full'` returns the whole body **plus a ~3 KB codeBehindIdioms block every call**.
   reserve it for the displays you are actually editing or auditing.
3. **Let row fields settle before you judge a read-back.** `get_objects` can briefly return a stale row field
   right after a write. re-read after the solution file settles before concluding a field was dropped.
   Element-body reads (Elements/locks) are fresh.
4. **Screenshots: use the file-path return, then Read the PNG.** `include_base64=true` overflows the
   tool-result token cap on a full-size render.
5. **Wrap a workspace import in the envelope shape** `{ObjectIdentification:…, Data:[…]}`. A raw top-level
   array does not import and ends the Designer session (`DESIGNER_CLOSED`).

### Responsive list + detail: the fixed pane is a DOCKED region, never a Canvas sibling (corrected 2026-06-07)

> **History (so we don't loop again).** An earlier note here first claimed a Responsive Canvas fills "the grid to
> a fixed-width *sibling* rail" (wrong), then over-corrected to "Canvas can't fill at all, use a Dashboard"
> (also wrong). **Both errors came from one missing rule, below.** `IsWidthAlign` genuinely **fills the
> container**, the shipped **Asset Monitor "Area"** Canvas proves it (its DataGrid carries
> `IsWidthAlign`+`IsHeightAlign` and fills). It is NOT proportional pixel-scaling. The decisive fact nobody had
> written down: **element locks anchor to the element's CONTAINER, never to a sibling element.**

**The rule.** "A grid that fills next to a fixed pane" is built by making the **fixed pane a docked Layout
region**, not a sibling element on the same Canvas:

1. **Docked-rail Canvas (preferred, keeps Canvas, no rebuild).** Put the detail rail in a Layout
   **Menu / SubMenu** region with `LockedWidth=true`; put the grid Canvas in the **Content** region with the grid
   carrying `IsWidthAlign`+`IsHeightAlign`. The Content region *is* the grid's container, so the grid fills it up
   to the docked rail. This is the shipped **Asset Monitor "Area + MenuTree"** pattern.
2. **Dashboard 2-column (alternative).** `PanelType=Dashboard`, `Columns:["*","360"]`, the `*` cell fills up to
   the fixed 360px cell. Use when the detail belongs *inside* the page rather than as a docked region; auto-stacks
   on mobile.

**Why grid + rail as Canvas siblings FAILS:** both anchor to the whole page, so the grid has no fixed right
boundary to fill *to* and the rail just floats: a gap opens between them. (Also confirm the Layout's **Content
region actually stretches** to the client: a non-stretching region caps the grid at a native-sized container,
which is the letterbox/gap seen in the 2026-06-07 runtime test.)

**Where plain Canvas locks suffice (no docking):** a single dominant control that fills the WHOLE region (one
grid / chart / viewer, no fixed pane beside it) → `IsWidthAlign`+`IsHeightAlign` is correct (Asset Monitor
"Area"). The per-object lock rule below covers this.

**List pages that scale uniformly today:** a list page left on `StretchUniform` scales uniformly and does not
fill. To give it grid-fill, apply pattern (1), dock the detail rail per page/layout. A real change, decided
per page (record it in `Decisions/`), not a free lock edit.

### The general per-object lock rule + the gaps it can't close (verified 2026-06-07)

The list+detail contract above is the worked case; this is the general rule for any **Canvas** element under
`OnResize=Responsive` (no-op on other OnResize; Dashboards reflow by grid → locks N/A). Signals from element
geometry vs display `Size` W×H: `spanFrac=Width/W` · `areaFrac=elemArea/displayArea` · `leftFrac=Left/W` ·
`rightGapFrac=(W-(Left+Width))/W` · `bottomGapFrac=(H-(Top+Height))/H` · `centerBias=(Left+Width/2)/W-0.5`.
First-match-wins:

1. **Dominant control** (chart/grid/graph/chat, `areaFrac≥0.50`) → `IsWidthAlign`+`IsHeightAlign`.
2. **Wide spanning banner** (text, `spanFrac≥0.50`, **not** flush-right `rightGapFrac>0.05`, `centerBias<0`) →
   `IsWidthAlign` only.
3. **Left-clustered nav row** (icon/button cluster, `leftFrac≤0.15`, `spanFrac<0.30`) → none (native top-left
   origin). 4. **Right-edge control** (small, `rightGapFrac≤0.05`, `spanFrac<0.40`) →
   `IsLeftAlign` (+`IsTopAlign` if flush-bottom). 5. **Bottom input row** (`bottomGapFrac≤0.05`,
   `spanFrac≥0.50`) → `IsTopAlign`+`IsWidthAlign`.
   6. **Small fixed label/logo** (`spanFrac<0.25`, `areaFrac<0.05`, near a corner) → none. 7. **Fallback** →
   none, never invent a stretch.

**Overrides (after the table):** rule 1 beats 2; rule 4 beats 2. **Axis-pinning override (load-bearing):**
`LockedHeight` forces `IsHeightAlign`=no **and** `IsTopAlign`=no; `LockedWidth` forces `IsWidthAlign`=no
**and** `IsLeftAlign`=no: a banner in a LockedHeight header gets a width-axis decision only. (A *wide
flush-right* band caption, e.g. an asset-name title: fails rule 2's not-flush-right guard AND rule 4's small
guard → Fallback → **no locks**.)

**Four gaps to log + ask, never guess:**
- **Decidability, geometry fits opposite intents.** A wide center/right-biased title is consistent with
  `IsWidthAlign` (keep spanning) *or* `IsLeftAlign` (hug the right edge) *or* none; a Canvas list+detail has no
  relative-layout container, so the panes scale independently. Geometry alone cannot settle these. Only author
  intent can (ask, or migrate the reflow-critical page to a docked region / Dashboard grid); record the answer
  in the project's `Decisions/`.
- **Breakpoint swap vs fluid.** A Layout region that *swaps* displays at discrete widths (RESS: the region
  carries `Page`/`Mobile`/`MobileLandscape` refs to different displays, e.g. `Page=Header`,
  `Mobile=HeaderPad`) renders each near native → element locks barely matter → **zero-lock is correct**. A region
  that *fluidly widens* one display needs locks. Read the Layout region refs (`DisplaysLayouts_*`) first.
- **Absent-lock ambiguity.** Zero locks ≠ "done": indistinguishable from "never authored." Report
  present/absent + heuristic-consistency, never "correct"; record a deliberate zero-lock choice in `Decisions/`.
- **Runtime-verification gap.** Locks manifest only at a **non-native** size, and driving the client to a
  second size + screenshot is outside the MCP surface, so a native-size render says nothing about reflow. From
  it you may NOT conclude that reflow is correct, that an absent lock was intentional, that a sibling's locks
  transfer "by analogy," or that Responsive is "verified". Resize the client by hand if you need that
  evidence; otherwise record "authored, runtime-resize unverified" and move on.

Add to the **interaction-cost** list above: **(6)** OnResize sweep = one
`get_objects(DisplaysList, detail='summary')` listing (`OnResize` + `PanelType` + `Size` + `Category` per
display, where the summary projection carries them; scoped per-display full reads only as the fallback);
per-display MCP-writability = the `Category` column. **(7)** `get_ui_tree` can return over ~1.6 MILLION chars,
past the token cap: save it to a file and python-parse a slice to find one control; most lock work needs
no tree at all. **(8)** Request **one display per `get_objects(DisplaysList, detail=full)` call**. Full reads
do not batch: passing multiple names returns empty objects (`[{},{}]`) rather than the rows.

### Composition patterns

- **Home page** = a Dashboard with **two ChildDisplays**: the standard landing shape.
- **Canvas on mobile** = split a wide Canvas into two child displays, each its own Canvas.

*(Verify against your build: `get_table_schema('DisplaysList')` returns the authoritative OnResize decision tree
plus the `LockedWidth` / `LockedHeight` props; the full reference is
`search_docs(query='Responsive Design', labels='skill')` and docs.tatsoft.com → Responsive Design and RESS /
Skill Display Construction.)*

## Use library symbols for equipment, not raw primitives

Build equipment from the symbol library, not from hand-placed shapes. Symbol source-order preference:
**Solution-local → `HPG/` → `HMI/` → `Wizard/` → raw primitives**. Compose a vessel from `Wizard/TANK` or
`Library/HMI/Vessels/*` and bind its `Level` / `State` parameters: don't hand-build it from a Rectangle +
Ellipse.

## Empty `LabelLink` renders a literal placeholder

A Button with `LabelLink=""` renders the literal text **"Button"**; a TextBox with no label renders
**"TextBox"**. `write_objects` succeeds and the config round-trips faithfully, so this shows up only in
the *rendered* result. To suppress: set `LabelPosition: None`, or bind the label. **After authoring a Display,
confirm the rendered / resolved state: a clean write and a clean config read-back are not sufficient for
Displays** (this is why `display-authoring-loop` reads the resolved tree, not just the write envelope).

## Color discipline

Use a hex color only when it carries **process meaning** (red = heat / alarm, etc.). Decorative or arbitrary
text colors use the theme token (e.g. `theme:TextForeground`), not hardcoded hex, so the Display follows the
solution theme.

## Button defaults

Set `HorizontalContentAlignment: Center` + `VerticalContentAlignment: Center` and an explicit `FontSize`
(≈12 for compact buttons, 14-16 for primary actions). The defaults left-align and under-size the label.

## `IsOpenInterval`

Leave at the 1000 ms default unless the Display's CodeBehind does measurable per-frame work. Lower values burn
CPU on every connected client for no benefit when CodeBehind is empty.

## Element types are normalized on write

`list_elements` lists more type names than the writer keeps as distinct types. On write, a fixed set is
normalized to canonical primitives, and the read-back `Type` shows the canonical name:

- → **Polygon:** Triangle, Star, Hexagon, Pentagon, Octagon, Arrow, Parallelogram, Trapezoid
- → **Path:** Cylinder, Gear, Cloud, TJunction, Hill, Curve, Senoid, Wave
- → **TrendChart:** XYChart;  → **SemiCircleGauge:** SemiCircle;  inside a Dashboard cell, **TextBlock → Label**
- **Don't author with `SvgGroup`**: it does not round-trip (it resolves to an empty Symbol with no SymbolName).

The write response's `warnings[]` is the authoritative prediction of the read-back `Type`. So for a diff-clean
round-trip, read the warnings or author the canonical `Type` + its geometry yourself. First-class shapes
(Rectangle, Ellipse, Polygon, Polyline, Path, Spline, Gridline) and all Dynamic types are not normalized.

*(The alias lists were observed against one build. Verify against your installed build's `list_elements` and
the write `warnings[]`.)*
