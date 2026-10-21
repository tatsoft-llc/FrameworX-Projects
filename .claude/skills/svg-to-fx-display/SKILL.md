---
name: svg-to-fx-display
description: >-
  Translate a designer- or integrator-supplied SVG mockup of an operator/HMI screen into FrameworX Display
  elements by mapping each visual signature (gauges, tanks/pumps/valves mimics, trend plots, level bars, alarm
  lists, setpoint fields, state lamps, command buttons) to the FX control that actually carries that pattern.
  Recognition-only: does NOT write the Display JSON, does NOT make layout decisions, does NOT invent
  controls. Use when handed an .svg mockup that has to land as a FrameworX HMI Display (customer/integrator
  screen drawing, design-tool export, legacy-screen redraw). Maps to the FX control set verified live via
  list_elements(). Trigger phrases include "translate this screen mockup", "convert this SVG to a Display",
  "what FX control is this gauge/tank/trend", "is this a gauge or a label", "I have a screen drawing from the
  customer".
license: Apache-2.0
metadata:
  author: Marc Taccolini
  version: "1.0.0"
---

# SVG → FX Display: Recognition Rules (HMI)

## Why this exists

An SVG mockup is shape-and-style: rectangles, arcs, text runs, fills, strokes, paths. A FrameworX HMI Display is
control-and-dynamic: a `RadialGauge` with a linked value, a `Tank` symbol with a built-in level dynamic, a
`TrendChart` with a pen list, an `AlarmViewer` with its own severity rendering. The two vocabularies are not
parallel: a circle with tick-marks and a needle in the SVG is a `RadialGauge` in FX, not an `Ellipse` with a
hand-rotated `Polyline`.

Naive translation reads the SVG element-by-element and emits the shape primitive that looks closest. The result
compiles, the read-back confirms what was written, and you move on. But the user gets a Display with a tank
hand-drawn from a rectangle and a fill rect where every operator-built FX Display would have dropped the Tank
symbol and bound its level. The mockup ships pixel-correct and conceptually wrong. And dead, because none of
the dynamics that make an HMI screen *live* are there.

This skill is a recognition layer between the SVG and the write step. It does not author the JSON. It tells the
authoring path WHICH control each region of the mockup is.

## When this skill triggers

Fire when an SVG mockup of an operator screen is the input and a FrameworX Display is the target:

- An `.svg` file is the source-of-truth for an HMI/SCADA Display build.
- The user says "convert this screen mockup", "translate this SVG", "what control is this gauge / tank / trend",
  "is this a gauge or a label".
- An agent about to author a Display has SVG content as the layout source.

Do NOT fire for: hand-drawn mockups (no SVG to parse), design-tool links without an export, PNG/JPG raster
mockups (no parseable structure), or in-Designer authoring with no external mockup.

## What this skill does NOT do

- **Does not author Display JSON.** No write calls, no XAML emission. The output is a recognition map (region →
  FX control + key properties + verification path), nothing more.
- **Does not make layout decisions.** Canvas vs Dashboard, cell sizing, anchor math, out of scope. A Display's
  panel type comes from design intent, not from the SVG.
- **Does not invent FX controls.** If an SVG pattern has no FX equivalent verified via `list_elements()`, the
  rule emits `NO-FX-EQUIVALENT, flag to the user`. Never invent a control.
- **Does not write the solution.** Recognition only. Authoring is downstream.
- **Does not bind data.** Recognition says "this region IS a RadialGauge"; it does not pick the tag, the range,
  or the pen list. Data wiring is a separate workflow grounded in the IO register / UNS, not in the SVG.

## How to use the rules below

For each visually-distinct region of the mockup:

