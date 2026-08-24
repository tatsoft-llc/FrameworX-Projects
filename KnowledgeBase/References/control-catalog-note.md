# Displays: use the real control catalog

The single most common way an AI-built screen goes wrong is inventing a control that does not
exist, or guessing a property name. FrameworX has a specific control set, and it is
discoverable. Use it.

## Always list before you build

Before authoring a Display, call `list_elements` (Designer or Console). It returns the controls
the installed product actually offers, with their real names. Bind to that list, not to memory.

## Common patterns and the control that carries them

These are starting points. The authoritative names come from `list_elements` on your install.

- A live numeric readout: a text or label control bound to the tag, with the engineering unit
  shown. Confirm the binding resolves; an empty binding renders as a default placeholder, not
  an error.
- A tank, gauge, or level: a gauge or symbol control. Many shapes are convenience configurations
  of the same underlying control rather than separate controls. Do not assume a separate control
  exists for every visual; check the catalog.
- A trend: the trend chart control. An XY chart is the same control in an XY configuration.
- A semicircle gauge: a configuration of the circular gauge control.
- An alarm list: the alarm display control bound to a group or area.
- A button that acts: bind its command, and confirm the label and command both resolve. A button
  with an empty label link renders the control's default text rather than reporting an error, so
  only a screenshot catches it.

## The render is ground truth

JSON that looks correct can render wrong. After a Display change, take a `get_screenshot` and read
it. The `display-authoring-loop` discipline (correctness pass, then composition pass) exists because
the file and the screen can disagree. Trust the screen.

## Reuse with Symbols

A production screen set is built from Symbols (reusable composites), not from twenty hand-placed
copies of the same widget. Define the Symbol once, instance it per asset, bind each instance to its
asset's tags. This is the screen-layer echo of building from UserTypes.
