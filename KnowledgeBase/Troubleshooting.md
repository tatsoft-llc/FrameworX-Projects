# Troubleshooting: symptom → the right doc, fast

The operating knowledge in this workspace is deep but spread across ~20 files. This is the index: find
your symptom, jump to the file that carries the answer. (Deeper background on any entry:
`Patterns/MCP-Reliability-Practices.md` consolidates the cross-cutting behaviors and how to check each one on
your build.)

## Tool calls that don't complete

| Symptom | Go to |
|---|---|
| Every FrameworX tool call fails / server not available | `verify-mcp-setup` skill → `Method/mcp-setup.md` |
| `open_solution` returns `READ_ONLY_MODE` / "already open elsewhere"; bridge port "address already in use" | `kill-zombies` skill ([companion repo](https://github.com/tatsoft-llc/Claude-Code-Skills)) |
| `DESIGNER_BUSY` / `DESIGNER_CLOSED` / pipe errors mid-session | retry / re-`open_solution`, `Method/Runtime-Operations.md`; size write batches down (`Conventions/Working-Rules.md` write sizing) |
| A driven flow reported success but its dialog-dependent effect didn't happen | refused-modals contract, `Patterns/MCP-Display-Authoring-Recipes.md` |

## Confirm what a write landed

| Symptom | Go to |
|---|---|
| `write_objects` returned success but the object/value isn't there | `Patterns/Validation-and-Readback.md` (read back to confirm; merge vs full-replace) |
| `set_object_value` returned success but the value didn't change | `Patterns/Validation-and-Readback.md` (readback-mandatory rule) |
| Write returns "skipped existing" / "Only Description can be updated" | the object lacks the MCP `Category`: `Patterns/Validation-and-Readback.md`; don't retry, toggle the object's Category in the Designer, then re-run the write |
| A field you wrote reads back empty (query body, display Description, report contents) | `Patterns/MCP-Reliability-Practices.md` + `Patterns/MCP-Schema-Field-Gotchas.md` |
| Write confirmed, but the combo/tree/picker doesn't show the new object | `Patterns/Registration-Chain.md` |

## Runtime and live values

| Symptom | Go to |
|---|---|
| First read after runtime start times out (~10 s) | allow for a slow first read, retry once before treating it as a fault: `Patterns/Validation-and-Readback.md` (cold-boot) |
| Tag reads bad quality / value frozen | `first-device-channel` skill § triage → `References/Protocol-Vendor-Notes.md` |
| Simulated point frozen or ~0 | `Method/Verification-Channels-and-Simulators.md` (integer bounds, FLOAT floor, dead OnChange) |
| Designer says runtime "disconnected" after hot_reload | verify via Runtime tools first, `Method/Runtime-Operations.md` |
| Dataset query returns 0 rows | `.Select` toggle + lazy DB open, `Patterns/MCP-Reliability-Practices.md`; credentials rejected with `28P01` → check the connection's stored `LogonPassword` |
| Runtime screenshot blank where a web control sits | WebView2 content is not in a WPF capture, `Patterns/MCP-Reliability-Practices.md`; verify in the HTML5 web client (`Patterns/Test-Web-Displays-in-Chrome.md`) |

## Displays and scripts

| Symptom | Go to |
|---|---|
| Display writes pass but the screen looks wrong / element missing | `display-authoring-loop` skill (correctness pass) + `Conventions/Display-Authoring.md` |
| Display bindings only fail at build, never at write | build gate: `Patterns/Validation-and-Readback.md` |
| Binding shows literal text compiled as code (or vice versa) | `Patterns/Display-Value-Binding-Literals.md` |
| Script CS0246 / CS0234 calling another class | `Conventions/Script-Class-Invocation.md` |
| Script error on a tag path containing `/` | `Patterns/Script-Tag-Path-Escapes.md` |
| Static caption on a TextBlock shows its quote marks (10.1.6) | use the `Text` property: `Patterns/Display-Value-Binding-Literals.md` |
| `CS7036` calling a Script Class method from Display code-behind | optional params aren't honored across the wrapper: `Patterns/Script-Runtime-Gotchas.md` #2 |
| `CS1061` "'TDataTable' does not contain a definition for 'Rows'" | a DataTable tag is a wrapper; use `.Value` / `GetRowsCount()`: `Patterns/Script-Runtime-Gotchas.md` #11 |
| Method definition rejected in a Script Task; or `await` questions | wrong environment: `Conventions/Script-Environments.md` |
| Display freezes while a script runs | blocking the single UI thread: `Patterns/Script-Runtime-Gotchas.md` #5 |
| Dataset tag holds garbage after a query; DDL/INSERT silently did nothing | un-`await`ed `SelectCommandAsync` / discarded rows-affected: `Patterns/Script-Runtime-Gotchas.md` #8 |
| Number breaks a SQL statement or device command on a non-English machine | locale decimal comma; use `InvariantCulture`: `Patterns/Script-Runtime-Gotchas.md` #3 |
| Deleting a grid row deletes the wrong DB record | row index is not DB identity: `Patterns/Script-Runtime-Gotchas.md` #9 |
| Shared socket/device handle resets or interleaves reads | needs a `static` lock: `Patterns/Script-Runtime-Gotchas.md` #1 |
| Two Script Tasks double-run the same initialisation | one shared class instance, no method lock: `Conventions/Script-Class-Invocation.md` (re-entrancy) |
| A Display's dynamics need proof at runtime, without an operator | `Method/Runtime-Display-Verification.md` |

## Still stuck?

Reproduce it minimally in an `ai-test-` sandbox (never the customer solution), then treat it as a
finding: check `Patterns/MCP-Reliability-Practices.md` first; if it isn't there, add it, log it in your
ChangeLog, and raise it with Tatsoft support (see `CLAUDE.md`).
