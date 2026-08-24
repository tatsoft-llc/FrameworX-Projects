# Highland Municipal Water Treatment Plant: System Handover

As-built summary of the FrameworX SCADA / HMI / Historian solution for the Highland Municipal WTP, for the
utility's engineering/IT staff and the next integrator. Generated from the live solution on 2026-06-09
(FrameworX 10.1.5.2000).

## System overview

Operations, compliance-evidence, and historian layer for a conventional surface-water treatment plant
serving ~18,000 residents (design **5 MGD**, average **3.2 MGD**). It monitors and visualizes the four
process areas, Raw Water Intake, Chemical Feed, Filtration, Disinfection & Clearwell, historizes every
process variable for regulatory compliance, alarms on the TCEQ / EPA Surface Water Treatment Rule limits,
and computes operational KPIs. **Closed-loop control stays in the plant ControlLogix PLC**; this solution
does not run the loops. Requirements: [Requirements.md](../Specifications/Requirements.md).

> **Build status:** hardware-free build. The ControlLogix channel is **disabled** and a tuned ValueSimulator
> drives live values. Go live by enabling `PLC_Main` (and disabling the simulator). See *Architecture*.

## Architecture & topology

- **Runtime:** single FrameworX server runtime (Development profile) with rich/web clients.
- **Two device channels:**

  | Channel | Protocol | Node / station | State |
  |---|---|---|---|
  | `PLC_Main` | Allen-Bradley **ControlLogix** | `Controller` @ `192.168.1.10;44818;0` (slot 0, EtherNet/IP) | **Disabled**, enable to go live |
  | `SimChannel` | ValueSimulator | `SimNode` (`simulator`) | Enabled, drives demo data |

- **45 device points** mapped 1:1 from `Highland_WTP_Main.L5K`. To cut over to the real plant: enable
  `PLC_Main`, disable/detune `SimChannel`.

## Tag / UNS register

ISA-95 area hierarchy `Highland/<Area>/<Leaf>`, leaf names kept PLC-faithful. **20 area tags** (9 UDT
instances + 11 analog) + 9 computed KPI/Plant tags, 29 total.

- **3 equipment UserTypes (from the L5K):** `Pump` (VFD raw-water pumps), `ChemPump` (chemical metering
  pumps), `Filter` (dual-media gravity filter, headloss, effluent turbidity, valve, backwash counters).
- **Area 100, Raw Water:** `P101`, `P102` (Pump); `FT101`, `AIT101` (turbidity), `AIT102` (pH), `LT101`.
- **Area 200, Chemical Feed:** `P201` alum, `P202` hypochlorite, `P203` fluoride (ChemPump); `LT201`,
  `LT202`, `LT203` tank levels.
- **Area 500, Filtration:** `Filter1`-`Filter4` (one-at-a-time backwash).
- **Area 600, Disinfection & Clearwell:** `AIT601` free chlorine, `AIT602` pH, `AIT603` turbidity, `LT601`.
- **Computed (scripts):** `Plant/TreatedVolumeTotal`, `Plant/TreatedVolumeShift`, `Plant/EnergyTotal`,
  `Plant/CoagulantConsumed`, `Plant/ShiftId`, `KPI/SpecificEnergy`, `KPI/TurbidityCompliancePct`,
  `KPI/ChlorineCompliancePct`, `Filtration/BackwashActiveFilter`.

Full point list: [IO-Register.md](../Specifications/IO-Register.md).

## Displays

Four area P&IDs plus a dashboard and home (Startup layout, Header / Menu / Content; Content opens MainPage):

| Display | Type | Shows |
|---|---|---|
| MainPage | Canvas | Project home page, plant overview / navigation. |
| Area100_RawWater | Canvas | Raw Water Intake P&ID, P101/P102, LT101, FT101, AIT101/102. |
| Area200_ChemFeed | Canvas | Chemical Feed P&ID, P201/202/203 metering pumps, LT201/202/203 tanks. |
| Area500_Filtration | Canvas | Filtration P&ID, Filter1-4, one-at-a-time backwash. |
| Area600_Disinfection | Canvas | Disinfection & Clearwell P&ID, AIT601/602/603, LT601. |
| PlantDashboard | Dashboard | Operations dashboard, headline quality gauges + trend, alarms, lab samples. |

