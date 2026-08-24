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

## When it applies

Any control whose *value* you set from a constant: Dashboard text cells, a TextBox showing a fixed string, a
Symbol's `LinkedValue`. If the text is a caption (a label/title), put it in the caption/text property, not the
value binding. If it must go in the value binding, quote it.

*(Observed on the value-binding path of the builds in scope. Confirm the exact error and the Label-vs-TextBox
divergence on your installed build. The rule "quote a literal in a value binding" is the safe default
regardless.)*
