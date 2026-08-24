# Verify your work

A written row is not a working feature. This is the long form of Section 4 of `CLAUDE.md`. It is
the single discipline that most separates a production solution from a demo.

## The trap

`write_objects` returns success when the row is written to the solution. That tells you the
authoring succeeded. It does not tell you:

- whether the value is what you intended (a typo writes cleanly),
- whether the runtime serves it (a tag with no source holds no value),
- whether an operator can reach it (a control with an unresolved binding renders blank),
- whether a new option appears in a picker (registration is a separate step from writing a row).

Each of these has shipped as a "done" that was not done. The fix is to verify at the layer that
proves the outcome.

## Four checks, by layer

1. **Round-trip the data.** After a write, `get_objects` it back. Confirm names, members, units,
   and values match intent. This catches typos and silent coercions.
2. **Check the running runtime.** Start the runtime and use the Runtime tools. Confirm a tag holds
   a live value with **good quality and a recent timestamp**. Confirm an alarm goes active when its
   condition is true. Confirm history accumulates. The file having a row is necessary, not
   sufficient.
3. **Look at the screen.** For any Display change, `get_screenshot` and read it. A control with an
   empty binding can render its default placeholder, which reads as real content at a glance: confirm
   the value on screen is the tag's, not the placeholder. The render is ground truth for UI.
4. **Walk the staging chain.** When a change should make a new entry appear in a combo, picker,
   ribbon, or sidebar, confirm it appears. A protocol, provider, or dialog entry becomes reachable
   only after the product registers it (config XML, DLL, ribbon entry). A clean write is not a
   visible option.

## How to report status honestly

- "Written and confirmed in runtime: tag holds 47.2 with good quality, timestamp 2s old." Good.
- "Written, not yet confirmed in runtime." Honest and useful. Says exactly what is unverified.
- "Done." Without a check, this is a guess dressed as a fact. Do not use it.

If a check cannot be run (the runtime is not up, a screenshot is not available for a non-rendered
area), say which check is missing and why. A named gap is a finding; a silent gap is a bug waiting
to surface on someone else's machine.

## The harness encodes this

The run-tests skill (`.claude/skills/run-tests/`, checker `check.py`; per-project tests live at
`Sites/<Name>/Tests/`) is verify-your-work made repeatable. It collects the real structure and
live values over MCP and checks them against the spec. Run it at the end of a build and read the
result. Green is evidence. But a green count or a `success` flag is not proof the loop closed;
stats are not verification, drive the complete path. The review skill
(`.claude/skills/review-the-ai-build`) is the human-judgment companion to the mechanical test.
