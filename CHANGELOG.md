# Changelog

What changed in each release of the FrameworX Solution Workspace. Newest first. Each skill also carries its
own `metadata.version`, so you can tell which skills changed.

## v1.1.2 (2026-10-21)

**Expanded**
- `References/Protocol-Vendor-Notes.md`: the ControlLogix Tag Importer reads `.L5K` files only. An `.L5X`
  file imports an empty tag list with no error, and renaming it does not help; export L5K instead.
- `Conventions/Startup-Layout-and-MainPage.md`: put a shared header and nav bar once in the layout's Header
  and Footer (or Menu) regions, keep each page to its own content, and navigate into Content.

## v1.1.1 (2026-10-21)

**Fixed**
- `README.md`, `CLAUDE.md`: the `frameworx.skill` install step for Claude Code. The bundle already contains
  the `frameworx/` folder, so extract it into `~/.claude/skills/`. Extracting it into
  `~/.claude/skills/frameworx/`, as the old text said, nested it one level too deep and the skill did not
  load. The README now carries the PowerShell command.

**New**
- `.claude/skills/manage-context-on-large-solutions` (1.0.0): keep a large build coherent. Scope by layer
  and area, browse instead of dumping, verify each batch, and leave a resumable trail. Listed in the build
  loop, the task routing and the working agreement.

**Expanded**
- `Patterns/MCP-Display-Authoring-Recipes.md`: write a very large display through
  `open_solution(from_workspace=...)` instead of an inline `write_objects` payload, with the envelope shape
  and the caveats.
- `References/Protocol-Vendor-Notes.md`: the EtherNet/IP station is `IP;Port;Slot` only; multi-hop CIP
  routes are not supported, and what to do instead.

## v1.1.0 (2026-10-20)

**New in the KnowledgeBase**
- `Conventions/Script-Environments.md`: the three script environments (Script Task, Script Class, Display
  code-behind), their threading, and the `@`-namespace.
- `Patterns/Script-Runtime-Gotchas.md`: eleven script traps that compile green and fail later (static locks,
  the UI thread, `CS7036`, InvariantCulture, async Dataset calls, `TDataTable`, and more).
- `Method/Runtime-Display-Verification.md`: testing a Display's dynamics in the running client with only the
  Designer MCP, and what still needs a human.
- `Patterns/Canvas-Drawing-Replica-Mechanics.md`: Canvas mechanics for reproducing a supplied drawing.

**Expanded**
- `Conventions/Display-Authoring.md`: the fidelity contract (drawing as spec vs source), theme brushes as the
  default with the brush map, value-field element choice, Symbol labels in braces, and `Path` vs `Polygon`
  geometry.
- `Patterns/Display-Value-Binding-Literals.md`: on FrameworX 10.1.6, static TextBlock captions go in `Text`;
  state-dependent captions use one element with a nested `IIf`.
- `Conventions/Script-Class-Invocation.md`: re-entrancy guard for Script Class methods called from more than
  one Task, and the `TDataTable` cause of `CS1061`.
- `Patterns/MCP-Display-Authoring-Recipes.md` (probe the importer), `Patterns/MCP-Schema-Field-Gotchas.md`
  (`list_dynamics` overview vs schema), `Conventions/Startup-Layout-and-MainPage.md` (build after a Content
  change), `Method/Verification-Channels-and-Simulators.md`, and `Troubleshooting.md` (script and Display rows).
- `CLAUDE.md`: read the governing convention before authoring (theme brushes, solution placement).
- Skills: `commission-the-points` (Designer-only readback), `run-tests` (Display testing pointer); every skill
  now carries `metadata.version`.
- Invariant linter: IL004 (in-tree markdown link integrity) and IL005 (folder-index inventory).
- README: "See it in action" videos, a clearer link to the download request form, an "Example solutions"
  table of eight downloadable solutions on docs.tatsoft.com, and a note on long file names when cloning on
  Windows.
- CONTRIBUTING: skill versions, and no AI co-author trailers on commits.

**Aligned with Claude-Code-Skills 1.1.0**
- References to the companion skills retired in 1.1.0 are gone: `session-summary` replaces
  `cold-start-prepare`; the batching and pacing guidance from `work-in-verified-batches` and
  `one-topic-at-a-time` is now written in place (with Claude Code's plan mode and task list); browser setup
  points at Claude Code's built-in browser support instead of `chrome-connector-setup`. Touches
  `CLAUDE.md`, `AISessions/README.md`, the Quickstart, the build method, the Chrome web-test pattern, and the
  `commission-the-points`, `uns-from-io-register`, `verify-mcp-setup` and `premise-check` skills.
- README: "The other half" now describes the eight-skill companion set.

## v1.0.1 (2026-10-20)

- FrameworX 10.1.6 remote access: the remote example config sends the bridge API key (`X-API-KEY` from
  `FX_MCP_API_KEY`) with `--allow-http`; the setup guide, `verify-mcp-setup`, SECURITY.md and the security
  baseline describe the key.
- `Patterns/Script-Tag-Path-Escapes.md` corrected: the slash form `@Tag.Plant/Pump01/Temperature` compiles;
  the dotted form fails.
- Session hooks: record the processes the session starts after each reply, and stop only those when the
  session ends. The CPU check now holds solution creation while the machine is above 90 percent CPU.
- `.gitignore`: customer sites are ignored by default (only the worked example is tracked), and `Origin/`
  folders and certificate files never are.
- README: the free Community Edition can be used in production within its limits.

## v1.0.0 (2026-08-24)

First public release: twelve delivery skills, the KnowledgeBase (conventions, patterns, references, the
five-layer build method), templates, and the worked water treatment example under `Sites/Example-HighlandWTP`.
