# Hardware and topology spec: Highland Municipal Water Treatment Plant

> The hardware envelope the solution targets. The first version runs simulation-only (the PLC channel is built
> but disabled), so the field devices are specified for the re-point while a ValueSimulator drives live values.

## 1. Field devices

| Device | Vendor / model | Protocol | Point count | Poll rate | Notes |
|---|---|---|---|---|---|
| `PLC_Main` | Allen-Bradley ControlLogix `1756-L8X`, 1756-A13 (13-slot) chassis | EtherNet/IP (CIP) | 20 | default | `192.168.1.10`, slot 0. **InitialState = Disabled** in v1. |
| `SimChannel` | FrameworX ValueSimulator | (internal) | 25 | n/a | **Enabled** in v1. SINE patterns tuned inside the compliance bands. |

- **Total points:** 20 controller (PLC) + 25 simulation.
- **Total tags:** 20 area tags (9 UDT instances + 11 analog) + 9 derived KPI/Plant tags = 29 + UI/internal.

> **v1 is simulation-driven.** `PLC_Main` mirrors the L5K 1:1 but ships disabled; `SimChannel` animates the
> analog measurements so the solution builds and verifies without field hardware. Enable `PLC_Main` (and
> detune/disable `SimChannel`) to go live.

> **Source naming inconsistency (resolved):** the equipment spec §2 labels the processor "1756-L83E
> CompactLogix," but L83E is a *ControlLogix* part and the L5K `CommPath` is chassis/backplane-based
> (`AB_ETH-1/192.168.1.10/Backplane/0`). Built to the **ControlLogix** driver accordingly.

## 2. Network and topology

- **Segments:** control network (PLC + runtime host), plant/operations network (operator clients).
- **Where the runtime host sits:** control network, plant MCC room.
- **Where operators connect from:** rich client on the plant network; HTML5 Web Client for read-mostly views.
- **Remote access for the AI MCP bridges:** localhost only (the Designer/Console/Runtime bridges). See
  `KnowledgeBase/Method/mcp-setup.md`; never expose a bridge to the public internet.

## 3. Protocol load and redundancy

- **Protocols in use:** EtherNet/IP to the ControlLogix; ValueSimulator internally for v1.
- **Redundancy:** none in v1 (single controller, single runtime). A standby raw-water pump (P102) provides
  process redundancy.
- **Expected update rate end to end:** sub-second for the monitored analogs at this point count.

## 4. Runtime host sizing

| Resource | Minimum | Recommended | Notes |
|---|---|---|---|
| CPU | 2 cores | 4 cores | headroom for the historian and any local-AI feature |
| RAM | 4 GB | 8 GB | scales with tag count and historian retention |
| Disk | 20 GB | 50 GB | sized for ≥ 1-year historian retention (below) |
| OS | Windows 10/11 or Server 2019+ | | |

- **Historian growth estimate:** ~25 analog tags, on-change with 60 s time-deadband + 1 % value deadband,
  365-day retention, modest; tens of MB/year at this deadband. Size disk for retention margin, not today's rate.
- **Local AI (optional):** the §5 ML opportunity (filter-headloss / turbidity prediction for proactive dosing)
  would need host room for a model; not part of v1.

## 5. Growth

The foundation grows by adding instances of the existing UserTypes (Pump / ChemPump / Filter) and area folders,
not by reworking it. Next two growth steps: (1) enable `PLC_Main` and add the field layer for a second train /
additional instruments; (2) add the predictive-dosing ML feature (§5 of the equipment spec) as a Script.Class
consumer of the historized headloss and turbidity trends.
