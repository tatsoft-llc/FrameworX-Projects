# Security policy

This workspace is published as is under Apache 2.0. It is not a supported Tatsoft product and carries no
SLA, and this policy adds no response commitment. What it does is tell you what counts as a vulnerability
here, what belongs somewhere else, and how to send it privately.

## Report privately, never in an issue

Do not open a public issue, a pull request, a forum post, or a Discord message describing a suspected
vulnerability. Ordinary bugs and feature requests still go to issues.

Use either channel:

- This repository's **Security** tab, **Report a vulnerability**. That opens a private advisory only the
  maintainers can read.
- Email **security@tatsoft.com** with the repository name in the subject.

Include the commit or tag you tested, the exact file, what an attacker gains and what access they need
first, a minimal reproduction, and your Windows, PowerShell, Python, FrameworX and Claude Code versions.
A proposed patch is welcome, never required.

**Leave customer data out of the report.** No tag values, no site names, no solution files, no
credentials. This repository already forbids storing those (`KnowledgeBase/Conventions/Security-Baseline.md`).
Redact first; if you cannot describe the issue without customer data, say so rather than attaching it.

## In scope

Anything shipped here that runs on your machine, is executed by the product, or steers an agent:

- `.claude/settings.json`, the shipped permission file. An entry granting more than the README's warning
  describes, or a destructive verb added without updating that warning.
- `.claude/hooks/*.ps1`. At session end, the reap hook force-terminates processes recorded against a
  baseline file under `%TEMP%`.
  A way to make it kill something outside that baseline, or to steer it by tampering with the baseline
  from another local account, is in scope.
- `.claude/tools/invariant-linter/invariant_lint.py`, which is read only except for `--reseed` writing its
  allow-list sidecar, and `.claude/skills/run-tests/check.py`.
- Skill instruction files under `.claude/skills/`: text that makes an agent take a destructive or unscoped
  action, skip a confirmation the skill documents, or write a secret into a repository file.
- `.mcp.json` and `.mcp.remote.example.json`, which launch a package at run time and can move bridge ports
  onto a network.
- `Sites/Example-HighlandWTP/` and `Templates/`, including scripts and CodeBehind that compile and run
  inside FrameworX when the example is opened.
- `KnowledgeBase/` guidance that would put a reader in an unsafe posture.
- Anything committed here that should not have been: a credential, a real customer solution, real site data.

## Not in scope here

- **The FrameworX product itself**: Designer, Console, Runtime, TServer, the MCP servers and their bridges.
  This harness drives an installed product; it does not contain it. A product vulnerability still should
  not be posted publicly: send it to `security@tatsoft.com` rather than to the forum, the Discord, or an
  issue here.
- **Third party software**: Claude Code, Node.js and `npx`, the `mcp-remote` package, Python. Report those
  to their own maintainers.
- **Your own clone.** `.gitignore` keeps customer sites and received source material out of commits by
  default. If you remove that default to version your sites, keeping that repository private is your
  responsibility, as `.gitignore` says in place.

## Documented by design, please do not re-report

These are written down here on purpose. They are posture and deliberate defaults, not defects:

1. **The network is the security boundary for the MCP bridges** (`KnowledgeBase/Method/mcp-setup.md`). On
   FrameworX 10.1.5 and earlier they listen unauthenticated on their port. From 10.1.6 a bridge with no key
   accepts only local connections, and a network client sends a key that travels over plain HTTP. The
   documented answer is to control reach: localhost only, or a trusted LAN or VPN, and never a public port
   forward. An error inside that guidance is in scope; the posture itself is not a finding.
2. **The shipped permission file auto-approves the write verbs** (README, "Safety"). Deliberate, because
   prompting on every write makes a build session unusable, and the README gives the opt-out.
3. **This workspace writes to a control system, and a tag write can move a physical output.** That is what
   the harness is for.
4. **The session-end hook terminates processes**, scoped to the ones this session started: pre-existing Designer
   and TServer processes, and processes started by another session, a shared bridge or by hand, are never
   touched. A demonstrated failure of that scoping is in scope.

## Research safely

Do this work on a disposable `ai-test-` prefixed sandbox solution, never on a customer solution and never
on a live or safety-critical process. A tag write here can move real equipment.
