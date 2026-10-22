# Evaluation: durable-harness

**Repo:** [vercel-labs/durable-harness](https://github.com/vercel-labs/durable-harness)
**Stars:** 177 | **Last updated:** 2026-10-19 (pushed) | **License:** Apache-2.0
**Last verified:** 2026-10-22
**Dev loop stage:** Implement
**Layer:** Infrastructure

---

## What it does

Vercel Labs runtime that runs Pi, OpenCode, fx, Claude Code and Codex sessions as durable Workflow SDK runs. Catalogued as the `durable-harness` row by the 2026-10-22 discovery pass.

Mechanically, it wraps an existing harness rather than replacing it: `durable-harness/<harness>` packages adapt Pi, OpenCode, libfx's `fx`, Claude Code and Codex to run as workflow runs on a Workflow SDK "World". Each session becomes a workflow whose event log holds the conversation, the turn in flight, and every model and tool call, so a crash resumes the turn from the log on another machine. Tool calls that are unsafe to repeat are not re-run. Model-chosen commands and file writes run on a virtual workspace (files live in the session log) or in a per-session Vercel Sandbox, never on the machine driving the session. Local development uses the SDK's local World with no configuration; deployment options are Vercel's managed storage or a self-hosted Postgres World.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: GitHub repo
metadata (stars, pushed date, licence, fetched 2026-10-22) plus the README and repository tree
read at HEAD. Nothing here was installed, invoked, or benchmarked, and no run is claimed.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at discovery-log rather than SKIPped.

## Triage note

P2/P3 on arrival — the `Overlaps with` cell names no STACK pick, so a redundancy SKIP has no incumbent to name, and the row arrived with no eval file so it could never carry a stamp. It is also `0.0.x` and explicitly experimental, so its API may change week to week; that is a reason to keep it a lead, not a reason to dispose of it. The differentiated mechanism is durability: resumable turns and never-repeated unsafe tool calls across five different harnesses is not something the catalogued harnesses offer natively.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [durable-harness](https://github.com/vercel-labs/durable-harness) | harness | Vercel Labs runtime (Apache-2.0) that runs Pi, OpenCode, fx, Claude Code and Codex sessions as durable Workflow SDK runs | A coding-agent session dies with its process, losing the in-flight turn and tool calls; want crash-resumable sessions that never re-run an unsafe tool call | trigger.dev, deer-flow, ralph |
