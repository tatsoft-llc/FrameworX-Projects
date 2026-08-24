# Pattern: a clean config write is necessary, not sufficient (the registration chain)

The first thing to check when the config is right and the option still isn't there. A successful
`write_objects` lands a row in the solution's config table. A connector, provider, or UI entry only becomes
**user-reachable** if a separate **registration substrate** exists in the installed product's file tree. The
write path goes straight to the config surface: it does not run the discovery / filter / default-seeding
steps the Designer's own dialog runs.

## Why this happens

The AI (over the MCP) and a human (in the Designer GUI) write to the **same** config surface. There is no
separate "AI database." What differs is the **pre-call plumbing**: the Designer's dialogs scan the install
tree, filter to what's registered, and seed defaults *before* the row is written. `write_objects` does none
of that. So a table write can succeed for an option that stays unreachable in the UI, because the thing that
makes it *appear* lives on disk, not in the config table.

The shape to recognize: **"code clean, write OK, combo empty."** The row is there; the dropdown is not, so
check the substrate on disk before re-writing the row.

## The substrate map: verify the file, not just the row

The install tree is **flat** (`C:\Program Files\Tatsoft\FrameworX\fx-10\` with `DBProviders\`, `Protocols\`,
`Templates\`, etc. directly under the root, no nested `bin\` subpath). For each user-facing surface, the
substrate that must exist:

| User-facing surface | Backing substrate (must exist on disk) |
|---|---|
| Channel **Protocol** combo | `Protocols\T.ProtocolDriver.<Name>.config.xml` **+** the assembly it names |
| **UNS Tag Provider** | the *same* protocol XML with `<TagProvider Enable="true">` |
| Dataset **DB Provider** combo | `DBProviders\<Provider>.xml` **+** the connector DLL |
| **Historian storage** combo | `HistorianStorage\<Backend>.xml` **+** its DLL |
| Protocol-specific Node/Point editor | the same protocol XML **+** the editor DLL (a generic editor in place of the protocol-specific one means the DLL is missing) |
| New-Solution **template** | `Templates\<Name>.dbsln` |
| Sidebar button / ribbon entry / wizard step | compiled into the Designer UI assembly (no XML, verify by screenshot) |

**The driver-config filename is matched by an exact glob, the dot matters.** The loader globs
`T.ProtocolDriver.*.config.xml`; a file that doesn't match the glob (e.g. missing the dot:
`<Name>config.xml`) is not picked up, and the driver stays unregisterable **even with its DLL present.**
Check the filename character by character before looking anywhere else.

## Install tree is not the build tree

A DLL or XML present in a **build/source tree** may never have been copied into the **installed** product;
the channel then fails at runtime with nothing in the config to explain it. When a registered option doesn't
work, verify the **install** tree (`…\Protocols\`, `…\DBProviders\`), not the dev tree. "The file exists in
the build output" is not "the file is in the installed product."

## The verify recipe

1. **Write** the config row.
2. **Confirm** it landed: `get_objects(detail='full')`, diff the fields you wrote.
3. **Inspect the substrate file** on disk (the XML from the table above) and **its companion DLL(s)**.
4. **Confirm reachability from the live UI**: the option actually appears in the combo/picker
   (`get_screenshot`). A row in the table is not a visible option.

## Sibling failure: the solution was never built

A related "config is fine, nothing flows" case with a *different* fix: starting the runtime against an
**unbuilt** solution. The channel starts (`IsRunning = 1`) but **`TotalPoints = 0` and tag values sit at
`StartValue`**: the points exist in config but were never bound to the live driver, so read `TotalPoints`,
not just `IsRunning`, when you check a channel. Not a registration or device fault: **build, then start.** (This is one of three causes of `TotalPoints = 0`. See the differential
on docs.tatsoft.com → *Devices Channels Reference* → "Diagnosing a channel reading TotalPoints = 0".)

*(Install-tree paths and the flat layout were observed on the builds in scope, confirm against your
installed product. The principle, write the row, then verify the substrate and the live reachability,
holds regardless of layout.)*
