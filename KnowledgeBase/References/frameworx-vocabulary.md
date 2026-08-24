# FrameworX vocabulary for the AI

A short, load-bearing glossary. The terms here are how the product names things. Use them
exactly. Guessing a near-synonym produces config that looks right and binds to nothing.

For terms that *collide*, Solution vs Application vs Environment, Profile vs ExecutionProfile, Build vs
Create, the two meanings of Workspace, and the Runtime API's name, see
[`Product-Vocabulary-Disambiguation.md`](Product-Vocabulary-Disambiguation.md).

## The data foundation

- **Solution.** A FrameworX project. A `.dbsln` file. The whole thing you build.
- **Tag.** An addressable value in the runtime. Lives in the UNS as `Tag.<path>`.
- **UNS (Unified Namespace).** The tag layer. Pillar 1, the data foundation. Strict scope:
  `Tag.*` only. Name hierarchically, `Tag.Area/Unit/Signal`.
- **UserType (UDT).** A reusable structured type with members. Instances of a UDT are tags
  whose members are addressable (`Tag.Tank01/Level`). Build from UDTs, not loose tags.
- **Asset Tree.** The plant-shaped hierarchy over the UNS. Areas, lines, units. This is how
  an operator and an integrator both navigate a large solution.

## The Object Model

The runtime exposes twelve roots. The UNS is one. The other eleven are built-in namespaces
and are **peers of the UNS, not parts of it**:

`Server`, `Client`, `Alarm`, `Device`, `Historian`, `Dataset`, `Script`, `Report`,
`Display`, `Security`, `Info`.

When you walk all twelve roots, you are walking the Object Model. When you walk only `Tag.*`,
you are walking the UNS. Keep the words straight; the distinction is deliberate.

## The functional modules

- **Devices.** Channels, Nodes, Points. A channel is a protocol connection; a node is a
  device on it; a point maps a device register to a tag. Verify available protocols with
  `list_protocols`.
- **Alarms.** Items (a condition on a tag), grouped into Groups, assigned to Areas.
- **Historian.** Historian Tags (which tags to log), Historian Tables (where), Storage
  Locations (the backing store).
- **Displays.** Operator screens, built from controls (Symbols are reusable composites).
  Verify the real control set with `list_elements`. Do not invent a control name.
- **Scripts.** Tasks (run on a trigger or interval), Classes (reusable code, the universal
  escape hatch via `Script.Class`), Expressions (inline logic on a binding).
- **Datasets.** Database connections, tables, and queries for relational data.
- **Reports.** Report forms and web-data outputs.
- **Security.** Users, Policies, Permissions.

## Execution and addressing

- **Execution Profile.** Production, Development, Validation, Custom. Each runs the runtime
  (TServer) on its own port. Production 3101, Development 3201 by default. Develop and test
  on the Development profile.
- **TServer.** The runtime process that serves live values, alarms, and history.
- **`@`, `.`, `/`.** `@` prefixes a runtime object reference in a binding. `.` separates a
  member from its object. `/` separates levels of a hierarchical name. So
  `@Tag.Area1/Tank01.Level` reads the `Level` member of `Tank01` under `Area1`.

## Quality and time

A live tag value carries quality and a timestamp, not just a number. When you verify a
runtime value, confirm the quality is good and the timestamp is recent. A stale value with a
plausible number is a common trap.

## Naming rules the harness keeps

- Tag and member names are PascalCase. Translate external snake_case at the boundary.
- Hierarchical names always. Flat lists do not scale past a small demo.
- Built-in namespaces are peers of the UNS. Do not call them part of the UNS.
