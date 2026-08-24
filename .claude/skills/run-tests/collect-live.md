# Collecting actual.json over MCP

This is the call sequence the `run-tests` skill follows to gather the real structure and live
values from the running product and write `Sites/<Name>/Tests/results/actual.json` in the shape
`check.py` expects. The AI runs these calls; the output is a JSON file, not prose.

Bootstrap first (`open_solution` on the `ai-test-` sandbox). The runtime must be up on the
Development profile before the live section.

## Structure (counts and domain UserTypes)

Use the Designer or Console MCP. For each, record the actual number.

| Field | How to collect |
|---|---|
| `userTypes.domain` | `get_objects` the UserTypes; list the names that match the expected domain types. |
| `uns.topLevelTagCount` | `browse_object_model` the UNS root (or `get_objects` UnsTags); count the top-level tags. |
| `alarms.itemCount` / `groupCount` / `areaCount` | `get_objects` the Alarms items, groups, and areas; count each. |
| `historian.tagCount` / `tableCount` | `get_objects` the historian tags and tables; count each. |
| `displays.count` | `get_objects` the display list; count. |
| `security.userCount` | `get_objects` the security users; count. |

Write these into `structure` in the actual.json exactly as `expected.json` names them.

> Collecting these through the product is the only path: the `.dbsln` is encrypted, so the structure
> cannot be read by parsing the file (see `KnowledgeBase/References/dbsln-format-note.md`). Run the
> structural gate with `check.py --structure-only` against the collected numbers; run the full gate for
> structure plus live.

## Live values

For each entry in `expected.live.tags[]`:

1. **Resolve the leaf path.** Use `runtime_browse_object_model` (or `runtime_search_uns`) to find a
   concrete leaf tag that matches the entry's `match` and `memberHint`. For the brewery example,
   that is a Tank `Level` member under a `BrewLine` instance. Record it as `resolvedPath`.
2. **Read it twice.** Call `runtime_get_value` on the resolved path. Record `read1` with its
   `value` and the age of its timestamp in seconds (`ageSeconds`). Wait a few seconds (long enough
   for the simulation to move the value). Call `runtime_get_value` again. Record `read2` the same
   way.
3. **Record quality.** Put the runtime's quality string in `quality` (the checker passes when it
   contains "good").

Write each as an object in `live.tags[]` with the same `id` the expected entry uses, so `check.py`
can match them.

## Then run the checker

```
python .claude/skills/run-tests/check.py Sites/<Name>/Tests/expected.json Sites/<Name>/Tests/results/actual.json
```

## If a value is missing from the MCP surface

If `runtime_get_value` returns a value without a quality flag or without a timestamp, you cannot
fill `quality` or `ageSeconds` honestly. Do not guess. Record what you got, mark the gap, and add it
to the `## MCP findings` block in your summary. A test that cannot read what it needs to assert is
itself a finding about the tool surface.
