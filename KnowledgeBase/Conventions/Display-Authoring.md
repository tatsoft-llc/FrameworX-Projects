# Convention: Display / HMI authoring

House rules for authoring FrameworX Displays. Pairs with the `display-authoring-loop` skill (which enforces a
correctness + composition self-review) and the `svg-to-fx-display` recognition map.

## The fidelity contract: settle it BEFORE authoring

When the customer supplies a drawing of the screen (a PFS, a P&ID, an integrator's SVG, a screenshot of an
existing screen), decide one thing first: **is that drawing the spec, or the source material?**

| | **Replica** | **Derived** |
|---|---|---|
| The drawing is | the spec; its geometry *is* the requirement | authoritative for the *process*, not the layout |
| Acceptance test | positional identity: "the FC is upper-left, 101 directly below it" | readability |
| Elements are | **extracted** from the source: measured, not chosen | **composed** zone-first |

**Default to Replica, and say so in one line.** Ask only when the request explicitly signals adaptation
("modernise this", "make it operator-friendly"). The failure modes are not symmetric: a faithful replica is
never *rejected*. At worst you're asked to improve it, and the customer still recognises their plant. A
re-composition gets *"that's not my diagram"*, and the customer concludes the tool can't do the job. Default
to the recoverable failure, not the prettier one.

**Replica means measure, not eyeball.** Placing elements where they *look* right yields a plausible,
well-composed, **wrong** drawing, and because it looks fine, no review step catches it. The
`display-authoring-loop` will converge on a polished wrong answer, because every individual fix succeeds.
The method:

1. Render the source at a known scale with a **labelled coordinate grid** overlaid; read positions off it.
2. Record one row per object (equipment, bubble, valve, stream label, off-site connector) in the source's own
   coordinate space.
3. **Verify the table by drawing it back.** Render the measured boxes, bubble centres and diamond positions
   as an overlay on the original image, with the same grid, and compare it cell by cell. Reading positions
   *off* a drawing and drawing them *back* are different operations, and only the round-trip exposes what a
   single forward pass cannot: a misread coordinate, geometry that needs clipping, labels colliding with the
   symbol they annotate, an object overlapping a panel edge. On one P&ID replica this caught four such
   defects, including an unclipped hatch that drew a giant X across the sheet. Keep the overlay next to the
   table in `Specifications/`: it is the evidence that the table matches the drawing.
4. Map with **one transform**, `X = (x-x0)*s + margin`, so every relative position and proportion survives.
5. **Generate** the Elements array from that table; never hand-place.
6. **Keep the table.** It is the asset: it drives the preview mockup *and* the FX Canvas without the two
   drifting, and a re-scale or re-target is then a one-line change.

*Scanned source with no text layer:* pull the **embedded raster at its native resolution**
(PyMuPDF: `page.get_images()`, then `doc.extract_image(xref)`) rather than rasterizing the page at a guessed
DPI. You get the scan's true pixel grid to measure against, and no resampling blur on small instrument text.
Then read it in **native-resolution tiles** with a labelled grid; a whole A1 sheet downscaled to fit a vision
window loses exactly the loop numbers and stream digits you need.

Fidelity is about **position**, not austerity: a Replica still gets live bindings, colour by pipe service,
level fills and inline readouts. What it must not get is re-arrangement: don't move equipment to balance the
composition, don't swap in your own symbol vocabulary, don't stub a pipe run because routing it is
inconvenient. List the departures you genuinely need explicitly on hand-back; silent ones are what turn a
good display into "that's not my diagram".

*Canvas element mechanics for the generate step (transparent Label backgrounds, quoting generated literals,
primitive recipes, importing a large Elements array as a workspace JSON file):
`../Patterns/Canvas-Drawing-Replica-Mechanics.md`. Literal quoting in depth:
`../Patterns/Display-Value-Binding-Literals.md`.*

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

## Symbol label (mnemonic) in a TextBlock goes inside braces

