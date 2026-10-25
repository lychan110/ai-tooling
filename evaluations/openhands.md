# Evaluation: OpenHands

**Repo:** [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands)  <!-- All-Hands-AI/OpenHands → OpenHands/OpenHands rename re-checked 2026-10-25; the product surface is now "Agent Canvas" and the standalone OpenHands/agent-canvas repo redirects here -->
**Stars:** 91,548 (repo-metadata cache, fetched 2026-10-22; live API read 91,803 on 2026-10-25) | **Last updated:** 2026-10-25 | **License:** MIT (enterprise/ directory separate)
**Last verified:** 2026-10-25  <!-- live GitHub API read + npm registry read + a bounded install attempt on this host, all 2026-10-25; not a hands-on run -->
**Last triaged:** 2026-10-25  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Infrastructure

---

## What it does

Self-hosted developer control center for coding agents and automations — the "Agent Canvas" web UI plus the local agent-server stack it orchestrates. It runs the open-source OpenHands agent out of the box and can drive third-party agents (Claude Code, Codex, Gemini CLI, Pi, OpenCode) over the Agent-Client Protocol, against backends that can be local, Docker, a VM, or cloud. An automation service adds scheduled and webhook-triggered runs: publish a report to Slack, decompose a GitHub issue into tasks, refresh dependencies.

The shape changed during 2026. It is no longer "OpenDevin, a Devin clone" and no longer a single web app: this repo is the control center and orchestration layer, the agent itself lives in `OpenHands/software-agent-sdk` as the Agent Server (a REST API for running several agents on one host), scheduling lives in `OpenHands/automation`, and the browser client in `OpenHands/typescript-client`. The standalone `OpenHands/agent-canvas` repo now redirects here, so the three-repo split this eval recorded in August has been re-consolidated. The published artifacts are the npm package `@openhands/agent-canvas` (1.33.0, published 2026-10-23) and the matching image `ghcr.io/openhands/agent-canvas:1.33.0`.

## How we tested it

**Evidence:** REVIEW

**Source-grounded review — not run hands-on.** This pass re-read the README and repository-boundaries table at HEAD, re-resolved the published artifact on npm, and attempted the documented install on this host. The install did not complete — it exhausted the disk before unpacking — and the host's Docker socket is not usable by this user, so the sandboxed modes are unavailable too. What follows is an architecture and configuration review with the install attempt recorded verbatim; no agent run, no task, no metrics.

```
# prerequisites the README names, checked here
$ node --version      # v26.12.1   (README requires Node.js 24 or later)  OK
$ uv --version        # uv 0.11.26 (runs the agent server via uvx)        OK
$ npm --version       # 12.0.2

# the published artifact resolves, so the install command is current
$ npm view @openhands/agent-canvas version dist.unpackedSize time.modified bin
version = '1.33.0'
dist.unpackedSize = 76321859            # 76 MB unpacked
time.modified = '2026-10-23T15:03:48.734Z'
{ 'agent-canvas': 'bin/agent-canvas.mjs' }

# Option 1 (no sandbox), attempted — FAILED on disk
$ npm install --prefix ~/.hermes/cache/scratch/oh-probe @openhands/agent-canvas
npm warn tar TAR_ENTRY_ERROR ENOSPC: no space left on device, write
npm error A complete log of this run can be found in: ~/.npm/_logs/2026-10-25T17_05_58_032Z-debug-0.log
# This host's root filesystem is 38 GB with ~1.1 GB free (98% used). The partial
# tree reached 343 MB before ENOSPC and was moved off the volume; `npm cache
# clean --force` recovered ~800 MB of npm cache. The local stack additionally
# fetches the Python Agent Server through uvx (PyPI `openhands-agent-server`,
# publishing through the 1.7.x line), which needs more space again.

