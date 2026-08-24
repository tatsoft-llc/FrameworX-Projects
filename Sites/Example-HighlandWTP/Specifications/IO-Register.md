# Hardware / IO Register: Highland Municipal Water Treatment Plant

The point list that drives the solution design, every controller signal mapped to its UNS tag. Transcribed
1:1 from `Highland_WTP_Main.L5K` (controller tags) and the §3 equipment list in `HMWTP-SPEC-2026-001 Rev C`.

> **How it's used:** UNS authoring reads this to create tags, UserTypes, and device channels; commissioning
> reads it to know what to loop-check. Target UNS Tag is PascalCase in the ISA-95 area hierarchy
> (`Highland/<Area>/<Leaf>`): see `KnowledgeBase/Conventions/UNS-Naming.md`. Leaf names are kept PLC-faithful
> (P101, AIT601, Filter1-4) so the UNS mirrors the controller tag database.

**Source data path (two channels):** `PLC_Main` = Allen-Bradley ControlLogix (`192.168.1.10`, slot 0), one
point per controller tag, **InitialState = Disabled** for the hardware-free build. `SimChannel` = ValueSimulator,
**Enabled**, driving the analog measurements with SINE patterns tuned inside the compliance bands. Enable
`PLC_Main` (and disable / detune `SimChannel`) to re-point at the real plant.

## Area 100: Raw Water Intake

| Tag ID | Description | Type | Address (PLC tag) | Units | Range | Alarm Limits | Target UNS Tag |
|---|---|---|---|---|---|---|---|
| P101 | Raw Water Pump 1, 100 HP VFD, 2500 GPM | UDT Pump | `DATATYPE:P101` | n/a | n/a | Fault → Warning | `Highland/Area100_RawWater/P101` |
| P102 | Raw Water Pump 2, 100 HP VFD, standby | UDT Pump | `DATATYPE:P102` | n/a | n/a | Fault → Warning | `Highland/Area100_RawWater/P102` |
| FT101 | Raw water flow | AI | `REAL:FT101` | GPM | 0-5000 | n/a | `Highland/Area100_RawWater/FT101` |
| AIT101 | Raw water turbidity (Hach 1720E) | AI | `REAL:AIT101` | NTU | 0-100 | n/a | `Highland/Area100_RawWater/AIT101` |
| AIT102 | Raw water pH (Hach pHD sc) | AI | `REAL:AIT102` | n/a | 0-14 | n/a | `Highland/Area100_RawWater/AIT102` |
| LT101 | Intake wet-well level | AI | `REAL:LT101` | % | 0-100 | n/a | `Highland/Area100_RawWater/LT101` |

## Area 200: Chemical Feed

| Tag ID | Description | Type | Address (PLC tag) | Units | Range | Alarm Limits | Target UNS Tag |
|---|---|---|---|---|---|---|---|
| P201 | Coagulant pump, alum (flow-paced) | UDT ChemPump | `DATATYPE:P201` | n/a | n/a | Fault → Warning | `Highland/Area200_ChemFeed/P201` |
| P202 | Pre-chlorine pump, NaOCl (operator) | UDT ChemPump | `DATATYPE:P202` | n/a | n/a | Fault → Warning | `Highland/Area200_ChemFeed/P202` |
| P203 | Fluoride pump, H₂SiF₆ (flow-paced + trim) | UDT ChemPump | `DATATYPE:P203` | n/a | n/a | Fault → Warning | `Highland/Area200_ChemFeed/P203` |
| LT201 | Coagulant tank level (2500 gal) | AI | `REAL:LT201` | % | 0-100 | Warn Lo 15 / Crit Lo 10 | `Highland/Area200_ChemFeed/LT201` |
| LT202 | Hypochlorite tank level (5000 gal) | AI | `REAL:LT202` | % | 0-100 | Warn Lo 15 / Crit Lo 10 | `Highland/Area200_ChemFeed/LT202` |
| LT203 | Fluoride tank level (1500 gal) | AI | `REAL:LT203` | % | 0-100 | Warn Lo 15 / Crit Lo 10 | `Highland/Area200_ChemFeed/LT203` |

## Area 500: Filtration (four dual-media gravity filters)

Backwash trigger: `HeadLoss` > 8.0 PSI or operator-initiated; ~15-min cycle; only one filter at a time.

| Tag ID | Description | Type | Address (PLC tag) | Units | Range | Alarm Limits | Target UNS Tag |
|---|---|---|---|---|---|---|---|
| Filter1 | Gravity Filter 1 (HeadLoss, EffluentTurbidity, valve, status) | UDT Filter | `DATATYPE:Filter[0]` | mixed | n/a | Turbidity Warn Hi 0.15 / Crit Hi 0.5 NTU | `Highland/Area500_Filtration/Filter1` |
| Filter2 | Gravity Filter 2 | UDT Filter | `DATATYPE:Filter[1]` | mixed | n/a | Turbidity Warn Hi 0.15 / Crit Hi 0.5 NTU | `Highland/Area500_Filtration/Filter2` |
| Filter3 | Gravity Filter 3 | UDT Filter | `DATATYPE:Filter[2]` | mixed | n/a | Turbidity Warn Hi 0.15 / Crit Hi 0.5 NTU | `Highland/Area500_Filtration/Filter3` |
| Filter4 | Gravity Filter 4 | UDT Filter | `DATATYPE:Filter[3]` | mixed | n/a | Turbidity Warn Hi 0.15 / Crit Hi 0.5 NTU | `Highland/Area500_Filtration/Filter4` |

Filter UDT members: `InService` (DI), `Backwashing` (DI), `HeadLoss` (AI, 0-10 PSI), `EffluentTurbidity`
(AI, 0-5 NTU), `ValvePosition` (AI, 0-100 %), `TimeSinceBackwash` (AI, h), `BackwashCount` (DINT).

## Area 600: Disinfection & Clearwell

| Tag ID | Description | Type | Address (PLC tag) | Units | Range | Alarm Limits | Target UNS Tag |
|---|---|---|---|---|---|---|---|
| AIT601 | Free chlorine residual (Hach CL17sc) | AI | `REAL:AIT601` | mg/L | 0-10 | Warn Lo 0.2 / Hi 3.5 · Crit Lo 0.1 / Hi 4.0 | `Highland/Area600_Disinfection/AIT601` |
| AIT602 | Finished water pH (Hach pHD sc) | AI | `REAL:AIT602` | n/a | 0-14 | Warn Lo 6.5 / Hi 8.5 · Crit Lo 6.0 / Hi 9.0 | `Highland/Area600_Disinfection/AIT602` |
| AIT603 | Finished water turbidity (Hach TU5400sc) | AI | `REAL:AIT603` | NTU | 0-5 | Warn Hi 0.3 / Crit Hi 1.0 | `Highland/Area600_Disinfection/AIT603` |
| LT601 | Clearwell level (0.5 MG, ultrasonic) | AI | `REAL:LT601` | % | 0-100 | Warn Lo 25 / Hi 95 · Crit Lo 15 / Hi 98 | `Highland/Area600_Disinfection/LT601` |

**Totals:** 20 controller points (9 UDT instances, 2 Pump, 3 ChemPump, 4 Filter, + 11 analog). Derived
KPI/Plant tags (TreatedVolume, EnergyTotal, SpecificEnergy, compliance %, ShiftId, …) are computed by scripts,
not acquired: see `Solution-Spec.md` §3 and the ChangeLog.

Type = AI / AO / DI / DO; UDT instances carry mixed-type members (listed per type above).
