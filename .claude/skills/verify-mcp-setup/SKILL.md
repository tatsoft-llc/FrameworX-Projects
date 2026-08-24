---
name: verify-mcp-setup
description: >-
  Probe, diagnose, and fix the FrameworX MCP connection (Designer / Console / Runtime bridges) before a
  session depends on it. Fires on explicit user request ("verify the MCP setup", "is FrameworX connected",
  "the MCP tools aren't working", "check the bridges", "list solutions fails", "set up the FrameworX MCP",
  "can you see my Designer") AND as a pre-flight when the FIRST FrameworX tool call of a session fails with a
  server-not-available / connection error. Probes each bridge the session needs → identifies the failure mode
  from the inventory → surfaces the specific remediation → re-probes → confirms with a real bootstrap call
  (list_solutions / list_workspaces / runtime_connect). The core-bridge counterpart to chrome-connector-setup,
  which ships in the companion Claude-Code-Skills repository, not here.
license: Apache-2.0
metadata:
  author: Marc Taccolini
---

# Verify MCP Setup: the connection pre-flight

## Why this exists

Every capability in this workspace rides on three MCP bridges into the installed FrameworX product.
When they aren't up, every tool call fails. And a brand-new user can't tell a missing bridge from a
firewall block from a wrong host in `.mcp.json`. This skill mechanizes probe → diagnose → fix → re-probe
so the session starts from a verified connection instead of a mystery failure. The full setup reference
(same-machine, remote, VM, and the security model) is `KnowledgeBase/Method/mcp-setup.md`: this skill
is the interactive front door to it.

## The three bridges

| Bridge | Port | Needs | Bootstrap probe |
|---|---|---|---|
| FrameworX AI Designer | 10150 | the FrameworX install (Designer launches on demand) | `list_solutions` |
| FrameworX AI Console | 10151 | the FrameworX install (no Designer) | `list_workspaces` |
| FrameworX AI Runtime | 10120 | a RUNNING TServer for the target solution | `runtime_connect` |

Only probe the arms the session needs. A Console-only authoring session doesn't need the Runtime arm up.

## Process

### 1. Probe

Call the cheapest bootstrap tool on each needed arm: `list_solutions(detail='count')` (Designer),
`list_workspaces` (Console), `runtime_connect` (Runtime). A success that returns the platform context
package (`solutionContext` / Context Package) is a PASS. The session is bootstrapped as a side effect.

Note: the very first tool call of a session may trigger a host consent prompt that is invisible to you.
If a first call hangs or is denied, tell the user to check for a permission dialog before diagnosing.

### 2. Diagnose: failure-mode inventory

Match the error to the mode; apply the one remediation; re-probe.

1. **Connection refused / server not available (same machine).** The bridge isn't running. Start it from
   the FrameworX install: `Documents\FrameworX\Utilities\StartDesignerMCPHttp.bat` (10150),
   `StartConsoleMCPHttp.bat` (10151), `StartRuntimeMCPHttp.bat` (10120). Each keeps a console window
   open: it must stay open. Start the bridge, then retry; if Claude Code was started first, the retry
   still works (the client reconnects per call).
2. **Bridge window reports "address already in use" when starting.** A host process from an earlier session
   still holds the port → run the `kill-zombies` skill (companion repo), then start the bridge again.
3. **Timeout to a remote host.** Firewall or wrong IP. On the FrameworX machine open inbound
   10150/10151/10120 (only the ones used); confirm the host IP in `.mcp.json` matches. For a same-host VM
   (Parallels/VMware), keep `127.0.0.1` and port-forward instead of using the LAN IP.
4. **`.mcp.json` still carries the `YOUR-WINDOWS-IP` placeholder** (or points at localhost when FrameworX
   is remote). Copy `.mcp.remote.example.json` over `.mcp.json`, set the real host, restart Claude Code
   (MCP config loads at startup).
5. **Designer/Console probes pass but the Runtime probe fails.** The runtime isn't running, or the bridge's
   `RuntimeMCPHttp.json` (next to its .bat) points at the wrong TServer host/port/credentials. Start the
   solution's runtime first (Development profile: TServer port auto-increments from 3201: never hardcode;
   use the connect response). `runtime_connect` with explicit arguments rebinds without a bridge restart.
6. **Everything fails and the install predates 10.1.5.** Pre-10.1.5 installs do not ship the MCP servers:
   there is no degradation path. The fix is a product update, not configuration.
7. **`DESIGNER_NOT_RESPONDING` / pipe error mid-session.** Don't re-run setup diagnosis for this one:
   reconnect via `open_solution` with the current solution name and retry. A Designer dialog waiting on
   input blocks the pipe the same way, so ask the user to check the Designer window.
8. **Two clients wired to one backend** (Claude Desktop `.mcpb` extensions AND this workspace's
   `.mcp.json`). Each client starts its own host process against the same backend, so an unclean exit
   leaves duplicates behind. Pick one client per backend (`mcp-setup.md` § One client per backend).
9. **All three servers fail to even spawn, `npx` / Node not found.** The shipped `.mcp.json` launches
   each server via `npx -y mcp-remote`, so the machine running Claude Code needs Node.js (LTS) with
   `npx` on PATH. The symptom is a spawn/ENOENT error on every FrameworX server at Claude Code startup,
   before any port is probed. Install Node.js, restart Claude Code.

### 3. Confirm: the smoke test IS the bootstrap

Re-run the step-1 probes until the needed arms PASS. State the result concretely: "Designer bridge up.
`list_solutions` returned N solutions and the platform context package." Do not declare setup verified
from a ping or a port check alone: only a successful tool round-trip counts. Never build a mock or
proceed "offline" as a workaround; connect for real first.

## Anti-patterns

- **Diagnosing before probing.** One cheap call tells you which arm is broken; start there.
- **Widening timeouts or retry loops on a refused connection.** Refused = not running; fix the cause.
- **Probing all three arms when the session needs one.** Cost discipline: probe what the work requires.
- **Telling the user to reinstall.** Every mode above has a lighter fix; reinstall is never step one.
- **Skipping the consent-prompt warning on the first call of a session.**

## Composition

- **kill-zombies**: mode 2 (held port) and any `.dbsln` lock found on the way route there.
  Ships in the [companion repo](https://github.com/tatsoft-llc/Claude-Code-Skills).
- **chrome-connector-setup**: the same probe→diagnose→fix shape for the browser connector.
  Ships in the same companion repo.
- **new-project-bootstrap / ground-first**: both assume a bootstrapped session; this skill is what runs
  when that assumption fails.
- **`KnowledgeBase/Method/mcp-setup.md`**, the full reference this skill fronts, including the auth model
  (bridges are unauthenticated HTTP, the security boundary is the network; localhost or trusted LAN/VPN only).
