# Security baseline: roles before screens, verified by logon

Minimum security posture for a delivered solution. The Security module's exact tables and fields come
from `get_table_schema('Security')` on your build: this file carries the decisions and the verification
bar, not the schema. (The *bridge* security model, plain HTTP with an API key for network clients from
10.1.6, network as the boundary, is separate: `Method/mcp-setup.md` § auth model.)

## Decide the roles first

Define the role set with the customer before authoring users or scoping a single display. The durable
default is three: **Operator** (view + acknowledge + normal setpoints), **Supervisor** (plus shelving,
wider setpoint ranges), **Engineer** (plus configuration surfaces). Map each requirement in
`Specifications/Requirements.md` to a role; record deviations in `Decisions/`.

- Users get roles; displays, commands, and setpoint writes get scoped to roles. Never per-user
  permissions (they don't survive staff turnover).
- One shared "operator" account is common in plants; if the customer wants per-person accountability
  (who acked what), that's per-user accounts. Ask, don't assume.
- Never ship the delivered solution with a default/blank engineering password, and never store real
  credentials in this repo's files (specs, ChangeLogs, Decisions included).

## FrameworX specifics observed at 10.1.5: verify on your build

- **User passwords are set in the Designer UI**, not over the MCP write surface, plan a human step for
  credential provisioning; the AI can author users/roles but not their secrets.
- A **minimum password length policy** applies (observed ~6). Seed passwords at or above that length and
  confirm with a logon: a shorter one is accepted at write time and only surfaces as a failed logon.
- A Designer engineering logon (`designer_action` logon) is an **engineering-session identity only**: it
  does not make runtime clients or server-side queries execute as that user. Per-role behavior must be
  verified where it runs (see below). If the solution's data layer enforces per-user row security in an
  external database, certify it at the database layer with the real mechanism, not via the Designer logon.

## The verification bar

Role scoping is only done when **each role has been exercised live**: log on to the runtime client (web
client is the cheap path) as one user per role and confirm. The screens/commands that must be hidden or
denied ARE, and the allowed ones work. A configured permission row is config; a denied button under an
Operator logon is evidence. Record the per-role check in the commissioning record like any other point.

## Anti-patterns

- Scoping displays before the role model is agreed. Every later role change re-opens every screen.
- Testing security "by analogy": one role verified says nothing about the others (§ Verify each path).
- Leaving engineering access in the operator role "temporarily" for commissioning and shipping it.
- Credentials in prompts, specs, or logs. If one leaks into a session artifact, rotate it.
