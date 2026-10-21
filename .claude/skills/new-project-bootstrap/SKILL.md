---
name: new-project-bootstrap
description: >-
  Set up a new FrameworX automation project from scratch via a short interview. Use at the start of a NEW
  project, when the user says "set up a project for my <plant/skid/line>", "new FrameworX project", "start a
  solution for ...", "bootstrap this project". Creates Sites/<Name>/ from Templates/SiteProject/, interviews
  for site/scope, hardware/IO, and requirements; writes Specifications/Requirements.md +
  Specifications/IO-Register.md; creates the FrameworX solution into Solutions/ via the Designer/Console MCP;
  seeds Documentation/Commissioning-Record.md and the per-author ChangeLogs/; then hands off to UNS authoring
  and commissioning. Do NOT use for an existing project that already has a folder under Sites/. Go straight
  to authoring there.
license: Apache-2.0
metadata:
  author: Marc Taccolini
  version: "1.0.0"
---

# new-project-bootstrap

Turns a request into a started project folder under `Sites/<Name>/`, captured IO list, written
requirements, a created solution, and a commissioning skeleton, in one guided pass.

## Before you start: bootstrap the platform

Your first action is ALWAYS to connect to the installed FrameworX through the Designer (or Console) MCP
(`list_solutions` / `open_solution` / `create_solution`). That returns the platform mental model (Four
Pillars, UNS, object schemas, naming, syntax). Everything below assumes it is loaded. Never paraphrase
platform knowledge from memory: the product just gave it to you.

## Step 1: Create the project folder

- Ask for the project / site name. Copy the `Templates/SiteProject/` skeleton into `Sites/<Name>/`, then
  rename the `*.template.md` files to their working names (`Specifications/Requirements.md`,
  `Specifications/IO-Register.md`, `Documentation/Commissioning-Record.md`). In `ChangeLogs/`, rename
  `ChangeLog-AUTHOR.template.md` to `ChangeLog-<your-login>.md`: one file per contributor, per
  `KnowledgeBase/Conventions/ChangeLog-Convention.md`.
- Open your `ChangeLogs/ChangeLog-<login>.md` with a first dated entry: "Project bootstrapped."

## Step 2: Project & scope (short)

Ask in one batch; accept partial answers:
- One-line description of what the project controls or monitors.
- Deployment size: small-but-critical / medium / large. (Sets rigor, not a different process.)
- Target FrameworX version (default: the installed one).
- Who signs off commissioning (name / role).

→ Set the model tier: **balanced** for routine; escalate to **most-capable** for large or
safety/availability-critical scope (see `CLAUDE.md` → "Model tiers").

## Step 3: Hardware / IO

Either **interview** point-by-point or invite the user to **paste** their IO list / instrument index in any
format and normalize it. Per point (leave unknowns blank, do not invent): instrument/tag ID, description,
signal type (AI/AO/DI/DO), protocol & device/channel, address, units, range, scaling, alarm limits, and the
**target UNS tag path** (PascalCase, area/equipment hierarchy; confirm with the user, check
`KnowledgeBase/Conventions/UNS-Naming.md` for the house convention).

→ Write into `Sites/<Name>/Specifications/IO-Register.md`.

## Step 4: Requirements

Capture briefly: purpose; functional behaviors (loops, sequences, interlocks); operational needs (Displays,
alarms, trends, reports, roles); KPIs; acceptance criteria.

→ Write into `Sites/<Name>/Specifications/Requirements.md`.

## Step 5: Create the solution & seed commissioning

- Create the FrameworX solution via `create_solution`, name it after the project, target the project's
  `Solutions/` folder (or the user's normal solutions location; record where in `Solutions/README.md`).
  **This is the customer's REAL solution, not a sandbox.**
- Seed `Documentation/Commissioning-Record.md` with one row per IO point (status: pending).

## Step 6: Confirm, log & route

- Summarize what was created (IO points, requirements sections, solution name/path) and append it to your `ChangeLogs/ChangeLog-<login>.md`.
- Route to next: **author the UNS** from the IO register → **build Displays** → **commission** point-by-point
  (drive each tag with `set_object_value`, read back value + quality + timestamp, record in the commissioning record).

## Notes

- Don't over-collect. A small skid needs the IO register + a handful of requirements; a large plant fills
  more. Capture what the user has, mark the rest TODO, move on.
- A trick that will help future projects → capture it in `KnowledgeBase/`, not buried in one project.
- If something the project needs isn't reachable through the MCP, say so plainly.
