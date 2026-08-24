# Harness validation record: 2026-05-30

The committed record of the golden build and test run that validated this harness. The raw run
output (captured gate text and collected JSON) lives in `results/` and is kept as reference
evidence of this pass: it is regenerated on every run of the test gate; this file is the
durable summary.

Harness version 0.1.0. Target: the shipped Brewery Plant Example, copied to the sandbox
`ai-test-brewery-golden` per the Sandbox Rule.

## What ran, end to end

Through the FrameworX AI Designer and Runtime MCP:

1. Copied `Brewery Plant Example.dbsln` to the `Dev Test\` sandbox folder as `ai-test-brewery-golden`.
2. `open_solution`. The source was a legacy `fx-10.1.3` solution, so this also exercised the upgrade
   path: a second `open_solution` upgraded it to `fx-10.1.5.2000` (auto-backup written first).
3. Quieted the sandbox per the Sandbox Rule: Development `RuntimeStartup` with splashes off and
   Devices, Reports, OpenBrowser off.
4. The solution carried a valid prior build of all 35 objects, with only a config row changed, so
   the runtime ran on valid build artifacts.
5. `start_runtime` on Development (TServer 3201). Polled `get_state('runtime')` to confirm bind.
6. Started the brewery simulation as an operator does: `set_object_value Tag.Simulation[1].Start = 1`
   and `[2].Start = 1`. The sim drives the tanks through a sequential brew cycle.
7. Collected structure and live values over MCP and ran both gates, golden run and re-take.

## Result

Both gates PASS, golden and re-take.

| Gate | Golden | Re-take |
|---|---|---|
| Structural (`--structure-only`) | 8/8 PASS (exit 0) | 8/8 PASS (exit 0) |
| Full (structure + live) | 13/13 PASS (exit 0) | 13/13 PASS (exit 0) |

The live assertions resolved `Tag.BrewLine[1].MashTun.Level` (a Tank Level under a BrewLine
instance): Good quality (192), timestamp under 30s old, value in 0..100, and movement between two
reads. The same MashTun carries OutletPump (Pump), SupplyValve and ValveWater (Valve), and Tank
members, confirming the domain UserTypes at runtime.

## Determinism

- **Structural gate: deterministic.** Golden and re-take output are byte-identical (verified by
  `diff`). The same built solution reports the same counts and present-by-name tags every run.
- **Live gate: tolerant.** The Tank Level was cycling under the simulation: golden read pair
  98.0 then 33.0; re-take read pair 33.0 then 0.0. Different numbers each run, same verdict. A
  moving process value cannot be asserted by equality, so the live gate asserts what must stay true
  while the value changes (present, good quality, recent, in range, moved).

## Human-time

Autonomous run. A human issued the one-line directive and reviewed the result: a few minutes of
hands-on time. The agent's own wall-clock for the build-and-validate sequence was roughly five to
seven minutes, most of it waiting on the TServer cold boot and the brew-cycle simulation to drive
the tanks.

## Sandbox artifacts

`C:\Users\<you>\Documents\FrameworX\Dev Test\ai-test-brewery-golden.dbsln` (+ auto-backup).
Disposable; the `ai-test-` prefix marks it for the janitor sweep.