# Option 2/3 (Docker sandbox) — unavailable on this host
$ docker system df
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
```

Three things would have to be true for a measured number, and none is true here:

- **Option 1 (no sandbox)** — `npm install -g @openhands/agent-canvas && agent-canvas` — needs the 76 MB JS package *plus* a `uvx`-fetched Python agent server, on a volume with ~1.1 GB free. The JS package alone exhausted it. The README's own warning applies too: no-sandbox mode runs the agent server directly on the machine with full access to your filesystem, which is not something to start unattended on a shared dev box.
- **Option 2/3 (Docker sandbox)** is the safe mode and the one this host cannot use — the Docker CLI is installed but the socket is permission-denied for this user.
- **Even with the stack up there is no one-shot headless task.** Agent Canvas is a server plus a web UI: model configuration is an "LLM profile" created in the Canvas settings UI, and the documented headless split is `agent-canvas --backend-only`, which serves the stack rather than running a single task. There is no `-t "<task>"` equivalent to hang an objective oracle on, so the oracle this eval would use — one tiny repo with a failing test as the task, `pytest` as the judge, the Canvas local backend against a bare model on the same task — needs a host where the UI-driven stack can actually run.

## What worked

- **The consolidation is legible now.** The README carries an explicit repository-boundaries table (Canvas = control center and orchestration; `software-agent-sdk` = SDK + Agent Server; `automation` = scheduling and dispatch; `typescript-client` = browser client) and the orphaned `agent-canvas` repo redirects here. That is a real improvement over the three-repo split this eval recorded on 2026-08-04.
- **Bring-your-own-agent is the differentiator.** ACP support makes Canvas a front end for Claude Code, Codex, Gemini CLI, Pi, OpenCode, or OpenHands itself, with an honest "Bring your own model" path to LLM profiles rather than a locked-in model.
- **Backend choice is a first-class concept**, not a config flag: local, Docker, VM, cloud, and mixed backends can be switched from one frontend, and the automation service covers scheduled/webhook runs that plain CLI agents do not.
- **The published artifact is current and reachable** — npm 1.33.0 published 2026-10-23, a Docker tag pinned to the same version, still MIT.

## What didn't work or surprised us

- **The install has outgrown a laptop eval.** A JS package plus a `uvx`-fetched Python agent server, plus a UI session for model setup, is heavier than the value one objective oracle adds. The honest outcome is a disclosed review, not an invented n=1 run.
- **The default runtime is unsandboxed.** Options 1 and 4 both run the agent server directly on the host "with full access to your filesystem"; the safe path needs a working Docker socket, which this host does not have for this user.
- **Still an either/or platform.** It replaces your agent environment rather than augmenting it, and it ships the runtime without an engineering methodology — TDD gates, verification, debugging discipline are yours to add through AGENTS.md or skills.
- **Packaging churn keeps invalidating install docs.** In about three months the surface moved from `All-Hands-AI/OpenHands` to `OpenHands/OpenHands`, split into `software-agent-sdk` + `agent-canvas`, then merged back with the product renamed Agent Canvas. Any install instruction older than the last move is wrong, which is why the commands above were re-resolved rather than trusted.
- **License still split.** The repo is MIT but `enterprise/` carries a separate commercial license, so some features are restricted despite the MIT branding.

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | neutral | Agent quality depends on the underlying model, not the platform |
| Speed | + | Multi-backend lets you run agents on faster hardware; automations run unattended |
| Maintainability | neutral | No methodology built in; you bring your own engineering process |
| Safety | +/- | Docker sandbox adds isolation; no-sandbox mode is dangerously permissive; no built-in guardrails like agentlint |
| Cost Efficiency | + | Self-hosted means no per-seat SaaS fees; but infrastructure costs replace them |

## Verdict

**discovery-log — tentative read**

Tentative read, and it stays a lead: OpenHands / Agent Canvas is the strongest self-hosted control center for coding agents — multi-backend, multi-agent over ACP, with scheduled and webhook automations — but adopting it replaces your agent environment rather than augmenting it, its default runtime is unsandboxed, and it could not be stood up on this host (no Docker socket, ~1 GB free disk), so there is nothing run-backed to push it toward STACK. Re-check it when a machine with Docker access and spare disk is available — the oracle sketched above needs only that host. Choose Claude Code directly when you want the deepest ecosystem (skills, plugins, marketplace, hooks) and structured methodology with the simplest setup. Like goose and opencode, this is a platform choice, not a complement.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [OpenHands](https://github.com/OpenHands/OpenHands) | platform | Self-hosted agent control center — multi-backend, multi-agent, automations (77.7K stars) | Want a full AI dev platform with scheduled automations and team agent servers | claude-squad, goose, opencode |
