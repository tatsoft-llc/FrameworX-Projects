---
name: ground-first
description: >-
  Before writing a spec, authoring UNS tags or a Display, configuring a device channel, or making any
  non-trivial change, ground first in (1) the platform Context Package the MCP injects at bootstrap, the
  SolutionCenter / Designer / Runtime trio + the Four Pillars + the Unified Namespace, and then (2) this
  project's own prior art under Specifications/, Decisions/, ChangeLogs/, and the shared KnowledgeBase/. The
  lightweight pre-flight that stops you producing artifacts that contradict, duplicate, or drift from what the
  project already settled. Triggers BROADLY for any productive task on a project. User signals include "before
  I start", "what's already in this project", "ground first", "what did we decide here", "is there prior art",
  "did we already build this".
license: Apache-2.0
metadata:
  author: Marc Taccolini
---

# Ground First: Read Before You Write

## Why this exists

Ungrounded work is the quiet, daily failure: artifacts that drift, duplicate, or contradict because nobody
read what the project already settled. A new tag duplicates one under a different path. A Display reaches for
a control the project's `KnowledgeBase/` convention already standardized away from. A requirement contradicts
a `Decisions/` note nobody re-read. A "still pending" answer cites something the solution already implements.
Each ungrounded artifact becomes the next person's "wait, I thought we agreed…" moment.

The fix is cheap: a few minutes of reading before producing new material, with the platform Context Package
as the very first step. This skill names the reflex.

## When this skill triggers

Fire when about to produce new material on a project:

- Writing or revising a spec in `Specifications/` (requirements, the IO register).
- Authoring UNS tags or device channels, building a Display, a script, or alarms.
- Adding a `Decisions/` note or a `ChangeLogs/` entry.
- Answering a question whose answer depends on a decision already made on this project.
- User signals: "before I start", "what's already here", "did we already build this", "ground first",
  "is there prior art".

Do NOT fire for: mechanical lookups (find / count / list a tag), one-line typo fixes, or a trivial isolated
addition. Just do those.

## The protocol

Four steps. Step 1 typically runs once per session; steps 2-4 are ~30 seconds for a small task, a few minutes
for a larger one. **Each step's output should change what you write next**, if reading something didn't update
your draft, you didn't read it for content.

### 1. Load the platform Context Package

Before any project material, prime on the platform's own mental model. None of the platform's identity, its
principal product modes, or its design philosophy is derivable by grepping one project file.

Your first action is the MCP bootstrap, `open_solution` / `create_solution` / `list_solutions` through the
Designer (or Console). That call returns the Tier-1 Context Package: the Four Pillars, the Unified Namespace,
the runtime Object Model, object schemas, naming, and syntax. This usually already ran at session start (per
`CLAUDE.md` → "The one rule that matters first"). Confirm it ran; call it now if not. For anything you're
unsure the package covers, query `search_docs`, never paraphrase platform knowledge from memory.

**The three product modes** the package describes, every grounded session should know which one the work
lives in:

- **SolutionCenter**, lists solutions on the machine, picks which to open, handles licensing and version
  routing.
- **Designer**: authors the solution: tags, Displays, scripts, devices; deploys to runtime.
- **Runtime**: executes the solution: real-time database, alarm engine, historian, device drivers, web
  services.

Work routinely confuses behavior that belongs to a different mode. Naming the mode up front prevents that.

**Skip-cost:** every later step gets interpreted against a guess at what the platform IS, not against how it
actually behaves.

### 2. Identify the area

Name the part of the project the new artifact lands in. Be specific: not "the solution", but "the
`Area/Pump01` UNS branch", "the Modbus channel for FT-101", "the Overview Display", or "the high-level alarm
group". Confirm you're in the right project folder under `Sites/`, never mix two projects' material.

### 3. List and read what's already there

For each area, read in this order (skip what doesn't exist):

- **`Decisions/`**: the "how & why we configured it this way" notes for this area, including alternatives
  already rejected and gotchas already hit.
- **`Specifications/`**: the requirements and the IO register; the design inputs that drive the UNS.
- **Recent `ChangeLogs/` window**: entries touching this area. Highest-signal source for what just changed.
- **`KnowledgeBase/`**: the cross-project conventions (UNS naming, alarm style) and reusable patterns that
  apply here. A trick captured on a past project starts this one ahead.
- **The live solution**: when adding a new instance of an existing pattern (another channel, another
  Display, another tag branch), read the closest existing peer first via `get_objects` / `list_elements` /
  `browse_object_model`.

If two existing sources conflict (a `Decisions/` note says X, the spec says Y), STOP. Resolve before writing,
that drift is exactly what compounds without this skill.

### 4. Write: anchored on what you just read

Cite what you grounded on, briefly:

- Spec / Decisions note: a "Grounding" or "Prior art" line referencing the decision / spec / convention / peer.
- A config or script: a one-line note of the source ("follows `KnowledgeBase/Conventions/UNS-Naming.md`") only
  when the alignment isn't self-evident.

If grounding reveals the task is genuinely complex (multiple sources disagree, the area has a known unresolved
question, a prior attempt failed), STOP and treat it as a most-capable-tier piece of work (see `CLAUDE.md` →
"Model tiers"); don't push through on a quick-pass budget.

## Output shape

A grounded spec or change opens with a brief grounding pointer:

```
## Grounding

- Read `Decisions/Pump-Control-Loop.md`. Settled on PID in the runtime, not the PLC; do not re-add a PLC loop.
- Read `Specifications/IO-Register.md`. FT-101 is an AI, 4-20 mA, scaled 0-250 m³/h.
- KnowledgeBase: `Conventions/UNS-Naming.md`, area/equipment PascalCase; this branch follows it.
- ChangeLog: 2026-05-20 reworked the high-flow alarm deadband.

## Proposal

[the actual spec / change starts here]
```

Discipline:

- **Cite specific files**, not "the docs say". Vague citations rot silently.
- **Surface conflicts** when grounded sources disagree: don't silently pick one.
- **Three to six bullets is enough.** This is a pre-flight, not an investigation.

## Anti-patterns

- **"I'll just start and look things up as I go."** First drafts contradict existing material; later "alignment
  passes" rarely catch it.
- **Reading a `Decisions/` note without changing the draft.** If it didn't update your hypothesis, you read it
  for show.
- **Citing "the project" or "the docs" without a path.** Vague = performative grounding. Name the file.
- **Skipping the ChangeLog as "just history".** Recent entries are the highest-signal source for what just
  changed.
- **Mirroring a peer without reading it.** Parallel names are not parallel behavior. Per `CLAUDE.md` →
  "Verify each path", identical config with one different input is a real divergence. Read the peer; don't
  assume it.
- **Quoting prior-session memory as ground truth.** Re-check against the live solution before claiming "X is
  missing" or "X is already done": those beliefs go stale fast.

## Composition with other skills

- **`new-project-bootstrap`**: on a brand-new project there's no prior art yet; bootstrap first, then this
  skill grounds every task after.
- **`premise-check`**: once grounded, test whether the question itself is sound before answering
  ("does the platform actually do this natively?").
- **`KnowledgeBase/`**: when grounding reveals a convention is missing or stale, capture the fix there so the
  next project starts ahead.

This skill is the lightweight counterpart to the bootstrap rule in `CLAUDE.md`. Bootstrap grounds you in the
PLATFORM (step 1); this skill grounds you in the PROJECT (steps 2-4).
