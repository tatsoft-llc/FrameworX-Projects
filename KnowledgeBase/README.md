# KnowledgeBase: shared across all your projects

What you learn once and reuse everywhere. Tier-2 knowledge that the product can't inject and that isn't
specific to a single site. When a convention, reference, or trick would help the *next* project, it belongs
here, not buried in one project's folder.

| Area | Holds | Examples |
|---|---|---|
| `Glossary.md` | the workspace's controlled vocabulary | what Project, Solution, Application, Commissioning, Template mean here |
| `Troubleshooting.md` | symptom → the doc that fixes it | the first stop when something misbehaves |
| `Conventions/` | how you always do it | UNS naming, tag/UDT casing, Display authoring standards (fidelity contract, theme brushes, value fields, geometry), the three script environments, working rules, solution file placement, startup layout and main page |
| `Patterns/` | reusable solution-authoring discoveries | read-merge-write, schema field gotchas, MCP display-authoring recipes, Canvas drawing-replica mechanics, script runtime gotchas, the registration chain, slash-path tag paths |
| `References/` | curated lookup facts | FrameworX vocabulary, names-that-collide disambiguation, the control catalog, the `.dbsln` format, protocol vendor notes |
| `Method/` | the build-and-verify process | the 5-layer build order, verify-your-work, the verification channels + simulators, runtime Display verification |

**What does *not* belong here, point, don't copy.** The product serves its full docs, Object Model, and
control catalog **live over the MCP** (`search_docs` / `browse_object_model` / `get_table_schema` /
`list_elements`), the supported, build-fresh source of truth. If a fact lives there, **point at the tool;
don't bulk-copy it**: a stale copy drifts and the live product wins. A curated, *build-pending*-labeled
digest earns its place only where it adds judgment those tools can't reconstruct, or as the fallback a cold
clone needs: each fact pointing at its live home. See
[`References/Live-Product-Sources.md`](References/Live-Product-Sources.md).

**Promotion rule (borrowed from the Tatsoft engineering teams):** a trick used on **three** projects is a
convention. Move it from a project's `Decisions/` into `Conventions/` so every future project starts ahead.

Start with `Conventions/UNS-Naming.md`. It's the one convention you'll apply on day one.