Inside a Symbol definition, a TextBlock that shows a label value must wrap the mnemonic in braces:
`"LinkedValue": "{#HoldTemp:0}"`. The bare form `#HoldTemp:0` (correct in a Dynamic's `LinkedValue`, for
example `BargraphDynamic`) is NOT a value reference in a TextBlock: it renders as the literal text
("#HoldTe..."), with a clean write and a clean build. Rule: **TextBlock uses `{#Label:Default}`; Dynamics use
`#Label:Default`.** Don't "fix" the braces away. *(Observed on FrameworX 10.1.6.)*

## Value fields: pick the element by what the field must do

Verified at runtime on FrameworX 10.1.5:

| The field must... | Use | Key properties |
|---|---|---|
| Show a **number with a format** (decimals, integer) | `TextBlock` | `LinkedValue`, `FormatLink`, `TextWrapping: "NoWrap"`. **Not** `Label`: Label has no `FormatLink`, and the runtime ignores one if you write it (the write still succeeds) |
| Show **text or a value that needs content alignment** (centre / right) | `Label` | `LinkedValue`, `HorizontalContentAlignment`, `VerticalContentAlignment`, `BorderThickness: "0"`, `Background: "#00000000"` |
| **Accept input** | `TextBox` | `LinkedValue`, `FormatLink` (honoured), `LabelLink: ""`, `LabelPosition: "None"`, `BorderBrush: "#00000000"` |
| Show a date | `TextBlock` | `LinkedValue: "@Server.DateTimeInfo.Now"`, `FormatLink: "MM/dd/yyyy"`, NoWrap (`DateTimeInfo.Date` carries a time part and wraps) |
| Show a time | `TextBlock` | `LinkedValue: "@Server.DateTimeInfo.Time"` |
| Show a scaled / derived value | `TextBlock` or `Label` | an expression in `LinkedValue` (`"@Tag.A/B / 1000"`, `"Math.Truncate(@Tag.Max * 0.3)"`); compiles |
| Show a bitmap | simplified `Image` | `ImageName`, `Stretch: "Fill"` for a replica (the default is `Uniform`, which keeps aspect and leaves gaps) |

Rules that go with the table:
- **Number formats: use `F<n>`, not `N<n>`, unless you want a thousands separator.** `N0` renders 1750 as
  `1,750`; `F0` renders `1750`. `F1` = one decimal, rounded.
- **Always set `TextPreviewMode: "Placeholder"`** on a bound Label/TextBox/TextBlock. Otherwise the Designer
  canvas shows the raw `{Tag....}` path clipped inside the field, which reads as a broken binding.
- **Prefix and suffix text are separate elements.** A field shown as `SP: 42` is a static TextBlock `SP:` plus
  the value element beside it; there is no prefix property.
- **TextBlock has no text alignment.** To centre a static or variable caption, place it by measured width
  (a glyph-width table per font) or use a Label.
- Observation, same build: a `TextBox` with `Foreground: "#FFFFFF00"` and a transparent background **did**
  render yellow text on a Canvas page. Test before relying on the "platform controls are theme-only" rule
  below for TextBox foregrounds.

## Color discipline: theme brushes are the default, hex is the exception

**Every FrameworX element is already themed.** `list_elements('Rectangle')` reports `Fill` default
`"theme:DefaultFill"` with the note *"Themed by default, OMIT to use theme. Only specify to override."* Writing
a hex `Fill` does not add colour to an unstyled element: it **overrides and disables** that element's theming.
Do it on every element of a screen and the solution's theme controls nothing.

### The decision, in one line

Use a hex colour only when it carries **process meaning** that must not move when the theme changes
(red = alarm / heat). Everything else (grounds, panels, cards, borders, text, accents, KPI figures) takes a
**theme brush**.

### How to set one

Two spellings, both valid; prefer the `*Theme` property when the schema exposes one:

