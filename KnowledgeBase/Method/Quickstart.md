# Quickstart: your first solution in about ten minutes

This walks you from a connected Claude Code session to a built, running, tested solution.
It assumes you have followed the connect steps in [`README.md`](../../README.md) and `list solutions`
returns a list.

---

## 1. Write a one-page spec (3 minutes)

Run the **`new-project-bootstrap`** skill: it creates `Sites/<Name>/` and interviews you for the
spec. Manual path: copy `Templates/SiteProject/Specifications/Solution-Spec.template.md` to
`Sites/<Name>/Specifications/Solution-Spec.md` and fill it in. You do not need every section for a
first build. The parts that matter most:

- **UserTypes.** The structured types you will reuse. Even one (`Tank` with `Level`,
  `Temperature`, `Valve`) is enough to start.
- **UNS and Asset Tree.** The areas and units, and which tags live under each.
- **Alarms.** Which tags get a condition.
- **Historian.** Which tags get logged.
- **Screens.** One or two displays and what they show.
- **Acceptance checks.** The handful of statements that, if true in the running solution,
  mean the build worked. These become the test.

The worked example `Templates/Examples/Brewery/brewery-plant.spec.md` shows what a fuller spec
looks like.

## 2. Capture the hardware envelope (1 minute)

Copy `Templates/SiteProject/Specifications/Hardware-Spec.template.md` to
`Sites/<Name>/Specifications/Hardware-Spec.md`. For a simulated first build you can say "no field
hardware, tags driven by simulation scripts" and move on. The point is that the solution knows its
target, even when the target is a simulator.

## 3. Ask Claude Code to build it (a few minutes of supervised work)

A good opening prompt:

> Build the solution described in `Sites/<Name>/Specifications/Solution-Spec.md`, following the
> harness method in CLAUDE.md. Create an `ai-test-` sandbox solution first, on the Development
> profile, with splashes off. Build the data foundation before anything else, and verify each layer
> before moving to the next. Show me what you did at each layer.

Watch the layers go by. The model should define UserTypes first, then the UNS, then connect,
then monitor, then screens. If it jumps straight to drawing screens, stop it and point back
at the build order.

## 4. Review the build (1 minute)

> Run the `review-the-ai-build` skill against the sandbox.

This is an independent pass over what was built: does the structure match the spec, are there
orphan references, is anything alarmed or historized that should not be, do the screens bind to
real tags. Read its findings before you trust the build.

## 5. Run the tests (2 minutes)

> Run the `run-tests` skill against the sandbox, using `Sites/<Name>/Specifications/Solution-Spec.md`
> as the source of the expected structure.

The harness builds the solution, starts the runtime on the Development profile, collects the
real structure and live values over MCP, and checks them against the expectations derived from
your spec. Green means the running solution matches the spec. Red names exactly what did not.

## 6. Read the result and iterate

A failing check is information, not a setback. It tells you which layer to go back to. Fix,
re-verify that layer, re-run the tests. When the tests are green and the review is clean, you
have a solution you can hand to an operator, not a demo.

---

## What to do when something is off

- **The MCP is not connected.** Do not let the AI build a mock. Fix the connection first
  (`KnowledgeBase/Method/mcp-setup.md`), then build for real.
- **A write succeeded but the feature is not visible.** That is the staging chain. See
  `KnowledgeBase/Method/verify-your-work.md`. Confirm the runtime, not the file.
- **The build is large and the model is losing the thread.** Build by area and verify each batch before
  the next. Claude Code's plan mode and task list keep the batches visible across a long session.
- **Something behaves other than documented, or a tool cannot do what you need.** Capture it in the
  `## MCP findings` block at the end (`KnowledgeBase/Method/Solution-Build-Method.md` §8). That is
  worth more than working around it quietly.
