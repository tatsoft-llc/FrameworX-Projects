# Commissioning Record: <ProjectName>

The verifiable deliverable a chat transcript can't produce: per-point evidence that the system works. For
each point, Claude drives the tag with `set_object_value` and reads it back. The response carries the
post-write value, **quality** (Good / Uncertain / Bad), and **timestamp**. And records the result here.
Forcing a *physical* field input (real sensor / wired loop) is a manual site step; note it in "By" when done by hand.

> Seeded by `new-project-bootstrap` with one row per IO-Register point (status: pending).

## Loop checks

| Target UNS Tag | Expected | Written | Read-back | Quality | Timestamp | Result | By | Date |
|---|---|---|---|---|---|---|---|---|
| _(one row per IO point)_ | | | | | | pending | | |

## Outstanding items
-

## Acceptance / sign-off

| Role | Name | Signature | Date |
|---|---|---|---|
| Commissioning engineer | | | |
| Customer representative | | | |

*An automated "PASS" is evidence, not acceptance, a named human signs off.*
