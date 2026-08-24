# Pattern: authoring Display elements over MCP (Dynamics & Drawing properties)

How to add, remove, and edit a Display element's **Dynamics** (Visibility, Color, Position, Action, …) and
**Drawing** properties (size, position, label, colors) through the MCP and confirm the result, without driving
the Designer's Properties dialog by hand. The reliable path is a **read-modify-write** on the Display document
via `write_objects(DisplaysList, …)`, then a read-back and a runtime check.

> Verify field and Type names against your installed build. `get_table_schema('DisplaysList')` and
> `list_dynamics()` are authoritative. The value here is the *mechanics and the gotchas*, not the enumeration.

## The one rule that prevents lost work: read-modify-write

`write_objects(DisplaysList, …)` **replaces the whole Display document**. Nothing you leave out of the payload
is merged back in: after the write, every field and every element you didn't include is gone. (Displays are
*document objects*. The full-replace regime of the two-regime upsert rule; see `Validation-and-Readback.md`.)
So always:

1. **Read first**: `get_objects(table_type='DisplaysList', detail='full', names=['<Display>'])`. Returns the
   Display's full JSON: every element, every attribute, and each element's current `Dynamics:[...]` array.
2. **Modify** the element in that payload (append/replace a Dynamic; change a Drawing field).
3. **Write back** the element's **full row**: every attribute it had, not just the changed one. Missing fields
   fall back to class defaults, which is almost never what you want.

## Add a Dynamic

After the read, append to the element's `Dynamics:[...]` array and write the full element row back:

```json
{
  "tool": "write_objects",
  "params": {
    "table_type": "DisplaysList",
    "data": [
      { "name": "MainPage",
        "Elements": [
          { "name": "Button1", "Type": "TButton", "X": 100, "Y": 100, "W": 80, "H": 30, "LabelLink": "Start",
            "Dynamics": [
              { "Type": "VisibilityDynamic", "Source": "Tag.Plant1.IsRunning", "TrueValue": true, "FalseValue": false, "Invert": false }
            ] } ] } ],
    "mode": "upsert"
  }
}
```

- The `Dynamics:[...]` array must be **complete**. Every Dynamic the element should have after the write. To
  add, append to the array you read; to replace, substitute.
- **A Dynamic only takes effect inside the `Dynamics:[...]` array.** An inline `ActionDynamic: {...}` on the
  element body does nothing: it must be an entry inside the array.
- Confirm the canonical Type name with `list_dynamics()` (e.g. `VisibilityDynamic`, `ColorDynamic`,
  `PositionDynamic`, `RotationDynamic`, `ActionDynamic`, `BargraphDynamic`, `TooltipDynamic`, `ValueDynamic`).
  A wrong Type name (e.g. `Visibility` instead of `VisibilityDynamic`) is filtered out on write without an
  error, so get the name right up front and check the Dynamic on read-back.

## Remove a Dynamic

Same shape, but write the `Dynamics:[...]` array **without** the entry to remove: there is no "remove one
entry" verb, you rewrite the array. Supply the surviving subset, or `[]` to remove all. If `[]` is rejected on
an element that historically had Dynamics, try `Dynamics: null`. Always read first; never write the array blind.

## Edit a Drawing property

Same read-modify-write with the changed field(s) set (`X`, `Y`, `W`, `H`, `LabelLink`, `FillColor`,
`StrokeColor`, `FontSize`, …). **Don't use `set_object_value` for this**. It writes the runtime value path and
**bypasses the event chain**, so a success return is not evidence that the element's handler ran.
`write_objects` + a cold runtime reload is the path that lands the config and renders it.

## Confirm it: read-back, then runtime

A successful `write_objects` envelope is necessary, not sufficient. Confirm twice:

1. **Document read-back**: `get_objects(detail='full', names=['<Display>'])`; assert the element's
   `Dynamics:[...]` (or the changed Drawing field) is now what you wrote.
2. **Runtime render**: `start_runtime`, then `get_display_tree(element='<Display>')`; drive the Dynamic's
   source (e.g. set the source tag false for a VisibilityDynamic) and confirm the element's rendered state
   flips. For an HTML5 Display, also open the Web Client in Chrome (see `Test-Web-Displays-in-Chrome.md`).
   The runtime must reload the Display since the write, if the change doesn't show, `stop_runtime` +
   `start_runtime` for a cold reload.

## Modals under MCP: the refusal / suppression contract

Driving the Designer headlessly does not pop blocking modals the way a human session does. Current builds ship
a refusal/suppression contract:

- **Dialog-class modals are auto-cancelled.** A UI flow that would open one (a Properties dialog, a wizard, a
  popup editor) does not proceed. The call returns, and nothing changed.
- **Message-box prompts auto-return OK.** A Yes/No confirmation therefore acts as **NOT confirmed**: the
  guarded action does not proceed.
- **Recovery surface:** when a flow "succeeded" but nothing changed, call `get_state` and read
  `refusedModals[]`: it lists the modals refused on your behalf, which is the tell that the flow was
  modal-gated. For the residual dialog class that does open, `designer_action('close_dialog')` dismisses
  the topmost (cancel semantics).

The teaching, in one line: **"the flow appeared to succeed but nothing changed" → `get_state` →
`refusedModals[]`**: then make the change through the data path (`write_objects`) instead of the dialog.
*(This is the shipped contract, not a workaround, permanent.)*

## Failure cheat sheet

| Symptom | Likely cause | Fix |
|---|---|---|
| `write_objects` succeeds but the Dynamic doesn't appear on read-back | Wrong Dynamic `Type` name, filtered out on write | `list_dynamics()` for the canonical name; rewrite |
| Write succeeds but the element lost other fields | Payload omitted fields the element had | Re-read `detail='full'`, restore all fields, rewrite |
| `created:0, updated:0, unchanged:1` | Payload was byte-identical to disk (idempotent no-op) | The change was already present, or the payload wasn't actually changed |
| Inline `ActionDynamic:{...}` does nothing | Dynamic placed outside the `Dynamics:[...]` array | Wrap it as an array entry |
| Runtime doesn't reflect the change | Display not reloaded since the write | `stop_runtime` + `start_runtime` (cold reload) |
| `set_object_value` "passed" but behavior is wrong | It bypasses the event chain, so the handler never ran | Use `write_objects` + cold reload for config; reserve `set_object_value` for runtime-only values |
| A UI flow "succeeded" but nothing changed | A modal was auto-refused (dialog cancelled; message box auto-OK = not-confirmed) | `get_state` → `refusedModals[]`; make the change via `write_objects` |
| A grid-toolbar New/Add button click has no effect | Grid Create/Add buttons are command-routed: a headless `ui_action` click cannot drive them | Create the rows via `write_objects` instead |
| Envelope timeout on a very large Display | Big payloads can exceed the call timeout | Wait for the solution file mtime to stabilize, then re-read `detail='count'` to confirm it landed: the write usually completed |

## Why this beats the dialog

The dialog UI (Drawing Properties / Dynamics Properties) is for a human author. For building and verifying a
Display over MCP, the read-modify-write path lands the same configuration deterministically, with a read-back
you can assert on and a runtime check that proves it renders. No dialog open/close races. Reserve UI-driving
for the rare case where the dialog itself is what you're exercising.
