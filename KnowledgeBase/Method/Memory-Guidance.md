# Memory guidance: what to remember across sessions

Guidance on what is worth remembering across sessions when you build solutions with this harness.

Claude Code keeps its own per-machine memory outside this repo. The project's `Decisions/` folder
(`Sites/<Name>/Decisions/`) is not that: it is where you write down the **solution-specific** facts
that a future session (yours tomorrow, or a teammate's) needs and cannot re-derive cheaply from the
spec or the solution file. Facts that are reusable **across** projects go to `KnowledgeBase/` instead.

## What belongs in `Decisions/`

- **Decisions and their reasons.** "We drive the levels with a bounded random walk, not a sine, so
  the high-level alarm actually trips during a demo." The solution file shows the what; this shows
  the why.
- **Non-obvious constraints.** "Line 2's simulation runs slower on purpose to show the trend
  difference." "The operator role must not see the engineering screens."
- **Where the bodies are.** "The flow calculation lives in the `LineFlow` script class, not on the
  tag." A pointer that saves a future session a search.
- **Open threads.** "Historian retention is set to 7 days for the demo; production wants 90.
  Revisit before handing over."

## What does not belong here

- Anything the spec already says. Update the spec instead.
- Anything the solution file already encodes (tag lists, alarm limits, display layouts). Read it
  from the solution.
- Secrets, credentials, customer-confidential data. Those do not go in a repo.

## Format

One fact per file, short, named for what it is (`why-bounded-random-walk.md`,
`operator-role-screen-scope.md`). Lead with the fact, then a line on why it matters and when it
applies. Keep the folder small. A memory you have to scroll past is a memory no one reads.

## Relationship to the spec

The spec is the contract and the first thing anyone reads. Memory is the margin notes. If a memory
note grows into a requirement, promote it into the spec and delete the note. The spec is canon;
memory is scaffolding.
