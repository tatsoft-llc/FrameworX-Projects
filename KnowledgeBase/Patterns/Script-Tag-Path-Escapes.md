# Pattern: referencing slash-containing UNS tag paths in Scripts & Expressions

How to reach a tag that lives under asset-tree folders from a script body.

> **Corrected in v1.0.1.** Earlier versions of this page said that `/` in a script body is always the C#
> division operator and that `@Tag.Area/Line/Temp` does not compile. For plain UNS asset-folder paths the
> opposite is true: the slash form compiles and the dotted form fails. See *Evidence*.

## The rule for plain UNS asset-folder paths

Use the **slash form**, the same full path you use everywhere else in the product:

```csharp
// CORRECT: compiles, and matches the path shown in the Designer and in config fields
@Tag.Plant/Pump01/Temperature = 130;
@Tag.Plant/Tank01/Level = 98;
```

```csharp
// WRONG: dotted traversal does NOT walk asset folders
@Tag.Plant.Pump01.Temperature = 130;
// CS1061: 'UnsTags' does not contain a definition for 'Plant'
```

The `@Tag.` preprocessor resolves the longest matching tag path before C# sees the line, so the slashes are
consumed as part of the path token, not as division.

**One path, one spelling.** This is the same string you put in `AlarmsItems.TagName`, `DevicesPoints.TagName`,
a display binding and `set_object_value`. There is no separate script spelling to remember.

## Evidence

Compile-tested on FrameworX 10.1.5, in Display code-behind, on a solution whose tags live at
`Plant/<Asset>/<Point>`:

| Form | Result |
|---|---|
| `@Tag.Plant/Pump01/Temperature = 130;` | compiles clean; full solution build, 0 errors |
| `@Tag.Plant.Pump01.Temperature = 130;` | **CS1061**: `'UnsTags' does not contain a definition for 'Plant'` |

The dotted form failing with CS1061 (rather than CS0103 on an unknown identifier) is the tell: `@Tag` resolves
to a generated `UnsTags` type whose members are leaf tags, not folder nodes.

## Arithmetic on a folder-path tag: assign to a local first

Whether a trailing `/ 2` after a folder-path tag stays division in the same expression has not been tested.
Sidestep the question: read the tag into a local, then do the arithmetic on the local.

```csharp
double level = @Tag.Plant/Tank01/Level;   // safe: no trailing operator
double half  = level / 2;                 // plain C# arithmetic on a local
```

Plain division between tags without folders is unaffected:

```csharp
var ratio = @Tag.FlowRate / @Tag.Pressure;   // division, as expected
```

A clean compile is not a runtime guarantee. After a script writes a tag, read the tag back before calling the
work done.

## TagProvider paths: a different case

For a tag published by a **TagProvider** whose branch separator is `/`, the documented form is the
parenthesized-quoted escape:

```csharp
var t = @Tag.<Provider>.("MODEL/INPUTS/Temperature");
@Tag.<Provider>.("MODEL/OUTPUTS/Setpoint") = newSetpoint;
```

This resolves through the provider namespace, not the local UNS asset tree, and it was not part of the compile
test above. Confirm it in the product docs (`search_docs("MQTT Integration")`), and check the provider's
branch-separator setting when a path misbehaves.

## When sources disagree, trust the compiler

If a guide, an example or an AI session tells you something different about `/` in script bodies, write the
one-line probe and read the compile diagnostics. A `write_objects` on a Display or Script returns the compile
status and diagnostics immediately: it is the cheapest arbiter available, about one call.
