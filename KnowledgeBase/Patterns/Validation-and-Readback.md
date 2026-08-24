# Pattern: validating a delivered solution (what the MCP can confirm, and what it cannot)

How to prove a solution actually works through the MCP, the capability surface, and the checks that keep a
broken thing from reading as fine. Pairs with each project's `Documentation/Commissioning-Record.md`.

## The validation surface

| Tool | Confirms | Sweet spot / limit |
|---|---|---|
| `set_object_value` | Drives a tag and echoes `requestedValue` + `currentValue` + **quality** + **timestamp** in one call | The core commissioning primitive. **Compare `currentValue` to `requestedValue`**: the `success` envelope attests the call, and a read-only prop, a runtime-managed value, or a type-coercion case can leave the stored value unchanged. |
| `runtime_get_value` | Live value + quality + timestamp | Read-back of a point you didn't just write. Quality: **Good 192 / Uncertain 64 / Bad 0**: a number with Bad/stale quality is not a pass. |
| `runtime_get_active_alarms`, `runtime_query_alarm_history` | An alarm tripped / cleared | Drive a tag past its limit → confirm it goes active → confirm it clears on return. |
| `runtime_get_tag_history` | A point is being logged | Confirms the Historian path end-to-end. |
| `browse_object_model`, `get_objects` | The **shape** exists (a tag, an alarm config, a binding) | Checkable with the runtime down. Shape ≠ behavior: see below. |
| `get_screenshot` + a browser on the WebClient URL | A Display renders **live values** | WPF render is an out-of-process client: treat its live render as a human / screenshot attestation, not a guaranteed MCP read. For the browser / HTML5 path (open the Web Client in Chrome and verify), see `Test-Web-Displays-in-Chrome.md`. |
| Built-in simulators (MQTT, OPC UA, Modbus) | A driver / channel round-trips | Exercise IO against `localhost` before the real PLC is wired: so loop checks run with no bench. |

## Separate "shape verified" from "behavior verified"

- **Shape**, the tag / alarm / binding *exists and is configured*, is checkable before the runtime starts.
- **Behavior**, the value actually moves, the alarm actually trips, the Display actually renders, needs the
  runtime running and the point driven.

Record which one you did. "The alarm config exists" is not "the alarm fired."

## Driver-health signals (commissioning a channel)

A slave-side driver (Modbus slave, OPC UA server, MQTT broker) with no external master shows `SuccessAmount` /
`TotalPoints` at **expected-zero**, that is not a failure. The affirmative "alive" signals are `IsRunning` +
a nonzero process id + a ticking watchdog, populated a few seconds *after* the runtime connects. Give the
subprocess its settle window before judging it dead.

## What to confirm on a write: the envelope is not the proof

- **Confirm the stored value, not the envelope.** `success: true` attests the call, not that the kernel
  accepted the value: read-only, runtime-managed, type-coercion-failure and headless cases can leave it
  unchanged under a success envelope. After EVERY `set_object_value`, re-read and compare against the intended
  value with type-coercion tolerance (string compare for strings, epsilon for numerics, boolean normalization
  for `"true"` / `"True"` / `1`). **Mismatch = hard FAIL**, whatever the envelope said. `set_object_value`
  echoes `currentValue` for exactly this: use it. The caller-side comparison is mandatory.
- **Check the `result` string on every success.** A `success: true` envelope whose `result` string starts
  with `DESIGNER_BUSY` or `Error [` carries a transport condition: **the call did NOT run**. `DESIGNER_BUSY` =
  retry the same call in 2-5 seconds; nothing was written.
- **Read `warnings[]`, and the other action fields, on EVERY write success.** Success envelopes carry
  action items that are unread by default: `warnings[]` (e.g. the authoritative prediction of a normalized
  element `Type` on a Display write), `skipped` / `skippedDetails` (covers BOTH a `mode='create'` over an
  existing row AND the MCP permission gate, a skip is not a write), `unchanged` (the free idempotency
  check, your payload matched what is stored), and `commissioningWarnings` where present. A clean `success`
  with an unread `skipped: 1` is a silent no-op you just called "done."
- **A permission-gated skip is a wall, not a flake.** A write skipped with *"Only Description can be updated"*
  or *"Skipping existing"* against an object that lacks the MCP category is a **permission wall**. The object
  (or its category) has MCP editing disabled in the Designer. Do NOT retry; a retry cannot succeed. Surface it
  to the operator for the one-time category toggle in the Designer, then re-run the write. Pre-filter by the
  object's `Category` field before planning a batch of edits, so the wall costs one read instead of a string
  of dead writes.
- **Cold-runtime first read: a ~10 s timeout is retry-once, not an outage.** The first browse / `get_value`
  after a runtime start can exhaust the read budget while JIT and caches warm. Retry the same call ONCE; the
  second attempt typically lands in under half a second. Only a second consecutive timeout points at a
  runtime that is genuinely stuck. Do not widen the timeout: the budget is a deliberate fail-fast bound, and
  widening it only delays the diagnosis. (Full rule:
  `KnowledgeBase/Method/Verification-Channels-and-Simulators.md`.)
- **Know your upsert regime: merge vs full-replace.** Current builds are two-regime. **Simple config tables**
  (tags, alarm items, device points, …) property-MERGE on upsert: omitted fields keep their stored values.
  **Document objects** (Displays, Layouts, Reports, script bodies, …) FULL-REPLACE. Omitted `Elements` /
  contents are **cleared**, and the `updated` envelope reads the same either way. Build sensitivity: on older
  builds, simple tables full-replaced too: so when in doubt treat ALL upserts as full-replace.
  **Read → merge → write** is always the safe default when editing an existing object.
- **A write counter isn't persistence.** A "fields updated" count can include a field that was not stored:
  confirm by per-field read-back.
- **Assert present-by-name, not row totals.** Built-in objects are hidden from some counts, upgrades add rows,
  and a legacy-shaped solution can report zero UserTypes even when UDTs exist, verify the specific named
  object you care about, not a total. On solutions migrated from older product versions, cross-check a
  zero-UserTypes count with `search_uns(scope='udts')` before concluding none exist.
- **A long write that "timed out" may have succeeded.** A large import can blow the call's time budget while the
  server keeps working. On a timeout, reopen and read the count back (or wait for the solution file to settle)
  *before* retrying, or you double-write.
- **Read back through the surface you wrote with.** A value written via one client can read stale through
  another, verify on the same surface.
- **A missing field on read-back isn't always a bug.** Check the field name against the schema
  (`get_table_schema`) first; it may be named differently or be a managed property.
- **A working sibling is not proof for a divergent one.** Two objects with the same config shape but a different
  input (address, startup arg, empty-vs-set field) are a real divergence. Drive each one live. (See
  `KnowledgeBase/Conventions/Working-Rules.md` → "Verify each path.")
