# Evaluation: OrcaReplay

**Repo:** [Continuum-AI-Corp/OrcaReplay](https://github.com/Continuum-AI-Corp/OrcaReplay)
**Stars:** 248 | **Last updated:** 2026-09-16 (pushed) | **License:** Apache-2.0
**Last verified:** 2026-09-02
**Last triaged:** 2026-09-16  <!-- triaged: bulk -->
**Dev loop stage:** Reflect
**Layer:** Tooling

---

## What it does

"Time travel for AI agents" — records an agent's run and lets you replay, fork, and debug
it with any model, built by the OrcaRouter.ai team.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo
metadata (license, stars, description) from the daily discovery scan. That is not enough
to support an ADOPT, and this eval offers no verdict.

## Triage note

Left at `discovery-log` on 2026-09-16. The 2026-09-02 disposition was a mechanical
`SKIP — no declared license`, which was right at the time: GitHub reported NOASSERTION and
no LICENSE file existed. The metadata refresh of 2026-09-16 reports **Apache-2.0** (repo
pushed 2026-09-16, 248 stars), so that ground is withdrawn and the lead is open again —
it wants a real read rather than another mechanical call.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [OrcaReplay](https://github.com/Continuum-AI-Corp/OrcaReplay) | tool | Time travel for AI agents (Apache-2.0) — record, replay, fork, and debug any agent run with any model | An agent run that misbehaves can't be replayed, forked, or debugged after the fact — only the transcript survives | claude-devtools, roundtable, zoetrope |
