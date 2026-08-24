# Convention: Working rules (how Claude works on a delivery project)

The operating discipline applied on every project in this workspace, whatever the domain. Domain conventions
(naming, alarm style) live elsewhere in `KnowledgeBase/`; these are about *how the work is done*. Each rule
has a why and a when-it-fires.

## Bootstrap before anything
Your first action in a session is to connect to the installed FrameworX via the MCP (`open_solution` /
`list_solutions` / `create_solution`). That call injects the platform's own model, the Tier-1 Context Package
(the Four Pillars, the Unified Namespace, the Object Model, schemas, naming, syntax). Never paraphrase
platform knowledge from memory; fetch it. No `write_objects` / `designer_action` before the bootstrap.

## Verify each path: don't generalize a sibling "by analogy"
"Read it back" means the **specific** thing you built, not a lookalike. When two channels, tags, Displays, or
device points share a config shape but differ in one input, a different address, a different startup argument,
an empty-vs-set field, a working sibling is **not** evidence the other works: identical config + a different
input is a real divergence. Drive each one with the live MCP and confirm the actual result. "Low risk,
identical setup" is the phrase that masks a missed divergence. Treat it as a prompt to go test the difference.

## After a write, read it back and compare
An MCP call returning `success` says the call was accepted, not that the value landed. `set_object_value`
echoes `requestedValue` and `currentValue`: compare them, a rejected value shows up as a mismatch between the
two rather than as an error. When editing an existing object, know the upsert regime: **simple config tables
property-merge** on upsert (omitted fields keep their stored values), while **document objects** (Displays,
Layouts, Reports, script bodies) **full-replace**. omitted contents are cleared. On older builds simple tables full-replaced too, so **read → merge → write** is
always the safe default. (Details: `KnowledgeBase/Patterns/Validation-and-Readback.md`.)

Runtime-profile rows have a special case: rows other than **Development** are protected, so **author the
Development row**. A write aimed at a Production / Validation `RuntimeStartup` row does not update that row:
the Designer applies it to the **Development row** instead, the Console **skips it with a warning and
`updated: 0`**. Never assume a non-Development profile write landed. Check the updated counts and
`warnings[]`. *(This is by design, permanent.)*

## Names are identity: never rename or "consolidate" a reserved object
A name is not a free label you own; for a platform-defined object it is a **contract**. Some objects carry
their identity in a fixed name or ID and must never be renamed, deleted, or merged: `MainPage` (Display **ID 0**,
the SolutionCenter preview anchor), the `Startup` layout, predefined alarm groups (`Critical` / `Warning` /
`AuditTrail`), predefined pages (`SelectPage` / `LogonPage`). Treat any platform-seeded name as reserved unless
the product explicitly says otherwise.

Three traps put this rule here. All three converge on the same move, renaming the protected ID-0 `MainPage`
to something like `MainPage_Classic` and promoting a `Home` page into its name:
- **"Orphaned, so safe to retire."** A special object with `referencesFound: 0` is load-bearing by its
  *identity*, not by a reference count. Zero references is *normal* for it, not a cleanup signal.
- **Unrequested structural cleanup is scope drift.** Renaming / merging / "consolidating" objects the user
  didn't ask you to touch is the same drift Output Discipline warns about. Find two things that look redundant?
  Surface it: don't unify them by force.
- **Build-green is not verification of a name change.** Object refs are by internal ID, so a rename *always*
  compiles: the build status carries no signal about it either way. Verify the *semantic effect* instead,
  read the actual behavior back (is the preview anchor still attached? is the first screen the intended one?),
  never the build status. (Sibling of "Verify each path" and the readback rule above; "verified structurally +
  build-green" was the exact phrase that masked this one.)

When two conventions collide (e.g. the `Home` landing-page pattern vs. the `MainPage` preview anchor), **stop
and surface the conflict: do not mutate one object to resolve it.** The answer is almost always "keep both":
see `KnowledgeBase/Conventions/Startup-Layout-and-MainPage.md`.

## Verify a capability before you claim it
Before asserting "FrameworX does / doesn't do X," confirm it against the product, `search_docs`,
`browse_object_model`, `list_protocols`, `list_elements`, not from memory. A method or feature name implies
behavior it may not have; ground the claim, then state it. (The supported source of truth is the MCP.
`search_docs` / `browse_object_model` / `get_table_schema`; the install's JSON is their *backing store*, not
an interface to read directly. Point at the tool; don't copy its output into a doc that will drift. See
`KnowledgeBase/References/Live-Product-Sources.md`.)

## Work on the real solution; copy only to throw away
You build directly on the project's solution: that is the point. Make a copy first only for a genuinely
disposable experiment.

## Sandbox solutions: `ai-test-` prefixed, created in a disposable folder the operator names
Automated tests, smoke runs, and disposable experiments run against a **sandbox solution**, never the real
one. The rules: name it **`ai-test-<slug>`** (the prefix tells every human and every later session it is
disposable); **CREATE it** (`create_solution` / `create_workspace`). Never open a real or demo solution "just
to have a sandbox"; put it in a **dedicated disposable test folder, never in a customer project's
`Solutions/` folder**, and **ASK the operator where that folder is; don't assume a path** (it differs per
machine, and probing for one wastes turns). Quiet it: set `RichClientNoSplash=true` +
`SmartClientNoSplash=true` on the Development profile row (the splash covers screenshots and console output),
and **never write `AutoPorts=false` on the Development row**. The auto-bump is what lets parallel sandboxes
coexist (field details: `KnowledgeBase/Method/Runtime-Operations.md`). If a test must exercise an existing
solution, copy it first and rename the copy with the prefix: never run on the original. (Full rule:
`KnowledgeBase/Method/Solution-Build-Method.md` §7.) *Why:* an untested path can cost you the Designer
session or leave the solution file held open. Keep that cost on a sandbox: real solutions are trust
artifacts, not test fixtures.

## Size your writes: keep the batch under the call timeout
Keep `write_objects` batches modest, on heavy tables, around a dozen objects per call. A batch big enough to
exceed the call timeout ends the Designer session (`DESIGNER_CLOSED`); and a timed-out write may still have
landed, so **read the count back before re-sending** or you double-write. After a `DESIGNER_CLOSED`: recover
the session, re-`open_solution`, and continue with smaller batches.

## One writer per solution; recover cleanly
Only one editing session should hold a solution at a time. If a tool reports a lock, "solution open
elsewhere," or an unresponsive Designer, recover the orphaned Designer/Runtime process and re-open the
solution, then retry: don't abandon a multi-step task on a single connection error.

## Match effort to the stakes
A data-loss risk or a safety/availability-critical loop earns full rigor; a cosmetic or naming question earns
a line or two. Don't frame a settled behavior as an open decision, and don't rabbit-hole a simple one.

## Propose new rules; let them earn their place
A fresh insight from one session is a **proposal**, not yet a rule. Apply existing conventions freely, but
don't unilaterally ratify a new one. When the same trick recurs, promote it: a domain trick → a
`KnowledgeBase/Conventions` or `Patterns` entry; an operating rule → this file. Propose; a human ratifies.
(Companion to the KnowledgeBase promotion rule: a trick used on three projects is a convention.)

A **reliability** lesson promotes faster: capture it in the project's `Decisions/` first, and on its
**second recurrence**, it bit a second project, or a second time on the same one, promote it (to a
`Conventions/` or `Patterns/` entry, and upstream to the product docs at docs.tatsoft.com if it's a platform
behavior). That bar is tighter than three projects on purpose: a reliability lesson you have to re-learn is
an outage, not just lost time.
