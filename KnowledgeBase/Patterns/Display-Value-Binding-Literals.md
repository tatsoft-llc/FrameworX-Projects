# Pattern: quote literal text in a Display control's value binding

A compile error that passes the write and surfaces at render. It bites the first time you put plain text into
a control's *value* field instead of its *caption*.

## What happens

A control's **value / `LinkedValue`** field treats anything that is **not numeric, not quoted, and not a
tag/object reference** as a **VB expression**. Feed it a bare literal: say the cell text `Cell 0,0`: and the
platform emits `Return Cell 0,0` into a generated VB function body, which trips a compile error at the
Designer's XAML-emit step:

- **`BC30205`** ("End of statement expected"), or **`BC30451`**.

Quote the literal before you write it: **`write_objects` accepts the unquoted form** and the config round-trips
faithfully. The failure only surfaces when the Display is **built or rendered**: it renders empty or fails to
load. A clean write and a clean config read-back are *not* evidence the Display works (the same reason
`Display-Authoring.md` says to confirm the rendered/resolved state).

## The fix

**Wrap literal display text in double quotes**, or use a tag reference:

```
"Cell 0,0"        ✅ a quoted string classifies as a constant: compiles clean
@Tag.Area/Value   ✅ a tag reference resolves to the live value
Cell 0,0          ❌ parsed as a VB expression → BC30205 at render
```

## Why "it worked on my Label" doesn't transfer

A **Label** control can compile clean with a bare literal because its dynamic's save body is effectively
inert; a **TextBox** (and Dashboard text cells) does **not**. Its generated body runs the literal through the
VB compiler. So quote the literal in every control: one that rendered fine in a Label will break in a TextBox.
Don't generalize "it worked in that control" across control types, the value-binding path differs.

## Label: compiles clean, but can still *render* a placeholder

Refinement to the section above (observed on FrameworX 10.1.5). A Label whose `LinkedValue` is the bare
literal `TAG` (a legend column header) rendered as the literal text **`{Tag}`**, the unresolved-tag
placeholder. So "a Label tolerates bare literals" is true only about *compiling*: the literal is still on the
expression path, and one that happens to resemble a tag or token resolves to a placeholder instead of the
text you wrote. Quoting it (`"TAG"`) is the fix; switching the element type is not.

This is mainly a **generated-Display** hazard. Hand-authoring yields a handful of literals you eyeball; a
generator yields hundreds, of which only the token-shaped ones show a visible symptom, while the rest sit
latent on the expression path. Emit quotes for every static string in a value binding, unconditionally,
rather than deciding per string (`Canvas-Drawing-Replica-Mechanics.md`).

## 10.1.6: a quoted literal in `TextBlock.LinkedValue` renders WITH its quotes, so use `Text`

Observed on FrameworX 10.1.6, RichClient runtime: a `TextBlock` with `LinkedValue: "\"MAINTENANCE\""` compiles
clean and renders **`"MAINTENANCE"`**, quote characters included, at design time AND at runtime. The same
TextBlock with **`Text: "MAINTENANCE"`** (no quotes) renders clean; `\n` line breaks and
`TextAlignment: "Center"` work there too. Composite templates on `LinkedValue` with UNQUOTED literal text
around `{@Tag.X}` render correctly at runtime (`"HEARTBEAT {@Tag.X} SEC"` shows `HEARTBEAT 1 SEC`, `\n`
honoured).

So for **static captions on a TextBlock, use the `Text` property**, and keep `LinkedValue` for bindings and
composite templates (`"Level {@Tag.X} %"`). The "quote every literal" rule above still holds for value
bindings that must carry a constant (TextBox, Dashboard cells). Verify the render per control type on your
build.

## State-dependent captions: ONE element with a nested `IIf`, never a stack of per-state copies

Runtime-proven on FrameworX 10.1.6 (HTML5 client): a TextBlock with
`LinkedValue: "{IIf(@Tag.X = 1, \"Opened\", \"Open\")}"` renders the caption for the current state, and
multi-line captions work with `"SHUT" & vbLf & "DOWN"` inside the expression. Nest `IIf` for more states, and
put the per-state colour on the same element (`TextColorDynamic` for text, `FillColorDynamic` for a face or
background).

Why: one TextBlock per state, each behind a `VisibilityDynamic`, is correct at runtime but shows every state
stacked on top of each other in the Designer and duplicates elements. The design-time preview of the single
element is the value placeholder (`#`), like any live value. Rule: one element per visual; the state lives in
the dynamics.

## When it applies

Any control whose *value* you set from a constant: Dashboard text cells, a TextBox showing a fixed string, a
Symbol's `LinkedValue`. If the text is a caption (a label/title), put it in the caption/text property, not the
value binding. If it must go in the value binding, quote it.

*(Observed on the value-binding path of the builds in scope. Confirm the exact error and the Label-vs-TextBox
divergence on your installed build. The rule "quote a literal in a value binding" is the safe default
regardless.)*
