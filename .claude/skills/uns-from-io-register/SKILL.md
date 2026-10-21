---
name: uns-from-io-register
description: >-
  Turn a project's Specifications/IO-Register.md into the solution's UNS foundation, UserTypes for repeated
  equipment, the Area/Equipment/Signal folder hierarchy, and one tag per register row, then verify the result
  by read-back and reconcile the register's "Target UNS Tag" column as built. The Pillar-1 counterpart to
  display-authoring-loop: the most consequential design layer, mechanized. Use when the user says "build the
  UNS", "create the tags from the IO register", "author the tag layer", "model the plant", "set up the
  UserTypes", "turn the point list into tags", or right after new-project-bootstrap hands off to authoring.
license: Apache-2.0
metadata:
  author: Marc Taccolini
  version: "1.1.0"
---

# UNS from the IO Register: the foundation layer, traceable

## Why this exists

The UNS is the first and most consequential design decision in a solution, every device point, alarm,
historian entry, script, and display binds to it. Building it ad-hoc produces the two classic failures:
tags that don't trace back to the register (orphan signals nobody commissions) and near-duplicate
structures where a UserType should have been. This skill makes the register the single source: every row
becomes exactly one tag, every tag traces to a row, and the register's **Target UNS Tag** column is
updated as built, that column is the traceability contract `commission-the-points` later drives.

## Hard rules

- **Ground first.** Read `Specifications/IO-Register.md` + `Specifications/Requirements.md` and
  `KnowledgeBase/Conventions/UNS-Naming.md` before writing anything. The platform's UNS design rules come
  from the bootstrap Context Package: fetch, don't recall.
- **Naming:** `<Area>/<Equipment>/<Signal>`, PascalCase members, `/` for hierarchy, `.` only for member
  access. Units live in the tag's engineering-unit property, never in the name.
- **UserType when instances repeat.** Two or more pieces of equipment with the same member set (every
  Pump has Run, Speed, Fault…) = define the UserType once, instantiate per equipment. One-off signals
  stay plain tags. Don't force a UDT onto a single instance "for the future."
- **Never create tags for object-model state.** Alarm counts, server time, device status live in the
  runtime object model (`Alarm.Group.*`, `Server.*`, `Device.*`), bind to them directly.
- **TagProvider boundary:** if an external source (OPC UA server, MQTT broker) publishes the catalog, the
  source is authoritative, surface it via a TagProvider (load the platform's TagProvider skill via
  `search_docs`), never hand-author shadow tags of provider-published names.

## Process

### 1. Derive the model from the register

Group rows by area and equipment. Propose the shape *before* writing: the UserTypes (name + members with
data types), the folder tree, the plain tags, and the count ("42 rows → 3 UserTypes × 9 instances + 6
plain tags"). One short confirmation with the user on the shape: the UNS is the decision worth a
question; everything after is mechanical.

### 2. Write in dependency order, in batches

`get_table_schema('UnsUserTypes')` / `('UnsTags')` for the real field names (data type, engineering
units, min/max, description, never guess), then write UserTypes first, then folders/instances/tags,
related tables can share one multi-table `write_objects`. Keep batches modest (a dozen-odd objects on
heavy tables); read every response's warnings and skipped counts. Carry the register's engineering
columns (units, range, description) onto the tags now: they feed alarms, displays, and the historian
later, and retrofitting them costs a full second pass.

### 3. Read back: counts and spot paths

- `get_objects` / `search_uns` to confirm the created counts match the plan (UserTypes, instances, tags).
- Spot-read full paths, including at least one member per UserType (`Tag.Area1/Pump1.Run`). Instance
  member access is the thing that breaks when a member name drifted.
- On a large register, batch by area and verify each batch before the next. Track the batches in Claude
  Code's task list, so a long build stays legible and resumable.

### 4. Reconcile the register

Update `Specifications/IO-Register.md`'s **Target UNS Tag** column with the as-built paths. Any register
row without a tag, or tag without a row, is a finding to surface, not to silently absorb. Note the layer
in your `ChangeLogs/ChangeLog-<user>.md`; a non-obvious modeling choice (why this UDT boundary, why that
area split) goes to `Decisions/`.

### 5. What this skill does NOT do

Alarm limits, historian selection, and device addresses in the register are *recorded* here but *built*
in their own layers (Pillar 2, `first-device-channel` for comms, alarm authoring per
`KnowledgeBase/Conventions/Alarm-Style.md`). Finish and verify the foundation before fetching any
Pillar-2 schema: pillar isolation is the platform's rule, not a preference.

## Anti-patterns

- **Writing tags straight from the register without proposing the UDT/folder shape first.** The shape IS
  the design decision.
- **Mirroring an external system's naming (snake_case columns, PLC symbol names) into member names.**
  One convention, PascalCase; alias at the boundary (query aliases, provider mapping), never duplicate members.
- **A 200-tag single write.** Batch by area; errors stay isolated and progress stays visible.
- **Leaving the Target UNS Tag column stale.** An unreconciled register makes commissioning drive ghosts.
- **"The sibling instance works, so they all do."** Each instance path you bind to later is its own
  verification (`CLAUDE.md` § Verify each path).

## Composition

- **new-project-bootstrap**: produces the register this skill consumes; hands off here.
- **first-device-channel**: next layer: map the built tags to device points and prove comms.
- **ground-first / premise-check**: the shape-confirmation step is a natural premise check moment.
- **run-tests**: `expected.json`'s structural assertions (UserTypes, tag counts) come from step 1's plan.
