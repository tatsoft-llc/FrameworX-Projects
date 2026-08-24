# Pattern: MCP reliability practices (what to verify, and why)

The consolidated list of things to confirm when you author through the FrameworX MCP surface: which calls need
a read-back before you trust the result, and which results need a second look before you act on them. One
short entry per practice, symptom, what to do. The deeper write-ups live in the linked Patterns /
Conventions / Method files; this page is the index you scan when a result surprises you.

**Discipline for every entry: verify the behavior on your own build first.** Tool behavior moves between
builds, so when yours behaves differently, update the entry. When something costs you time twice, add it here
(one entry, 2-4 lines) and put the full write-up in the right deep file.

## Confirm what a write landed

- **Read back after EVERY `set_object_value`.** A `success: true` envelope attests the call, not the stored
  value: read-only, runtime-managed, type-coercion and headless cases can leave the value unchanged. Read back
  and compare with type-coercion tolerance; mismatch = hard FAIL. Full rule: `Validation-and-Readback.md`.
- **Write DatasetsQueries one row at a time, then read `SqlStatement` back.** A batch create can place a body
  on the wrong row, and a create issued while that query's editor is open can leave the stored body different
  from what you sent, under an envelope that reports "Modified". Single-row creates + `SqlStatement` read-back
  are mandatory. Full rule: `MCP-Schema-Field-Gotchas.md`. 10.1.5 servers detect the open-editor case and
  restore `SqlStatement` from the imported payload, and say so in the write result: keep the read-back, and
  treat that notice as the tell that the case fired.
- **Close a display's editor before writing that display, and count elements on read-back.** With the editor
  open on it, a write can add the new elements alongside the old set (duplicate Uids) instead of replacing
  them, while reporting Modified with a clean per-display compile. Element-count read-back after EVERY display
  write; to repair, navigate off the editor (`designer_action('navigate','Tags')`) then re-write.
- **Keep one statement per query row.** A query body with a statement prefix (e.g. a DO-block before the
  SELECT) binds its consumers to the first resultset, not the final SELECT. Put setup statements somewhere
  other than the query row.
- **Set a Display row's `Description` in the Designer UI.** A Canvas update does not carry it: the write
  reports success and the stored Description is unchanged, and neither `write_objects` nor a workspace import
  sets it. Confirm the field with a read-back. Full rule: `../Conventions/Display-Authoring.md`.
- **Treat a `Category`-gated skip as a permission wall.** A write skipped with *"Only Description can be
  updated"* / *"Skipping existing"* means the object lacks the MCP category: that is a **permission state, not
  a transient error**. Do not retry; surface it for a one-time category toggle in the Designer. Full rule:
  `Validation-and-Readback.md`.
- **On a `DatasetsDBs` auth failure, check `LogonPassword` before the connection string.** The stored
  encrypted `LogonPassword` cell takes precedence over an inline `Password=`, so a stale cell fails auth (e.g.
  Postgres `28P01`) with an otherwise correct connection string. That cell is not writable over MCP: set it in
  the Designer UI, or author a fresh connection row.

## Confirm what a read is telling you

- **Allow for a slow first read after a runtime start.** The first browse / `get_value` can spend the whole
  ~10 s read budget while JIT and caches warm. Retry ONCE (the second call lands in milliseconds) before
  treating a timeout as a fault; a second consecutive timeout is a real wedge. Never widen the timeout. The
  budget is deliberate. Full rule: `../Method/Verification-Channels-and-Simulators.md`.
- **Don't pull `get_ui_tree` into context on a big display** (~1.6 million chars, past the token cap). Save it
  to a file and parse the slice you need. Most lock/layout work needs no tree at all. Full rule:
  `../Conventions/Display-Authoring.md`.
- **Read `DisplaysList` full detail one display at a time.** A multi-name full-detail `get_objects` comes back
  as empty objects (`[{},{}]`), which says nothing about the displays. Use a single `detail='summary'` listing
  for sweeps.
- **Confirm an outage through the Runtime tools, not the Designer.** After a device or historian hot reload,
  the Designer's `get_state` can show its runtime link down while the TServer keeps serving. Check
  `runtime_get_value` before declaring an outage. Full rule: `../Method/Runtime-Operations.md`.
- **Verify web-view-hosted controls in the browser, not in a WPF screenshot.** A control that renders through
  an embedded WebView2 shows **blank** in a WPF runtime capture whether or not it works, so a blank region
  there is not evidence either way. Verify via the HTML5 Web Client in a browser (see
  `Test-Web-Displays-in-Chrome.md`).

## Match the call to the surface's contract

- **ReportsForms has no `Contents` field over MCP**: the config API carries the row, not the report body; a
  body-carrying write is rejected. Author the body in the Designer's report editor. Full rule:
  `MCP-Schema-Field-Gotchas.md`.
- **Re-running a dataset query needs a `.Select` 0→1 toggle.** Writing a value equal to the stored one is a
  no-op, so an equal-write never re-triggers the query, toggle 0 then 1. And the DB connection opens lazily,
  so the FIRST trigger can return 0 rows: trigger again before concluding the table is empty.
- **IndustrialIcon glyph is set via the `Icon` property** with a catalog name (from
  `list_elements('IndustrialIcon')`). Writing `Text` / `LinkedValue` leaves the default gear glyph.
- **Digital / UDT boolean-ish members are `int` 0/1, not `bool`.** In a C# script, assign via ternary
  (`condition ? 1 : 0`); assigning `true` / `false` does not give you the value you meant.
- **Normalize `ObjectIdentification.SolutionName` before sharing a headless export.** The FrameworX AI Console
  `get_solution_export_files` export writes that field as the full path the solution was created at (e.g.
  `C:/Dev/.../HighlandWTP`), read from inside the `.dbsln` rather than from where the file sits now. It costs
  nothing locally; when an export is shared or published, set the field to the bare solution name first.
- **Strip `Children` from a ChatSession element on write-back.** A full `get_objects` emits the control's
  internal bubble template as a `Children` subtree of raw WPF types (`StackPanel`, `RowDefinition`), which
  `write_objects` rejects with `INVALID_ELEMENT_TYPE`. Write the element without that subtree: the control
  regenerates its own template (verified by read-back).

*(Every entry above was observed on a specific build. The live tool descriptions, `get_table_schema`, and a
read-back on your own solution are authoritative, when your build behaves differently, update the entry.)*
