# Convention: LLM endpoint placement (never on the solution host)

**Date:** 2026-06-11 · **Type:** Recommendation · **Status:** standing

## The rule

It is **against this recommendation to install or run LLM models on the computer that runs the FrameworX solution**, for end-users and for internal testing alike. This applies to every project in this repo, every demo, every commissioning, and every QA fixture.

- The model (Ollama or any OpenAI-compatible server) runs on a **separate machine**: a LAN GPU box, a sibling server, or a cloud endpoint.
- `SolutionCapabilities[LocalAI].Settings.URL` always names that separate machine, never `localhost` / `127.0.0.1`.
- **Set `Settings` explicitly, never leave it empty:** an empty `Settings` resolves to a loopback URL (same-host), which is the placement this rule excludes. Populate the JSON with the remote URL and the model name the endpoint actually serves.
- Cloud endpoints use a SecuritySecrets-backed key (`Authorization: BearerToken` + `/secret:<Name>`), never a plaintext key.

## Why

LLM inference saturates CPU/GPU. Co-located with TServer the two compete for the same cores and the runtime is what pays for it: Property Watch stops updating, heartbeats time out, alarms lag. CPU-only inference is also too slow (~2-4 tok/s) even to demo. Beyond performance, a model install (~2-5 GB weights + runtime) changes the character of the solution host, which is why the recommendation covers testing boxes too.

## Worked example

The LLM endpoint lives on a separate host:
`SolutionCapabilities[LocalAI].Settings.URL = "http://<llm-host>:11434"`: a LAN GPU box, a sibling server,
or a cloud endpoint; never `localhost` / `127.0.0.1` on the TServer machine. The remote host serves the model
bound to all interfaces (e.g. `OLLAMA_HOST=0.0.0.0:11434`, inbound TCP 11434 open). That is the pattern to copy.

## History

The separate-machine endpoint is the one current placement, testing included. If you come across an older same-host example ("run the model on the same box for testing"), treat it as superseded, not as a pattern to copy.