```jsonc
{ "Type": "Rectangle", "FillTheme": "PanelBackground" }      // preferred: named property
{ "Type": "TextBlock",  "Foreground": "theme:TextForeground" } // theme: token form
{ "Type": "Rectangle", "Fill": "#FF3498DB", "FillTheme": "" }  // deliberate override: CLEAR the theme
```

The `*Theme` family covers `FillTheme`, `StrokeTheme`, `ForegroundTheme`, `BackgroundTheme`,
`BorderBrushTheme`. **To force a custom hex you must blank the paired `*Theme` string**: setting only the hex
leaves the theme brush in place and the result is undefined.

### Find the brush before you invent a colour

`list_elements('ThemeColors')` is the catalog, grouped by purpose; it states outright *"PREFER these over
hardcoded hex colors."* `list_elements('ColorGroups')` gives the same names by group.
`list_elements('ThemeNames')` lists the 16 themes: light `Light / Platinum / Steel / Pearl / Gold / Sky /
ContrastLight / CustomLight`, dark `Dark / Onyx / Graphite / Indigo / Coffee / Navy / ContrastDark / CustomDark`.

The mapping most screens need:

| Role on the screen | Brush |
|---|---|
| Page ground | `PageBackground` |
| Card / panel / popup / control ground | `PanelBackground`, `PopupBackground`, `ControlBackground` |
| Card chrome | `ItemBackground`, `ItemBorder`, `ItemTitle`, `HeaderBrush`, `TitleBrush` |
| Body / heading / dimmed / link text | `TextForeground`, `TextAccentForeground`, `TextSubtleForeground`, `TextHyperlinkForeground` |
| The KPI the user is judged on | `AccentBrush`, or `ColorCyan` / `ColorTeal` |
| "A human owes an action" | `ColorAmber` |
| Process state | `StateOK`, `StateAlert`, `StateAlarm`, `StateActive`, `StateInactive`, `StateGreen`, `StateRed` |
| Alarm severity | `AlarmHighPriority`, `AlarmMediumPriority`, `AlarmLowPriority`, `AlarmDiagnostic`, `AlarmNormal` |
| Equipment on / off | `OnFill` / `OnStroke`, `OffFill` / `OffStroke` |
| Fluids | `Water`, `Waste` |
| Buttons / hover / focus / selection | `ButtonBackground`, `HoverBackground`, `FocusBrush`, `SelectBrush` |

### Platform controls are theme-only: colour properties on them are inert

`DataGrid`, `ComboBox`, `TextBox` and `TrendChart` follow the **client theme** and ignore per-element
`Background` / `Foreground`. The write still reports success, so a dark canvas with white grids looks like a
binding failure and isn't. Set the theme once instead, in the always-loaded Menu display's `DisplayOpening()`:

```csharp
@Client.Theme = "Onyx";
```

Or `designer_action('set_theme', '<name>')` at design time. Do **not** try to fight this per control.

### The one place theming does not reach: `FillColorDynamic` thresholds

`ChangeColorItem` takes `LimitColor` as `#AARRGGBB`, plus an optional numeric `LimitColorResourceId`
(-1 = custom). There is no exposed name-to-id mapping, so **state colours inside a dynamic cannot be written
as brush names.** Accept the hex there, and keep it consistent with the `State*` brushes you use statically so
the two agree. Flag it on hand-back when the customer cares about re-skinning.

### Why this matters commercially

A themed screen re-skins to a customer's brand by switching one theme, or by editing `CustomLight` /
`CustomDark` once. A hex-painted screen re-skins by editing every element. When the engagement involves
white-labelling or "can it look like *our* product", theming **is** the answer to that question, so building
in hex quietly forfeits it. Setting `@Client.Theme` afterwards does not rescue a hex-painted canvas: every
element has already overridden the theme.

## Button defaults

Set `HorizontalContentAlignment: Center` + `VerticalContentAlignment: Center` and an explicit `FontSize`
(≈12 for compact buttons, 14-16 for primary actions). The defaults left-align and under-size the label.

