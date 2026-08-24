# Golden validation run: Brewery Plant Example

Date: 2026-05-30. Harness: FrameworX Solution Workspace v1.0.0. Target: the shipped Brewery Plant Example,
copied to the sandbox `ai-test-brewery-golden` per the Sandbox Rule.

## What ran

The full harness method, end to end, through the FrameworX AI Designer and Runtime MCP:

1. Copied `Brewery Plant Example.dbsln` to `Documents\FrameworX\Dev Test\ai-test-brewery-golden.dbsln`.
2. `open_solution` on the copy. It was a legacy `fx-10.1.3` solution, so the harness exercised the
   upgrade path: a second `open_solution` upgraded it to `fx-10.1.5.2000` (auto-backup written first).
3. Quieted the sandbox per the Sandbox Rule: wrote the Development `RuntimeStartup` row with
   `RichClientNoSplash=true`, `SmartClientNoSplash=true`, `Devices=false`, `Reports=false`,
   `OpenBrowser=false`.
4. The solution carried a valid prior build of all 35 objects, with only a config row changed, so
   the runtime started on valid build artifacts.
5. `start_runtime` on Development (TServer 3201). Cold boot took longer than the 10s grace; polled
   `get_state('runtime')` to confirm bind (connected and synchronized at ~25s).
6. Started the brewery simulation the way an operator does: `set_object_value Tag.Simulation[1].Start = 1`
   and `Tag.Simulation[2].Start = 1`. The sim drives the tank values through a sequential brew cycle.
7. Collected structure (counts and domain tags) and live values over MCP, then ran the gates.

## Result

Both gates PASS, golden run and re-take. Captured output is in the sibling `*-golden.txt` and
`*-retake.txt` files; collected data in `brewery-plant-actual.json` and `*-retake.json`.

| Gate | Golden | Re-take |
|---|---|---|
| Structural (`--structure-only`) | 8/8 PASS (exit 0) | 8/8 PASS (exit 0) |
| Full (structure + live) | 13/13 PASS (exit 0) | 13/13 PASS (exit 0) |

The live assertions resolved `Tag.BrewLine[1].MashTun.Level` (a Tank Level under a BrewLine
instance), confirmed Good quality (192), a timestamp under 30s old, an in-range value (0..100),
and movement between two reads. The same MashTun also carries OutletPump (Pump), SupplyValve and
ValveWater (Valve), and Tank members (Level, Temperature, pH, Status), which confirms the domain
UserTypes at runtime.

## Determinism

- **Structural gate: deterministic.** Golden and re-take output are byte-identical (verified by
  `diff`). The same built solution reports the same counts and the same present-by-name tags on
  every run.
- **Live gate: tolerant, and passes on invariants, not numbers.** The Tank Level was actively
  cycling under the simulation: golden read pair 98.0 then 33.0; re-take read pair 33.0 then 0.0.
  Different numbers each run, same verdict (present, good quality, recent, in range, moved). This
  is the intended behavior: a moving process value cannot be asserted by equality, so the live gate
  asserts what must stay true while the value changes.
- The structural counts also proved stable across the upgrade and across the physical-vs-MCP
  reading boundary once expressed as stable invariants.

## Human-time

The run was autonomous. A human issued the one-line directive and reviewed the result. Hands-on
human time was on the order of a few minutes (the directive plus reading this report). The agent's
own wall-clock for the build-and-validate sequence (open, upgrade, configure, build attempt,
runtime boot, sim start and settle, collect, check, re-take) was roughly five to seven minutes,
most of it waiting on the TServer cold boot and the brew-cycle simulation to drive the tanks.

## Sandbox artifacts

`C:\Users\<you>\Documents\FrameworX\Dev Test\ai-test-brewery-golden.dbsln` (+ auto-backup).
Disposable; the `ai-test-` prefix marks it for the janitor sweep.
