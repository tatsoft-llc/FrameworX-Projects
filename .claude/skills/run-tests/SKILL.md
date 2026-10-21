---
name: run-tests
description: >-
  Run the FrameworX solution test harness: validate that a built solution matches its spec by asserting its
  structure and live runtime behavior. Use when the user says "run the tests", "test the solution", "validate
  the build", "check it against the spec", or after a build or review is done. Builds the solution if needed,
  starts the runtime on the Development profile, collects the real UserTypes, UNS and asset tree, alarms,
  historian, and live values over the Designer/Console and Runtime MCP into Sites/<Name>/Tests/results/, then
  runs the Python checker against Sites/<Name>/Tests/expected.json and reports pass or fail. Pairs with
  review-the-ai-build (judgment) as the mechanical gate.
license: Apache-2.0
metadata:
  author: Marc Taccolini
  version: "1.1.0"
---

# Run the tests

The test harness proves a built solution does what the spec asked. It collects the real structure
and live values from the running product over MCP, and checks them against expected values derived
from the spec. Green is evidence. Red names exactly what is wrong.

There are two gates, run in order. The structural gate is fully deterministic. The live gate
asserts invariants with tolerance, because a simulated process value moves.

## Prerequisites

- **Python 3.x on PATH** (`python --version`). The checker (`check.py`) is a Python script; without
  Python on PATH the gates cannot run.

## Inputs

- `Sites/<Name>/Specifications/`: the source of truth.
- `Sites/<Name>/Tests/expected.json`: the machine-readable expectations derived from the spec's acceptance criteria.
  If it does not exist for this solution, create it from the spec's acceptance checks first (see
  `.claude/skills/run-tests/tests-README.md`, including the worked derivation from the Brewery spec).
- The `ai-test-` sandbox solution to test.

## Steps

### 1. Bootstrap and prepare the sandbox

- Bootstrap the MCP (`open_solution` on the `ai-test-` sandbox). Re-bootstrap on a solution switch.
- Confirm the sandbox is on the Development profile with splashes off and only the needed modules
  enabled (for the brewery example: Scripts, Datasets, Alarms, Historian, Displays).

### 2. Build and start the runtime

- Build the solution (`designer_action` build). If the build fails, stop and report the build error;
  there is nothing to test yet.
- Start the runtime on the Development profile. Give it a moment to bring modules up.

### 3. Collect structure and live values over MCP

- Follow `.claude/skills/run-tests/collect-live.md`: use the Designer/Console and Runtime MCP tools to gather the actual
  structure (counts and domain UserTypes) and the live values, and write them to
  `Sites/<Name>/Tests/results/actual.json` in the shape `Sites/<Name>/Tests/expected.json` expects. The `.dbsln`
  is encrypted, so structure is read through the product over MCP, not by parsing the file (see
  `KnowledgeBase/References/dbsln-format-note.md`).
- For the live-value invariant, read the target tag twice a few seconds apart so the checker can
  confirm the value moved.

### 4. Structural gate (deterministic)

- Run `python .claude/skills/run-tests/check.py Sites/<Name>/Tests/expected.json Sites/<Name>/Tests/results/actual.json --structure-only`.
  This asserts the counts (domain UserTypes, UNS tags, alarms and groups and areas, historian tags and
  tables, displays, users) from the collected numbers. These are stable across re-takes of the same
  built solution.
- Capture its output to `Sites/<Name>/Tests/results/structural-<runlabel>.txt`.

### 5. Live gate (tolerant)

- Run `python .claude/skills/run-tests/check.py Sites/<Name>/Tests/expected.json Sites/<Name>/Tests/results/actual.json` (full gate).
  This re-asserts the structure and adds the live invariants (present, good quality, recent timestamp,
  in range, moved).
- Capture its output to `Sites/<Name>/Tests/results/live-<runlabel>.txt`.

### 6. Report

- State pass or fail for each gate. On fail, name the exact assertion that failed and the layer it
  points back to (a foundation count mismatch points at Layer 1; a dead live value points at Layer 2).
- Note determinism: the structural gate result, and whether the live gate's tolerant invariants held.
- Do not declare success without the checker's exit code. An AI "looks right" is not the test record.
- **Displays are not covered by the checker.** To test a Display's dynamics in the running client (repoint
  Startup Content, build, restart, drive with `set_object_value`, screenshot, list what needs a human),
  follow `KnowledgeBase/Method/Runtime-Display-Verification.md` and record the result under
  `Sites/<Name>/Tests/`.

## Determinism note for the validation run

When validating the harness itself, run the gates once as the golden run, then re-run them as a
re-take and compare. Expect the structural gate to be bit-identical across re-takes (same file, same
counts). Expect the live gate to pass both times but with different tag values (the simulation moved
between runs); that difference is the point of the tolerant invariant, not a failure. Record both in
`Sites/<Name>/Tests/results/` and summarize the determinism story in the run report.

## MCP findings

If a needed value was not exposed over MCP (a quality flag, a timestamp, a count you had to infer),
record it in an `## MCP findings` block per `KnowledgeBase/Method/Solution-Build-Method.md` §8. The test harness is also a probe
of the tool surface.
