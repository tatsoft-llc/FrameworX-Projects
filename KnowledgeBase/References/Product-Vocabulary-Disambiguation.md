# Product vocabulary: names that collide

FrameworX has several term pairs where the everyday word and the precise product word differ, or where one
English word names two different things. Picking the near-synonym produces config, docs, or tool calls that
read right and bind to nothing. This is the disambiguation reference; it complements `frameworx-vocabulary.md`
(which defines the data-foundation and Object-Model terms). The installed product is always the authority, if
a term here differs from what the Designer/Runtime UI or docs.tatsoft.com show, the product wins.

## Solution / Application / Environment / Tool: the big four

| Term | Means | NOT |
|---|---|---|
| **Solution** | What you create with FrameworX: a `.dbsln` plus its runtime artifacts. The primary user-facing term. | Not a "Workspace". Not an "Environment". |
| **Application** | A natural-English synonym for Solution where it reads better ("my SCADA application"). Default to **Solution**. | Never the collective for the three Environments. |
| **Environment** | One of three standalone contexts, **SolutionCenter**, **Designer**, **Runtime**, each its own application with its own UI and lifecycle. The three share one Solution. | Not a "Workspace". Not a Profile (a Profile runs *inside* the Runtime Environment). |
| **Tool** | A smaller utility *within* an Environment (MQTT Tag Tool, OPC Discovery Tool, diagnostics). | Not a peer of the three Environments. |

The collective for SolutionCenter + Designer + Runtime is **the FrameworX Environments** (or "the three
Environments"). Singular use ("the Designer Environment") is fine.

## Profile vs ExecutionProfile: and never "production environment"

- **Profile** is the execution mode the Runtime is running: **Production**, **Development**, **Validation**,
  plus user-defined **Custom**. It's the user-facing word (the `--profile=Development` CLI parameter, the docs).
  Develop and test on the **Development** profile; the same Solution can run on several Profiles at once on
  different ports.
- **ExecutionProfile** is the same concept's internal/schema name. You'll see it in object schemas; in prose,
  say **Profile**.
- **Do not call a Profile an "Environment."** They sit on different layers. Environment = which of the three
  apps; Profile = how the Runtime is running. Industry habit says "production environment" for the production
  profile; in FrameworX that phrasing is wrong. Write **"production profile"** or "the Runtime on the Production
  profile."

(This is the general **user-facing-name vs schema-name** split: the short surface word is what appears in UI,
CLI, and docs; the longer qualified name lives in schemas. Other pairs: a Tag's Name vs its internal ID; the
short MCP verbs like `open_solution` vs their schema entries.)

## Workspace: two unrelated meanings

| Where | Means |
|---|---|
| **ConsoleMCP** | A JSON-on-disk representation of a Solution, a ConsoleMCP-only term, the file mirror of what Designer holds live in the `.dbsln`. |
| **FrameworX user-facing docs / UI** | **Not a product term.** Don't use "Workspace" as a synonym for Environment or Solution in solution docs. Where you find it used that way, replace it: say **Environment** (collective) or the specific Environment name. |

## Build vs Create: verb discipline

| Verb | Means | Where |
|---|---|---|
| **Build** | Compile and package an **existing** Solution for deployment. | Designer "Build Solution"; CLI build commands. |
| **Create** | Author a **new** Solution (or a new artifact within one). | SolutionCenter "Create New Solution"; Designer "Create" actions; the MCP `create_solution` verb. |

They aren't interchangeable. "Build this solution" means compile what exists; "create a solution" means author
a new one. When you name anything (a script, a task, a file), keep the verb honest to which you mean.

## Runtime API: the integration surface's name

The HTTPS surface that exposes a running Runtime's data (tag values, historian, alarms, the Object Model) over
a per-solution port is the **Runtime API**.

| Surface | Call it | Use in |
|---|---|---|
| The HTTPS surface a system integrates against (per-solution Runtime port) | **Runtime API** | Integration docs, specs, file names. |
| The same surface, when you must name the protocol (e.g. beside RuntimeMCP) | **Runtime API (REST)** / "Runtime REST API" | Technical / integration guides. |
| The AI-client tool surface (Model Context Protocol) over the runtime | **RuntimeMCP** | AI-client tooling and docs. |

Avoid "Runtime WebAPI", "Partner API", or bare "REST API" for this surface: the first is dated and
protocol-vague, the second names the consumer not the surface, and the third drops the "Runtime" qualifier and
collides with the SolutionCenter API (also REST, different port and auth).
