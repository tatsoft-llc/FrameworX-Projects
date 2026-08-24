---
name: project-handover-docs
description: >-
  Generate the concise handover document set for a FrameworX project, a System Handover (as-built summary)
  and an Operator Manual, into the project's Sites/<Name>/Documentation/ folder. Reads the LIVE solution for
  every factual section (UNS tags, displays, device channels, alarms, version) and interviews the user only
  for the intent config cannot reveal (screen purpose, alarm-response procedure, support contacts, backup
  schedule, safety notes). Use when the user wants the customer-facing deliverable documentation for a
  project. Trigger phrases include "generate the project docs", "create the handover package", "write the
  operator manual", "as-built documentation", "what do I hand the client". CRITICAL scope rules: VERIFY EACH
  PATH (never describe a display or alarm by analogy, enumerate the actual ones); NEVER overwrite
  Documentation/Commissioning-Record.md or anything under Specifications/; stay concise, two documents by
  default. Anti-overengineering is a hard requirement.
license: Apache-2.0
metadata:
  author: Marc Taccolini
---

# Project Handover Docs: concise end-user / integrator documentation

## What this is for

An integrator finishes a FrameworX solution and has to hand the customer documentation: *what was built* and
*how to run it*. This skill generates that deliverable set from the **live solution**. Pulling the facts
that are knowable from config, and asking the user only for the intent that isn't.

It is **not** a documentation framework. The bias is toward the smallest set an integrator can hand a client
and have it be useful, the standard small-project handover minimum, not an enterprise binder. (The product
documentation's system-integrator guidance is the reference. Find it via `search_docs`; its own rule of
thumb, documentation around 15% of development effort, is a sanity *ceiling*, not a target.)

## What it produces (default: two documents)

Both land in `Sites/<Name>/Documentation/` as Markdown.

| Document | Audience | One-line contents |
|---|---|---|
| `System-Handover.md` | The end-user's engineer / IT: and the next integrator | As-built summary: what the system does, topology, the tag/UNS register, device channels, displays, alarms, versions, and a link to the commissioning record. |
| `Operator-Manual.md` | Day-to-day operators | How to start and log in, a one-paragraph guide per screen, alarm response, routine tasks, backup & who-to-call. |

Optional, **only if the user asks**: `Training-QuickReference.md`, a one-page cheat sheet. Do not generate
it by default. Offer it; don't produce it unprompted.

**House style:** clean, useful, to the point, objective, correct. Lead each doc with a one-line summary.
Headings: `##` sections, `###` subsections only, no deeper.

## Pull from the live solution vs. ask the user

State this split to the user up front, so they know what you'll interview them on.

| **Pull live** (factual, read it, don't ask) | **Ask the user** (intent, config can't know it) |
|---|---|
| Solution name, FrameworX version, file location (`get_solution_info`) | Operational *purpose* of each screen (one line each) |
| UNS asset tree, tag count, UserTypes/UDTs (`browse_object_model`, `search_uns`) | Alarm **response procedure** per alarm / priority |
| Device channels, protocols, addresses (`list_protocols`, channel tables) | Who to call for support; escalation contacts |
| Display list + navigation tree (`get_display_tree`, DisplaysList) | Backup schedule / restore responsibility |
| Alarm definitions + priorities (alarm tables) | Site-specific safety notes |
| Commissioning results (read `Commissioning-Record.md`, link, never inline) | Routine shift tasks not derivable from screens |

## Workflow

1. **Frame & scope.** Confirm which project under `Sites/`. State the 2-document default and the
   pull-vs-ask split in one line. Confirm before writing: don't surprise the user with files.