System / layout pages (not operator content): `Header`, `HeaderMobile`, `HeaderPad`, `LogOn`, `SelectPage`.
One reusable display Symbol is defined.

## Alarms

Four groups: **Critical** (disinfection failure, SWTR violations, extremes), **Compliance** (TCEQ/EPA action
levels), **Warning** (operational), **AuditTrail**. 34 configured alarms:

| Tag | Group(s) | Conditions |
|---|---|---|
| Area100/AIT101 (raw turbidity) | Warning | Hi 15 NTU |
| Area100/AIT102 (raw pH) | Warning | Lo 6.0 |
| Area200/LT201 (coagulant) | Critical / Warning | LoLo 10 · Lo 15 |
| Area200/LT202 (hypochlorite) | Critical / Warning | LoLo 10 · Lo 15 |
| Area200/LT203 (fluoride) | Critical / Warning | LoLo 10 · Lo 15 |
| Area500/Filter1-4 .EffluentTurbidity | Compliance | Hi 0.15 · HiHi 0.5 NTU (each filter) |
| Area500/Filter1-4 .HeadLoss | Warning | Hi 8.0 PSI (backwash due) |
| Area600/AIT601 (free chlorine) | Critical / Compliance | LoLo 0.1 · Lo 0.2 · Hi 3.5 · HiHi 4.0 mg/L |
| Area600/AIT602 (finished pH) | Compliance | LoLo 6.0 · Lo 6.5 · Hi 8.5 · HiHi 9.0 |
| Area600/AIT603 (finished turbidity) | Critical / Compliance | Hi 0.3 · HiHi 1.0 NTU (SWTR violation) |
| Area600/LT601 (clearwell) | Critical / Warning | LoLo 15 · Lo 25 · Hi 95 · HiHi 98 % |

## Historian, datasets & reports

- **Historian:** 25 process variables (incl. pump MotorCurrent/SpeedFeedback, chem-pump DoseRate, per-filter
  HeadLoss/EffluentTurbidity) logged to `PlantHistory` with deadband. Target retention **≥ 365 days** for
  regulatory compliance.
- **Business data (`Business`, SQLite):** LIMS grab-samples, compliance log, shift summaries. Queries:
  `BusinessSchemaInit` (DDL), `InsertLabSample`, `LabSamplesRecent`, `ComplianceLogRecent`,
  `ShiftSummaryRecent`.
- **Report:** `ShiftComplianceReport`, per-shift treated volume, specific energy, turbidity/chlorine
  compliance %.
- **Scripts (server):** `FlowTotalizer`, `EnergyMeter`, `ChemicalConsumption`, `ComplianceMonitor`,
  `FilterBackwash` (one-at-a-time enforcement, trigger 8.0 PSI / clear 2.0 PSI), `ShiftKpiRollup`.

## Security

Role-based access, 4 users (`Administrator`, `User`, `Guest`, `MCP`), 8 policies, 24 permissions.
Administrator + operator roles. Log on via the `LogOn` screen.

## Versions & files

- **Solution:** `HighlandWTP` · FrameworX **10.1.5.2000**
- **Location:** `Sites/Example-HighlandWTP/Solutions/HighlandWTP.dbsln`
- **Source of truth:** `HMWTP-SPEC-2026-001 Rev C` + `Highland_WTP_Main.L5K` (staged in `Specifications/`).
- **External dependency:** SQLite (`Business`); ControlLogix PLC at `192.168.1.10` when live.

## Acceptance status

The commissioning record ships seeded (one pending row per IO-Register point), loop checks **not yet
executed or signed**. See [Commissioning-Record.md](Commissioning-Record.md).
