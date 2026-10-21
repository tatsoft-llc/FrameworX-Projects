---
name: manage-context-on-large-solutions
description: >-
  Keep a FrameworX build coherent when the solution is too large to hold in context at once. Use
  when a build spans hundreds of tags or many displays, when the session is long, when the model
  starts losing track of what was built, or when the user says "this is getting big", "manage the
  context", "build this in batches", "the solution is large", or "don't lose the thread". Provides
  the method for scoping by layer and area, browsing instead of dumping, verifying each batch, and
  leaving a resumable trail so a later turn or a fresh session can continue without re-deriving.
license: Apache-2.0
metadata:
  author: Marc Taccolini
  version: "1.0.0"
---

# Manage context on large solutions

A production solution is large. Hundreds or thousands of tags, dozens of displays, many scripts.
You cannot hold all of it in context, and trying to is how a build loses coherence: the model
re-reads the same dump, forgets what it already changed, and starts contradicting earlier work.
The fix is to work in scoped batches and keep a trail.

## Scope, do not dump

- **Browse the part you are changing.** Use `browse_object_model`, `runtime_search_uns`, and
  `get_objects` on a named scope. Do not pull the whole object model into context to change one
  area.
- **Work the spec and the asset tree, not the full export.** The spec says what to build; the asset
  tree says where it goes. Those two are small. The full object dump is large and mostly irrelevant
  to the current batch.

## Batch by layer, then by area

Build in the order of `KnowledgeBase/Method/build-order.md`, and within a layer, by area:

1. All UserTypes (small, do them together; everything binds to them).
2. The UNS and asset tree for one area. Verify. Then the next area.
3. Alarms for one area. Verify. Then the next.
4. Historian for the logged tags. Verify.
5. Displays, one screen or one Symbol at a time. Verify each with a screenshot.

Verify each batch before starting the next (`get_objects` round-trip, or a runtime check for live
behavior). A verified batch is one you can stop thinking about. An unverified batch is weight you
carry into every later turn.

A single display of hundreds of elements is a batch of its own: write it through a JSON workspace
rather than an inline payload (`KnowledgeBase/Patterns/MCP-Display-Authoring-Recipes.md`, "Large
displays").

## Leave a resumable trail

When a build spans many turns, write down where you are, so a later turn or a fresh session can
pick up without re-deriving:

- Keep a short running checklist in the spec or a session note: which areas are built and verified,
  which are next, any decision made mid-build.
- Record decisions and non-obvious constraints in the site's `Decisions/` folder (see `KnowledgeBase/Method/Memory-Guidance.md`).
- Name the sandbox clearly (`ai-test-<slug>`) so it is obvious what it is on return.

## Signs you are losing the thread, and the recovery

- You are re-reading objects you already changed: you lost the trail. Stop, write the checklist,
  resume from it.
- The model proposes something the spec already settled: re-read the relevant spec section, not the
  whole solution.
- Context is genuinely full: summarize the build state into a session note and the spec checklist,
  then continue from that summary rather than the raw history.

## The principle

A large build is many small, verified builds in a defined order, with a written trail between them.
It is not one heroic pass. Aim high on the whole plant; start simple on one area; scale by adding
the next area to a foundation that already holds.
