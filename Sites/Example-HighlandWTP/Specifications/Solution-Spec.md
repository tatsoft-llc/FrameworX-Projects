# Solution spec: Highland Municipal Water Treatment Plant

> The whole-solution design input. Reproduces the published Highland example (docs.tatsoft.com page 200704150)
> source-faithfully from the staged PDF + L5K, plus an enrichment superset (business datasets, KPI scripts,
> reports) and live verification. v1 is simulation-driven; the PLC channel is built but disabled.

## 1. Intent

Give Highland's operators and compliance staff a single SCADA/HMI/Historian solution over the plant
ControlLogix PLC: live process views for the four areas, TCEQ/EPA compliance alarming and 1-year historian
evidence, and operational KPIs (energy, throughput, specific energy, compliance %). Ambitious goal: a
commission-grade municipal-water solution with the evidence to prove it. Simplest first version: build the
full data foundation + monitor + business layers against a tuned simulation, verify the live KPI chain, then
re-point at the real controller by enabling one channel.

## 2. Target and profile

- **Field hardware:** Allen-Bradley ControlLogix `1756-L8X` @ `192.168.1.10` slot 0 (see `Hardware-Spec.md`);
  channel built but **disabled** in v1, with a ValueSimulator channel driving live values.
- **Runtime host:** see `Hardware-Spec.md`.
- **Build and test profile:** Development (TServer 3201). Production configured, not the build target.
- **Sandbox name for testing:** `ai-test-highland-wtp`

## 3. Data foundation

### 3.1 UserTypes (UDTs): mapped 1:1 from the L5K DATATYPEs

| UserType | Member | Type | Unit | Range | Notes |
|---|---|---|---|---|---|
| `Pump` | Running, Fault, Ready, AutoManual | Digital (int 0/1) | | | feedback + mode |
| `Pump` | SpeedCmd, SpeedFeedback | Double | % | 0..100 | VFD |
| `Pump` | MotorCurrent | Double | A | | |
| `Pump` | RunHours | Double | h | | totalizer |
| `ChemPump` | Running, Fault, AutoManual, FlowPaced | Digital (int 0/1) | | | |
| `ChemPump` | DoseRate, DoseSetpoint | Double | mL/min | | |
| `ChemPump` | TankLevel | Double | % | 0..100 | |
| `ChemPump` | TotalChemUsed | Double | gal | | totalizer |
| `Filter` | InService, Backwashing | Digital (int 0/1) | | | |
| `Filter` | HeadLoss | Double | PSI | 0..10 | backwash trigger > 8.0 |
| `Filter` | EffluentTurbidity | Double | NTU | 0..5 | compliance |
| `Filter` | ValvePosition | Double | % | 0..100 | |
| `Filter` | TimeSinceBackwash | Double | h | | |
| `Filter` | BackwashCount | Integer | | | cumulative |

> Digital members are **int 0/1**, not bool. Script assignments use ternary, not boolean.

### 3.2 UNS and Asset Tree

```
Highland/
  Area100_RawWater/    P101, P102 (Pump); FT101, AIT101, AIT102, LT101
  Area200_ChemFeed/    P201, P202, P203 (ChemPump); LT201, LT202, LT203
  Area500_Filtration/  Filter1..Filter4 (Filter)
  Area600_Disinfection/ AIT601, AIT602, AIT603, LT601
  Plant/               ShiftId, TreatedVolume (Total/Shift), EnergyTotal, CoagulantConsumed
  KPI/                 SpecificEnergy, TurbidityCompliancePct, ChlorineCompliancePct
```

- **Area tags:** 20 (9 UDT instances + 11 analog), PLC-faithful leaf names mirroring the controller database.
- **Derived tags:** 9 KPI/Plant tags (script-computed).
- **Asset tree root:** `Highland`, with the four ISA-95 area folders.

## 4. Connect

- **Mode:** dual source. `PLC_Main` (ControlLogix, **disabled** in v1) maps 20 points 1:1 to the L5K
  (`DATATYPE:` for UDTs, `Filter[0..3]` array, `REAL:` for analogs). `SimChannel` (ValueSimulator, **enabled**)
  drives 25 analog measurements with SINE patterns tuned inside the compliance bands.
- **Tags that must hold live, moving values in runtime:** the raw and finished analogs (e.g. `AIT603`,
  `AIT601`, `FT101`) and the derived KPIs (`KPI/SpecificEnergy`, `KPI/TurbidityCompliancePct`).

## 5. Monitor

### 5.1 Alarms: 34 items, 3 rationalized groups (from the §4 compliance table)

| Group | Covers |
|---|---|
| `Critical` | disinfection failure, SWTR violations, extreme deviations |
| `Compliance` | TCEQ/EPA action levels, incl. per-filter turbidity |
| `Warning` | operational (pump faults, chemical tank lows) |

Limits per `Requirements.md` (AIT603 0.3/1.0 NTU; AIT601 0.2/3.5/0.1/4.0 mg/L; AIT602 6.5/8.5/6.0/9.0;
LT601 25/95/15/98 %; chem tanks 15/10 % lo; per-filter turbidity 0.15/0.5 NTU).

- **Expected alarm item count:** 34.  **Groups:** 3.

### 5.2 Historian

| Table | Trigger | Deadband | Retention |
|---|---|---|---|
| `PlantHistory` | SaveOnChange | 60 s time + 1 % value | 365 days |

- **Expected historian tag count:** 25.  **Tables:** 1.

## 6. Screens (Pillar 4: the target set)

| Display | Shows | Key controls |
|---|---|---|
| `Dashboard` | plant at a glance | **3×2**, gauges row (turbidity, chlorine, pH, clearwell); trend + active-alarm list + KPI datagrid row. `PanelType=Dashboard`. |
| Area pages (×4) | each process area | symbol per pump/filter/instrument, area alarms |
| `Home` | landing | wired into the **Startup Content** region (not the template default) |

- **Expected display count:** 6 (1 dashboard + 4 area pages + 1 home). Build with the `display-authoring-loop`.

## 7. Security

- **Users / roles:** administrator + operator roles (layout template seeds 4 users / 8 policies / 24 perms).

## 8. Acceptance checks (the contract for `Tests/expected.json`)

- [ ] The solution defines exactly 3 domain UserTypes: `Pump`, `ChemPump`, `Filter`.
- [ ] The UNS exposes 20 area tags across the four `Area*` folders (9 UDT instances) plus the derived
      `Plant/*` and `KPI/*` tags; asset-tree root `Highland`.
- [ ] 34 alarms exist across 3 groups (Critical / Compliance / Warning).
- [ ] 25 historian tags log into 1 table (`PlantHistory`), retention ≥ 365 days.
- [ ] 6 displays exist, including a `PanelType=Dashboard` dashboard wired into Startup Content.
- [ ] At least 4 users are defined.
- [ ] In the running runtime, `KPI/SpecificEnergy` holds a good-quality value equal to
      `Plant/EnergyTotal ÷ Plant/TreatedVolume/Total` within tolerance, timestamp recent.
- [ ] `KPI/TurbidityCompliancePct` reads 100 % while the simulation holds AIT603 inside its band.
- [ ] Forcing AIT603 above 1.0 NTU raises the Critical finished-water-turbidity alarm.
