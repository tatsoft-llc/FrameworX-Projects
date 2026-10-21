# Pattern: MCP write & schema field gotchas

The config-table field names and write semantics that bite the first time you author through the MCP. Always
`get_table_schema(<TableType>)` and a dry-run write before authoring a table you haven't written before. But
these are the ones that recur.

> The field lists below (the `DataType` enum, the composite keys) **mirror `get_table_schema` output as of one
> build**: a build-pending convenience. The live `get_table_schema(<Table>)` call is authoritative; trust it
> over this page when they differ. The *value* here is the gotcha framing, which fields bite, and why, not
> the enumeration itself.

## Reference objects by Name, not by ID: and order your writes

Every FrameworX write surface (JSON import, `write_objects`, reports) references other rows by their
human-readable **Name**, never by a hand-encoded `@type:id` token. Don't invent ID tokens.

Because Name→object resolution needs the target to exist, **split a write that has forward references into
passes**: write the skeletons first (the objects being referenced), then the rows that reference them. A single
batch that references a row it also creates later in the same batch can fail to resolve.

## "Description" vs "Notes": pick by whether the row defines or references

Name-identified *definition* rows use a **`Description`** field; composite-key / *reference* rows use a
**`Notes`** field. Examples: `UnsTags`, `UnsUserTypes`, `DevicesChannels`, `DevicesNodes`, `DisplaysList` →
`Description`. `DevicesPoints`, `ScriptsExpressions` → `Notes`. Match the field to the row type: a comment
written to the other one is not stored, and the write does not flag it.

## DevicesPoints: identity and types come from the protocol, not the UNS

- Row identity is **`TagName`**, not `Name` (uniqueness is `TagName` + `Node`).
- The parent-node reference field is **`Node`** (not `NodeName`); always populate it, a point whose Node
  reference is empty is rejected on import and the channel comes up with `TotalPoints = 0`.
- `DataType` is the **driver's** type taxonomy, **not** the UNS tag taxonomy: there is no `Double` or `Bool`
  here. The full enum: `Native, Bit, Byte, Char, Word, Short, Dword, Integer, Long, ULong, BCD, LBCD, Single,
  Real, ASCII, Unicode, OPCDateTime, Timer, Counter, Control, SBCD, LSBCD`. Map `Double → Real`, `Bool → Bit`
  when authoring the device side.

## Composite-key tables have no `Name`: and a write needs the full key

Four config tables are identified by a **pair of columns**, not a `Name`:

| Table | Composite identity (key columns) |
|---|---|
| `DevicesPoints` | `TagName` : `Node` |
| `AlarmsItems` | `TagName` : `Condition` |
| `HistorianHistorianTags` | `TagName` : `HistorianTable` |
| `ScriptsExpressions` | `ObjectName` : `Expression` |

- **There is no `Name` field on these**: don't send one, and don't expect one back.
- **Write is strict: supply the full composite.** Read and delete tolerate the bare primary (e.g. `TagName`
  alone acts on *every* row across the secondary axis: handy for "delete every point for this tag"), but a
  *create* needs both halves or the secondary axis is ambiguous.
- On `AlarmsItems` specifically: **`Area` lives on the item, not the group, and `Priority` is per-item, not
  per-group.** Author both on the alarm item.
- `get_table_schema(<table>)` emits the `KeyColumns` for these: read it before authoring.

## DatasetsQueries: read the SQL body back; "Modified" does not attest it

A `DatasetsQueries` write that carries `SqlStatement` is not attested by its envelope: the stored body can end
up different from what you sent while the result reports "Modified". Three rules:

- **After any DatasetsQueries write carrying `SqlStatement`, read `SqlStatement` back and compare.** The write
  counter does not attest the body landed. An identical re-send repairs a stale row.
- **Avoid `get_objects(detail='full')` on DatasetsQueries around your write window.** The full-detail read
  navigates the query editor surface, and an editor open on that query is what puts the stored body at risk.
  Read `detail='summary'` unless you are actively editing that specific query.
- **Keep stored references tokenized when re-authoring.** A row read back can carry its tag references in a
  tokenized ID form; keep them in that form when round-tripping through a workspace JSON import. Converting
  them to name-form slash paths can mangle the reference on import. (Authoring *new* rows by Name stays
  correct: the platform tokenizes on write; this rule is about not re-writing what the product already
  stored.)

> **Scope:** re-check the read-back against your own build, behavior here moves between builds and the
> read-back costs one call either way. The tokenized-reference rule is not build-dependent. Keep it.

## ReportsForms: there is no `Contents` field; the body is not config

The config API carries the report **row** (name, format, save settings), not the report **document body**, a
`ReportsForms` write that includes a `Contents` (or similar body) field is rejected. Author the report body in
the Designer's report editor; over the MCP you create and configure the form row, then hand the body work to
the editor. (Seen independently on two projects: this is a real API boundary, not a field-name typo.)

## Field names are case-sensitive and diverge from the UI labels

The Designer UI label is not always the JSON-API field name, and casing matters. Known divergences:

- Historian: **`DeadBand`** (capital B), and **`HistorianTable`** (not `Table`). The logging rate lives on
  the table (`SavePeriod` / `SaveOnChange` / `SaveOnEvent`): there is no per-tag `Interval`.
- Devices: a node's parent-channel reference is **`Channel`** (not `ChannelName`).
- Datasets: the SQL body is **`SqlStatement`** (not `Query`).
- Security: the contact field is **`ContactInfo`** (not `Email` / `FullName`); `SecurityUsers` has **no
  `Description`** column; a user's `Password` is read-only on the config surface (set it through the product,
  not a column write).
- Scripts: "Object" → `ObjectName`; "Label" → `Notes`; "Execution Mode" → `Execution` (enum values like
  `Trigger_TimeInterval` / `Change_Startup` / `Trigger_TimeOfDay`).

A `FIELD_TYPO` / unknown-field error almost always means a label-vs-field-name or casing mismatch. Check the
exact field name with `get_table_schema` first, then a dry-run write, before authoring at scale.

*(These were observed against one build; if `get_table_schema` shows a different field name on your installed
build, the schema wins. Verify, don't assume.)*

## `list_dynamics()` overview vs. the per-dynamic schema: trust the schema

The no-argument `list_dynamics()` response is a *summary*, and on two points it disagrees with the
authoritative per-dynamic schema you get from `list_dynamics('<Type>')`. Both were observed on FrameworX
10.1.5; fetch the specific dynamic before writing it.

| Dynamic | Overview says | Actual property |
|---|---|---|
| `BargraphDynamic` | `Direction` | **`Orientation`**, enum `VerticalUp / VerticalDown / VerticalCenter / HorizontalLeft / HorizontalRight / HorizontalCenter` |

And the colour dynamics' `ChangeColorItems` appears in the overview's `commonPatterns` as a **bare array**:

```json
"ChangeColorItems": [ { "Type": "ChangeColorItem", "ChangeLimit": 0, "LimitColor": "#FF808080" } ]
```

but the authoritative shape (`get_table_schema('DisplaysList')` → `ExtendedInfo.CanvasExample`, and the
`quickStart` on `list_elements('Canvas')`) is **wrapped in a `ColorChangeList`**:

```json
"ChangeColorItems": { "Type": "ColorChangeList",
                      "Children": [ { "Type": "ChangeColorItem", "ChangeLimit": 0, "LimitColor": "#FF808080" } ] }
```

The wrapped form imports clean. The bare form was not tested, but since the overview is demonstrably the
looser of the two sources on `Direction`, prefer the wrapped form.

*(Caveat: verified only to a clean write/import on that build; neither shape was exercised at runtime.)*
