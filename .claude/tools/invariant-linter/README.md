# Invariant linter: repo tooling info-doc

A read-only, offline drift check for the structural invariants this workspace
guards by **prose + human discipline** only. It is OPS / repo tooling, tracked
in-tree, not a product feature.

- **Script:** [`invariant_lint.py`](invariant_lint.py)
- **Allow-list sidecar:** [`invariant-lint.allow`](invariant-lint.allow)
- **Reads:** the plaintext `Sites/*/Solutions/DesignerData/<sol>-Designer/Git/*.json`
  exports + folder structure. It does **not** open the encrypted `.dbsln`, and
  needs no MCP, runtime, or decrypt.

## Why it exists

Several invariants here live only in `CLAUDE.md` and `KnowledgeBase/Conventions/`.
Prose drifts silently. The per-solution test harness
(`.claude/skills/run-tests/check.py`) is per-project and runtime-dependent; it
covers none of these repo-level structural rules.

The anchor check (**IL001**) guards the reserved-object rule: the protected ID-0
`MainPage` display keeps its name. A rename compiles (display refs are by internal
ID, so the build status carries no signal about it), and afterwards the
SolutionCenter preview anchor is detached, with nothing in the build to flag it. An
invariant the build cannot report on, guarded only by a prose hard-rule, is the
textbook case for turning prose into a deterministic check.

## The checks

| ID | Invariant | Derived from | Severity | Cost |
|---|---|---|---|---|
| **IL001** | Every in-tree solution export has a display named exactly `MainPage` and a layout named exactly `Startup`; no `MainPage_*` rename variant. | `Conventions/Startup-Layout-and-MainPage.md`, `Conventions/Working-Rules.md` ("Names are identity") | FAIL (missing) / WARN (rename-smell) | low |
| **IL001b** | The `Startup` layout's Content region points at a display that exists and is populated (not empty/placeholder → blank first screen + blank preview). | `Conventions/Startup-Layout-and-MainPage.md` | FAIL (unset / page missing) / WARN (page blank) | low |
| **IL002** | Every `Sites/<Name>/` carries the core folders {Specifications, Solutions, Documentation, Decisions, ChangeLogs}; `Tests/` recommended. | `CLAUDE.md` project table, `INDEX.md`, `README.md` Layout, `Templates/SiteProject/` | FAIL (core) / WARN (Tests) | trivial |
| **IL003** | Every `Sites/<Name>/Solutions/` holds a `.dbsln` **or** a `README.md`; every `.dbsln` stem is a clean bare name (letters/digits/underscore). | `Conventions/Solution-File-Placement.md` | FAIL | trivial |
| **IL004** | *(REF-INT)* Every relative in-tree markdown link in a scanned doc resolves to a path that exists. | `CLAUDE.md` "point, don't copy"; the index tables in `KnowledgeBase/README.md` + `INDEX.md`; the pervasive "see `<path>`" habit | FAIL | low |
| **IL005** | *(INV-DRIFT)* Every item in a governed folder is named in that folder's governing index. | `INDEX.md` ("read this to know where things live"), `KnowledgeBase/README.md` area table | FAIL (unlisted item) / WARN (index or folder missing) | trivial |

Run `python invariant_lint.py <ROOT> --list` for the full definition + mechanical
method + cost of each check (kept in the `CHECKS` registry in the script, single
source of truth).

### Mechanical method (summary)
- **IL001**: for each `…/Git/`, read `Data[].Name` from all `DisplaysList-*.json`
  (assert `MainPage` present; warn on `MainPage_*`) and all `DisplaysLayouts-*.json`
  (assert `Startup` present). A JSON parse failure is reported as WARN, not a crash.
- **IL001b**, resolve `DisplaysLayouts-Startup` → Members → the Content region's
  `Page` (strip a `Display.` prefix); FAIL if unset or the named display is absent
  from `DisplaysList-*.json`; WARN if that display is unpopulated, content is
  Canvas `Elements` **or** Dashboard `Cells` **or** a `Xaml` body with a child
  control beyond the root `<TDisplay>` (a Dashboard page keeps content in `Cells`,
  not `Elements`). Missing `Startup` layout is deferred to IL001.
