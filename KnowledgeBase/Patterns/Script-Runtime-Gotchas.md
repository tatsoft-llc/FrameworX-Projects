# Pattern: FrameworX script traps that only surface at runtime

Eleven traps that cost real debugging time. Each compiles green (or worse, *runs* green) and fails later,
which is why they belong in a pattern file rather than being rediscovered per project.

*Provenance: field experience captured across real FrameworX builds on FrameworX 10.1.5. Gotcha 8's call
table was checked against the product's Dataset query API; the rest are observed behavior. Verify against your
installed build: the live product always wins.*

Environment model (Task vs Class vs code-behind) first: `../Conventions/Script-Environments.md`.

## Concurrency and threading

**1. Serialize a shared external resource with a `static` lock.** If a Task, a watchdog, and screen buttons all
hit the same socket or device handle, concurrent access corrupts it: resets, interleaved reads. Keep ONE
connection plus ONE `static readonly object _lock`, and wrap every access in `lock (_lock) { ... }`. Use
`static`, not instance, so serialization holds even if FrameworX instantiates the class more than once.

**5. Never block the UI thread in code-behind.** A 60-second blocking call, a network round-trip, or a tight
loop freezes the whole Display. Push heavy work to a Script Task, or make it non-blocking (fire-and-poll
instead of wait). Even a preview screenshot that shows/hides a window visibly stutters the UI while it runs.

## Cross-context calls

**2. Don't pass optional/default parameters across a code-behind to Script Class call.** FrameworX generates
an internal wrapper (`__Internal_<Class>_<Method>`) that does **not** honor C# default values. Calling
`Send("cmd")` from a Display when the method is `Send(string, int = 5000)` throws **`CS7036`**. Fix: pass every
argument explicitly (`Send("cmd", 5000)`), or expose a wrapper with no optional params. The default works fine
*inside* the class; only the cross-context call breaks.

**10. A read-back needs a value-returning transport, not a status int.** A `Send` that returns `1/0/-1` cannot
hand back a device value. Keep a parallel `SendGet` that returns the raw response string, then parse it (with
`InvariantCulture`). This is what lets a panel reflect live device state instead of just command success.

## Strings, locales, and SQL

**3. Use `InvariantCulture` for numbers you concatenate into strings**: SQL, device protocol commands, file
content. On a machine with comma decimals, `85.5` becomes `85,5` and breaks the statement. Keep a helper:

```csharp
string Fmt(double d) => d.ToString(System.Globalization.CultureInfo.InvariantCulture);
```

**4. Escape single quotes in SQL built by concatenation.** A recipe name or payload containing `'` breaks the
statement, and it is an injection risk. Wrap text values:
`"'" + (Convert.ToString(v) ?? "").Replace("'", "''") + "'"`. Prefer parameterized queries where the Dataset
supports them.

## Datasets

**8. SELECT and non-query are different calls, and the `*Async` ones must be `await`ed.**

| Call | Returns |
|---|---|
| `SelectCommandAsync()` | `Task<DataTable>` |
| `SelectCommand()` | `DataTable` |
| `ExecuteCommandAsync()` | `Task<int>` |
| `ExecuteCommand()` | `int` |

- SELECT uses `Select*`; INSERT / UPDATE / DELETE / DDL use `Execute*`.
- **`var dt = @Dataset.Query.Q.SelectCommandAsync();` silently hands you the `Task`, not the table.** Assigning
  that to a DataTable tag "works" with no compile error, then the tag is wrong at runtime. Always `await` the
  async form, or call the sync form deliberately.
- **Don't discard the `ExecuteCommandAsync()` int.** It is rows-affected; throwing it away makes a failed DDL
  or rejected INSERT completely silent, and the symptom surfaces much later as an empty table, which sends
  you looking at the connection instead of the SQL.
  `int n = await ...ExecuteCommandAsync(); @Info.Trace("seed=" + n);`
- Set `@Dataset.Query.Q.SqlStatement` before each call; reusing one query object is fine since you reset the
  statement each time.
- Seed tables with `CREATE TABLE IF NOT EXISTS` + `INSERT OR IGNORE` (SQLite) so bootstrap is idempotent and
  safe on every startup. **Caveat:** a row the operator *deletes* comes back on the next start; gate the seed
  on a flag row if deletions must stick.

**9. Delete/update DB rows by a KEY, not by grid row position.** The grid row number is a display index, not a
stable DB identity. Add `id INTEGER PRIMARY KEY AUTOINCREMENT`, use the row index only to look up the `id` in
the DataTable, then `DELETE ... WHERE id = <n>`. Note that `CREATE TABLE IF NOT EXISTS` will **not** add the id
column to a table that already exists: recreate it (development) or migrate it.

**11. A DataTable tag is a `TDataTable` wrapper, not a `System.Data.DataTable`.** `@Tag.X = someDataTable` works
(the platform unwraps on assign), so it is easy to assume the tag *is* a DataTable; then `@Tag.X.Rows.Count`
fails with **`CS1061`: 'TDataTable' does not contain a definition for 'Rows'**. The wrapper
(`T.Kernel.Tags.TDataTable`) exposes `.Value` (the real `System.Data.DataTable`), plus `GetRowsCount()`,
`GetColumnsCount()`, `RemoveRow(int)`, `RemoveAll()`, `Update(DataTable)`. Prefer the helpers; use `.Value` when
you need the real DataTable API (`Select`, `Rows[i]`, `Columns`). **Null-check `.Value`, not the tag**: a failed
query leaves the wrapper in place and empty.

## Defensive habits

**6. Guard external reads and check return codes** before using results. `File.ReadAllBytes` on a file a
previous command failed to write throws; check the command's return and `System.IO.File.Exists` first. Same
for DataTables (`dt == null`, index out of range).

**7. Trace liberally with `@Info.Trace`.** It is your only window into a running script: log the command sent,
the raw response, and the branch taken. Cheap insurance.

## See also

- `../Conventions/Script-Environments.md`: the three environments and the `@`-namespace
- `../Conventions/Script-Class-Invocation.md`: `CS0246` / `CS0234` when calling a class from a Server Task
- `Script-Tag-Path-Escapes.md`: UNS paths that contain `/`
