# The build order, in detail

The harness builds a solution foundation-first, in five layers. This is the long form of
Section 3 of `KnowledgeBase/Method/Solution-Build-Method.md`. The validation record at the end
shows the order applied to a real solution.

## Why order matters

Every layer binds to the one before it. A Display binds to a tag. An alarm binds to a tag. A
historian entry binds to a tag. The tag belongs to a UserType and lives in the UNS. If you draw
the screen before the foundation is right, you bind to names that change under you, and you spend
the rest of the build chasing broken references. Foundation first is not a style preference. It
is the cheapest path to a solution that holds together.

## Layer 1: Data foundation

1. **UserTypes first.** Identify the things that repeat (tanks, motors, valves, lines) and define
   a UDT for each, with members and engineering metadata (units, ranges, retentive flags).
2. **UNS and Asset Tree.** Lay out the areas and units. Instance the UDTs into the tree. Name
   hierarchically from the first tag.
3. **Verify.** `get_objects` the UDTs and a sample of instances back. Confirm members, units, and
   names are what the spec said. Do not proceed on a foundation you have not read back.

## Layer 2: Connect

1. **Real hardware.** Add Devices: a channel per protocol connection, nodes for devices, points
   mapping registers to foundation tags. Verify the protocol exists with `list_protocols` and
   confirm a point actually reads.
2. **No hardware yet.** Drive the foundation tags with simulation scripts so the rest of the
   build has live-moving values to bind, alarm, historize, and display against. A simulated
   foundation is a legitimate way to build and test everything above it.
3. **Verify.** Confirm tags hold live values with good quality in the runtime, not just that a
   point row exists.

## Layer 3: Monitor

1. **Alarms.** Put conditions on the tags that an operator must react to. Group them and assign
   areas. Resist alarming everything; alarm fatigue is a real failure mode.
2. **Historian.** Log the tags an operator or analyst will look back on. Choose retention per
   table. Resist historizing everything; storage bloat and slow queries are the cost.
3. **Verify.** Force an alarm condition and confirm the alarm goes active. Confirm history rows
   accumulate for a logged tag.

## Layer 4: Screens

1. **List the catalog.** `list_elements` before authoring. Bind to the real control set.
2. **Build from Symbols.** Define a reusable composite per asset type, instance it per asset, bind
   each instance to its asset's tags. The screen-layer echo of building from UserTypes.
3. **Two-pass authoring.** Correctness first (renders, bindings resolve), composition second
   (alignment, grouping, readability). Use `get_screenshot` as ground truth.

## Layer 5: Run and verify

1. **Build** the solution.
2. **Start the runtime** on the Development profile.
3. **Confirm live behavior.** Values move, alarms fire on condition, history accumulates, screens
   update.
4. **Run the test harness** (`Sites/<Name>/Tests/` via the `run-tests` skill). Read the result
   against the spec's acceptance checks.

---

## Validation record

This section records the one golden build and test run used to validate the harness. Update it
when the harness is re-validated.

- **Target:** the shipped Brewery Plant Example, a script-simulated brewery solution (no field
  devices). Known structure: 20 UserTypes, 13 UNS tags plus an asset tree, 32 alarms in 3 groups
  across 2 areas, 40 historian tags in 3 tables, 20 displays, 7 script tasks, 3 users.
- **Method:** copied to an `ai-test-` sandbox per the Sandbox Rule, opened on the Development
  profile with splashes off, built, runtime started, structure and live values collected over
  MCP and checked against `brewery-plant.expected.json`.
- **Note on reading structure:** the `.dbsln` is an encrypted SQLite file, so structure is read
  through the product over MCP, not by parsing the binary (see
  `KnowledgeBase/References/dbsln-format-note.md`). The expected counts were confirmed against the
  real solution through the product before the run.
- **Result, determinism, and human-time:** the committed record is
  [`validation-2026-05-30.md`](../../Templates/Examples/Brewery/validation-2026-05-30.md); the raw
  run output is in `results/` (regenerated each run, not version-controlled). The run passed both
  gates, golden and re-take (structural 8/8, full 13/13, exit 0 each). The structural gate is
  deterministic across re-takes (byte-identical output); the live gate asserts invariants with
  tolerance (the Tank Level cycled 98 to 33 to 0 under the simulation, so the check asserts present,
  good quality, recent, in range, and moved, not an exact number). Human time was a few minutes;
  the agent's build-and-validate wall-clock was about five to seven minutes.
