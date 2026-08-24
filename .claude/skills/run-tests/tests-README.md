# Tests: the per-project test harness

The test harness proves a built solution does what its spec asked. It is verify-your-work made repeatable.
The `run-tests` skill drives it; this README is the reference for the pieces. Each project keeps its test data
under `Sites/<Name>/Tests/`; the checker is shared at `.claude/skills/run-tests/check.py`.

**Prerequisite:** Python 3.x on PATH (`python --version`). The checker is a Python script.

## One checker, two assertion sets

The `.dbsln` is an encrypted SQLite file, so the harness reads solution structure **through the product over
MCP**, not by parsing the binary (see `KnowledgeBase/References/dbsln-format-note.md`). The collect step
(`collect-live.md`) gathers structure and live values into `Sites/<Name>/Tests/results/actual.json`, and
[`check.py`](check.py) asserts against `Sites/<Name>/Tests/expected.json`. Two assertion sets run from that one
collected file:

1. **Structural gate (deterministic).** Counts and domain UserTypes. The collected numbers are stable across
   re-takes of the same built solution, so this set is identical golden-run to re-take. Run it alone with
   `--structure-only` (good for CI, and for the determinism check):

   ```
   python .claude/skills/run-tests/check.py Sites/<Name>/Tests/expected.json Sites/<Name>/Tests/results/actual.json --structure-only
   ```

2. **Live gate (tolerant).** Runtime invariants on a target tag: present, good quality, recent timestamp, in
   range, and moved between two reads. Live values change, so this set checks invariants, not exact numbers.
   Run the full gate (structure + live):

   ```
   python .claude/skills/run-tests/check.py Sites/<Name>/Tests/expected.json Sites/<Name>/Tests/results/actual.json
   ```

## Files (per project)

| Path | Role |
|---|---|
| `Sites/<Name>/Tests/expected.json` | Golden expectations, derived from the spec's acceptance checks. |
| `.claude/skills/run-tests/check.py` | The shared checker. Structural gate (`--structure-only`) and full live + structural gate. |
| `.claude/skills/run-tests/collect-live.md` | The MCP call sequence that produces `Tests/results/actual.json`. |
| `Sites/<Name>/Tests/results/` | Run output (gitignored): the run report, captured gate output, and `actual.json`. |

## The expected.json shape

```json
{
  "solution": "...",
  "structure": {
    "userTypes": { "domain": ["Tank", "Pump", "..."] },
    "uns":       { "topLevelTagCount": 13 },
    "alarms":    { "itemCount": 32, "groupCount": 3, "areaCount": 2 },
    "historian": { "tagCount": 40, "tableCount": 3 },
    "displays":  { "count": 20 },
    "security":  { "userCount": 3 }
  },
  "live": {
    "tags": [
      { "id": "tank-level-line0", "match": "BrewLine", "memberHint": "Level",
        "qualityGood": true, "maxAgeSeconds": 30, "range": [0, 100], "mustMove": true }
    ]
  }
}
```

## The actual.json shape (what the collect step writes)

```json
{
  "solution": "...",
  "structure": {
    "userTypes": { "domain": ["Tank", "Pump", "..."] },
    "uns":       { "topLevelTagCount": 13 },
    "alarms":    { "itemCount": 32, "groupCount": 3, "areaCount": 2 },
    "historian": { "tagCount": 40, "tableCount": 3 },
    "displays":  { "count": 20 },
    "security":  { "userCount": 3 }
  },
  "live": {
    "tags": [
      { "id": "tank-level-line0", "resolvedPath": "Tag.BrewLine[0]/.../Level",
        "quality": "Good",
        "read1": { "value": 41.8, "ageSeconds": 4 },
        "read2": { "value": 43.2, "ageSeconds": 1 } }
    ]
  }
}
```

## Deriving expected.json from the spec's acceptance checks: the worked example

The expectations file is a *translation*, not an invention: every node in `expected.json` traces back to one
acceptance check in the spec, and every acceptance check lands as a node. The validated worked derivation is
the Brewery example: read `Templates/Examples/Brewery/brewery-plant.spec.md` **Section 8 (Acceptance
checks)** side-by-side with `Templates/Examples/Brewery/brewery-plant.expected.json` and you can see each
check become an assertion:

| Spec acceptance check (Brewery §8) | expected.json node | Derivation rule applied |
|---|---|---|
| "The UNS exposes the domain instance tags `BrewLine` and `Simulation` … and their selection references" | `structure.uns.domainTagsPresent: ["BrewLine", "Simulation", "refBrewLine", "refSimulation"]` | **Present-by-name beats raw totals**: built-in tags are hidden from MCP counts, so asserting a raw tag total is brittle; asserting the named domain tags is stable. |
| "32 alarms exist across 3 groups and 2 areas" | `structure.alarms: { itemCount: 32, groupCount: 3, areaCount: 2 }` | **Exact counts only where stable**: alarm/historian/display counts don't drift across re-takes or upgrades. |
| "40 historian tags log into 3 tables" / "20 displays exist" | `structure.historian`, `structure.displays` | Same rule. |
| "At least 3 users are defined" | `structure.security.userCountMin: 3` | **Minimum, not exact**, where the product adds rows (an upgrade adds a user account), a `Min` assertion survives that. |
| "a Tank Level … holds a value with good quality, a timestamp under 30 seconds old, within its 0..100 range, and the value changes between two reads" | `live.tags[0]: { match, memberHint, qualityGood, maxAgeSeconds, range, mustMove }` | **Live checks assert invariants with tolerance, never exact values**: the simulation moves the number; present + good quality + recent + in-range + moved is what stays true. |
| "The domain UserTypes are present at runtime: a `BrewLine` instance contains Tank instances …" | covered by the live tag's resolution through the instance members | **Confirm types via an instance's members at runtime** rather than a config-table type count. |

The derivation rules, summarized: (1) assert **stable invariants, not raw totals**, present-by-name for
domain objects, exact counts only where re-take-stable, `Min` where the product adds rows; (2) **live values
get tolerant invariants** (present / quality / age / range / moved), never exact numbers; (3) every assertion
must trace to a spec acceptance check, if you can't point at the check, don't assert it; if a check has no
node, the expectations file isn't done.

## Adding a new project

1. Fill the project's `Sites/<Name>/Specifications/` with acceptance checks (the checklist at the end of
   `Requirements.md`).
2. Translate those checks into `Sites/<Name>/Tests/expected.json` in the shape above, applying the derivation
   rules from the worked example.
3. Run the `run-tests` skill. It builds, starts the runtime, collects, and runs both gates.

## Worked example

The validated golden is the Brewery example under `Templates/Examples/Brewery/`. See its
`brewery-plant.expected.json` and `validation-2026-05-30.md` for a complete expected-file and run record. (The
example uses named files, `brewery-plant.expected.json`, `results/brewery-plant-actual.json`, because it
lives outside `Sites/`; a per-project Site uses the unqualified `Tests/expected.json` + `Tests/results/`.)

## Determinism, recorded

The structural gate is deterministic and should be reported as such. The live gate passes on invariants while
the underlying values change between runs; that difference between a golden run and a re-take is expected and
is the reason the live checks carry tolerance. Record both in `Tests/results/` so the determinism story is
visible, not assumed.
