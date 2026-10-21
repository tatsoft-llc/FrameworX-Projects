# FrameworX Solution Workspace

**`v1.1.0`** · targets FrameworX **10.1.5+** · [what changed](CHANGELOG.md)

FrameworX is an industrial automation platform from Tatsoft: SCADA, HMI, historian, alarming and device
connectivity in one product, with MCP servers that let an AI agent read and write the solution directly.
This repository is the workspace our own team uses to build FrameworX projects with Claude Code: the working
agreement, the delivery skills, the templates, and a worked water treatment project. Clone it, point Claude
Code at a FrameworX installation with the Designer MCP connected, and build.

**See it in action:** [Claude Builds Industrial Solutions in Minutes](https://youtu.be/TwIOFw0r_M4) ·
[A real HMI application moved to FrameworX, start to finish](https://youtu.be/bZyK041Y4cc) · more on
[YouTube](https://www.youtube.com/@TATSOFT) and in the [AI Integration docs](https://docs.tatsoft.com/display/FX/AI+Integration).

**Get FrameworX:** [request the free download](https://tatsoft.com/fx-101/#download), then open one of the
[example solutions](#example-solutions) below or start your own project.

One workspace hosts **many projects**: clone it once, and every customer site, skid or line you build lives
as its own project inside it.

## Safety: this workspace writes to a control system

The skills here author and change a real FrameworX solution, and they can start and stop its runtime. If
that solution is attached to live field hardware, a tag write can move a physical output: a pump, a valve, a
dosing setpoint. Treat a session here as work on a control system, not as work on a document.

**Commission against a simulator or an isolated bench first.** Do not point this workspace at a live or
safety-critical process until you have run the same steps somewhere a wrong value cannot hurt anyone or
damage anything. The `first-device-channel` skill covers the no-hardware-yet path using the built-in
ValueSimulator.

**The shipped permission file auto-approves the write verbs.** [`.claude/settings.json`](.claude/settings.json)
puts the FrameworX MCP tools on `permissions.allow`, `write_objects`, `bulk_write_objects`,
`set_object_value`, `rename_objects`, `create_solution_file`, `update_solution_file`, `run_workspace` and
`stop_workspace` among them. That is deliberate, because prompting on every write makes a build session
unusable. It also means Claude changes your solution, and starts or stops your runtime, without asking each
time. If you would rather be asked, delete those entries from `permissions.allow` before your first session.
Everything still works; you approve each verb once per session instead.

## Get FrameworX first

FrameworX is a free download, and no license is needed to work through everything in this repository.
Without a license, each runtime session and each Designer session stops after 4 hours; start it again to
continue. Register the free **Community Edition** on the License page of Solution Center to remove that limit
for solutions up to 1,000 tags and 100 communication points. Community Edition is free and perpetual, and it
can be used in production within those limits. Larger systems take a licensed edition: see
[Product Editions](https://docs.tatsoft.com/display/FX/Product+Editions). Get **10.1.5 or newer**: earlier
builds do not ship the MCP servers this workspace drives.

**[Request the free download](https://tatsoft.com/fx-101/#download)** (a short form on tatsoft.com)

Then: install it, open the Designer, start the MCP bridges, connect Claude Code, clone this repository, and
run `new-project-bootstrap`. If the bridges do not come up, `verify-mcp-setup` diagnoses them before
anything else fails.

Product documentation lives at https://docs.tatsoft.com. FrameworX itself ships no language model and no
weights; it connects to the model you choose, local or on premises included, and you supply your own key.

## Example solutions

Ready-made solutions you can download and open in FrameworX, to see what a finished build looks like before
you start your own. Each page on docs.tatsoft.com describes the solution and carries its `.dbsln` file.

| Example | What it shows |
|---|---|
| [Water Treatment Plant AI Designer Example](https://docs.tatsoft.com/display/FX/Water+Treatment+Plant+AI+Designer+Example) | a water treatment plant built with the AI Designer; the published version of this repository's `Sites/Example-HighlandWTP` |
| [NovaBio Pharmaceutical AI Designer Example](https://docs.tatsoft.com/display/FX/NovaBio+Pharmaceutical+AI+Designer+Example) | a pharmaceutical bioprocess plant built with the AI Designer |
| [PID Process Trainer AI Designer Example](https://docs.tatsoft.com/display/FX/PID+Process+Trainer+AI+Designer+Example) | closed-loop PID control, cascade and loop tuning |
| [Process Diagrams AI Designer Example](https://docs.tatsoft.com/display/FX/Process+Diagrams+AI+Designer+Example) | an existing process drawing turned into a live display with the AI Designer (two solutions) |
| [BytePizza AI Designer Example](https://docs.tatsoft.com/display/FX/BytePizza+AI+Designer+Example) | a complete restaurant-operations solution generated from two natural-language prompts |
| [SolarPanels MCP Demo](https://docs.tatsoft.com/display/FX/SolarPanels+MCP+Demo) | a solar power plant monitored through the Runtime MCP, with MQTT data |
| [LocalAI KnowledgeGraph Demo](https://docs.tatsoft.com/display/FX/LocalAI+KnowledgeGraph+Demo) | an ISA-88 pharmaceutical plant with an interactive knowledge graph and a local AI chat panel |
| [Brewery Plant Example](https://docs.tatsoft.com/display/FX/Brewery+Plant+Example) | a craft brewery with batch processing and recipe management; the target of this repository's `Templates/Examples/Brewery` reference build |

More, by industry and by architecture: [Solution Examples](https://docs.tatsoft.com/display/FX/Solution+Examples).

## The build loop

Twelve skills, each a named step in how a solution gets built and verified:

| Stage | Skills |
|---|---|
| Start | `new-project-bootstrap`, `ground-first` |
| Connect | `verify-mcp-setup`, `first-device-channel` |
| Model | `uns-from-io-register` |
| Build | `display-authoring-loop`, `svg-to-fx-display` |
| Question the ask | `premise-check` |
| Prove | `commission-the-points`, `review-the-ai-build`, `run-tests` |
| Hand over | `project-handover-docs` |

`svg-to-fx-display` is the one to watch first: hand it a designer's SVG mockup and it maps the visual
signatures it recognizes, gauges, tanks, trends, alarm lists, setpoint fields, to the FrameworX control that
carries that pattern.

## What is inside

`CLAUDE.md` (the working agreement, the document a session loads first), `.claude/skills/`, `.claude/hooks/`
(session hygiene), `.claude/tools/invariant-linter/` (turns a rule written in prose into a deterministic
check), `Templates/` (site project skeleton plus a brewery validation set), `Sites/Example-HighlandWTP/` (a
worked project: synthetic data, real structure), `KnowledgeBase/`.

**About the worked example.** `Sites/Example-HighlandWTP/` ships built but not commissioned, on purpose. All
20 rows of its `Documentation/Commissioning-Record.md` read `pending`, and six `> TODO:` markers sit in
`Documentation/Operator-Manual.md`, four of them on alarm responses. That is the discipline, not an
omission. Commissioning evidence is only worth something when a person actually drove the point and read it
back, so the record ships seeded and unexecuted for you to run yourself with `commission-the-points`. The
TODOs are there because `project-handover-docs` is forbidden from inventing a site procedure or a support
contact (see the no-fabrication rule in `.claude/skills/project-handover-docs/SKILL.md`), and a made-up SOP
on a chlorine alarm is worse than a blank one. Everything the configuration can state, the example states.

The example also ships without its runtime databases (`.dbAlarm`, `.dbHistorian`, `.dbRetentive`,
`.dbRuntimeUsers`, `.dbBusiness`), `*.backup` files, and Designer machine state: those are stripped by
design and FrameworX regenerates them on first run, so their absence in a fresh clone is expected. The
solution itself ships alongside a complete diffable JSON export set under `DesignerData/…/Git/`.

> The build method, conventions and reliability notes are distilled from real FrameworX
> engineering practice and validated end to end against worked
> examples: the **Brewery Plant** build under [`Templates/Examples/Brewery/`](Templates/Examples/Brewery/)
> (golden plus re-take test runs) and the **Highland WTP** project under
> [`Sites/Example-HighlandWTP/`](Sites/Example-HighlandWTP/). Every FrameworX-specific claim in
> `KnowledgeBase/` is either grounded in observed product behavior or flagged to **verify against your
> installed build**. The live product is always the authority.

## The other half

The skills we use in every repository, FrameworX or not, live in their own tree:
**https://github.com/tatsoft-llc/Claude-Code-Skills**. Eight skills for working with Claude Code as a
counterpart: decisions as one recommendation instead of a menu, a mirror look that re-decides from your
seat, session close, hand-off and resume, a memory check against what actually happened, safe renames, and
lock release after a crash (`kill-zombies`, which the Troubleshooting index routes to). Install both if you
want the full loop; this repository does not depend on it.

## What you need first

- **A Windows machine** (FrameworX and the harness hooks are Windows; PowerShell 5.1+), with
  **Python 3.x on PATH** for the `run-tests` checker and the invariant linter. A few file names in the worked
  example's solution export are long: clone into a short folder, or run
  `git config --global core.longpaths true` first, or the clone fails with "Filename too long".
- **FrameworX installed** (the product). This workspace drives it; it does not contain it.
- **Node.js (LTS) on the machine running Claude Code** for the shipped [`.mcp.json`](.mcp.json), which
  connects through the `npx mcp-remote` bridge, so `npx` must be on PATH.
- **The FrameworX MCP servers connected** in Claude Code: Designer, Console, Runtime. (Product
  documentation search ships inside Designer/Console as the `search_docs` tool, no separate server.)
  The workspace ships [`.mcp.json`](.mcp.json) preconfigured for a same-machine install (bridge ports
  10150 / 10151 / 10120 on `127.0.0.1`); for a remote FrameworX machine, copy
  [`.mcp.remote.example.json`](.mcp.remote.example.json) over it, set the host and, on FrameworX 10.1.6 or
  later, the bridge API key. Full connect steps,
  including starting the bridges and the security model: [`KnowledgeBase/Method/mcp-setup.md`](KnowledgeBase/Method/mcp-setup.md).
- **The FrameworX skill (`frameworx.skill`), strongly recommended.** A lightweight `SKILL.md` bundle that
  loads at the start of every session and conditions Claude *before the first tool fires*, so the session
  knows it is working in FrameworX (the platform model, the build playbooks, the on-ramp to the **AI
  Tutor**). It pairs with the MCP tools: the skill is the knowledge, the MCP is the hands. It is optional,
  but it turns a cold session into a FrameworX-aware one from message one. **It ships with the product**,
  not from a download page: after installing FrameworX, find `frameworx.skill` in
  `Documents\FrameworX\AISetup`
  ([docs.tatsoft.com → MCP and Claude Setup](https://docs.tatsoft.com/display/FX/MCP+and+Claude+Setup),
  step 2). The install path documented there is Claude Desktop; for **Claude Code**, unpack the bundle into
  `~/.claude/skills/frameworx/` so the file lands at `~/.claude/skills/frameworx/SKILL.md`, which is where
  Claude Code looks for it
  ([docs.tatsoft.com → Claude Code MCP Setup](https://docs.tatsoft.com/display/FX/Claude+Code+MCP+Setup),
  Quick Reference: Config Files).
- **Your own Claude API key.** You control your AI spend; the workspace defaults to an economical model
  tier and tells you when a task is worth a more capable one.

**Version compatibility.** This harness requires **FrameworX 10.1.5 or newer**. Pre-10.1.5 installs do not
ship the MCP servers or the Context Package shape the harness assumes, so the skills and knowledge base have
no tool surface to land on; there is no graceful degradation path. The `KnowledgeBase/` digests are written
against a 10.1.5-era build and are labeled "verify against your installed build"; the live product is always
the authority.

## Getting started

1. Clone this repo and open the folder in Claude Code.
2. **Start the MCP bridges before you start Claude Code.** The shipped `.mcp.json` uses the `npx mcp-remote`
   HTTP bridge, which needs three server processes already listening. On the FrameworX machine, open
   `Documents\FrameworX\Utilities\` and run `StartDesignerMCPHttp.bat` (port 10150),
   `StartConsoleMCPHttp.bat` (10151) and `StartRuntimeMCPHttp.bat` (10120). Leave each console window open.
   Skipping this is the most common first failure. Details, including the direct stdio alternative that
   needs no Node.js: [`KnowledgeBase/Method/mcp-setup.md`](KnowledgeBase/Method/mcp-setup.md).
3. Confirm the FrameworX MCP servers are connected, and install the **`frameworx.skill`** bundle (above) so
   the session is FrameworX-aware from the start. New to the platform? Say **"teach me FrameworX"** in your
   MCP session and the AI Tutor runs a 45-lesson curriculum with progress tracking
   ([docs.tatsoft.com → MCP and Claude Setup](https://docs.tatsoft.com/display/FX/MCP+and+Claude+Setup),
   Next Steps).
4. **Verify the connection before anything else:** say *"verify the MCP setup"*. The `verify-mcp-setup`
   skill probes the three bridges, runs a `list solutions` smoke test, and diagnoses the common failure
   modes (bridge not started, firewall, wrong host) if a tool call fails. Claude bootstraps the full
   platform context on that first successful MCP call; you do not load it from here.
5. Start a project: *"Set up a project for my water-treatment skid."* `new-project-bootstrap` creates
   `Sites/<YourProject>/` from the templates, interviews you for hardware/IO and requirements, and
   creates the FrameworX solution.
6. Author the UNS and Displays, then commission point-by-point with evidence.
7. Each project keeps its own `ChangeLogs/` (one file per contributor) and handover `Documentation/`, ready
   to maintain for years.

## Layout

```
FrameworX-Projects/
├── Sites/                 one folder per customer site / deployment
│   └── <ProjectName>/
│       ├── Specifications/   requirements + IO register (the design inputs)
│       ├── Solutions/        the FrameworX solution (.dbsln) for this project
│       ├── Documentation/    handover docs, as-builts, the commissioning record
│       ├── Decisions/        deep "how & why we configured it" notes (grows as needed)
│       ├── ChangeLogs/        per-author "what changed and when" (ChangeLog-<user>.md)
│       └── Tests/             acceptance checks + expected results run-tests drives (recommended)
├── Templates/                new-site skeleton + reusable prompts & examples
├── KnowledgeBase/            shared across ALL your projects: conventions, reference, reusable patterns
├── AISessions/               your working notes / cold-start resumes (git-ignored; never the deliverable)
└── .claude/                  the harness: skills, hooks, permissions
```

## How knowledge works here (two tiers)

- **Tier 1, the product teaches the platform.** On connect, FrameworX injects its own mental model (Four
  Pillars, Unified Namespace, object schemas, build recipes), so you do not paste platform documentation
  into the chat.
- **Tier 2, this workspace teaches your projects.** What the product cannot know: each site's hardware,
  requirements, commissioning record, decisions, plus the conventions and patterns you reuse across all of
  them (`KnowledgeBase/`). That is what persists here, across sessions.

You do not fill every folder. A small skid leans on `Specifications/` plus the commissioning record; a large
plant fills more. The workspace scales with the deployment.

> **Hooks:** three ship here. `check-cpu-before-sandbox.ps1` guards solution creation on a busy machine;
> the `session-start-baseline.ps1` + `session-stop-reap.ps1` pair snapshots the FrameworX processes at
> session start, records after each reply the ones the session itself spawned, and stops those when the
> session closes, so your pre-existing Designer/TServer are never touched. `/clear` and `/resume` stop
> nothing, because the same Claude Code process keeps running. For the mid-session case, a `.dbsln` still held (`READ_ONLY_MODE`)
> or a bridge port still bound by a process from an earlier session, the `kill-zombies` skill in the
> [companion skills repository](https://github.com/tatsoft-llc/Claude-Code-Skills) releases it on
> demand.

## Support

Questions, bug reports and feature requests for **this workspace**: open an issue on this repository.
**Suspected security vulnerabilities go to [`SECURITY.md`](SECURITY.md), privately, not to an issue.**
Before opening a pull request, read [`CONTRIBUTING.md`](CONTRIBUTING.md).
Questions about the **FrameworX product itself**: the documentation is at https://docs.tatsoft.com, the
community forum at https://forum.tatsoft.com, and the Discord at https://discord.gg/BYhbTfyRyh.
This workspace is published as is under Apache 2.0; it is not a supported Tatsoft product and carries no SLA.

## License

Licensed under the **Apache License, Version 2.0**, see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
You may use, modify, and redistribute this workspace, including commercially. Keep the attribution in
`NOTICE` and the per-skill `metadata.author` credit. © 2026 Tatsoft LLC, authored by Marc Taccolini.

Built by Marc Taccolini and the Tatsoft team, makers of FrameworX. Walkthroughs and demos: https://tatsoft.com/videos/

*Aim High. Start Simple. Scale Without Limits.*
