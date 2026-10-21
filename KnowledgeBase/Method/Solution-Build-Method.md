# FrameworX Solution Workspace: the engineering build method

This workspace is a Claude Code project for building **production-grade industrial
automation solutions** on FrameworX by Tatsoft, using the FrameworX AI Designer,
FrameworX AI Console, and FrameworX AI Runtime MCP tools.

It is not a playground. The point of cloning this repo instead of opening a blank
chat is **discipline**: a repeatable method, a spec before a build, a review after a
build, and a test that proves the running solution does what the spec asked. The
output is a solution an operator can trust on a plant floor, not a one-off demo.

> **Design check on every decision: Aim High. Start Simple. Scale Without Limits.**
> Ambitious goal, minimal first version, an architecture that grows by addition.
> When a design starts to over-reach, snap back to "what is the simplest version
> that still hits the ambitious goal?"

---

## 1. What FrameworX is, in one screen

FrameworX is a unified SCADA, HMI, and Historian platform. You build a **Solution**
(a `.dbsln` file) made of objects organized under a runtime **Object Model**. The
parts you will touch most:

- **UNS (Unified Namespace).** The tag layer, Pillar 1 of the data foundation.
  Everything addressable lives here as `Tag.*`. Hierarchical names (`Tag.Area1/Tank1/Level`)
  are how you keep a large solution legible.
- **UserTypes (UDTs).** Reusable structured types. A `Tank` UDT with members `Level`,
  `Temperature`, `Valve` lets you stamp out twenty tanks without repeating yourself.
  Production solutions are built from UDTs, not loose tags.
- **Asset Tree.** The hierarchical, plant-shaped view of the UNS. Areas, lines, units.
- **Devices.** Protocol channels, nodes, and points that map field data to tags
  (Modbus, OPC UA, MQTT, EtherNet/IP, and so on). A solution can also be driven by
  simulation scripts when no field hardware is present.
- **Alarms.** Conditions on tags, grouped and assigned to areas.
- **Historian.** Time-series logging of selected tags into storage tables.
- **Displays.** The operator screens. Built from the FrameworX control set (verify the
  real catalog with `list_elements`, never invent a control name).
- **Scripts.** Tasks, classes, and expressions. Also the universal escape hatch
  (`Script.Class`) when a built-in does not cover a need.
- **Execution Profiles.** Production, Development, Validation, Custom. Each runs the
  runtime (TServer) on its own port. Development is the safe sandbox profile.

The broader 12-root **Object Model** spans the UNS plus eleven built-in namespaces
(Server, Client, Alarm, Device, Historian, Dataset, Script, Report, Display, Security,
Info). The built-ins are **peers of the UNS**, not parts of it. Keep that distinction in
prose and comments.

---

## 2. The MCP tools are your hands. Bootstrap first.

Three MCP servers reach the installed FrameworX product. They do **not** see this repo's
files; they operate the live product.

| Server | Use it for |
|---|---|
| **FrameworX AI Designer** | Drives a running Designer IDE. Live read/write of objects, build, runtime start/stop, screenshots. Tools: `open_solution`, `create_solution`, `get_objects`, `write_objects`, `browse_object_model`, `designer_action`, `get_screenshot`, `get_state`, `list_elements`, `list_protocols`. |
| **FrameworX AI Console** | File-based authoring with no running Designer. Reads and writes solution JSON workspaces. Tools: `open_workspace`, `create_workspace`, `get_objects`, `write_objects`, `get_table_schema`, `list_protocols`. Good for CI and offline build. |
| **FrameworX AI Runtime** | A running TServer. Live values, alarms, historian. Tools: `runtime_connect`, `runtime_get_value`, `runtime_browse_object_model`, `runtime_get_active_alarms`, `runtime_get_tag_history`, `runtime_search_uns`. |

**Bootstrap is mandatory and comes first.** Before any `write_objects`, `get_objects`,
`designer_action`, or schema call, invoke one bootstrap tool so the server injects the
Context Package (the platform mental model):

- Designer: `list_solutions`, `open_solution`, or `create_solution`.
- Console: `list_workspaces`, `open_workspace`, or `create_workspace`.

Re-bootstrap whenever you switch solutions or workspaces. Never call a write tool before
a solution context has been delivered. The server enforces this; respect it proactively.

**Tools expose features, they do not invent them.** If a step seems to need a capability
the product does not have, that is a finding to report (see Section 8), not a thing to
fake. Do not build a mock dashboard when the MCP is not connected. Get connected first.

---

