# Convention: UNS Naming

How tag paths are named in this workspace, applied on every project. The IO register's **Target UNS Tag**
column follows this.

## Shape

`<Area>/<Equipment>/<Signal>`: slash-separated folders, PascalCase at every level.

- **Area**: the plant area or process section: `WaterTreatment`, `Inlet`, `Clarifier`, `Filter`, `Clearwell`, `Outlet`.
- **Equipment**: the unit or loop, when it helps: `Pump1`, `DosingPump`, `InletValve`. Omit when the signal sits directly on an area.
- **Signal**: the measured or actuated quantity: `Level`, `RawFlow`, `pH`, `Turbidity`, `RunCmd`, `RunFeedback`.

Examples:
```
WaterTreatment/Clarifier/Level
WaterTreatment/Dosing/CoagulantSpeed
WaterTreatment/Filter/InletValveCmd
WaterTreatment/Clearwell/ChlorineResidual
```

## Rules

- **PascalCase, no spaces, no underscores.** `RawFlow`, not `raw_flow` or `Raw Flow`.
- **Commands vs feedback are distinct signals**: `...Cmd` (output) and `...Feedback` / `...Fb` (input).
- **Units live in the tag's engineering-unit property**, not the name. The name says *what*, not *how measured*.
- **Match the instrument index where practical**: but the UNS path is for operators and the data model, so
  prefer readable area/equipment names over raw instrument tags (keep the instrument tag in the IO register).

When an external system (a corporate ontology, an asset-framework hierarchy) imposes names, translate at the
boundary: keep this convention inside FrameworX.