2. **Ground.** Bootstrap the FrameworX MCP (`open_solution`) per the workspace rule. Read
   `Specifications/Requirements.md` and `Specifications/IO-Register.md` (the design inputs: reference
   them, don't restate them wholesale). Skim `Decisions/` for the why, so the manual can link out
   instead of re-deriving.
3. **Pull the live facts.** Enumerate the actual tags, displays, channels, and alarms from the running
   solution. This is the as-built: it must match reality, not the spec's intent.
4. **Short interview, intent only, one topic at a time.** Walk the ask-user column. Keep it tight:
   one screen's purpose, one alarm's response, etc. If the user doesn't have an answer, write a clearly
   marked `> TODO:` placeholder, **never fabricate** a procedure or a contact.
5. **Write into `Documentation/`.** Use the templates below. Link to `Commissioning-Record.md` for
   acceptance status: do not copy its contents and do not touch that file. Do not touch `Specifications/`.
6. **Verify each path + read back.** Confirm the files were written. Cross-check that the display list,
   alarm list, and tag/asset summary in the docs match the live solution exactly. A screen described
   "by analogy" to a sibling is a defect (the workspace "Verify each path" rule in `CLAUDE.md`). Two
   near-identical screens still get two enumerated entries.
7. **Log.** Add a line to `ChangeLogs/ChangeLog-<user>.md`: which docs were generated and from which
   solution build.

## Anti-overengineering guardrails (hard rules)

- **Two documents by default.** A third only on explicit request. Never spin up a folder of templates.
- **One screen = a few lines**, not a page. One alarm = name, priority, one-line response. Brevity is the
  product.
- **Don't invent.** If a fact isn't in the solution and the user didn't supply it, mark it `> TODO:` and
  move on. A short honest doc beats a padded fictional one.
- **Don't duplicate what exists.** Requirements/IO live in `Specifications/`; acceptance lives in
  `Commissioning-Record.md`; the why lives in `Decisions/`. Link, don't re-author.
- **It's a real solution.** Read it back; the as-built must be true on the day it's written.
- **`Commissioning-Record.md` is read-only to this skill.** The record is owned by the commissioning pass
  (`commission-the-points` skill), seeded at bootstrap, filled by commissioning, never overwritten by
  handover docs; link to it, never regenerate or edit it.

## Document templates

Replace every `[bracketed]` note with pulled-live or asked content. Keep prose tight.

### `System-Handover.md`

```markdown
# [Project]: System Handover

[One-line summary: what this solution is and who it's for.]

## System overview
[One paragraph from Requirements.md: purpose, site/scope, what it controls or shows.]

## Architecture & topology
[Runtime / clients / historian. Device channels with protocol + address: enumerate the real ones.]

## Tag / UNS register
[Asset tree summary + tag count. UserTypes/UDTs. Link to IO-Register.md for the full list.]

## Displays
[Each screen, one line: name: what it shows. Plus the navigation hierarchy. Enumerate ALL of them.]

## Alarms
[Each configured alarm: name, priority, condition. Enumerate the real ones.]

## Versions & files
[Solution name, FrameworX version, .dbsln location, key external dependencies (DB, LLM endpoint…).]

## Acceptance status
[One line + link to Documentation/Commissioning-Record.md. Do not inline the record.]
```

### `Operator-Manual.md`

```markdown
# [Project]: Operator Manual

[One-line summary: the day-to-day guide for operating this system.]

## Starting & accessing the system
[Launch the runtime, log in, how clients connect. Pull facts; ask for site-specific access.]

## Screen guide
[Per display, a short entry: what it shows and what the operator does there. Purpose = asked; screen = pulled.]

## Alarm response
[Per alarm/priority: condition (pulled) → recommended operator action (asked). Mark TODO if unknown.]

## Routine tasks
[Acknowledging alarms, setpoint changes, shift handover. Only the tasks this system actually has.]

## Backup, recovery & support
[Backup schedule + restore responsibility + who to call. All asked, never fabricate a contact.]
```

### `Training-QuickReference.md` (optional: only on request)

```markdown
# [Project]: Quick Reference

[One page. The 5-10 things an operator does most, each in one line. Pull the screen/tag names live.]
```
