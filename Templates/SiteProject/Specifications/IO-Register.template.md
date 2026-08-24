# Hardware / IO Register: <ProjectName>

The point list that drives the solution design, every signal mapped to its UNS tag. Populated by
`new-project-bootstrap` from an interview or a pasted instrument index; edit directly anytime.

> **How it's used:** UNS authoring reads this to create tags, UserTypes, and device channels; commissioning
> reads it to know what to loop-check. Keep **Target UNS Tag** in PascalCase following your area/equipment
> hierarchy: see `KnowledgeBase/Conventions/UNS-Naming.md`.

| Tag ID | Description | Type | Protocol·Device | Address | Units | Range | Alarm Limits | Target UNS Tag |
|---|---|---|---|---|---|---|---|---|
| _(your points here)_ | | | | | | | | |

Type = AI / AO / DI / DO. Leave unknown cells blank rather than guessing.
