# Pattern: testing a web (HTML5) Display in Chrome

How to open your solution's HTML5 Web Client in a real browser and confirm it renders live, the web-client
half of validation. Pairs with `Validation-and-Readback.md` (which covers the runtime-value / WPF side).

> This is the quick reference. For the full connect-and-diagnose loop, the 8 browser-bind failure modes,
> the `switch_browser`-vs-`select_browser` foot-gun, auto-pre-flight, and the session cache, the
> `chrome-connector-setup` skill mechanizes it and fires automatically before the first Chrome call.
> It ships in the [companion repo](https://github.com/tatsoft-llc/Claude-Code-Skills).

## Why a browser, and why it's a real test

FrameworX Runtime serves the HTML5 Web Client from a **built-in HTTP server**, no IIS or external web server
required. When you open that URL in a browser, the browser gets its **own operator session** (its own client
identity), separate from Designer and separate from the MCP. So what the browser shows is what a real operator
sees, a genuine end-to-end test of the web-deployed solution, not a Designer-side preview.

## 1. Get the Web Client URL

Start the runtime as the web client and use the URL it hands back:

- `designer_action('start_runtime', 'webclient')` → returns `runtime_url`, e.g. `http://127.0.0.1:3201/html5/`.

The port follows the runtime **profile** (an AI session runs the Development profile). **Use the `runtime_url`
the call returns. Don't hardcode a port.** (Background: `search_docs("Web Server Configuration")`.)

## 2. Connect Chrome (the Claude-in-Chrome connector)

The connector is **extension-based, not headless**: it drives a local Google Chrome running the Claude in
Chrome extension, signed in. Bind in three steps, in order:

1. `list_connected_browsers` → pick the one "on this computer"; note its `deviceId`.
2. `select_browser(deviceId)` (or `switch_browser` to pick in Chrome) → binds the session to that browser.
3. `tabs_context_mcp(createIfEmpty=true)` → **mandatory before any page verb.** Allocates an MCP-owned tab
   group so you don't collide with the user's own tabs. Skipping this is the #1 silent failure, `navigate`
   "succeeds" but nothing renders.

> The Chrome verbs (`mcp__Claude_in_Chrome__*`) are **not** in this workspace's pre-approved tool list by
> default: approve them when prompted, or add them to `.claude/settings.json`.

## 3. Open and verify

1. `navigate(tabId, <runtime_url>)`: opens the Web Client.
2. Drive operator input where the test needs it: `find` the control, then `computer.left_click` / `form_input`
   / `computer.type`.
3. Assert the render two ways: `read_page` (DOM / accessibility tree, more robust than pixels when the control
   exposes elements) and `computer.screenshot` (the visual).
4. Cross-check the data path: read the underlying tag with `runtime_get_value` and confirm value + quality +
   timestamp: so you've proven both "it rendered" *and* "it's bound to live data," not just one.

## Setup gotchas (quick triage)

| Symptom | Fix |
|---|---|
| `list_connected_browsers` returns nothing | Extension not installed or not signed in, open Chrome, sign in to the extension, re-probe |
| `navigate` "works" but no tab / nothing renders | You skipped `tabs_context_mcp(createIfEmpty=true)`, call it, then retry |
| `read_page` returns partial DOM | Page still loading, wait ~1s and retry once |
| Nothing happens on `navigate` / `read_page` | A Chrome permission popup is blocking, dismiss it in the Chrome window |
| `read_page` errors on a size cap | Narrow scope: `filter="interactive"`, lower `depth`, or target a `ref_id` |

## Boundaries

- This covers the **HTML5 / Web Client**. The **WPF rich client** renders in a separate out-of-process window
  the MCP can't drive. That's a human / screenshot attestation, not browser-automatable (see
  `Validation-and-Readback.md`).
- Never enter credentials, accept terms, or solve CAPTCHAs in the browser on the user's behalf, surface those
  to the user.
