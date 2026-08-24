# Verifying at scale: the channels, the in-runtime fixture, and the simulators

`verify-your-work.md` says the rule: confirm at the layer that proves the outcome, not the layer that wrote
it. This doc is the FrameworX-specific *toolkit* for doing that. The independent channels you can read truth
from, a fixture that runs the whole cascade inside the runtime, and the built-in simulators that make a
protocol round-trip a bench-free local test. Use it when an MCP readback alone isn't enough confidence.

## Four independent verification channels

A value written into the runtime can be confirmed through any of four channels. They have **different
false-negative risks**: pick by what the test question needs, and reach for a second channel when the stakes
are high:

1. **In-runtime readback**: a verification script *inside* the runtime reads `Tag.<name>.Value` /
   `Dataset.<name>.Rows` directly. Fast, in-process. Confirms the runtime's own view.
2. **REST from outside**: a small client (e.g. Python `requests`) hits the runtime API and confirms the
   runtime *really* holds the value, not just the test script's view. Auth is a per-solution bearer token
   (a GUID): read it from the solution's secrets, never borrow one from another solution. Prefer REST when
   you're testing the HTTP surface itself (status codes, response shapes), the MCP normalizes those away.
3. **Direct SQL against the backing store**: the truth layer; the database is what actually persisted.
   Read-only, **sandbox solutions only.** Two disciplines: **historian writes are not synchronous with tag
   writes** (wait the sampling interval + a buffer before querying), and for a SQLite backing file **close
   and reopen the connection** before re-querying (it's a point-in-time snapshot). Pull the real schema
   before trusting any column name.
4. **Trace-file parse**: scripts emit timestamped lines (an `@Info.Trace`-family call) to the runtime log.
   Instrument a cascade at each interesting point, run, then parse the file to assert: all expected lines
   present, in order, within timing bounds, with no unexpected error lines. This is the channel for
   **silent-fallthrough detection** (did it take path A or B?) and **error-paths-that-recover** (a catch
   fired but the script still reported success). *(The exact trace API set and the on-disk log path are
   build-dependent, confirm against a real run before quoting a path.)*

> A reusable historian sanity check on channel 3: `SELECT TagName, COUNT(*), MIN(ts), MAX(ts) … GROUP BY
> TagName` over a one-minute window, a 1-second-sample tag should show ~60 rows. Sparse counts mean dropped
> samples, the runtime wasn't connected, or a deadband filtered them.

## The in-runtime Server-Task fixture: verify the cascade at runtime speed

Instead of N slow MCP write-then-readback round-trips, author a **Server Task that runs the whole cascade
inside the runtime**: set tag values, read them back, query active alarms, persist results to a Dataset, and
emit a trace line at each step. Start the runtime → the task fires → read the Dataset back via any channel
above. This is roughly two orders of magnitude faster than MCP round-tripping and it exercises the **real**
end-to-end paths, not the tool's view of them. It's also how you build a solution that **verifies its own
cascades**.

The in-runtime script surface is the `TK.*` family (tags, SQL, alarms, trend, time, and a write-then-await
sync marker, among others). **Confirm exact `TK.*` signatures against your installed build**, they vary
between builds. Read an existing task in a shipped demo before authoring a non-trivial one, rather than
typing a signature from memory.

## Built-in simulators: a protocol round-trip with no bench

FrameworX ships server-side simulators so a full protocol round-trip runs on one box with **no external
broker, vendor PLC, or third-party OPC server**:

- in-process **MQTT broker**,
- MQTT **Sparkplug-B publisher** simulator,
- **OPC UA server** simulator,
- **Modbus PLC slave** simulator.

Point the FX-side driver / TagProvider / channel at `127.0.0.1`, drive the simulator from a Server Task, read
back on the consumer side, and verify through the channels above. This is the strongest fit for driver-load
correctness, Sparkplug topic/payload checks, OPC UA browse/subscribe/write, and Modbus register/function-code
coverage: all before the real PLC is wired. *(The exact wiring, which `RuntimeStartup` flag / channel /
TagProvider row, is build-dependent; inspect a shipped demo and `list_protocols` for the canonical setup.)*

## The simplest bench-free data source: ValueSimulator

To get live, moving values into a new solution with no hardware at all, use the **ValueSimulator** driver: a
`DevicesChannels` row with `Protocol = ValueSimulator`, and `DevicesPoints` whose **Address** is a waveform
string in the form **`Type;Min;Max;Step`** (the 4th field, Step, is the per-scan increment. Used only by
`RAMP`):

```
SINE;-50;150       a sine wave swept between -50 and 150
RAMP;0;1000;10     a ramp from 0 to 1000, +10 per scan, resetting at the top
FLOAT;0;5          a random float in the 0..5 range
```

The `Type` keywords are `BOOL`, `INTEGER`, `FLOAT`, `STRING`, `RAMP`, `SINE` (case-insensitive). `Min` / `Max`
default to `0` / `100` when omitted; a `STRING` point's length is set via the point's `Modifiers.StringLength`,
not the Address. Pair each point with a tag of `Type = Real` carrying its engineering range and a `StartValue`,
and drive the waveform **inside that range directly**; do not lean on tag scaling or the point's `Scaling`
field to shape a simulated value (see the address rules below). This is the canonical "give me a moving foundation
to build alarms, history, trends, and displays against" rig. And the waveform crossing a limit is the easy
way to make an alarm actually fire during a check. *(Verify the exact form with
`list_protocols('ValueSimulator')` on your build.)*

### ValueSimulator address rules, confirmed by live readback

Shape a simulated waveform with **integer bounds already inside the tag's engineering range**. These rules
apply to simulated points only, they stop mattering once a real device drives the points, but each one reads
like a solution-design defect until you read the point back live:

- **Use integer Min/Max.** Fractional bounds are not applied: `SINE;0.5;3.5` ran down to ~0.05 and tripped a
  Lo alarm on a simulated value. Use integer bounds inside the tag's range. `SINE;1;3` reads ~1.9, Good
  quality.
- **Pick bounds that land in range as-is; don't shape a simulated value with point `Scaling`.** `Scaling`
  (e.g. `Div:10`) is not applied on simulated points: `SINE;5;35` + `Div:10` yields the raw 5..35, clamped at
  the tag Max with Uncertain quality, not 0.5..3.5.
- **Use `FLOAT;min;max` for narrow-range analogs, `SINE` for wide spans.** A SINE point with a narrow range
  (span ~1) holds at an endpoint instead of updating, while a wide span animates fine. FLOAT produces real
  moving decimals across a narrow range.
- **Keep simulated magnitudes at or above 1.0.** A true 0.05-0.30 signal reads a flat 0.0 under both SINE and
  FLOAT, and scaling does not reshape it (above). Where the real signal is sub-1.0, design downstream logic
  so it does not depend on that point moving in simulation.
- **Trigger `OnChange` logic from a point that actually moves.** An expression with `Execution=OnChange` and
  `Trigger=<a static point>` never fires. The derived tag sits at its uninitialized StartValue with Uncertain
  quality and *looks* like a logic error in your own expression. Re-point the trigger to an always-moving
  heartbeat tag (a `RAMP` point); the expression then re-evaluates every scan. Continuous evaluation is
  usually the better design for a derived KPI anyway.
- **Restart the runtime fully after a device-point address change.** A hot reload republishes scripts and
  displays; channel point config is read at start, so a changed waveform Address takes effect only after a
  stop and start. Expression and script changes *do* hot-reload.

## Pick the channel by the question: and confirm *which* runtime first

- **Shape vs behavior.** `browse_object_model('<Namespace>.<Collection>.<Instance>')` returns a runtime
  object's property *shape* without the runtime even running, good for "does this exist / is the type
  right." **Behavior** (the value moves, the alarm trips) needs the runtime started *and* the upstream
  source driven. Report shape-PASS and behavior-PASS separately; don't let one stand in for the other.
- **Confirm the binding before you chase a wrong value.** Check the bound solution name and start time,
  and that you're on the intended profile's port (Production 3101 / Development 3201 / Validation 3301 /
  Custom 3401), not a stale instance. Reading from an unintended instance is an easy mistake to make and
  explains many surprising values.
- **Cold-boot first read: a 10-second timeout is retry-once, not an error.** The first browse/read after a
  runtime start may time out at the read budget (~10 s) while modules come up. Retry the same call once.
  Only a **second consecutive** timeout means a wedged runtime worth investigating. The budget is a
  deliberate design choice; never propose raising it.

*(The disciplines here, verify-first, probe state not events, file-valid ≠ behavior-valid, are generic; the
channels and APIs are FrameworX. Every API name above should be confirmed against your installed build before
you script against it.)*
