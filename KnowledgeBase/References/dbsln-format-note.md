# The .dbsln file is encrypted: read structure through the product

A FrameworX solution file (`.dbsln`) is an **encrypted SQLite database**. Its header is not the
`SQLite format 3` magic; it begins with random-looking bytes, and a plain `sqlite3` open fails with
`file is not a database`. The product reads it through its own SQLite library, which holds the
decryption. Tools that go through the product (the Designer, the Console, and the Runtime) read it
fine. A standalone script cannot crack it, and should not try.

## What this means for the test harness

- **Read solution structure through the MCP**, not by opening the `.dbsln` directly. The
  Designer/Console `get_objects` and `browse_object_model` return the decrypted truth. The collect
  step (`.claude/skills/run-tests/collect-live.md`) does exactly this, and
  `.claude/skills/run-tests/check.py` asserts against the collected numbers.
- **For a no-runtime, deterministic gate**, read an **exported JSON workspace** instead of the
  binary. The FrameworX AI Console works on unencrypted JSON workspaces; export the solution to one
  and the structure is plain JSON you can count in CI. The encrypted `.dbsln` is never the input to a
  standalone reader.
- **Do not store a decryption key in this repo** to work around the encryption. The point of the
  encryption is to protect solution contents at rest. The supported read path is through the product.

## Why the harness leans on the MCP for structure

This is also why the structural assertions live in `check.py` against collected data rather than in a
script that parses the file. The product is the source of truth for what a solution contains, and it
is the only thing that can read the file. The harness reads structure the same way an operator's tools
do: through FrameworX.
