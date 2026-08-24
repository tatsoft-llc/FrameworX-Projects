# Decision: UNS uses the flattened area hierarchy with PLC-faithful leaves

**Date:** 2026-06-01 (revisited 2026-07-02, reaffirmed at ship)
**Status:** Accepted. This is the form the shipped solution embodies
**Scope:** Highland WTP UNS / asset-tree structure (drives Layer 1 authoring)

## Decision

The Highland WTP Unified Namespace is authored in the **flattened area-hierarchy form** the IO-Register
targets:

```
Highland/<Area###_Name>/<Leaf>
  e.g.  Highland/Area100_RawWater/P101
        Highland/Area500_Filtration/Filter1/HeadLoss
        Highland/Area600_Disinfection/AIT601
```

- Area folders carry the plant's own area numbering (`Area100_RawWater` … `Area600_Disinfection`).
- Leaf names stay **PLC-faithful** (`P101`, `AIT601`, `Filter1-4`) so the UNS mirrors the L5K controller
  tag database; instrument descriptions carry the human names.
- Equipment classes `Pump` / `ChemPump` / `Filter` are FrameworX UserTypes; instances are the leaves.
- `Plant/*` and `KPI/*` are **site-level derived** nodes (script-computed), segregated from the
  acquired-equipment branch.

## Why

- One tree serves both audiences: operators navigate by plant area; engineers match tags 1:1 against the
  controller database.
- Fewer levels = shorter paths in displays, scripts, and alarms for a single-site plant.
- The spec, IO-Register "Target UNS Tag" column, and the built solution all agree. The contract and the
  build stay checkable against each other.

## Alternative evaluated: strict ISA-95 (IEC 62264) 5-level equipment hierarchy

```
Enterprise  Highland
  Site        HighlandWTP
    Area        RawWaterIntake | ChemicalFeed | Filtration | DisinfectionClearwell
      ProdUnit    IntakePumping | Dosing | FilterBank | Disinfection | Clearwell
        Unit        P101 | P201 | Filter1 | AIT601
```

Standards-faithful (every level declares its ISA-95 role) and a clean growth path for multi-site or
multi-train expansion: but for a single plant it adds two levels of path depth whose roles are implicit
anyway, and it would put the tree out of agreement with the IO-Register until every spec surface is
re-targeted. **If this project grows to multiple sites or trains, migrate to this form deliberately:
update `IO-Register.md` (Target UNS Tag column) and `Solution-Spec.md` §3.2/§8 first, then re-author
Layer 1: the contract moves before the build does.**

## Consequence

Any future hierarchy change is a contract change: spec and register update **before** authoring, so
`run-tests` and the build never disagree about path shape.
