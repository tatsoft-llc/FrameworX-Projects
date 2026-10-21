---
name: review-the-ai-build
description: >-
  Independently review a FrameworX solution that the AI just built, against its spec, before you trust it. Use
  after a build or a build layer completes, when the user says "review the build", "check what you built",
  "did this match the spec", "audit the solution", or before running the tests on a fresh build. Reads the
  real solution over the Designer or Console MCP and the running runtime, compares to
  Sites/<Name>/Specifications/, and reports findings by severity. It reviews; it does not fix. Distinct from
  run-tests (which mechanically asserts expected values): this is the human-judgment pass that catches
  structure, naming, anti-patterns, and reachability problems a fixed assertion list would miss.
license: Apache-2.0
metadata:
  author: Marc Taccolini
  version: "1.0.0"
---

# Review the AI build

The AI built a solution. Before anyone trusts it, look at what was actually built, against what the
spec asked for, with fresh eyes. This is the judgment companion to the mechanical test harness. It
finds the things a fixed assertion list does not: a foundation that drifted from the spec, an
anti-pattern, a screen that binds to nothing, an option that was written but is not reachable.

This skill reviews. It does not fix. It produces a findings list. The user decides what to do with
it.

## Before you start

- Confirm a spec exists at `Sites/<Name>/Specifications/`. The review compares the build to the spec. With no
  spec, say so and review against stated intent instead, flagging that there is no contract.
- Bootstrap the MCP first (`open_solution` / `open_workspace`). Re-bootstrap if you switched
  solutions.
- Review the `ai-test-` sandbox, not a real solution.

## The review, in four passes

### Pass 0: ground

Read `Sites/<Name>/Specifications/` end to end. Note the acceptance checks in `Requirements.md`; they are the spine of
the review. Read `KnowledgeBase/References/frameworx-vocabulary.md` if any term is unclear.

### Pass 1: scope and boundary

Before line-level detail, ask whether the build is the right shape:

- Does the foundation (UserTypes, UNS, asset tree) match the spec's, in count and in name? A
  foundation that drifted is a containment problem, not a detail to patch.
- Is anything built that the spec did not ask for? Scope creep in a solution is as real as in code.
- Is each layer present: foundation, connect, monitor, screens? A missing layer is the headline.

A build that is line-clean but structurally wrong is not approved. Scope first.

### Pass 2: correctness and anti-patterns

Now the detail. Use `get_objects` and `browse_object_model` to read the real objects.

- **Foundation:** UDT members, units, ranges, retentive flags match the spec. Names are PascalCase
  and hierarchical.
- **Connect:** tags have a source (a device point or a simulation). A tag with no source holds no
  value.
- **Alarms:** the right tags are alarmed, grouped, and area-assigned. Watch for alarm fatigue
  (everything alarmed, one threshold repeated everywhere).
- **Historian:** the right tags are logged, not all of them. Watch for historize-everything.
- **Displays:** controls are real (`list_elements`), bindings resolve, screens are built from
  Symbols rather than copy-paste. Take a `get_screenshot` of at least the main display; the render
  is ground truth, and an empty binding shows as a default placeholder, not an error.
- **Orphans:** references to objects that no longer exist. Spot-check bindings with `get_objects` and
  confirm each referenced tag, display, or symbol actually resolves.

### Pass 3: reachability in the runtime

A written row is not a working feature. Start the runtime (Development profile) if it is not up,
and confirm with the Runtime tools:

- Tags named in the spec hold live values with good quality and recent timestamps.
- An alarm goes active when its condition is forced true.
- History accumulates for a logged tag.

## Report

Findings by severity. For each: the exact object (table, name, member), what the spec said, what
the build has, and why it matters. Do not paraphrase; cite the object.

- **MAJOR:** structure or behavior that contradicts the spec or breaks at runtime. Must be fixed
  before the build is trusted.
- **MINOR:** drift, naming, or an anti-pattern that is not yet breaking but will cost later.
- **NOTE:** an observation or a suggestion, no action required.

Findings persist to the project record, not just the transcript: write the list as a dated table in
`Sites/<Name>/Documentation/` (for example `Review-Findings-<date>.md`), one row per finding with
finding / severity / object / status. Later sessions work from that table, not from a transcript, and
write their verdicts back into it, updating each row's status in place: `fixed`, `refuted-on-re-check`,
or `open`. Rows are never deleted; the table is the review-side twin of the commissioning record,
evidence with a status trail rather than a one-time report.

End with one line: approved, or not approved with the count of MAJOR findings. If you reviewed
against intent because there was no spec, say so. Then stop. Fixing is a separate, user-directed
step.

## MCP findings

If the review was blocked or degraded by a tool gap (a value you could not read, a state the MCP
does not expose), record it in an `## MCP findings` block per `KnowledgeBase/Method/Solution-Build-Method.md` §8.
