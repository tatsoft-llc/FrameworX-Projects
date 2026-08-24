# Recipes: paste-ready prompts for the harness

Copy a block, edit the bracketed parts, paste into Claude Code. They assume you are in this repo
with the MCP connected (see `README.md`).

---

## Start a build from a spec

```
Build the solution from this project's Specifications/ (Requirements.md + IO-Register.md), following the harness method in CLAUDE.md.
Create an ai-test- sandbox first on the Development profile with splashes off, enabling only
the modules the spec exercises. Build the data foundation (UserTypes, then UNS and asset tree)
before anything else, and verify each layer by reading it back before moving on. Report what you
did at each layer.
```

## Build the data foundation only, then stop for review

```
From this project's Specifications/, build ONLY the data foundation in the ai-test- sandbox: the
UserTypes first, then the UNS tags and asset tree instanced from them. Name hierarchically. Do
not add alarms, historian, or displays yet. When done, get_objects the UserTypes and a sample of
instances back and show me, so I can confirm the foundation before we build on it.
```

## Add the connect layer (simulation)

```
The data foundation is built and verified. Add the connect layer as simulation: scripts that move
the process tags named in Section 4 of the spec, within their ranges. Start the runtime on the
Development profile and confirm with the Runtime tools that those tags hold live, moving values
with good quality. Show me two reads a few seconds apart for one tag.
```

## Add monitor (alarms and historian)

```
Add the alarms and historian from Sections 5.1 and 5.2 of the spec. Group alarms and assign areas
as specified. Log the listed tags into the named tables. Then verify: force one alarm condition and
confirm it goes active, and confirm history rows accumulate for one logged tag.
```

## Build a screen with the authoring loop

```
Build the <Overview> display from Section 6 of the spec. First call list_elements and bind only to
real controls. Build the per-unit widget as a Symbol and instance it. Then run the correctness pass
(get_screenshot, get_display_tree, confirm bindings resolve), then the composition pass (alignment,
grouping, readability). Show me the screenshot after each pass.
```

## Review the build

```
Run the review-the-ai-build skill against the ai-test- sandbox, using this project's Specifications/ as
the source of truth. Report findings by severity. Do not fix anything yet; list what is wrong.
```

## Run the tests

```
Run the run-tests skill against the ai-test- sandbox, using this project's Specifications/. Build, start
the runtime, collect the structure and live values over MCP into the project's Tests/results/, run the checker,
and show me the pass or fail report.
```

## When the model jumps ahead

```
Stop. You are building screens before the data foundation is verified. Go back: read the UserTypes
and a sample of UNS instances back with get_objects, confirm they match the spec, and only then
continue. Foundation first.
```

## When a tool call blocks the work

```
Capture that as an MCP finding, do not work around it silently. In your summary, add an
## MCP findings block: the tool, what you attempted, what the result was instead, why it blocked the
work, and a suggested fix.
```
