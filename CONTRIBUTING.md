# Contributing

This workspace is maintained from Tatsoft's own day-to-day FrameworX practice, so most changes here
originate in real project work rather than in the repository. That shapes what is useful to send.

## Security issues do not belong here

Suspected vulnerabilities go to [`SECURITY.md`](SECURITY.md), never to an issue or a pull request.

## Reporting a problem

Open an issue. What makes one actionable:

- Your FrameworX build (`get_build_info` or the Designer's About box) and your Claude Code version.
- Which skill or KnowledgeBase file you were following, and the step you were on.
- What you expected, what happened, and the exact tool call plus the response envelope if a tool was
  involved. A response that reported success while the object did not change is worth quoting in full.
- Whether you reproduced it on a disposable `ai-test-` sandbox solution. Please do not paste customer
  data, tag values, site names, or credentials into an issue.

"The AI did X but should have done Y" is a legitimate report here. The instruction files are the product,
so a skill that steers a session wrong is a defect in this repository.

## Pull requests

Open an issue before you write one, so you do not spend effort on a change that will not land. Small,
self-contained corrections (a wrong path, a stale reference, a broken table) are easy to take.

If you send a change:

- **Keep the house voice**: terse, imperative, technical. State what to do and why, in the reader's
  seat.
- **A skill's frontmatter is a contract.** Keep `name`, `description`, `license: Apache-2.0`, and
  `metadata.author` intact, per the Agent Skills specification. The `description` is what makes a skill
  trigger, so changing it changes behavior.
- **Ground FrameworX claims in observed behavior on a real build**, and say which build you saw it on. A
  claim that cannot be reproduced against the live product does not belong in `KnowledgeBase/`.
- **Do not add a customer site.** `Sites/` in this public repository holds exactly one worked example.
- **Keep the attribution.** `NOTICE` and the per-skill `metadata.author` credit must survive in
  redistributions and derivative works, per Section 4 of the Apache License.

By sending a contribution you license it under Apache 2.0, the same terms as the rest of this
repository (Apache License, Section 5).
