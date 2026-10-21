# Pattern: Canvas mechanics for a measured drawing replica

The *method* for reproducing a supplied drawing (grid, coordinate table, one transform, generate) lives in
`../Conventions/Display-Authoring.md` § "The fidelity contract". This file is the layer below it: the Canvas
element mechanics you hit once you actually generate a few hundred primitives, and the transport that gets
them into the solution.

*(Observed on FrameworX 10.1.5 while authoring a 290-element P&ID replica. **Design-time only**: the runtime
was never started in that session, so nothing here attests Dynamics behaviour at runtime. Confirm against your
build.)*

## Text over a drawing: Label paints an opaque themed background

A `Label` (and `TextBlock`) placed over drawn geometry renders a **filled themed rectangle** behind its text.
Set `Foreground` alone and you get navy-on-navy: the text is invisible and, worse, the box *occludes the
graphics underneath*: bubbles, pipe runs and vessel outlines disappear under their own captions.

```json
{ "Type": "Label", "LinkedValue": "\"R-999\"",
  "Foreground": "#FF112D63",
  "Background": "#00000000",      // required over a drawing
  "BorderThickness": "0",
  "HorizontalContentAlignment": "Center", "VerticalContentAlignment": "Center" }
```

Corollary for the box itself: size the Label box generously and centre with `HorizontalContentAlignment`,
rather than guessing a tight box. Once the background is transparent an oversized box costs nothing and
survives font-metric differences between your generator and the renderer. Do keep boxes inside the drawing
border, though; a box that overhangs the canvas still extends its bounds.

## Quote every literal you generate, including short all-caps words

A generator emitting `LinkedValue: "TAG"` for a legend column header rendered the literal **`{Tag}`**, the
unresolved-tag placeholder, because a bare, unquoted, non-numeric literal goes down the expression path (see
`Display-Value-Binding-Literals.md`). The fix is to **quote it**, not to swap the element type. Generators are
where this bites at scale: hand-authoring produces a handful of literals, a generator produces hundreds, and
only the ones that happen to look like a token show a visible symptom while the rest sit as latent
expression-path text.

**Rule for generated Displays: emit `"\"" + text + "\""` for every static string in a value binding,
unconditionally.** On FrameworX 10.1.6, a static caption on a `TextBlock` goes in its `Text` property instead:
a quoted literal in `TextBlock.LinkedValue` renders with its quote marks (`Display-Value-Binding-Literals.md`).

## Primitive recipes (when the symbol library has no equivalent)

`../Conventions/Display-Authoring.md` says build equipment from library symbols, not primitives. That still
stands and is the first thing to try. A drawing replica is the standing exception: matching a specific
scanned outline means primitives. What worked:

| Need | Recipe |
|---|---|
| Vertical vessel with elliptical heads | **one** `Rectangle` with `RadiusX`/`RadiusY` about equal to the head height. Beats Rectangle + two Ellipse caps, which leaves visible cap seams inside the shell and needs three fills kept in sync. |
| Bowtie (gate / hand valve) | a **single self-intersecting `Polygon`**, points `0,0  0,h  w,0  w,h`. The default fill rule renders the bowtie; no second shape needed. |
| Predictable `Polygon` / `Polyline` geometry | normalise points to the shape's own bounding box and set `Left`/`Top` to the bbox origin with `Stretch: "Fill"`; the mapping is then identity and your table coordinates land verbatim. |
| Pipe runs | `Gridline` with `Stretch: "None"`, points local to `Left`/`Top`. Clamp `Width`/`Height` with `max(1, ...)`: a perfectly horizontal run has zero height. |
| Hatched region (catalyst bed, insulation) | there is **no clip property**. Clip the hatch segments to the region in the generator (Liang-Barsky) before emitting; an unclipped hatch draws a giant X across the whole drawing. |
| Drawing "paper" colour | set `Background` on the **DisplaysList row**. Do not add a background Rectangle; see the theme note in `list_elements('Canvas')`. |

## Transport: a large Display goes in as a workspace JSON file, not inline

A few hundred elements is about 100 KB of JSON. Pushing that through a `write_objects` argument is slow and
error-prone. Import it from a folder instead:

1. `get_solution_export_files(solution_path=...)` on any solution, to discover the exact file shape: one file
   per object, named `<TableType>-<ObjectName>_<timestamp>.json`.
2. Generate the same shape into a folder:
   ```json
   { "ObjectIdentification": { "TableType": "DisplaysList", "SolutionName": "<solution>" },
     "ExportMetadata": { "ExportFormat": "1.1" },
     "Data": [ { "Name": "MainPage", "PanelType": "Canvas", "Elements": [ ... ] } ] }
   ```
   (the timestamp in the filename is not required on the way in)
3. `open_solution(name=..., from_workspace="<folder>")`. The response carries a `workspaceImport` block with
   per-file `created / modified / skipped / errors`.

Caveats worth knowing before you rely on it: the import is **upsert / always-replace with no transaction**,
so a partial failure leaves a mixed state; `open_solution` writes a timestamped `.backup` of the `.dbsln`
first, and that backup is your only rollback. Displays are document objects: an imported row **replaces**
the canvas, so the file must carry the complete Elements array.

## What a clean import still does not tell you

The `workspaceImport` result reporting `modified: 1, errors: 0` attests that the row and its XAML landed.
It does not attest that the **bindings compile** (that surfaces only at a full build), and a design-time
`get_screenshot` shows unresolved bindings as placeholder text, not as errors. Sequence a drawing replica as:
import, then `get_screenshot` (catches occlusion, overlap, clipping, wrong geometry), then **build** (catches
binding compile errors), then runtime (catches Dynamics behaviour). Skipping the build is how quoting bugs
like the one above reach the operator.
