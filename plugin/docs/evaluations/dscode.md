# Evaluation: dscode

**Repo:** [qiz029/dscode](https://github.com/qiz029/dscode)
**Stars:** 1,019 | **Last updated:** 2026-10-03 (pushed) | **License:** MIT
**Last verified:** 2026-10-07
**Last triaged:** 2026-10-07  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Tooling

---

## What it does

Catalog one-liner: "DeepSeek coding agent harness (MIT, ★1.0K) — persistent shell, Ultra
subagents, auto-approval, Chrome MCP, and session telemetry." A terminal coding-agent
harness built around DeepSeek's model loop: a shell the agent keeps open across steps
rather than re-spawning per command, a subagent fan-out ("Ultra"), auto-approval for tool
calls, browser automation through Chrome MCP, and session telemetry for step/cost
visibility. It positions as a ready-made harness, not a library you wire together.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo
metadata plus the CATALOG "Overlaps with" cell. That is enough to place the lead, not to
judge the harness's behaviour hands-on, so it would not support a positive verdict — and
none is offered.

## Triage note

Left at `discovery-log`. Zero overlap pressure (P3 backlog): its cited peers — `opencode`,
`open-interpreter`, `gptme`, `forgecode` — are all `discovery-log` leads themselves, with
no STACK pick among them, so there is no incumbent to call this redundant against. A
maintained (pushed 2026-10-03), MIT-licensed DeepSeek-native harness with a persistent
shell and subagent fan-out is a differentiated tool in the terminal-harness cluster, not a
mechanical SKIP. It deserves a hands-on eval; the eliminate-only triage lane cannot run
one, so it is left here for a human or `eval-runner`.

_Triaged 2026-10-07 by the P3 backlog band._

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [dscode](https://github.com/qiz029/dscode) | harness | DeepSeek coding agent harness (MIT, ★1.0K) — persistent shell, Ultra subagents, auto-approval, Chrome MCP, and session telemetry | DeepSeek's agent loop ships without a persistent shell, parallel subagents, or MCP browser tooling; want a ready harness instead of wiring them yourself | opencode, open-interpreter, gptme, forgecode |
