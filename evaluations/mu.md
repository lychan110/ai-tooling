# Evaluation: mu

**Repo:** [qybaihe/mu](https://github.com/qybaihe/mu)
**Stars:** 450 | **Last updated:** 2026-10-08 (pushed) | **License:** MIT + Apache-2.0
**Last verified:** 2026-10-09
**Last triaged:** 2026-10-09  <!-- triaged: bulk -->
**Dev loop stage:** Implement (the judgment points run inside the agent loop, per turn)
**Layer:** Tooling (CLI + desktop app, built on `pi`)

---

## What it does

Catalog one-liner: "Coding agent with a judgment kernel (MIT+Apache-2.0, ★450) — a small fast judge answers 38 bounded decision points per turn (context admission, tool risk/approval, drift, completion) so the big model only does the work; CLI + desktop app, built on pi" — move the per-turn micro-decisions (what context to admit, whether a tool call is safe to auto-run, whether the agent has drifted, whether work is done) out of the frontier model and into a cheap, bounded judge.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo metadata plus the CATALOG "Overlaps with" cell. That is enough to place the lead, not to judge the judgment kernel's actual behaviour hands-on, so it would not support a positive verdict — and none is offered.

## Triage note

Left at `discovery-log`. Zero overlap pressure (P3 backlog): its cited peers — `pi`, `phi`,
`command-code`, `jcode`, `aider` — are `discovery-log` leads (command-code is already SKIPped),
with no STACK pick among them, so there is no incumbent to call this redundant against. A
maintained (pushed 2026-10-08), dual-licensed judgment-kernel agent is a differentiated mechanism
in the harness cluster — whether 38 bounded decision points actually save tokens and latency
*without* degrading quality is exactly the kind of claim only a hands-on eval can support. The
eliminate-only triage lane cannot run one, so it is left here for a human or `eval-runner`.

_Triaged 2026-10-09 by the P3 backlog band._

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [mu](https://github.com/qybaihe/mu) | harness | Coding agent with a judgment kernel (MIT+Apache-2.0, ★450) — a small fast judge answers 38 bounded decision points per turn (context admission, tool risk/approval, drift, completion) so the big model only does the work; CLI + desktop app, built on pi | Agents waste tokens/latency/attention on non-code decisions; want cheap bounded judgment for context, safety, and completion instead of the big model or fixed rules | pi, phi, command-code, jcode, aider |
