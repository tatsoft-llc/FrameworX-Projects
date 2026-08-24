# Pattern: referencing slash-containing UNS tag paths in Scripts & Expressions

The authoring rule to know before you script against an asset-tree (folder) tag path.

## The rule

In a Script or Expression body, FrameworX walks UNS tags with `.` (dot). A `/` in a script body is the
**C# division operator**, not a path separator: so `@Tag.Area/Line/Temp` parses as `@Tag.Area` divided by
`Line` divided by `Temp`, which is not the path you meant and does not compile.

When a UNS tag path genuinely contains `/` (an asset-tree folder separator, or a TagProvider whose branch
separator is `/`), use the **parenthesized-quoted escape**:

```csharp
// CORRECT, the "/" is data inside the quoted literal, not syntax
var t = @Tag.<Provider>.("MODEL/INPUTS/Temperature");
@Tag.<Provider>.("MODEL/OUTPUTS/Setpoint") = newSetpoint;

// WRONG, "/" is division here; everything after the first "/" is lost
var t = @Tag.MODEL/INPUTS/Temperature;
```

- The dotted form `@Tag.X.Y.Z` is for paths whose segments are **identifier-only** (letters / digits / underscore).
- The parenthesized-quoted form `@Tag.<Provider>.("…")` is the escape for any path with a **non-identifier**
  character (a slash, a dot inside a name, a leading digit) under a TagProvider namespace.

## Why `/` stays division

Script bodies are real C#, tag arithmetic has to keep working:

```csharp
var halfTemp = @Tag.Temperature / 2;          // division, must stay division
var ratio    = @Tag.FlowRate / @Tag.Pressure; // ditto
```

If `/` meant folder traversal, every arithmetic expression would silently re-bind to phantom child-tag
lookups. The boundary between "UNS folder path" and "script math" is the quoted literal: that is where the
string is interpreted as a path.

## Confirm before you rely on it

The parenthesized-quoted form is the documented one, confirm it in the product docs (`search_docs("MQTT
Integration")`). An `@Tag["path/with/slash"]` indexer form *may* also work but is not the documented/confirmed
answer; prefer the parenthesized-quoted form. When a path's separator is uncertain, check the TagProvider's
branch-separator setting: providers that use `/` carry literal slashes in their tag names and need the escape.
