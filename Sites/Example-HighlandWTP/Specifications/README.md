# Specifications/

The design inputs for this project: **what the solution must do and what's wired**. The build answers to
these files; the Commissioning Record checks against them. This site is the workspace's worked example, so
the set is fully filled in:

- [`Requirements.md`](Requirements.md): what the solution must do: functional and operational
  requirements, and the acceptance checks.
- [`IO-Register.md`](IO-Register.md), the point list mapping every controller signal to its target UNS
  tag. Drives UNS authoring; tells commissioning what to loop-check.
- [`Solution-Spec.md`](Solution-Spec.md), the solution shape: UserTypes, UNS, alarms, historian,
  displays, and the acceptance-check contract (§8).
- [`Hardware-Spec.md`](Hardware-Spec.md), controllers, protocols, and the runtime host.
- `Highland_WTP_Equipment_Spec.pdf` + `Highland_WTP_Main.L5K`: the staged source material these specs
  were transcribed from (the published Highland WTP example on docs.tatsoft.com: equipment spec and
  ControlLogix controller export).

Starting your own project? Don't copy these, `new-project-bootstrap` seeds a fresh `Sites/<Name>/` from
the blank templates in `Templates/SiteProject/Specifications/`.

## Keep specs surface-level

A spec states **what** the solution must contain and do, in product terms (UserTypes, tags, alarms,
displays, acceptance checks). It does not prescribe internal implementation, and it does not carry
acceptance-test scripts: those live in the project's `Tests/`. State the requirement; let the build
choose the mechanism.

## The acceptance checks are the contract

The requirements end with a short list of statements that are true in the running solution when the build
is correct. Write them as things a test can check, not as aspirations. The `run-tests` skill drives them
against the live solution and records results under `Tests/`.
