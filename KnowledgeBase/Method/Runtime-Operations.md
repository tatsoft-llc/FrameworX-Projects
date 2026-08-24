# Runtime operations: reference

Lookup material for starting, stopping, and probing the FrameworX runtime from this harness. This is
reference, not a workflow: the build method (`Solution-Build-Method.md` §3, layer 5) and the skills
(`run-tests`, `commission-the-points`) point here when they need a field or a port. Field and tool names here
follow a 10.1.5 build; `get_table_schema('RuntimeStartup')` and the live tool descriptions are
authoritative: verify against your installed build.

## Execution profiles and their ports

Each Execution Profile runs the runtime (TServer) on its own default port:

| Profile | Default port | Role |
|---|---|---|
| Production | **3101** | the plant-facing runtime |
| Development | **3201** | the safe sandbox profile, where harness work runs |
| Validation | **3301** | acceptance / staging |
| Custom | **3401** | site-specific |

Before trusting any runtime answer, confirm WHICH runtime you are bound to, solution name, start time, and
port. Reading from an unintended instance is an easy mistake to make (see
`Verification-Channels-and-Simulators.md` → "confirm *which* runtime first").

## Start / stop / build verbs

- **Designer path:** `designer_action` carries the build and runtime lifecycle actions (build the solution,
  start the runtime, stop the runtime). Confirm the exact action names in the tool's own description on your
  build. A config change a running Display should reflect needs a **cold reload**. Stop + start, not just a
  re-read (see `Patterns/MCP-Display-Authoring-Recipes.md`).
- **On a large solution, build via the runtime start, not a standalone build.** Starting the runtime builds
  **and** publishes all pending config as one step and is the reliable path; a bare `designer_action('build')`
  on a large solution can run past the MCP call timeout. (A build that "timed out" may still have completed.
  confirm before re-running; see `Patterns/Validation-and-Readback.md`.)
- **After a device/historian hot reload, confirm runtime state through the Runtime tools.** The Designer's
  link state can read "disconnected" while the TServer keeps serving correct, updated data, so verify with
  the FrameworX AI Runtime tools (`runtime_connect` + `runtime_get_value`), not the Designer's `get_state`,
  before declaring an outage. And remember a hot reload republishes **scripts and displays only**: a
  device-point (address) change needs a full stop + start (see
  `Verification-Channels-and-Simulators.md`).
- **Keep `write_objects` batches small on heavy tables.** An oversized batch can exceed the call timeout and
  end the Designer session (`DESIGNER_CLOSED`): keep writes to around a dozen objects per call on heavy
  tables. If the session ends, re-`open_solution` and continue with smaller batches; don't abandon a
  multi-step task on one dropped session.
- **Runtime probes:** `runtime_connect` binds the session to a running TServer; then `runtime_get_value`,
  `runtime_browse_object_model`, `runtime_search_uns`, `runtime_get_active_alarms`, `runtime_get_tag_history`
  read it.
- **HTTP liveness:** the runtime exposes a `/health` endpoint that reports `starting` → `healthy`. Probe it
  over plain HTTP when you need liveness without a full MCP bind (useful in scripts and CI).
- **Cold-boot read rule:** the first browse/read after a runtime start may time out at the ~10 s read budget
  while modules come up. Retry the same call once; only a second consecutive timeout means a wedged runtime.
  Never propose raising the budget. (Full rule: `Verification-Channels-and-Simulators.md`.)

## RuntimeStartup: the per-profile configuration row

`RuntimeStartup` holds one row per Execution Profile. The fields that matter to harness work (confirm exact
column names with `get_table_schema('RuntimeStartup')`):

| Field group | Fields | Notes |
|---|---|---|
| Module enables | `Scripts`, `Datasets`, `Alarms`, `Historian`, `Devices`, `Reports`, `Displays` | Opt-in per profile. For a sandbox, enable only what the test exercises: Scripts and Datasets stay on; everything else only when used. A runtime booting unused modules wastes startup time and adds diagnostic noise. |
| Splash / browser | `RichClientNoSplash`, `SmartClientNoSplash`, `OpenBrowser` | For sandboxes: splashes off (they cover screenshots and console output), `OpenBrowser` off (no surprise browser tab on start). |
| Ports | `Port`, `AutoPorts` | See below. |

**Profile-lock on writes (by design):** only the **Development** row is writable over the MCP, so author the
Development row directly. A write aimed at a Production / Validation row returns `success: true` while
landing on the Development row (Designer), or is skipped with a warning and `updated: 0` (Console): read the
updated counts and `warnings[]` rather than the success flag. (See `Conventions/Working-Rules.md` → "After a
write, read it back".)

## AutoPorts and the actual port

- A new solution seeds the Development row with `AutoPorts=true`: if the default port is busy, the runtime
  auto-bumps to the next free port so parallel sandboxes coexist instead of failing with a port-in-use error.
- **Never write `AutoPorts=false` on the Development row, including to pin a custom port.** If a test needs
  a preferred port, set `Port` and leave `AutoPorts=true`; if the runtime then bumps off a busy port, read
  the **actual** running port from the runtime surface rather than assuming the configured one.
- Auto-bump resolves the collisions the runtime can see, not every foreign listener on the box: when a
  connect fails, confirm the actual port and the actual bound solution before debugging anything else.

## Runtime diagnostics tool family

Beyond the read probes above, the Runtime MCP server carries a diagnostics family for "why is it not
behaving" questions, names of the shape `runtime_list_instances`, `runtime_describe_object`,
`runtime_describe_binding`, and the `runtime_debug_*` group (module states, process info, recent events,
recent alarm fires, display bindings). Confirm availability and exact names against your build and your
permission configuration (the harness pre-approves only the read probes; diagnostics prompt). Use them to answer, in
order: *is the runtime up* (`/health`, `runtime_connect`) → *which instance am I on*
(`runtime_list_instances`) → *did the module start* (module states) → *what happened just now* (recent
events / alarm fires).

## The sandbox quick-recipe (cross-reference)

For an `ai-test-` sandbox: Development profile · splashes off · `OpenBrowser` off · only the exercised
modules on · `AutoPorts=true` left alone. The full Sandbox Rule lives in
`Solution-Build-Method.md` §7; this page is just where the fields are.
