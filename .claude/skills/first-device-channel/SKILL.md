---
name: first-device-channel
description: >-
  Author a project's first device channel (Modbus, OPC UA, S7, EtherNet/IP, MQTT, BACnet, DNP3,
  ValueSimulator, ...) and verify the device is actually communicating (good quality on a live point) before
  building on it. The missing middle between the IO register and commissioning. Use when the user says
  "connect the PLC", "add a Modbus/OPC UA/S7 channel", "configure the device", "wire the IO register to the
  hardware", "the channel won't read", "bad quality on my points", "set up the simulator". Covers channel →
  node → points authoring, the list_protocols-first rule, quality-code verification through the runtime, and
  the no-hardware-yet path via ValueSimulator.
license: Apache-2.0
metadata:
  author: Marc Taccolini
---

# First Device Channel: connect it, then prove it reads

## Why this exists

Device communication is where a solution first touches the real world, and it is the layer where a
config that *writes* cleanly most often doesn't *work*: one wrong address digit, station number, or
access type produces a channel that builds green and reads bad-quality forever. This skill drives the
authoring in dependency order and refuses to call the channel done until a live point reads back with
good quality.

## Hard rules

- **`list_protocols` before ANY protocol-dependent write.** Connection parameters and address grammar
  come from the live product for the exact protocol, never from memory, never by analogy to another
  protocol. This applies to `DevicesChannels`, `DevicesNodes`, `DevicesPoints`, and `UnsTagProviders`.
- **Check `KnowledgeBase/References/Protocol-Vendor-Notes.md`** for the vendor-specific traps (address
  offsets, byte order, session limits) before writing: it exists because each protocol has one field
  that silently breaks the connection.
- **Comms proven means quality, not build.** A successful build says the config parses. Only a live
  read with good quality (192) on a real point says the device communicates.
- **Devices is Pillar 2.** The UNS tags the points map to must exist first (Pillar 1). If they don't,
  route to UNS authoring before touching Devices.

## Process

### 1. Ground

Read the project's `Specifications/IO-Register.md` (device, protocol, addresses per point) and
`Specifications/Hardware-Spec.md` (IPs, stations, serial params). One channel per protocol+network,
nodes per physical device, points per signal: confirm the intended shape with the user if the register
is ambiguous.

### 2. Author in dependency order

`get_table_schema('Devices')` for the tab list, then `list_protocols` for the chosen protocol, then
write, `DevicesChannels` (protocol + transport settings) → `DevicesNodes` (station/endpoint per
device) → `DevicesPoints` (address per signal, mapped to its existing UNS tag, with the correct
AccessType for read vs write points). Related tables can go in one multi-table `write_objects`; keep
batches modest. Read the write response fully. Warnings and skipped counts are corrections, not noise.

### 3. Verify live: the gate

Start the runtime (Development profile), then for at least one point per node:

1. `runtime_get_value` on the mapped tag: expect **quality 192 (good)**, a plausible value, and a
   fresh timestamp.
2. For a changing signal, read twice and confirm movement; for a write point, drive it and read it back.
3. Browse `Device.Channel.<Name>` / `Device.Node.<Name>` in the object model (`browse_object_model`)
   for the channel's own status/counters when a point is suspect.

**Bad quality triage, in order:** address grammar (re-check against `list_protocols`: the #1 cause) →
node station/endpoint → network reachability (firewall, serial params) → AccessType mismatch →
vendor trap (`Protocol-Vendor-Notes.md`). Fix one variable at a time and re-read.

### 4. No hardware yet? Simulate first, swap later

When the field device isn't available, wire the points to **ValueSimulator** first (grammar and its
gotchas: `KnowledgeBase/Method/Verification-Channels-and-Simulators.md`: integer bounds, RAMP
heartbeats) so the UNS, alarms, and displays can be built and tested. Swapping the channel to the real
protocol later re-opens the comms gate: a full runtime restart, then re-verify quality on the real
device: simulator-verified is not device-verified.

### 5. Verify each path

A working sibling is not evidence: every node and every differently-addressed point is its own
verification (`CLAUDE.md` § Verify each path). One good point per node is the *minimum* gate for this
skill; per-point evidence is `commission-the-points`' job.

## Anti-patterns

- **Guessing an address format** because it "looks like" the other protocol's. `list_protocols` is the
  contract.
- **Declaring comms working from a green build or a written row.** Quality 192 on a live read is the bar.
- **Retrying an identical failing read in a loop.** Same config + same input = same result; change one
  variable.
- **Alarming or displaying a point before its quality is proven.** Bad quality propagates downstream and
  looks like ten bugs instead of one.
- **Editing the real solution's channel to "test something".** Disposable experiments go to an
  `ai-test-` sandbox.

## Composition

- **uns-from-io-register**: Pillar 1 first; this skill maps points onto tags that already exist.
- **commission-the-points**: after comms are proven, the per-point evidence pass.
- **verify-mcp-setup**: when the tools themselves fail, not the device. For a held port or a locked
  `.dbsln`, `kill-zombies` is in the [companion repo](https://github.com/tatsoft-llc/Claude-Code-Skills).
- **run-tests**: the structural + live gates once the layer is built.
