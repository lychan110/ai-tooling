# Evaluation: TokenEconomizer

**Repo:** [microsoft/TokenEconomizer](https://github.com/microsoft/TokenEconomizer)
**Stars:** 4333 | **Last updated:** 2026-11-01 (pushed) | **License:** Apache-2.0
**Last verified:** 2026-11-02
**Last triaged:** 2026-11-02  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Tooling (agent cost control)

---

## What it does

A cross-harness plugin (Claude Code, Codex, GitHub Copilot CLI, Pi; experimental opencode and
Cursor Agent) that cuts coding-agent cost from session history without changing the agent
itself. Three mechanisms, each reversible and individually switchable:

- **Micro-skills** remember how a repository works — a build step that must run first, the
  spelling of a command that works here (`python -m pytest` where `pytest` is missing) — learned
  from repeated failures and from a model that reviews recent sessions every *k* sessions; a
  fact enters context once three sessions confirm it and is dropped when contradicted.
- **Tool pruning** stops loading tools that go unused over a threshold of prompts and sessions,
  through the agent's own settings; one command restores them.
- **Failure-loop intervention** has a judge model check whether a turn is stuck and adds a
  redirect note to context (at most once per turn), never stopping the turn itself.

Model calls run through the agent's own plan/login; learned state stays on the machine in
`~/.tokeneconomizer`. The accompanying paper (arXiv 2610.22732, UC Berkeley + Microsoft
Research/Security) reports 18.4–30.9% lower mean cost across five agent–model combinations on
277 SWE-Bench tasks, cheaper in all 30 repository×combination cells, with Pass@1 up in 4 of 5.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: GitHub repo
metadata (stars, pushed date, licence, fetched 2026-11-02) plus the README read at HEAD. The
repo is 20 days old (created 2026-10-13); the 18–31% cost figures are the paper's own
measurements, not reproduced here. No session was instrumented and no run is claimed.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at discovery-log
rather than SKIPped.

## Triage note

The `Overlaps with` cell names only reporting/prescriptive neighbors — `claude-context-optimizer`
(flags unused high-token files, Claude Code only), `optimaizr` (shows where tokens are wasted,
holds the expensive message), `headroom` (compresses tool output), `opensquilla` (token-efficient
agent) — and none is a STACK pick, so a redundancy SKIP has no incumbent to name. The distinct
claim is that it is *learned and cross-harness*: cost is cut from accumulated session history
across Claude Code/Codex/Copilot CLI/Pi (plus experimental opencode/Cursor), black-box and
reversible, where the neighbors are per-harness static optimizers. That mechanism is
uncatalogued here. Two supported harnesses (Claude Code, Codex) are this repo's historical
subjects and both are now benched, which makes a measured run more expensive than last year;
the deciding test would be a multi-session cost A/B on a real repository. Repo age (20 days)
and Microsoft-origin are reasons to keep it a lead rather than dispose of it. Left for the
P0/eval-runner lane.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [TokenEconomizer](https://github.com/microsoft/TokenEconomizer) | plugin | Cross-harness cost-control plugin (Apache-2.0, Microsoft Research/UC Berkeley) that learns from past sessions in a repo — micro-skills remember how it works, tool pruning stops loading tools that go unused, a loop guard redirects stuck turns — cutting mean cost 18–31% on SWE-Bench across Claude Code/Codex/Copilot CLI/Pi (experimental opencode/Cursor) without changing the agent | Every session re-pays for the same re-learned repo facts, unused tool definitions, and failing loops; want cost cut from session history, black-box, reversible | claude-context-optimizer, optimaizr, headroom, opensquilla |
