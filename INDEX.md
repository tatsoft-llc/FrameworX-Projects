# Workspace Catalog: read this to know where things live

A multi-project FrameworX solution workspace. This catalog says which folder holds what and which folder a
given task touches first.

## Top-level folders

| Folder | Holds | You touch it when |
|---|---|---|
| `Sites/<Name>/` | one customer site / deployment (Specifications, Solutions, Documentation, Decisions, ChangeLogs) | building or maintaining a specific project |
| `Templates/` | reusable building blocks: `SiteProject/` (new-site skeleton), `Prompts/`, `Examples/` (e.g. the Brewery reference build), plus placeholder folders (`Documents/`, `Snippets/`, `Solutions/`) that grow with your reusable content | seeding a new project; reusing a template, prompt, or example |
| `KnowledgeBase/` | shared conventions, patterns, and reference: `Conventions/`, `Patterns/`, `References/`, `Method/` (the 5-layer build method + quickstart), and `Troubleshooting.md` (symptom → the right doc) | grounding before design; capturing a reusable lesson; starting point when something misbehaves |
| `AISessions/` | per-session scratch, cold-start resumes (git-ignored) | mid-work notes; never the deliverable |
| `.claude/` | skills, hooks, permissions, and `tools/` (the harness) | configuring how Claude behaves here |
| `.claude/tools/invariant-linter/` | read-only structural drift check (reserved-object integrity, project layout, solution naming) + its ratchet allow-list and info-doc | checking the repo's prose-guarded invariants haven't drifted |

## Per-project folders

| Folder / file | Holds |
|---|---|
| `Specifications/Requirements.md` | what the solution must do |
| `Specifications/IO-Register.md` | point list → UNS tag mapping (drives the design) |
| `Solutions/` | the FrameworX `.dbsln` for this project |
| `Documentation/Commissioning-Record.md` | per-point write→readback evidence + sign-off |
| `Documentation/` (other) | handover, as-builts, O&M |
| `Decisions/` | deep how/why notes, alternatives rejected, gotchas |
| `ChangeLogs/` | per-author changelog files (`ChangeLog-<user>.md`), what-changed-when |
| `Tests/` | acceptance checks + expected results the `run-tests` skill drives (recommended) |

## Task → folder routing

| Task | First load | Output lands in |
|---|---|---|
| Verify the MCP connection | `verify-mcp-setup` (probes the bridges, smoke-tests `list_solutions`) | a confirmed, bootstrapped session |
| New project | `new-project-bootstrap` (reads `Templates/SiteProject/`) | `Sites/<Name>/` |
| Author UNS / Displays | the project's `Specifications/` (`uns-from-io-register` for the tag layer; `first-device-channel` for device comms) | the solution in `Solutions/` |
| Commission | the project's `Specifications/IO-Register.md` (the `commission-the-points` skill drives it) | `Documentation/Commissioning-Record.md` + `ChangeLogs/` |
| Hand over | the live solution + `Documentation/` (the `project-handover-docs` skill generates the set) | `Documentation/` |
| Reuse a convention/pattern | `KnowledgeBase/` | a new `KnowledgeBase/` entry when a lesson recurs |

When something doesn't fit any folder, say so. Don't invent a new top-level folder silently.
