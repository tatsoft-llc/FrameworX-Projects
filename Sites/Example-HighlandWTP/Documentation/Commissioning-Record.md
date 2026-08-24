# Commissioning Record: Highland Municipal Water Treatment Plant

The verifiable deliverable a chat transcript can't produce: per-point evidence that the system works. For
each point, Claude drives the tag with `set_object_value` and reads it back. The response carries the
post-write value, **quality** (Good / Uncertain / Bad), and **timestamp**. And records the result here.
Forcing a *physical* field input (real sensor / wired loop) is a manual site step; note it in "By" when done by hand.

> Seeded from `Specifications/IO-Register.md` with one row per IO-Register point (status: pending).
> UDT instances (Pump / ChemPump / Filter) are loop-checked member-by-member; add member rows as they run.

## Loop checks

| Target UNS Tag | Expected | Written | Read-back | Quality | Timestamp | Result | By | Date |
|---|---|---|---|---|---|---|---|---|
| `Highland/Area100_RawWater/P101` | | | | | | pending | | |
| `Highland/Area100_RawWater/P102` | | | | | | pending | | |
| `Highland/Area100_RawWater/FT101` | | | | | | pending | | |
| `Highland/Area100_RawWater/AIT101` | | | | | | pending | | |
| `Highland/Area100_RawWater/AIT102` | | | | | | pending | | |
| `Highland/Area100_RawWater/LT101` | | | | | | pending | | |
| `Highland/Area200_ChemFeed/P201` | | | | | | pending | | |
| `Highland/Area200_ChemFeed/P202` | | | | | | pending | | |
| `Highland/Area200_ChemFeed/P203` | | | | | | pending | | |
| `Highland/Area200_ChemFeed/LT201` | | | | | | pending | | |
| `Highland/Area200_ChemFeed/LT202` | | | | | | pending | | |
| `Highland/Area200_ChemFeed/LT203` | | | | | | pending | | |
| `Highland/Area500_Filtration/Filter1` | | | | | | pending | | |
| `Highland/Area500_Filtration/Filter2` | | | | | | pending | | |
| `Highland/Area500_Filtration/Filter3` | | | | | | pending | | |
| `Highland/Area500_Filtration/Filter4` | | | | | | pending | | |
| `Highland/Area600_Disinfection/AIT601` | | | | | | pending | | |
| `Highland/Area600_Disinfection/AIT602` | | | | | | pending | | |
| `Highland/Area600_Disinfection/AIT603` | | | | | | pending | | |
| `Highland/Area600_Disinfection/LT601` | | | | | | pending | | |

## Outstanding items
- All 20 points pending: the example ships with the record seeded, not executed. Run the
  `commission-the-points` skill against the live solution to fill it.

## Acceptance / sign-off

| Role | Name | Signature | Date |
|---|---|---|---|
| Commissioning engineer | | | |
| Customer representative | | | |

*An automated "PASS" is evidence, not acceptance, a named human signs off.*
