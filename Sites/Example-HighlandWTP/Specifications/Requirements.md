# Project Requirements: Highland Municipal Water Treatment Plant

What the solution must do. Source-driven from the Highland material (Lone Star Process Engineering
`HMWTP-SPEC-2026-001 Rev C` + the `Highland_WTP_Main.L5K` controller export, both staged in this folder).
Source of truth for "done."

## Purpose

A SCADA / HMI / Historian solution for the Highland Municipal Water Treatment Plant, a conventional surface
water treatment facility serving ~18,000 residents, design capacity **5 MGD**, average production **3.2 MGD**.
It monitors and visualizes the four process areas (Raw Water Intake, Chemical Feed, Filtration, Disinfection &
Clearwell), historizes every process variable for regulatory compliance, alarms on the TCEQ / EPA Surface Water
Treatment Rule limits, and computes operational KPIs. Closed-loop control stays in the plant ControlLogix PLC;
this solution is the operations, compliance-evidence, and historian layer over it. The first version runs the
PLC channel **disabled** with a tuned simulation channel driving live values, so the whole solution is built and
verified without field hardware, then re-pointed at the real controller by enabling the PLC channel.

## Functional

- **Acquire** all controller tags from the ControlLogix PLC (`192.168.1.10`, slot 0) 1:1 with the L5K database,
  3 equipment UserTypes (Pump, ChemPump, Filter) plus the analog instruments per area.
- **Simulate** the raw measurements for the hardware-free build: a ValueSimulator channel drives the analog
  process values with patterns tuned to sit inside the compliance bands.
- **Reflect plant control logic for monitoring** (the PLC owns the loops): coagulant (alum) dosing is
  flow-paced from FT101; pre-chlorine is operator-adjusted; fluoride is flow-paced with manual trim; filter
  backwash triggers at HeadLoss > **8.0 PSI** or operator command, ~15-minute cycle, **only one filter may
  backwash at a time** (the other three carry full flow).
- **Compute** the operational KPIs from the live tags (energy, treated volume, specific energy, chemical
  consumption, per-parameter compliance %), and roll them up per shift.

## Operational

- **Displays:** a plant dashboard (3×2: gauges row, then trend + active-alarm list + KPI datagrid), an area page
  per process area, and a populated home page wired into the Startup Content region.
- **Alarms:** three rationalized groups, **Critical** (disinfection failure, SWTR violations, extremes),
  **Compliance** (TCEQ / EPA action levels incl. per-filter turbidity), **Warning** (operational), mapped from
  the §4 compliance table.
- **Historian:** every analog process variable logged with deadband; digital status on-change; **minimum 1-year
  retention** for regulatory compliance.
- **Reports:** a shift compliance report.
- **Security:** administrator plus operator roles (the layout template seeds 4 users / 8 policies / 24
  permissions).

## KPIs / targets: water-quality compliance limits (TCEQ / EPA SWTR)

| Parameter | Tag | Warn Lo | Warn Hi | Crit Lo | Crit Hi | Unit |
|---|---|---|---|---|---|---|
| Finished water turbidity | AIT603 | n/a | 0.3 | n/a | 1.0 | NTU |
| Filter turbidity (each) | Filter[n].EffluentTurbidity | n/a | 0.15 | n/a | 0.5 | NTU |
| Free chlorine residual | AIT601 | 0.2 | 3.5 | 0.1 | 4.0 | mg/L |
| Finished water pH | AIT602 | 6.5 | 8.5 | 6.0 | 9.0 | n/a |
| Clearwell level | LT601 | 25 | 95 | 15 | 98 | % |
| Chemical tank levels | LT201 / LT202 / LT203 | 15 | n/a | 10 | n/a | % |

Derived KPIs: TreatedVolume (total + per shift), EnergyTotal, SpecificEnergy (kWh/m³), CoagulantConsumed,
TurbidityCompliancePct, ChlorineCompliancePct.

## Acceptance criteria

_Demonstrated and signed off in `Documentation/Commissioning-Record.md` (ships seeded, pending execution);
the machine-checkable subset lives in `Tests/expected.json` (contract: `Solution-Spec.md` §8)._

- [ ] UNS mirrors the controller database: 3 equipment UserTypes and 20 area tags across the four ISA-95 areas,
      PLC-faithful leaf names (P101…, AIT601…, Filter1-4).
- [ ] The compliance limits above are configured as alarms in the three groups.
- [ ] Every analog process variable is historized with deadband; retention ≥ 365 days.
- [ ] With the simulation channel running, the sim → device → script → KPI chain computes live with good
      quality (e.g. SpecificEnergy = EnergyTotal ÷ TreatedVolume), and a compliance % reads 100% inside the band.
- [ ] Forcing a parameter out of its compliance band raises the corresponding Critical/Compliance alarm.
