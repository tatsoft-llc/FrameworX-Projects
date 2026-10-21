# Convention: Startup layout and the main / first page

The page the application opens to, and the image SolutionCenter shows as the solution's preview, are the
SAME thing: whatever display sits in the Content region of the `Startup` layout. Wire it deliberately.

## The mechanism (one lever, two outcomes)
`DisplaysLayouts` ships a predefined `Startup` layout with five fixed regions: Header, Footer, Menu, Submenu,
Content. The display assigned to the `Startup` layout's **Content** region is:
- the page the operator sees first when the runtime starts, AND
- the content SolutionCenter renders as this solution's preview / thumbnail in the solution manager.

The HeaderLayout template assigns `Display.MainPage` ("Project home page") to that Content slot. The Content
assignment is the lever that *picks* the first screen / preview. But the `MainPage` display itself is **not**
disposable. `MainPage` is the fixed **ID 0** page and the SolutionCenter preview anchor: **never rename it and
never delete it** (see the hard rule below). You may point the Content region at a *different* page instead;
you must never move `MainPage` out of the way to do so.

It is NOT set in `RuntimeStartup` (which has no startup-display field, only module / port / splash flags) and
NOT in `SolutionSettings` (no preview field). It lives only in `DisplaysLayouts` -> `Startup` -> Content
region `Page`, inside the layout's `Regions` JSON.

**After changing the Content page: build before `start_runtime`.** On FrameworX 10.1.5, a Content change
written with `write_objects` and started without a build opened a different display; after
`designer_action('build')` the new Content opened.

## Hard rule: `MainPage` is protected, never rename it and never delete it
`MainPage` is the predefined **ID 0** display and the SolutionCenter preview anchor. Treat both its **name**
and its **existence** as fixed:
- **Never rename `MainPage`.** A rename *technically succeeds* (display refs are by internal ID, so the build
  stays green), which is exactly the trap: a green build carries no signal about a name change either way.
  After a rename the SolutionCenter preview anchor is detached and the canonical home name points at a
  different page. Build-green is NOT evidence the rename was safe.
- **Never delete `MainPage`.** It always exists by design.
- **Keep real content in `MainPage`** even when it is not the runtime's first screen, so SolutionCenter always
  has a thumbnail to render for this solution in the solution list.
- **Wanting to keep an older home page around is not a reason to rename.** Leave `MainPage` named as it is
  and point the Startup layout's Content region at the new page instead.

### Coexisting with the "Home" landing pattern
The documented good practice is a separate **`Home`** landing page, a Responsive Dashboard with two
`ChildDisplay`s in star columns (so it reflows to mobile); the *Asset Monitor Demo* is the reference. That
pattern is fine and **does not require touching `MainPage`**: build `Home`, point `Startup -> Content` at
`Home`, and **leave `MainPage` in place** as the preview anchor. Do NOT "consolidate" the two by renaming.
having both an orphaned-looking `MainPage` and a wired `Home` is the *intended* state, not a cleanup target.
(This is the exact mistake to avoid: an orphaned `MainPage` with `referencesFound: 0` is normal here, **not**
a signal to retire or rename it.)

## The rule
When you author a solution's operator first / home screen:
- Either author your content INTO the page already in the Startup layout's Content slot (the template's
  `MainPage`), OR assign your new page to the Startup layout's Content region.
- Either way the Content slot must end up holding a real, populated page. That page is both the first screen
  and the preview, so make it presentable (project name plus at-a-glance info is a good default home / cover).

**"Populated" depends on the page's panel type.** A Canvas page holds its content in `Elements`; a responsive
Dashboard holds it in `Cells` / `Xaml` (often composing child displays via `ChildDisplay`). Judge a Dashboard
home by `Elements` alone and you misread a fully-built page as blank. The authoritative Canvas-vs-Dashboard
split lives in the `DisplaysList` schema (`get_table_schema('DisplaysList')` → CommonMistakes: *"Use 'Elements'
for Canvas displays, 'Cells' for Dashboard displays"*). This is exactly what mis-fired in the invariant linter's
first `IL001b` cut: corrected to count `Elements` **or** `Cells` **or** `Xaml` children (see
`.claude/tools/invariant-linter/`).

`DisplaysLayouts` is a document object: read the `Startup` row's `Regions` JSON first, change the Content
region's `Page`, then write the whole document back.

## What this prevents
The anti-pattern is to author a new "first page" and never wire it into the Startup layout's Content region,
leaving the slot on an empty or placeholder page. Two failures follow from that one omission:
- run the application and the first screen is blank;
- select the solution in SolutionCenter and the preview is blank.

Never finish a solution with the Startup layout's Content region pointing at an empty or placeholder page.

## Where the rule is enforced, and where you enforce it yourself
The MCP data tools enforce the protection: `rename_objects` / `delete_objects` against `MainPage` is rejected
with the `PROTECTED_HOME_DISPLAY` error code (Designer and Console MCP). That guard covers the data tools.
The Designer UI tree-context-menu rename path is a different route, so apply the rule yourself when working
in the UI tree.

Supporting references, all consistent with the rule above:
- docs.tatsoft.com *Displays List Reference* lists `MainPage` under Special Pages as "Cannot be renamed", and
  carries the carve-out in its "Safe Renaming" section.
- The `Home`-pattern pages (*Responsive Design and RESS*, *Asset Monitor Demo*) carry the "leave MainPage in
  place; never consolidate by renaming" guard.
- Solution Center *Workspace Reference*: a blank preview means an unrendered or empty `MainPage`, not a
  missing one (`MainPage` / ID 0 always exists). Diagnose the content, not the existence.

Captured 2026-05-31 from a live build; references re-checked 2026-06-07.
