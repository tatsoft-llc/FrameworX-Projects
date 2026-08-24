# Specifications/

The design inputs for this project, **what the solution must do and what's wired**, written before the
build touches the Designer. The build answers to these files; the Commissioning Record checks against them.
When the build and the spec agree, the layer is done.

Copy each `*.template.md` to its working name and fill it in (drop the `.template` part):

- [`Requirements.template.md`](Requirements.template.md) → `Requirements.md`: what the solution must do:
  functional and operational requirements, and the acceptance checks.
- [`IO-Register.template.md`](IO-Register.template.md) → `IO-Register.md`, the point list mapping every
  physical signal to its target UNS tag. Drives UNS authoring; tells commissioning what to loop-check.
- [`Solution-Spec.template.md`](Solution-Spec.template.md) → `Solution-Spec.md`: the solution shape
  (UserTypes, UNS, alarms, historian, displays) for a larger build. Optional for a small skid.
- [`Hardware-Spec.template.md`](Hardware-Spec.template.md) → `Hardware-Spec.md`: controllers, protocols,
  and the runtime host, when there is field hardware.

A small skid often needs only `Requirements.md` + `IO-Register.md`; a larger plant fills more. You don't fill
every file: the spec set scales with the deployment.

## Keep specs surface-level

A spec states **what** the solution must contain and do, in product terms (UserTypes, tags, alarms, displays,
acceptance checks). It does not prescribe internal implementation, and it does not carry acceptance-test
scripts: those live in the project's `Tests/`. State the requirement; let the build choose the mechanism.

## The acceptance checks are the contract

End the requirements with a short list of statements that are true in the running solution when the build is
correct ("each brew line exposes a Tank with a Level that moves and is historized"; "a high-level alarm goes
active when Level exceeds its setpoint"). Write them as things a test can check, not as aspirations. The
`run-tests` skill drives them against the live solution and records results under `Tests/`.

For a worked, production-grade example of the detail a real spec carries, see
`Templates/Examples/Brewery/brewery-plant.spec.md`.