## 3. The build order: foundation, then connect, then monitor, then screens, then run

Build a solution in this order. Each layer depends on the one before it. Skipping ahead
produces a demo that looks right and breaks under load.

1. **Data foundation.** Define UserTypes first. Then lay out the UNS and Asset Tree using
   those types. Name hierarchically from day one (`Area/Unit/Signal`). Decide engineering
   units, ranges, and retentive flags here. This layer is the contract every later layer
   binds to. Get it right before drawing a single screen.
2. **Connect.** Add Devices: channels, nodes, points mapped to the foundation tags. If
   there is no field hardware, drive the tags with simulation scripts so the rest of the
   solution can be built and tested against live-moving values. Verify protocols with
   `list_protocols`; verify a connection actually reads before moving on.
3. **Monitor.** Add Alarms on the tags that matter, grouped and assigned to areas. Add
   Historian logging for the tags an operator or analyst will look back on. Avoid alarming
   everything and historizing everything; both are anti-patterns that bury the signal.
4. **Screens.** Build Displays from the verified control catalog (`list_elements`). Bind
   to the foundation tags. Compose from reusable Symbols. Use the `display-authoring-loop`
   discipline: correctness pass first (does it render, do bindings resolve), composition
   pass second (alignment, grouping, readability).
5. **Run and verify.** Build the solution. Start the runtime on the Development profile.
   Confirm live values move, alarms fire on condition, history accumulates, screens update.
   Then run the test harness (Section 6) and read the result.

This is the same order Tatsoft uses internally. It is the difference between a solution
that scales and a screen that demos.

---

## 4. Verify your work. Always.

A `write_objects` that returns success means the row was written. It does **not** mean the
feature works, nor that it is reachable by an operator. After every meaningful change,
verify at the layer that proves the outcome, not the layer that wrote it:

- **Round-trip the data.** After a write, `get_objects` it back and confirm the values are
  what you intended.
- **Check the running runtime, not the file.** Use the Runtime tools to confirm a tag holds
  a live value with good quality, an alarm is active when its condition is true, and history
  is being written. The file having a row is necessary, not sufficient.
- **Look at the screen.** For any Display change, take a `get_screenshot` and read it. JSON
  that looks correct can render wrong (a control defaulting to a placeholder, a binding
  resolving to empty). The render is ground truth for UI.
- **Mind the staging chain.** A new protocol, provider, or dialog entry only reaches the user
  after the product registers it (config XML, DLL, ribbon entry). A clean write is not the
  same as a visible option. When something should appear in a picker, confirm it appears.

If you cannot verify a claim, say so plainly. "Written but not yet confirmed in runtime" is
an honest and useful status. "Done" without a check is not.

---

## 5. Supervision and honesty

This harness assumes a human is in the loop on consequential moves.

- **Confirm before hard-to-reverse actions.** Deleting objects, overwriting a solution,
  anything outward-facing. Approval for one step is not approval for the next.
- **Never test against a real or demo solution.** Automated tests get a dedicated sandbox.
  See the Sandbox Rule in Section 7.
- **Report outcomes faithfully.** If a build fails, show the error. If a step was skipped,
  say it was skipped. If tests pass, say so plainly and point at the evidence. Do not
  smooth over a gap.
- **Surface unexpected behavior and limitations.** The MCP surface is the only window the AI has
  into the product. An unreported limitation is a silent ceiling on every future session. Name it
  (Section 8).

---

## 6. How this repo is organized

| Folder / file | What lives here |
|---|---|
| `CLAUDE.md` / `README.md` / `INDEX.md` | The working agreement, the front door, and the task-routing catalog. |
| `.claude/skills/` | The process skills that run the solution-development discipline: `new-project-bootstrap`, `run-tests`, `review-the-ai-build`, `display-authoring-loop`, `commission-the-points`, `project-handover-docs`, and the rest. They complement the product's own `frameworx` on-ramp skill; they do not duplicate it. |
| `KnowledgeBase/Method/` | The method shelf: this file, `Quickstart.md`, `build-order.md`, `verify-your-work.md`, `mcp-setup.md`, `Verification-Channels-and-Simulators.md`, `Runtime-Operations.md`, `Memory-Guidance.md`. |
| `KnowledgeBase/Conventions/` | House rules: naming, working rules, display authoring, changelog convention, solution-file placement, and the rest. |
| `KnowledgeBase/Patterns/` | Verified trap catalogs: validation and readback, schema field gotchas, display authoring recipes, registration chain, and the rest. |
| `KnowledgeBase/References/` | Vocabulary and product-source references, kept close so the model grounds in real product terms instead of guessing. |
| `Templates/SiteProject/` | The new-site skeleton `new-project-bootstrap` copies: Specifications templates, the Commissioning-Record template, ChangeLogs, Tests. |
| `Templates/Examples/Brewery/` | The golden worked example: spec + `expected.json` + validated test results. |
| `Templates/Prompts/recipes.md` | Paste-ready prompts for common build steps, written for this harness. |
| `Sites/<Name>/` | One folder per engagement: Specifications, Solutions, Documentation, ChangeLogs, Tests, Decisions. |
| `AISessions/` | Git-ignored per-session scratch and cold-start resumes, never the deliverable. |

