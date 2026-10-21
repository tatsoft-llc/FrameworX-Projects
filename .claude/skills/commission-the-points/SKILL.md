---
name: commission-the-points
description: >-
  Run a commissioning pass over a project's IO points: drive each point, read it back live with value +
  quality + timestamp, and record the evidence row-by-row in the project's
  Documentation/Commissioning-Record.md. Mechanizes the workspace flow's "Commission" step the way run-tests
  mechanizes testing. Reads Specifications/IO-Register.md for the point list; per point (batched by area)
  drives via set_object_value (or the device write path when field hardware is live), reads back through the
  runtime surface, compares requested vs current, and appends a PASS/FAIL evidence row. Failures get a defect
  line, never a silent skip. An automated PASS is evidence, not acceptance: the record's sign-off line
  requires a named human. Use when the user says "commission the points", "run commissioning", "commissioning
  pass", "drive and read back the IO", "fill the commissioning record", "sign off the points".
license: Apache-2.0
metadata:
  author: Marc Taccolini
  version: "1.1.0"
---

# Commission the Points: evidence-first IO commissioning

## What this is for

Commissioning is the workspace's declared core deliverable: every point driven, read back with quality and
timestamp, and recorded. This skill mechanizes that pass: it turns the IO register into a row-by-row
evidence record a customer can audit, the same way `run-tests` turns the spec's acceptance checks into a
test record.

The output is **evidence, not acceptance**. The skill produces the rows; a named human signs the record.

## Inputs

- `Sites/<Name>/Specifications/IO-Register.md`: the point list (point → UNS tag mapping). This is the
  contract being commissioned. If it doesn't exist, stop and say so. Commissioning without a register is
  just poking tags.
- A **running runtime** bound to the project's real solution (commissioning targets the real solution: this
  is the deliverable, not a sandbox test; the Sandbox Rule applies to automated *tests*, not to the
  commissioning pass the project exists to produce).
- `Sites/<Name>/Documentation/Commissioning-Record.md`: the record this skill appends to. Created by
  `new-project-bootstrap` from the template; **append rows, never overwrite or regenerate the file.**

## Hard rules (baked in, not optional)

1. **An automated PASS is evidence, not acceptance.** The record's sign-off line requires a **named human**.
   Never fill the sign-off; never imply the record is "accepted" because all rows passed. Close every run by
   reminding the user the record is unsigned until a human signs it.
2. **Quality must be Good (192), not merely present.** A value that arrives with Uncertain (64) or Bad (0)
   quality is a FAIL row even when the number looks right. Record the actual quality code.
3. **Read back through the runtime surface, not the write surface.** The write call's own echo is the first
   check, not the proof: the readback that lands in the record comes from `runtime_get_value` (value +
   quality + timestamp), so the evidence shows the runtime *serving* the value, not just accepting it.
4. **Failures get a defect line, never a silent skip.** A point that can't be driven, doesn't read back, or
   reads back wrong gets a FAIL (or BLOCKED) row with a one-line defect note. Skipping a point silently
   falsifies the record.
5. **Verify each path.** A working sibling point is not evidence for the next one. Identical config with a
   different address is a real divergence. Every register row gets its own drive + readback. No "by analogy"
   rows, ever.
6. **A PASS row is history, not current state.** A row is evidence about the moment its point was driven.
   After any change that touches a point's path (channel config, tag rename, UDT edit, address change),
   re-drive the affected points and append new rows; never cite an old row as today's state.

## The pass, per point (batched by area)

Work the register in area batches (`Area/Unit/Signal` order) so a long pass stays legible and resumable.

1. **Drive.** `set_object_value` on the point's UNS tag with a test value chosen from the register (a value
   inside the engineering range that differs from the current one). When live field hardware is wired,
   prefer driving through the device write path so the loop includes the field side; when simulation drives
   the tags, the tag write is the loop.
2. **First check.** Compare the call's echoed `requestedValue` vs `currentValue`. A silent rejection
   (read-only, runtime-managed, type-coercion) hides under a success envelope.
3. **Read back.** `runtime_get_value` on the same tag: value + quality + timestamp. PASS requires: value
   matches the driven value (within the register's stated tolerance, if any), quality **Good (192)**, and a
   fresh timestamp. If only the Designer MCP is available, read value, quality and timestamp with
   `browse_object_model('Tag.<path>')`; never take the timestamp from the `set_object_value` echo.
4. **Record.** Append one row to `Documentation/Commissioning-Record.md`:
   `point · expected (driven) · observed (read back) · quality · timestamp · PASS/FAIL · notes`.
   FAIL/BLOCKED rows carry the defect line (what was attempted, what came back).
5. **Restore.** Return the point to its pre-test value when the test value would mislead an operator or
   trip an alarm that shouldn't stay latched. Note the restore in the row when it matters.

**Cold-boot rule:** the first read after a runtime start may time out at the ~10 s budget. Retry once
before recording a failure; only a second consecutive timeout is evidence of a wedged runtime
(`KnowledgeBase/Method/Runtime-Operations.md`).

## Closing the run

End every run with:

- **The count:** commissioned (PASS) / failed / blocked, against the register's total.
- **The defect list:** one line per FAIL/BLOCKED row.
- **The unsigned-record reminder:** "The commissioning record is evidence only. It needs a named human
  sign-off before this counts as accepted."
- A `## MCP findings` block if a needed value wasn't exposed (a missing quality flag, a timestamp you had to
  infer): per `KnowledgeBase/Method/Solution-Build-Method.md` §8.

Log the run in the project's `ChangeLogs/ChangeLog-<user>.md` (date, areas covered, counts).

## What this skill does NOT do

- **Does not sign.** The sign-off line is human-only.
- **Does not invent points.** The register is the scope. A tag that exists in the solution but not in the
  register is a register gap to surface, not a row to add unilaterally.
- **Does not overwrite the record.** Append-only. The record's history is part of the evidence.
- **Does not replace run-tests.** `run-tests` proves the built solution matches the spec's structure and
  live invariants; this skill proves each IO point round-trips. They compose; neither substitutes.

## Composition

- **Pace a long register**: work one area per turn so the user can follow and interleave field actions
  (forcing a contact, opening a valve) where hardware needs a hand.
- **`run-tests`**: run the test gates before commissioning; a solution that fails its structural gate is
  not ready to commission.
- **`KnowledgeBase/Method/Runtime-Operations.md`**: ports, profiles, cold-boot retry, and the runtime
  diagnostics family when a point won't read back.
- **`KnowledgeBase/Patterns/Validation-and-Readback.md`**: the full readback-trap catalog (quality codes,
  success-wrapped errors, driver-health signals during channel commissioning).