- **IL002**: stat each required subfolder per site. Extra folders are allowed
  (the workspace scales; `README.md` says you don't fill every folder).
- **IL003**: glob `Sites/*/Solutions/`; check for a `.dbsln`/`README.md`, and
  regex each `.dbsln` stem against `^[A-Za-z0-9_]+$`.
- **IL004**: walk the root docs, `KnowledgeBase/`, `Templates/`, `Sites/`,
  `.claude/skills/` and `.claude/tools/`; strip fenced and inline code so
  non-navigable links are not linted; extract `[label](target)`; resolve each
  target against the doc's own directory; FAIL if it does not exist. Skipped by
  design: external URLs, `mailto:`, bare `#anchors`, `~`-relative paths, template
  placeholders, targets outside the root, and `AISessions/`.
- **IL005**: list the top-level folders and `Templates/` subfolders and assert each
  name appears in `INDEX.md`; list `KnowledgeBase/` subfolders and non-README
  `*.md` files and assert each appears in `KnowledgeBase/README.md`.

## How to run

```
python invariant_lint.py <ROOT>            # lint; exit 0 = clean, 1 = new FAIL
python invariant_lint.py <ROOT> --list     # print check definitions
python invariant_lint.py <ROOT> --quiet    # only WARN/FAIL lines + summary
python invariant_lint.py <ROOT> --reseed   # add today's FAILs to the allow-list
```

`<ROOT>` is the workspace root (the folder holding `Sites/`). Taking ROOT as an
argument keeps the tool location- and version-independent.

**Exit codes:** `0` = no unsanctioned FAIL. `1` = at least one new FAIL.
**WARN never fails the run.**

## The ratchet (allow-list sidecar)

You will have day-one violations. Do **not** try to fix them all. Grandfather
today's sanctioned reality into `invariant-lint.allow`. One finding-key per
line, `#` comments for *why* each is sanctioned. And the run then FAILs only on
**new** drift past that line.

- A FAIL whose `key:` (printed under each finding) appears in the allow-list is
  reported as `ALLOWED` and does not fail the run.
- **Seed deliberately.** Prefer hand-adding a key with a one-line WHY comment
  (confirm it is truly sanctioned first. See below). `--reseed` is the bulk
  escape hatch: it *appends* every current FAIL key with a generated comment;
  review each line afterward, because it cannot tell a sanctioned exception from
  real drift.
- To re-arm a check, delete its line from the allow-list.

Reseeding is a human decision, never a way to make a red run pass. After day
one, the AI's part is to propose: the reseed command and the keys it would
grandfather, each with its one-line WHY. A human reviews that list and runs the
command. A reseed run to quiet a failing check defeats the ratchet.

### Confirm before you fail
A first-cut flag is often a sanctioned exception or a mis-scoped check, not a
true violation. **Confirm with the repo owner before treating a flag as real**,
then seed the confirmed-sanctioned ones. (Two of this tool's first three flags
turned out sanctioned; one was fixed by adding a folder. An alarm-groups check
was considered and dropped. The export omits untouched predefined groups, so
"Critical/Warning present" would have been mis-scoped.)

## Deterministic vs. judgment: kept separate

This script is the **cheap, deterministic** pass: it runs unattended, offline,
in milliseconds, and only ever reports. The **judgment** pass ("is this still
the right invariant? should a new convention be promoted? refresh the
strategy?") is a separate, slower human/AI cadence. A judgment refresh is
**never** a precondition for this check to run. Don't fuse them.

## Adding a check later

Add an entry to `CHECKS` (definition/method/cost) and a `check_ILNNN(root)`
function returning `Finding`s, then append it to `CHECK_FNS`. Keep checks cheap
and derived from a named repo rule, resist a rules-DSL / plugin engine. A
linter that does a few drift checks reliably beats a framework that does nothing
yet.

## Seeding your baseline

On a fresh workspace, run the linter once and expect day-one findings. Triage
each one: fix the real drift, and grandfather the confirmed-sanctioned
exceptions into `invariant-lint.allow` (hand-add the key with a one-line WHY
comment, or `--reseed` and then review every generated line). From that point
the run FAILs only on **new** drift.

Two lessons from this tool's first live runs, worth keeping in mind when a
check flags something:

- **A flag can be a mis-scoped check, not a violation.** A first cut of IL001b
  counted only Canvas `Elements` and false-flagged every Dashboard page (whose
  content lives in `Cells`/`Xaml`). Live verification over the FrameworX AI
  Designer showed the page was populated. The fix went to the check, not the
  solution. Confirm against the live product before "fixing" a solution.
- **Prefer fixing over allow-listing.** A site missing its `Documentation/`
  folder was fixed by adding the folder; only genuinely sanctioned exceptions
  (an out-of-tree demo solution, a legacy pre-convention name) went on the
  ratchet.
