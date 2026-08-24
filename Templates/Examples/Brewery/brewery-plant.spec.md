# Solution spec: Brewery Plant (worked example)

> A worked, production-grade spec derived from the structure of the shipped Brewery Plant Example.
> It is here to show the level of detail a real spec carries and to give the test harness a known
> target. The acceptance checks in Section 8 map to `brewery-plant.expected.json`.

## 1. Intent

Monitor and visualize a two-line brewery process: tanks, pumps, and valves per line, with live
process values, alarming on out-of-range conditions, time-series history for trend analysis, and
an operator screen set. The first version runs entirely on simulated process values, so the full
solution (foundation, alarms, historian, screens) can be built and tested without field hardware,
then re-pointed at real controllers later by swapping the connect layer.

## 2. Target and profile

- **Field hardware:** none in this version. Process values are driven by simulation scripts.
- **Runtime host:** single Windows host (no field hardware in this version).
- **Build and test profile:** Development (TServer 3201).
- **Sandbox name for testing:** `ai-test-brewery-golden`

## 3. Data foundation

### 3.1 UserTypes (UDTs)

Six domain UserTypes carry the model. (The solution also defines UI and trend-helper types, which
are platform-side and not part of the process model.)

| UserType | Role |
|---|---|
| `Tank` | A process vessel: level, temperature, and status. |
| `Pump` | A pump: run state, speed or flow, fault. |
| `Valve` | A valve: open or closed state, command. |
| `BrewLine` | A production line: composes Tanks, Pumps, and Valves for one line. |
| `Simulation` | The per-line simulation driver that moves the process values. |
| `Enum_Status` | The status enumeration shared across equipment. |

The line is the unit of reuse. `BrewLine` is instanced as an array of two, so the whole two-line
plant is two instances of one type, not two hand-built copies.

### 3.2 UNS and Asset Tree

- `BrewLine` is an array of 2 (the two production lines), typed `BrewLine`.
- `Simulation` is an array of 2, typed `Simulation`, one driver per line.
- `refBrewLine` and `refSimulation` are reference tags that point at the line the operator has
  selected, so one screen set serves both lines.
- Supporting top-level tags: `ServerMonitorInfo`, `UI`, four `Internal_*` scratch tags, plus the
  platform built-ins (`Internal_Dynamic`, `Templates`, `Placeholder`).
- **Expected top-level UNS tag count:** 13.
- **Expected asset tree roots:** the brewery plant root.

## 4. Connect

- **Mode:** simulation. There are no device channels in this version.
- **Tags that must hold live, moving values in runtime:** the Tank levels and temperatures under
  each `BrewLine` instance, moved by the corresponding `Simulation` instance. The collect step
  discovers the exact leaf paths via `runtime_browse_object_model`; the test asserts movement,
  good quality, recent timestamp, and in-range value rather than an exact number.

## 5. Monitor

### 5.1 Alarms

Conditions on the process tags that an operator must react to (tank level and temperature
extremes, pump faults), grouped and assigned to plant areas.

- **Expected alarm item count:** 32.  **Groups:** 3.  **Areas:** 2.

### 5.2 Historian

The process values worth trending are logged across three storage tables.

- **Expected historian tag count:** 40.  **Tables:** 3.

## 6. Screens

An operator screen set: a plant overview, per-line detail built from a reusable line symbol, an
alarm page, and trend screens. Built from Symbols so the two lines share one definition.

- **Expected display count:** 20.

## 7. Security

- **Users:** 3 (administrator plus operator-level accounts).

## 8. Acceptance checks (the contract for tests/)

These are written as stable invariants, not raw totals. Raw counts drift across the physical file,
the MCP view, and a version upgrade (built-in tags are hidden from the MCP tag count, and the upgrade
adds a user account). The harness asserts what stays true. See `validation-2026-05-30.md`.

- [ ] The UNS exposes the domain instance tags `BrewLine` and `Simulation` (each an array of 2) and
      their selection references `refBrewLine` and `refSimulation`.
- [ ] The domain UserTypes are present at runtime: a `BrewLine` instance contains Tank instances
      (Level, Temperature, pH, Status), each Tank carries a Pump (OutletPump) and Valves
      (SupplyValve, ValveWater).
- [ ] 32 alarms exist across 3 groups and 2 areas.
- [ ] 40 historian tags log into 3 tables.
- [ ] 20 displays exist.
- [ ] At least 3 users are defined.
- [ ] In the running runtime, a Tank Level under a `BrewLine` instance holds a value with good
      quality, a timestamp under 30 seconds old, within its 0..100 range, and the value changes
      between two reads a few seconds apart (the simulation, started by setting
      `Tag.Simulation[*].Start = 1`, is moving it).
