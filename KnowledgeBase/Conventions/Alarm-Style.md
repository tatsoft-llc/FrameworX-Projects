# Alarm style: only actionable alarms, rationalized once

The alarm convention `CLAUDE.md` and `Working-Rules.md` point at. Scope: how this workspace decides
*what* becomes an alarm, at *what priority*, with *what settings*. The FrameworX mechanics (AlarmsGroups /
AlarmsItems fields) come from `get_table_schema('Alarms')` on your build, not from this file. The
underlying practice is standard alarm rationalization (ISA-18.2 shape); this is the working subset.

## The one test

**An alarm exists so an operator takes an action.** For every candidate: *what does the operator DO when
this fires?* No answer → not an alarm (it's a historian point, a display indication, or nothing).
"Alarming everything in the IO register" is the classic failure: it produces a screen the operator
learns to ignore, which is worse than no alarms.

## Priority bands

Map priorities to a small, fixed set of groups. Consequence + urgency decide the band, never "how
important the equipment feels":

| Band | Meaning | Operator response |
|---|---|---|
| **Critical** | safety / equipment-damage / shutdown consequence, act NOW | immediate action, always AckRequired |
| **High** | production or availability consequence, act within minutes | prompt action, AckRequired |
| **Warning** | drifting toward a consequence, act this shift | scheduled action |
| **Info** | event worth a record, no action | none, prefer historian/event log over an alarm |

Most points get **no** alarm; of the alarmed ones, most are Warning. If Critical is more than a small
fraction of the alarm list, the rationalization failed, re-triage.

## Settings that prevent a nuisance system

- **Limits come from the process, recorded in the IO register** (the spec's alarm columns): not invented
  at authoring time. A limit nobody can defend gets removed at the first nuisance complaint.
- **Deadband on every analog alarm.** A limit with no deadband chatters at the boundary. Size it below
  the smallest meaningful process change and above the signal noise (a few percent of range is the usual
  starting point; the process engineer's number wins).
- **Delay (on-time) for signals that spike benignly**: pumps starting, transients. Seconds, decided per
  point, recorded in the register.
- **Group by area, mirroring the UNS.** `Area` grouping is what lets a Display filter to "my alarms" and
  an `Alarm.Group.<X>.TotalCount` binding mean something.
- **AckRequired follows the band** (see table). An unacknowledged-forever Info alarm is register noise.

## Authoring and verification

- Alarms are Pillar 2. The tags exist first; alarm items bind to tags, priorities map to groups.
- After writing: fire at least one alarm per group **live** (drive the tag past its limit via the
  simulator or `set_object_value`), and confirm activation + acknowledge round-trip through
  `runtime_get_active_alarms`. A written AlarmsItems row is config; a fired-and-acked alarm is evidence.
- Record the per-point limits/deadbands/delays in `Specifications/IO-Register.md` (or the solution spec)
  so commissioning can assert them; non-obvious rationalization calls go to `Decisions/`.

## Anti-patterns

- Alarming a point because it exists in the register.
- Duplicate alarms for one root cause (the pump trip AND its low-flow AND its low-pressure consequence.
  alarm the cause, indicate the rest).
- Critical-by-default "to be safe": it inverts: everything Critical means nothing is.
- Copying limits from a sibling instance without checking the process difference (§ Verify each path).
- Inventing field names for deadband/delay: `get_table_schema` on your build is the contract.
