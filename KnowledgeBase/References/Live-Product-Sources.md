# Reference: the live product is the source of truth (and it ships on disk)

FrameworX ships its full documentation, its runtime Object Model, and its control catalog as **JSON files
inside the install**, regenerated with every build. These, plus the MCP tools that index them, are the
**Tier-1 source of truth.** This KnowledgeBase is **Tier-2 judgment layered on top**; it must never become a
stale copy of what these files already say.

## What ships, and what serves it live

Default location `C:\Program Files\Tatsoft\FrameworX\fx-10\` (a `net10.0\` copy of several exists too):

| File on disk | What it is | The live MCP surface |
|---|---|---|
| `Documentation.json` | The **full product docs**, a structured mirror of docs.tatsoft.com (the FX space), regenerated with the build | `search_docs` (Designer / Console) |
| `documentation_tree.json` | The doc **navigation tree** (~800 pages: titles, URLs, labels) | `search_docs` / the docs site |
| `RuntimeNamespace.json` | The runtime **Object Model**, every namespace, member, type, and description (`Server.*`, `Tag.*`, `Alarm.*`, `Device.*`, …) | `browse_object_model` / `runtime_browse_object_model` |
| `ControlSchemas.json` | The **control catalog**, every Display element with its default template | `list_elements` + the display schema tools |

Protocol address grammar and per-field hints additionally ship **per driver** in
`Protocols\T.ProtocolDriver.<Name>.config.xml`, the exact `<Hint>` / `<Format>` / `<Examples>` text the
Designer shows in the cell editor. And `get_table_schema(<Table>)` returns the authoritative, build-accurate
field set for any config table.

## How to ground: the MCP tools are the supported path, not the files

- **Ground through the MCP tools:** `search_docs`, `browse_object_model`, `get_table_schema`,
  `list_protocols`, `list_elements`. These are the **stable, supported, build-accurate contract**, and the
  only path when Claude Code runs on a *different* machine than FrameworX (the common Mac-client / Windows-VM
  split, see `Method/mcp-setup.md`).
- **The on-disk JSON is the *backing store* for those tools, not an interface to read directly.**
  `search_docs` indexes `Documentation.json`; the schemas back `get_table_schema` / `list_elements`. They are
  listed above so you know *why* the MCP answers are build-fresh, **not** as files to `Grep`. Their names and
  shape are an internal implementation detail that can change between builds, and they only exist on the same
  machine as the install. **Prefer the tool.** (A one-off `Grep` of `Documentation.json` is an occasional
  debugging convenience: never a pattern to build on, or to teach a customer.)

## What travels with a clone: and what doesn't

This repo is public and clonable, and the live sources above do **not** travel with it. The JSON files live
under `C:\Program Files\Tatsoft\…`, *outside* the repo; the MCP tools resolve to a **locally running**
FrameworX install. So a fresh clone on a machine that hasn't installed-and-connected FrameworX yet, an
evaluator browsing the repo, a first run, a Mac client whose install is in a VM not yet bridged, has
**neither** Tier-1 path live. On that clone, the `KnowledgeBase/` markdown is the **only** platform-adjacent
grounding present.

That is why the rule is not a blunt "never restate."

## The rule: point when connected; curate (and label) for when you're not

- **Don't bulk-copy** reference you can't keep fresh, the full docs, an exhaustive field dump, a whole table.
  That's what `search_docs` / `get_table_schema` / `browse_object_model` are for; a bulk copy only drifts.
- **Do keep a curated, banner-labeled digest** of the highest-value facts and gotchas, the fallback a cold
  clone needs, with each fact **pointing at its authoritative live home** ("verify via
  `get_table_schema('DevicesPoints')`", "the build's driver `<Hint>` wins"). Connected, the live source is
  authoritative and the digest is *build-pending*; disconnected, the digest is all you have.
- **When the two disagree, the live product wins** (see `Conventions/Working-Rules.md`): which is why every
  FX-specific fact in `KnowledgeBase/` carries a *"verify against your build"* flag.

So KnowledgeBase earns its place two ways: the *judgment* those sources can't reconstruct even when connected
(diagnosis, the details that validate at write time and still need a runtime check, the build method),
**and** the labeled, build-pending grounding that survives a cold clone.

*(Paths and file names were confirmed on one build, fx-10.1.5.x. Confirm the location on your install; the
principle holds regardless of where the files sit.)*
