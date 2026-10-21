# Convention: the three script environments and the `@`-namespace

Read this before writing any C# in a solution. FrameworX runs user code in **three distinct places**, each
with its own threading model and its own rules about what you may even declare. Picking the wrong one is the
single most common source of script behavior that compiles green and then misbehaves at runtime.

*Provenance: distilled from real FrameworX debugging sessions on FrameworX 10.1.5. The product serves the full
scripting reference live (`search_docs("Scripts")`), so this file carries only the model and the judgment
calls, not the API surface. Verify specifics against your installed build.*

## The `@`-namespace: how you reference platform objects

FrameworX injects an `@` namespace. **Always use it; never shadow these with plain local variables.**

| Reference | What it is |
|---|---|
| `@Tag.<path>` | a tag (the live process variable) |
| `@Tag.Global.<name>` | a global-scope tag |
| `@Script.Class.<Class>.<Method>(...)` | call a method on a Script Class; **read `Script-Class-Invocation.md` first**, this form has a Server Task gap |
| `@Dataset.Query.<Query>` | a dataset query object |
| `@Info.Trace("...")` | write to the trace/log window |
| `this.CurrentDisplay.GetControl("name")` | get a control (**code-behind only**) |

Two rules that follow from it:

- **Tags are dynamically typed: cast when you read.** `(int)@Tag.X`, `Convert.ToDouble(@Tag.Y)`,
  `Convert.ToString(@Tag.Z)`. A double tag concatenated into a string calls `.ToString()` with the *machine
  locale*; see the InvariantCulture gotcha in `../Patterns/Script-Runtime-Gotchas.md`.
- **Tag pointers redirect a reference tag at runtime:** `@Tag.RefPump.Link = @Tag.Pump1.GetName();` is the
  way to repoint a whole panel at a different underlying device without duplicating the screen.

For plain UNS asset-folder paths, write the slash form, `@Tag.Plant/Pump01/Temperature`; the dotted form does
not walk asset folders. Tags published by a TagProvider whose branch separator is `/` use the
parenthesized-quoted escape. Both cases: `../Patterns/Script-Tag-Path-Escapes.md`.

## 1. Script Task: background, its own thread

- Runs on its **own thread**, so it can do heavier or blocking work without freezing the UI.
- Triggered on a **period** (3 s, 5 s, 24 h), on a **tag value change**, or **on startup**.
- **Pure statements, top to bottom; NO method definitions.** You write the body, not methods. Local
  variables (`int n = ...`) are fine; `void Foo() { }` is not.
- **`await` works here**: the generated wrapper is async, so
  `await @Dataset.Query.Q.SelectCommandAsync()` compiles fine.
- Good for: watchdogs, polling/read loops, periodic housekeeping, reacting to a tag change, one-shot startup
  bootstrap (seeding a table, wiring tag pointers).
- Typical body: call into a Script Class and/or set tags. Keep the heavy logic in the class.

## 2. Script Class: reusable methods

- **This is the only place methods live.** Called from a Task or from code-behind.
- Holds shared state in fields. For a shared **external resource** (a socket, a device handle) use `static`
  fields so there is exactly ONE process-wide, independent of how many times the class is instantiated,
  and guard it with a `static` lock (gotcha 1 in `../Patterns/Script-Runtime-Gotchas.md`).
- Home for transport wrappers, batch-apply helpers, converters.
- **Authoring shape matters for cross-script calls.** A class other scripts will call should be authored in
  **`Namespace` mode** with an explicit `namespace Script { ... }` wrapper. The `Methods` shape does not land
  in `namespace Script`, and cross-class calls then fail with `CS0234`. Full rule: `Script-Class-Invocation.md`.

## 3. Display code-behind: the single UI thread

- Runs behind a Display on the **single UI thread**. Heavy or blocking work here **freezes the display**;
  push it to a Script Task instead (gotcha 5).
- Event handler shape:
  `public async Task MouseLeftButtonDown1(object sender, System.Windows.Input.InputEventArgs e)`
- Lifecycle hooks: `DisplayOpening()`, `DisplayIsOpen()`, `DisplayClosing()`, `DialogOnOK()`.
- Access controls via `this.CurrentDisplay.GetControl("name") as <WpfType>` (WPF types such as `Rectangle`,
  `ImageBrush`, `BitmapImage`).
- **Do not pass optional/default parameters on a call from here into a Script Class**: the generated wrapper
  ignores C# defaults and throws `CS7036` (gotcha 2).
- Code-behind polling rate: leave it at the 1000 ms default unless the Display does measurable per-frame work.

## When you're handed FrameworX code

1. **Identify the environment first.** It dictates threading and whether method definitions are legal at all.
2. **Preserve the `@`-namespace exactly.** Don't rewrite `@Tag.` references as locals.
3. Match the surrounding style: thin one-line wrappers per command, batch `Apply*` methods that map tags onto
   setters, `@Info.Trace` at each step.
4. Remember that **script bodies full-replace on write**: read, merge, then write (`Working-Rules.md`).

## See also

- `Script-Class-Invocation.md`: calling a class from a Server Task (`CS0246` / `CS0234` traps)
- `../Patterns/Script-Runtime-Gotchas.md`: the eleven runtime traps
- `../Patterns/Script-Tag-Path-Escapes.md`: UNS paths that contain `/`