The method, end to end: **write the spec, capture the hardware envelope, build in the order
of Section 3, review the build, run the tests, read the result.**

---

## 7. The Sandbox Rule for automated tests

When running an automated test or smoke run against a live Designer or Runtime, **create a
dedicated disposable sandbox solution.** Never test against a real customer solution or a
shipped demo.

- **Name prefix `ai-test-`** followed by a short purpose slug (for example
  `ai-test-brewery-golden`). The prefix is the signal to everyone, human and AI, that the
  solution is disposable.
- **Create, do not open a real one.** Use `create_solution` (Designer) or `create_workspace`
  (Console). If a test must run against an existing solution, copy it first and rename the
  copy with the `ai-test-` prefix. Never run on the original.
- **Quiet the sandbox.** On the Development profile, set `RichClientNoSplash=true` and
  `SmartClientNoSplash=true` so the splash does not cover screenshots and console output.
  Enable only the modules the test exercises (Scripts and Datasets are always on; turn on
  Alarms, Historian, Devices, Displays only when the test uses them).
- **One sandbox per test scope.** Sandboxes are cheap. Make a new one rather than reusing an
  unrelated old one. Clean up when done.

Why it matters: exercising an untested path against a real solution can end its Designer session
or leave its file locked. Demos and customer solutions are trust artifacts, not test fixtures.

---

## 8. Report findings: unexpected behavior and limitations

When using the MCP tools, surface two classes of finding:

1. **Unexpected behavior.** A result that does not match what the tool documents, a session that
   ends mid-task, an effect you could not confirm after a call reported success.
2. **Limitations.** Gaps that stop the AI doing the task well: a tool that returns no
   confirmation, a missing parameter, an action available in the UI but not over MCP, state
   the AI cannot read, a return shape that forces guessing.

Name a limitation the moment you hit it, in plain language ("`runtime_get_value` returned the
value but no quality or timestamp, so I cannot confirm staleness"). At the end of a task,
collect findings into an `## MCP findings` block: tool, what was attempted, what was missing
or wrong, why it blocked the work, and a suggested fix. A one-off fix repairs one outcome. Closing
a limitation lifts the ceiling for every session after.

---

## 9. Context discipline on large solutions

A production solution is large. You cannot hold every tag, display, and script in context at
once, and you should not try.

- **Work from the spec and the asset tree, not the whole dump.** Browse the part of the Object
  Model you are changing. `runtime_search_uns` and `browse_object_model` let you scope.
- **Batch by layer and by area.** Build all the UDTs, then all the tags for one area, then its
  alarms, then its screens. Verify each batch before the next.
- **Never call `get_table_schema` with `expand_protocols=true` on a full install.** It inlines
  every installed driver's protocol union: on a full install that is a payload in the
  ~50-150k-token range. Use `list_protocols(search)` instead; it auto-embeds up to 3 matched
  protocol schemas.
- **Write findings down.** When a build spans many turns, keep a short running note in the spec
  or a session file so a later turn (or a fresh session) can resume without re-deriving.
- Claude Code's plan mode and task list carry the same discipline for a long build: plan the batches by
  layer and area, and verify each one before starting the next.

---

## 10. Copy and naming conventions for anything in this repo

- Tag and member names are PascalCase (`TankLevel`, not `tank_level`). Translate external
  snake_case at the boundary.
- Name hierarchically. `Area/Unit/Signal`. Flat tag lists do not scale.
- Refer to the product extensions by their canonical names in prose: "FrameworX AI Designer",
  "FrameworX AI Console", "FrameworX AI Runtime". Internal names (`DesignerMCP`, `consolemcp`)
  are for config and commands only.
- Keep operator-facing copy (display text, object descriptions, alarm messages) plain and concrete:
  no marketing superlatives, no competitor names, no pricing. State what a thing does.
