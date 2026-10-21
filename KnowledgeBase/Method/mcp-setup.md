# MCP setup and the auth model

This is the full version of the connect steps in the README, plus the endpoint and security
model a customer needs to deploy the harness safely.

The FrameworX MCP servers operate the **installed FrameworX product**. They do not see this
repository. Three servers cover the harness:

| Server | Bridge port | Talks to | What it gives the AI |
|---|---|---|---|
| FrameworX AI Designer | 10150 | A running Designer IDE | Live read and write of solution objects, build, runtime start and stop, screenshots, `get_state` |
| FrameworX AI Console | 10151 | Local solution JSON workspaces (no Designer needed) | File-based authoring of the same object surface, good for offline build and CI |
| FrameworX AI Runtime | 10120 | A running TServer | Live tag values, active alarms, historian queries, runtime object browse |

Each bridge has one fixed listen port, independent of how many solutions or profiles are
running. The bridge ports (10150 / 10151 / 10120) are not the TServer ports. TServer runs
per execution profile: Production 3101, Development 3201 by default. On the **Development**
profile the port auto-increments, if 3201 is already taken the runtime searches for the next
free port, so the actual Dev port can differ from 3201 (use the `runtime_url` / connect
response, don't hardcode).

---

## Same machine (Claude Code and FrameworX on one Windows box)

1. Start the bridges you need. In the FrameworX install, run from
   `Documents\FrameworX\Utilities\`:
   - `StartDesignerMCPHttp.bat` (port 10150)
   - `StartConsoleMCPHttp.bat` (port 10151)
   - `StartRuntimeMCPHttp.bat` (port 10120)

   Leave each console window open. Start the bridge before Claude Code.
2. Use the shipped [`.mcp.json`](../../.mcp.json) as is. It points at `127.0.0.1` on the three
   ports. Prerequisite: Node.js (LTS) with `npx` on PATH, the config launches each server via
   `npx -y mcp-remote`.
3. Open Claude Code in this folder and ask it to `list solutions`.

### Simpler same-machine alternative for Console only

If all you need is file-based authoring (no live build, screenshot, or runtime), you can skip
the bridge and the Node dependency and run FrameworX AI Console directly over stdio:

```
claude mcp add consolemcp dotnet "C:\Program Files\Tatsoft\FrameworX\fx-10\net10.0\ConsoleMCP.dll"
```

The FrameworX install also ships `AISetup\Code\AddConsoleMCP.bat`, which does this for you and
guards against double-wiring. This path does not give you the live Designer or Runtime tools, so
the test harness's live-value checks need the bridge or Claude Desktop extensions instead.

---

## Separate machine (Mac, VM, or a second PC)

This is the common case for a Mac user with FrameworX in a Windows VM, or a workstation talking
to a server.

1. **FrameworX 10.1.6 or later: set an API key on each bridge you use.** From 10.1.6, a bridge with
   no key accepts connections only from its own machine. Connections from another computer, or from
   the host of a VM through port forwarding, are refused. The steps are STEP 0 of
   `AISetup\Http\README.txt` in the FrameworX install: copy `<Server>.json` (for example
   `DesignerMCPHttp.json`) into the `MachineSettings` folder if it is not there yet, set
   `appSettings` → `X_API_KEY` to a random value of 32 or more letters and digits (A-Z, a-z, 0-9
   only: other characters are altered on the way and the key is then refused), keep
   `ListenLoopbackOnly` false for `RuntimeMCPHttp`, and restart the bridge. Each bridge reads its own
   key; the example config below sends one variable to all three, so set the same value on each
   bridge you use. On 10.1.5 and earlier, skip this step.
2. On the **Windows** machine, start the bridges as above.
3. Open the bridge ports in **Windows Firewall**: 10150, 10151, 10120 (only the ones you use).
4. On the **Claude Code** machine, copy [`.mcp.remote.example.json`](../../.mcp.remote.example.json)
   over `.mcp.json` and replace `YOUR-WINDOWS-IP` with the Windows machine's LAN address.
5. **Give Claude Code the key without writing it into a file.** The example sends the header
   `X-API-KEY:${FX_MCP_API_KEY}`, and Claude Code fills `${FX_MCP_API_KEY}` from the environment it
   starts in. Set that environment variable to the bridge key on the Claude Code machine, then start
   Claude Code. If the variable is missing, `claude mcp list` shows a missing-variable warning and the
   literal text `${FX_MCP_API_KEY}` is sent, which the bridge refuses. Against a 10.1.5 bridge, delete
   the two `--header` entries from each server instead.
6. If FrameworX is in a same-host VM (Parallels, VMware) rather than across the network, keep
   `127.0.0.1` and set up VM port forwarding for the three ports instead of using the LAN IP. On
   10.1.6 or later this still counts as a remote connection: the key from step 1 is required.
7. **Every path in an MCP call resolves on the FrameworX host, not on the machine running Claude
   Code.** A `create_solution` folder, an `import_tags` file, a sandbox path: the bridge opens each
   one on the Windows machine, so write it as that machine sees it (`C:\...`), never as a client-side
   path. A client-side path here fails file-not-found, which is easy to misread as a connection problem.

---

## The auth model, stated plainly

This matters for any deployment beyond a single trusted machine.

- **Bridge access depends on the release, and the network is the security boundary in both.**
  - **FrameworX 10.1.6 and later:** a bridge with no API key accepts only connections from its own
    machine. With a key set, it accepts network clients that send it in the `X-API-KEY` header. The
    key grants full access to that bridge and travels over plain HTTP, so anyone who can watch the
    network can read it. Keep it private, and treat it as a guard against accidental reach, not as
    protection on an untrusted network.
  - **FrameworX 10.1.5 and earlier:** the bridges listen unauthenticated on their port. A client that
    can reach `http://<host>:10150/mcp` can drive the Designer, with no credential at the bridge.

  Either way, control who can reach the port. Terminating TLS in front of a bridge changes the
  transport, not that fact. Two safe postures:
  - **Localhost only.** Keep the bridges on `127.0.0.1` and do not open the firewall ports. The
    AI client runs on the same machine. This is the default and the recommendation for a single
    workstation.
  - **Trusted LAN or VPN.** If the client is on another machine, expose the ports only on a
    trusted, segmented network or over a VPN. Never port-forward a bridge to the public internet:
    on 10.1.5 reachability is the only thing gating it, and on 10.1.6 a key sent in clear text is not
    enough.
- **The Runtime bridge holds the TServer credentials, not the AI client.** `RuntimeMCPHttp.json`
  (next to `StartRuntimeMCPHttp.bat`) carries the TServer Host, Port, and the runtime user
  credentials the bridge uses to connect. The AI client never sends those; it asks the bridge,
  and the bridge authenticates to TServer. To point the runtime tools at a different solution or
  profile, the AI calls `runtime_connect` with new arguments and the bridge rebinds. No restart.
- **The FrameworX Runtime web API itself uses a bearer token (a GUID) per session** for direct
  HTTP access to runtime values. The Runtime MCP bridge handles that token exchange on the AI's
  behalf, so a harness user does not manage tokens directly. If you call the runtime web API
  without the bridge (for a custom CI check), you obtain and present that bearer token yourself.
- **Treat solution data as customer-confidential.** A connected session can read tag values,
  alarms, and history. Scope access the same way you would scope a SCADA operator account.

---

## One client per backend

Wire each FrameworX MCP server in exactly one Claude client on a given machine. If you installed
the FrameworX `.mcpb` extensions in Claude Desktop, do not also wire the same backend here in
Claude Code, and vice versa. Two clients on one backend spawn two host processes per session, and an
interrupted session can leave both running. Pick one client per backend.

---

## Verify

- `list solutions` (Designer) or `list workspaces` (Console) returns a list. That confirms the
  Designer or Console arm.
- `runtime_connect` against a running solution returns the Context Package. That confirms the
  Runtime arm.

If a call fails with a server-not-available error, the bridge is not running or the port is not
reachable. Start the bridge, check the firewall, confirm the IP. Do not have the AI build a mock
in the meantime; connect for real first.
