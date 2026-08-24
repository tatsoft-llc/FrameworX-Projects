---
name: premise-check
description: >-
  Test whether the question itself is sound before answering it. Especially "does FrameworX actually support
  this, natively or at all?": by grounding the claim against the live platform through the MCP rather than
  answering from memory. Fires when the user challenges the framing or grounding of a question, or when your
  in-progress answer rests on an unverified platform capability. Trigger phrases include "is that grounded?",
  "did you ground that in what the product really does?", "does FrameworX even have that feature / protocol /
  control?", "is the premise right?", "check the premise first", "are you sure the platform does that?",
  "did you verify that against the product, or is that from memory?", "that assumes X, does it hold?".
license: Apache-2.0
metadata:
  author: Marc Taccolini
---

# Premise Check: test the question before you answer it

Default behavior is to answer the question as asked. When the question rests on a premise that does not
hold, a correct-looking answer is worse than no answer: it is confidently wrong, and in this workspace it
usually means describing a platform capability that is not there.

In this workspace the most common premise to test is **"does FrameworX actually do this, natively, or at
all?"** Ground it against the platform through the MCP (`browse_object_model`, `search_docs`,
`list_protocols`, `list_elements`), never from memory. Answering a capability question from memory is the
single highest-cost error available here, because the answer travels straight into a spec or a Display.

## Triggers

"is that grounded?", "did you ground that in what the product really does?", "does FrameworX even have that
feature/protocol?", "is the premise right?", "check the premise first", "are you sure the platform does
that?", "did you verify that against the product, or is that from memory?", "that assumes X, does it hold?".

Every one of these is capability-grounding shaped. Reframing utterances, "the big question is …" and "wrong
question, the real question is …", belong to `mirror-look` and its Inversion mode, not here.

It also fires unprompted: if you are about to claim the platform supports something and you have not
confirmed it this session, run the check before the claim leaves.

## Protocol

1. Stop the answer-loop. Don't produce the original answer yet.
2. Name the premises your in-progress answer assumes (e.g., "FX supports this protocol", "this point is an
   AO not an AI", "the customer wants on-prem").
3. Test each against grounded evidence: query the platform, read the IO register, check the spec. For
   "does FX support X", confirm via the MCP before claiming it.
4. Report the finding first: *"Premise check. [1] holds; [2] doesn't, here's the corrected framing.
   Proceed under it, or refine?"*
5. Only after the user accepts the corrected premise do you produce the answer.

**Failure mode, premise theater:** listing premises without actually testing them. The point is to *catch*
the broken one, not to recite the list.

## Standing note on constraints

Never hardcode the user's standing constraints, current priorities or open commitments into this file.
Derive them at runtime from whatever the workspace uses as its live record. A constraint written into a
skill file goes stale silently, and the skill then applies it with full confidence. The same rule is why
platform capabilities are queried rather than remembered: a capability list written into a skill file is
correct until the next build.

## When to skip

Mechanical lookups; clear execution flow; the premise was given as fact by the user this turn; a capability
you already confirmed against the platform earlier in this same session.

When in doubt, do not fire. The cost of a false positive, a full premise pass on a question that wanted one
line, is higher than the cost of a false negative, where the user simply asks "is that grounded?" and gets
it.

## Related

- **`ground-first`**: grounds in the platform Context Package and this project's prior art before work
  starts. Premise Check is the narrower, mid-flight version: it fires on a specific claim rather than at
  the start of a task.
- **`verify-mcp-setup`**: if the MCP cannot answer the grounding query, the bridge is the problem, not the
  premise.
