# Convention: calling a Server Script Class from a Server Script Task

The call form that works depends on the calling domain and on how the class was authored. Read this before
wiring a Server Task to call a Server Class.

## Pick the call form by domain

From a **Server-domain Script Task**, don't rely on the canonical form
`@Script.Class.<ClassName>.<MethodName>(args)`: it can raise **`CS0246`** ("type or namespace could not be
found") even when the class and method exist and the syntax is correct. The `@Script.Class.` prefix parses,
but the method binds to the class *collection* rather than the singleton instance. Use one of the forms
below from a Server Task.

## What works

- **Class → Class** (a Server Class calling another Server Class): `@Script.Class.X.Y()` works.
- **Namespace-shape classes** (`ClassContent = Namespace`): call by plain fully-qualified name from a Server
  Task, `MyCompany.Utilities.Processor.Process();`.
- **Methods-shape class from a Server Task, use the programmatic call:**
  `TK.Run.ExecuteClassMethodOnServer<T>(className, methodName, args...)`. This bypasses the wrapper. Or inline
  the formula directly into the Task.

## Shared classes: author in Namespace mode with an explicit `namespace Script { ... }`

A class authored in **`Methods` mode does not land in `namespace Script`**. So a cross-class call written as
`Script.<ClassName>.<Method>(...)` fails **`CS0234`** ("the type or namespace name '<ClassName>' does not
exist in the namespace 'Script'") while the class itself still compiles. For a shared helper class other
scripts will call (KPI helpers, counters, common utilities), author it in **`Namespace` mode** with an
explicit wrapper:

```csharp
namespace Script { public class KpiHelpers { /* ... */ } }
```

Then `Script.KpiHelpers.<Method>()` resolves from tasks and expressions as expected.

## Symptom → cause

| Error | Cause |
|---|---|
| `CS0103` | bare class name, missing the `@Script.Class.` prefix |
| `CS0234` | the `@` sigil was omitted, **or** the target class is `Methods`-shape and never landed in `namespace Script` (see the shared-classes rule above; re-author it in `Namespace` mode) |
| `CS1061` | the `.Class.` segment was omitted |
| `CS0246` | canonical form called from a Server Task, see above; use `TK.Run.ExecuteClassMethodOnServer` |

*Check your build: if `@Script.Class.X.Y()` compiles cleanly from a Server Task on your installed build, use
it directly; otherwise use one of the forms above.*