## `IsOpenInterval`

Leave at the 1000 ms default unless the Display's CodeBehind does measurable per-frame work. Lower values burn
CPU on every connected client for no benefit when CodeBehind is empty.

## Geometry primitives: `Path` for runs, `Polygon` only for closed shapes

**`Polygon` / `Polyline` `Points` are rescaled to fill the element's declared `Width`/`Height`; `Path` `Data`
coordinates are not rewritten.** This is the single most damaging trap in replica work, because the write
succeeds, the compile is clean, and the drawing simply comes out subtly wrong.

Observed on FrameworX 10.1.5, in one payload:

| Written | Declared box | Read back |
|---|---|---|
| `Polyline Points:"0,30 100,30 100,0 200,0"` | 200 x 60 | `"0,60 100,60 100,0 200,0"`: y stretched 30 to 60 |
| `Polygon Points:"30,0 60,30 30,60 0,30"` | 60 x 60 | unchanged (extents already matched the box) |
| `Path Data:"M0,10 L120,10 L120,50 L0,50 Z"` | 120 x 60 | coordinates unchanged (y extent 40, box 60) |

The Polygon case is the one that lulls you: it round-trips clean *only because* its extents happened to equal
its box. The divergent Polyline and Path cases in the same write are what prove the rule.

**Consequences for a measured drawing:**

- A horizontal pipe run has a y extent of **0**: a degenerate box, so undefined scaling. There is no correct
  `Width`/`Height` to declare for a Polyline.
- Every elbowed run is multi-extent, so any single box distorts at least one axis.

**The rule:**

- **Pipe runs, elbows, any open polyline: use `Path`**, with `Data` in coordinates *relative to the element's
  `Left`/`Top`*, and `Left`/`Top` set to the geometry's bounding-box origin. Set `Width`/`Height` to the
  bounding box, **and treat that as mandatory, not cosmetic**: a Path still *renders* stretched to fill its
  declared box, exactly like a Polyline. What Path buys you is that its **coordinates** are not rewritten, so
  a send-vs-readback comparison still tells you the truth. A Path in a wrong box draws wrong while its
  coordinates read back unchanged; set the box to the bounding box and the fill becomes the identity.
- **Do NOT byte-compare `Data` for an idempotency check.** The string is renormalized on every round-trip:
  `M 8,8 H 24 V 12 H 16 V 24 H 12 V 8 Z` comes back as `M8,8L24,8 24,12 16,12 16,24 12,24 12,8z` (`H`/`V`
  collapse to `L`, spaces become commas, `Z` lowercases). Compare **parsed coordinates**, never the raw string.
- **Closed regular shapes (stream-number diamonds, valve bowties, off-site flags, trapezoids): use `Polygon`**,
  and compute `Width`/`Height` from the exact point extents so the rescale is the identity transform.
- Never hand-write `Points` against a box you guessed. Generate both from the same coordinate table.

**Read-back is the detector.** The changed coordinates ARE returned by `get_objects detail='full'`: this trap
is caught for free *if you diff the geometry you sent against the geometry that came back*, and is invisible
if you only check `created`/`modified` counts.

**The box has two reasonable answers once the stroke is thick.** The fill fits the **stroked** geometry,
reserving a `StrokeThickness/2` pen margin per side:

| Box you declare | Stored Points | Render |
|---|---|---|
| exactly the point extents | unchanged | scale below 1: the shape draws `StrokeThickness` smaller than its own coordinates |
| extents + `StrokeThickness` (points shifted by T/2) | rewritten | scale 1.0: draws 1:1 |

The Designer's own drawing tools use the second form. At `StrokeThickness` 1 the difference is sub-pixel and
irrelevant. On a thick pipe run (T=10 on a 32-unit shape) it is about 24% and very visible. For thin strokes,
use the exact extents. For thick strokes, decide per drawing whether stored coordinates or on-screen scale
matter more, and *measure the result* rather than trusting either rule.

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
