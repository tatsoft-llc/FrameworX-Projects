# Convention: Where the solution file (.dbsln) lives

Keep a project's FrameworX solution file in that project's own `Sites/<Name>/Solutions/` folder. Highly
recommended for organization. Not required by the platform.

## The rule
When you create or author the solution for a project under `Sites/<Name>/`, place its `.dbsln` in
`Sites/<Name>/Solutions/`. With `create_solution`, set `output_folder` to that folder and give a clean bare
`name` (letters, numbers, underscore; no hyphens or spaces, since the name becomes the filename):

```
create_solution(
  name="HighlandWTP",
  output_folder="C:\FrameworX-Projects\Sites\Example-HighlandWTP\Solutions")
```

`output_folder` is created if missing and registered with the Solution Center, so later `list_solutions` /
`open_solution` calls find the solution by name.

## Why
The solution then sits beside the Specifications, Decisions, ChangeLog, and Commissioning-Record that explain
and verify it. One project is one self-contained folder. The next session, a teammate, or a fresh clone finds
the solution where the project says it is, with its design inputs and its audit trail next to it.

## Not mandatory, and why it is still worth doing
The MCP creates and opens a `.dbsln` from any path. FrameworX does not require the file to live beside the
project, and the Designer default location (`Documents\FrameworX\Solutions\`) works fine. Co-location is an
organization convention, not a platform constraint. If you do keep the solution in the FrameworX default
location instead, record its absolute path in `Sites/<Name>/Solutions/README.md` so the next session finds it.

## Exception: disposable sandboxes do not go here
Throwaway test and smoke-run solutions follow the Sandbox Rule: the `ai-test-` name prefix, created under a
dedicated disposable-solutions folder outside `Sites/` (e.g., `Documents\FrameworX\Dev Test\`) so sandbox
files never appear in the customer-facing solution list, never inside a `Sites/<Name>/Solutions/` folder.
Co-location is for a project's real, kept solution. A sandbox is meant to be swept, so keeping it out of the
project folder is the point. (See the Sandbox Rule in `KnowledgeBase/Method/Solution-Build-Method.md` §7.)
