# Brewery Plant: worked validation example

This folder is a worked **validation** artifact, spec → expected.json → test-gate evidence. Run
against the Brewery Plant demo that ships **inside the FrameworX product install**. It is not a
from-scratch build transcript; the from-scratch path lives in `Templates/Prompts/recipes.md`.

- `brewery-plant.spec.md`: the solution spec the gate answers to (Section 8 is the contract).
- `brewery-plant.expected.json`: the golden expectations the run-tests checker asserts against.
- `results/`: regenerated output from the test gate, kept as reference evidence.
- `validation-2026-05-30.md`: the recorded validation pass.

There is no `.dbsln` here: the solution under test is the product's built-in Brewery Plant demo.
Use this folder as the reference for what a passing spec → expected → evidence chain looks like.