1. **Match the SVG signature**: the shape primitives and their topology (e.g., "arc + tick marks + needle from
   center").
2. **Read the rule's FX target**: the control name verified in `list_elements()` plus the key properties that
   carry the pattern.
3. **Check the counter-example**: what looks similar but ISN'T this control. Most rules have one. Skipping this
   step is the main way SVG translation goes wrong.
4. **Emit a recognition entry** for the authoring step, in this shape:

   ```
   region: <mockup file> at <bounds>
   pattern: <rule name>
   fx_control: <element_type or Symbol path from list_elements()>
   key_properties: <name=value, name=value>
   verification: <how the authoring agent will confirm this is the right control>
   ```

The recognition map is the authoring agent's input. The recognition map is NOT itself a Display.

## The rules

Each rule cites: SVG signature → FX control (verify in `list_elements()` on the installed build) → key
properties → counter-example. Categories in parentheses are the `list_elements()` category. Work the mockup
region by region.

### R1: Circular / radial gauge

**SVG signature.** A circle or arc with tick marks around the perimeter, a needle/pointer from the center, a
numeric value near the hub, often colored zone bands (green/amber/red) along the arc.

**FX target.** `RadialGauge` (`Gauges`) for a full/round dial; `SemiCircleGauge` (`Gauges`, alias `SemiCircle`)
for a half-dial; `Compass` (`Gauges`) for a heading/direction dial specifically.

**Key properties.** Linked value to the process tag; Min/Max range; zone thresholds for the colored bands.

**Counter-example.** A circle with ONLY a number inside (no ticks, no needle, no arc) is a numeric readout,
`DigitalGauge` (R3), not a RadialGauge. A circle that is an equipment glyph (a pump impeller) is a mimic Symbol
(R9).

### R2: Linear gauge / level bar

**SVG signature.** A vertical or horizontal bar partially filled, usually with a tick scale alongside and
sometimes a setpoint marker. Or a bare rectangle whose fill height tracks a value.

**FX target.** `LinearGauge` (`Gauges`) when there is a scale with ticks and zones; a `Rectangle` (`Shapes`) +
`BargraphDynamic` (`Dynamic`) for a plain proportional fill with no scale; `ProgressBar` (`Viewer`) for a simple
0-100 % bar.

**Key properties.** Linked value, Min/Max, orientation. For the bargraph case, `BargraphDynamic` bound to the
value tag.

**Counter-example.** A tank shape with a liquid level is NOT a bare LinearGauge: it is the Tank Symbol (R9),
which carries the level as a built-in dynamic. Reach for LinearGauge only for an abstract scaled bar, not for a
vessel.

### R3: Numeric readout / digital value

**SVG signature.** A prominent numeric `<text>` (often 7-segment / monospaced), usually with a unit run, often
in a bordered box. No input affordance.

**FX target.** `DigitalGauge` (`Gauges`) or `DigitalMeter` (`Charts`) for a styled instrument readout; a `Label`
(`Interaction`) with a linked value for a plain bound number in body text.

**Key properties.** Linked value to the tag; numeric format + units.

**Counter-example.** An EDITABLE number (spinner arrows, an input border the operator types into) is a setpoint
field: `NumericTextBox` (R5), not a read-only DigitalGauge. Diagnostic: is there an input affordance?

### R4: Trend / time-series plot

**SVG signature.** A rectangular plot area with a time X-axis and a value Y-axis, one or more line traces,
gridlines, and usually a legend.

**FX target.** `TrendChart` (`Charts`): the FX time-series control (`XYChart` is the same control in XY-pen
configuration). For a categorical bar chart use `BarChart`; for proportions `PieChart` / `PieChartPlus`.

**Key properties.** Pen/tag list, time span, Y-axis range(s).

**Counter-example.** A Gantt-style horizontal band of states over time is `Timeline` (`Charts`), NOT TrendChart.
A static line drawing with no axes is just a `Polyline` (`Shapes`).

### R5: Setpoint / numeric entry

**SVG signature.** A box holding an editable number, spinner up/down arrows, an input border, a caret, often a
unit suffix. Operator-writable.

**FX target.** `NumericTextBox` (`Interaction`) for typed numeric entry; `Slider` (`Interaction`) for a
drag-to-set continuous setpoint. For free text, `TextBox`.

**Key properties.** Read/write linked value to the setpoint tag; Min/Max; step/increment.

**Counter-example.** A read-only number is a `DigitalGauge` / `Label` (R3). The diagnostic is writability: input
border + spinners = setpoint; styled static number = readout.

### R6: Command button

**SVG signature.** A rounded/square rect with a command label (Start, Stop, Open, Close, Reset, Ack), often
action-colored (green start, red stop). Lives in a control cluster, not inside a data row.

**FX target.** `Button` (`Interaction`) for a click command; `PushButton` (`Interaction`) for a momentary / jog
command (press-and-hold semantics). The click wires an `ActionDynamic` (`Dynamic`). RunScript / RunExpressions
to write the command tag, or OpenDisplay.

**Key properties.** One `ActionDynamic` carrying the command; theme fill (omit the color to use the theme).

**Counter-example.** A two-position control that shows AND sets state is a `ToggleSwitch` (R7). A colored lamp
that shows state but takes no click is a state indicator (R8).

### R7: Two-state switch / mode select

**SVG signature.** A pill toggle with a puck on one side, a labeled two-position switch, a checkbox, or a row of
mutually-exclusive option dots (Auto / Manual / Off).

**FX target.** `ToggleSwitch` (`Interaction`) for on/off; `CheckBox` (`Interaction`) for a boolean checkbox;
`RadioButton` (`Interaction`) for one-of-N mode select.

**Key properties.** Read/write linked value to a Boolean (or mode) tag.

**Counter-example.** A colored lamp that reflects run/stop but is not clickable is a state indicator (R8), not a
ToggleSwitch. Diagnostic: is it operable, or display-only?

### R8: State indicator lamp

**SVG signature.** A small circle or rectangle that changes fill color by state (green = run, red = fault,
gray = off), with no text or a short caption, and no input affordance.

**FX target.** An `Ellipse` or `Rectangle` (`Shapes`) + a `FillColorDynamic` (`Dynamic`) bound to the state
tag/expression; OR a richer multi-state glyph from `Library/HMI/Indicators` (a Symbol). For a status that flips a
whole equipment glyph, the equipment Symbol (R9) already carries its State dynamic.

**Key properties.** `FillColorDynamic` with the per-state color mapping.

**Counter-example.** A clickable two-state control is a `ToggleSwitch` (R7). A proportionally-filled bar is a
bargraph (R2), not a lamp.

### R9: Equipment symbol / mimic component (pump, valve, tank, motor, conveyor…)

**SVG signature.** A recognizable industrial component drawing, a tank (vessel outline with a level fill), a
pump (circle + impeller triangle), a valve (bowtie of two triangles), a motor, a conveyor belt, a silo, a
blower.

**FX target.** An HMI **Symbol** from the verified library, NOT a hand-built shape group:
- `Library/HMI/<Type>`: e.g. `HMI/Pumps/PumpColor`, `HMI/Valves/Valve`, `HMI/Tanks/VerticalTank_Scale`, plus
  `Motors`, `Conveyors`, `Silos`, `Blowers`, `Compressors`, `Pipes`, `Indicators`, and more.
- `Library/Wizard/{PUMP|VALVE|TANK|MOTOR|BLOWER}`: parameterized wizard symbols that ship **built-in dynamics**
  (State, Rotate, RPM, Level/Max/Min depending on type). Prefer these when the operator needs a live, animated
  component. Resolve the exact variant with `list_wizard_options` / `pick_wizard_variant`.

Verify the exact symbol with `list_elements('Library/HMI/<Type>')` or `list_elements('<keyword>')` (e.g.
`list_elements('pump')`).

**Key properties.** Bind the symbol's labels with `@Tag.<path>`, a tank's `Level`, a pump's `State` / `Rotate`.
The animation is inside the symbol; you bind, you do not rebuild.

**Counter-example.** A tank drawn as a `Rectangle` + a separate fill `Rectangle` is the shape-by-shape
anti-pattern: use the Tank symbol so the level is a real, bound dynamic. Only fall back to primitives + a
`BargraphDynamic` when the component genuinely has no library symbol, and flag that as a deviation.

### R10: Pipe / flow connector

**SVG signature.** Thick straight or right-angled line segments connecting equipment, sometimes colored or
dash-animated to show flow / no-flow.

**FX target.** `Polyline` or `Path` (`Shapes`) for the run; `Library/HMI/Pipes` symbols for junctions/elbows.
Flow state via a `LineColorDynamic` (`Dynamic`) bound to the flow tag; animated flow via `ShineDynamic`.

**Key properties.** `LineColorDynamic` bound to the flow/state tag; stroke width per the mimic style.

**Counter-example.** A thin axis line inside a chart is part of the `TrendChart` (R4), not a pipe.

### R11: Alarm summary list

**SVG signature.** A tabular region with alarm columns (time, area/tag, message, priority, state), rows
color-coded by severity, often with ack / silence controls.

**FX target.** `AlarmViewer` (`Viewer`): the FX live-alarm control, NOT a generic DataGrid. For an
area/group roll-up with active counts, `AlarmAreas` (`Viewer`).

**Key properties.** The alarm source binding; columns and severity row-coloring are built into AlarmViewer.

**Counter-example.** A generic table of process values (not alarms) is a `DataGrid` (R13). The severity coloring
is AlarmViewer's built-in rendering. Do NOT recreate it with per-row `FillColorDynamic`s on a DataGrid.

### R12: Screen tabs / navigation

**SVG signature.** A row of tab labels with one active (highlighted) switching content below; OR a strip of
screen-navigation buttons (Overview, Trends, Alarms, Settings).

**FX target.** `TabControl` (`Viewer`) for in-page tabbed panes; for screen-to-screen navigation, `Button`s each
wiring an `ActionDynamic` with OpenDisplay (commonly hosted in a layout header region).

**Key properties.** A TabItem per pane; or one OpenDisplay ActionDynamic per nav button.

**Counter-example.** The active-tab highlight is TabControl's own state, not a sibling `Rectangle` overlaid on
the active tab.

### R13: Process data table / list

**SVG signature.** A header band + repeating value rows enclosed in one outer rect, usually one row selectable.

**FX target.** `DataGrid` (`Interaction`) bound to a Dataset/query for a multi-column table; `ListBox`
(`Interaction`) for a simple selectable list.

**Key properties.** Items-source link; selected-values link for a list→detail pattern.

**Counter-example.** An ALARM list is `AlarmViewer` (R11), not a DataGrid. Diagnostic: are the rows alarms
(severity, ack) or plain process values?

### R14: Static label / value caption

**SVG signature.** A `<text>` run with no border, no click, no input, a tag caption, a unit, a section title,
or a "Showing N of M" status string.

**FX target.** `Label` (`Interaction`) for a single run; `TextBlock` (`Interaction`) for multi-run / mixed
formatting. A bound caption → a linked value.

**Counter-example.** An editable number is `NumericTextBox` (R5); a styled instrument number is `DigitalGauge`
(R3). A column header inside a recognized `DataGrid`/`AlarmViewer` is the container's own header, not a separate
Label.

### R15: Faceplate / grouped panel

**SVG signature.** A bordered or tinted rect grouping the controls for one piece of equipment (a "Pump 1" box
with its run lamp, speed gauge, start/stop buttons, setpoint), or a collapsible side panel.

**FX target.** A `Group` / `ShapeGroup` (`Container`) for a static grouping; a `ChildDisplay` (`Viewer`) hosting
a reusable faceplate Display when the same equipment box repeats; an `Expander` (`Viewer`) when the panel
collapses/expands.

**Key properties.** For a reusable faceplate, a `ChildDisplay` pointed at the faceplate Display with the
equipment tag passed as its context.

**Counter-example.** A single bordered control is just that control with a border, not a container. A faceplate
is a *grouping of several* controls for one asset.

## Multi-element composition rules

A single SVG region can match several individual rules and still resolve to one composite FX construct:

1. **The mimic heuristic.** A region of connected equipment shapes (tanks + pumps + valves + pipes) → recognize
   each component as its `Library/HMI/*` (or `Library/Wizard/*`) Symbol plus `Polyline`/`Pipes` connectors, NOT
   as the underlying `Rectangle` / `Ellipse` / `Path` primitives. The whole P&ID region is symbols + pipes.

2. **The table heuristic.** A header band + repeating row constructs inside one outer rect → recognize the WHOLE
   region as a `DataGrid` (R13), or `AlarmViewer` (R11) if the rows are alarms, not the per-row Label / lamp /
   text rules. Per-cell rules apply only OUTSIDE a recognized table container.

3. **The faceplate / Symbol-wrap heuristic.** If the same multi-element cluster repeats ≥3 times (a pump + speed
   gauge + run lamp + start/stop, one per pump) → emit ONE recognition entry naming the composite as a candidate
   `Symbol` or `ChildDisplay` faceplate, NOT N entries for the primitives. The authoring step builds one
   faceplate and instantiates it N times with per-instance tag bindings.

When a region matches both an individual rule and a composition heuristic, the composition wins.

## Workflow: when applied to a real mockup

1. **Read the SVG end-to-end.** Note canvas dimensions and the visual tokens (background, panel, equipment line
   color, alarm-severity colors, muted text), these map to the theme per the Context Package's theme guidance,
   not to literal hex.
2. **Identify the major regions, top-down.** Header / nav band; the mimic or P&ID area; the trend area; the
   alarm / summary area; faceplates and control clusters; footer/status.
3. **For each region, apply the rules above.** Match the SVG signature → emit a recognition entry. Apply the
   composition heuristics where they win (mimic, table, faceplate).
4. **Surface every "flag to the user" / "confirm" entry as a blocker** in the recognition output, NOT as a
   silently-resolved choice.
5. **Output the recognition map** as a list of entries in the shape under "How to use the rules below". Hand off
   to the authoring step (`display-authoring-loop`). This skill stops there.

## Anti-patterns

- **Translating shape-by-shape.** Reading every `<rect>`, `<circle>`, and `<path>` in source order and emitting
  one FX shape per SVG element produces a dead Display of hand-positioned primitives. A tank that is a rectangle
  with a fill, a gauge that is an ellipse with a line. Pixel-correct, conceptually wrong, and not live.
- **Hand-building what the library already ships.** A pump, valve, tank, or motor is a `Library/HMI/*` or
  `Library/Wizard/*` Symbol with built-in dynamics. Never reconstruct it from primitives when the symbol
  exists.
- **Silently inventing controls.** If a mockup pattern has no verified FX equivalent, emit `NO-FX-EQUIVALENT,
  flag to the user`, not "the closest analog".
- **Skipping the counter-examples.** Each rule's counter-example is the failure mode that separates it from its
  visual neighbor (a readout vs a setpoint, a lamp vs a toggle, a DataGrid vs an AlarmViewer). Skip it and you
  pick the wrong control.
- **Hard-coding hex colors.** The SVG uses literal hex; the FX Display uses theme tokens. Recognition output
  names the intent ("alarm-critical", "equipment-running", "panel-bg"), not the hex.
- **Recognizing without grounding the FX inventory.** `list_elements()` IS the authoritative control set for the
  installed build. Recognizing against memory of past releases produces references to controls that were renamed
  or never existed (and watch the aliases, `SemiCircle`→`SemiCircleGauge`, `XYChart`→`TrendChart`).

## Composition with other skills

- **`display-authoring-loop`**: the downstream authoring + self-review layer. After this skill produces the
  recognition map, `display-authoring-loop` drives the two-iteration loop: initial write, correctness pass,
  composition pass. Call `svg-to-fx-display` for recognition; hand the map to `display-authoring-loop` for
  authoring. (That skill calls this one as its recognition gate: they are a pair.)
- **`ground-first`**: call before this skill. The platform Context Package and the project's `KnowledgeBase/`
  conventions (UNS naming, alarm style) are what make the recognition entries usable and consistent downstream.
- **`premise-check`**: when a mockup region asks for something with no native FX equivalent (an animated
  transition, a control with no library symbol), the right answer is to re-question the design intent against
  what the platform does, not to invent a workaround.

## Sources and rationale

Recognition is grounded in the live FX control inventory from `list_elements()` on the installed build
(verified at 10.1.5): the `Gauges`, `Charts`, `Viewer`, `Interaction`, `Dynamic`, `Shapes`, and `Container`
categories, plus the `Library/HMI/*` and `Library/Wizard/*` symbol libraries. The skill is recognition-only by
design: authoring lives downstream (`display-authoring-loop` drives the write on the project's solution).
Splitting them keeps each rule learnable: one SVG signature, one FX control, one counter-example.
