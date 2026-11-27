# Evaluation: kanzo

**Repo:** [emanuele-em/kanzo](https://github.com/emanuele-em/kanzo)
**Stars:** 1,323 | **Last updated:** 2026-11-23 (pushed) | **License:** AGPL-3.0
**Last verified:** 2026-11-25
**Last triaged:** 2026-11-25  <!-- triaged: bulk -->
**Dev loop stage:** Outer Loop
**Layer:** Infrastructure

---

## What it does

A self-hosted kanban board for humans and agents — one 4.7 MB Rust binary, ~5 MB RAM, 3 ms start,
exposing an MCP server and a CLI so an agent can claim a card and return one in 10–60 tokens.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo metadata
plus the CATALOG "Overlaps with" cell (`agent-track`, `fleetpost`, `agentsview`). That is enough to
place the lead and to name the rows it overlaps; it is not enough to judge the board's behaviour, and
this eval offers no verdict beyond the leave.

## Triage note

Left at `discovery-log`. A fresh discovery-batch row (catalogued 2026-11-23) with no eval of its own
yet. The three rows it overlaps — `agent-track`, `fleetpost`, `agentsview` — are all themselves
un-disposed `discovery-log` leads, so a redundancy SKIP here would name incumbents nobody has
disposed; which board the cluster picks is a cluster question, not a per-row one.

The license raises a separate question worth recording: AGPL-3.0 is copyleft, but this is a binary
an agent *runs*, not a vendored artifact copied into the consuming repo, so the disqualifying-license
mechanical skip does not apply here.

_Triaged 2026-11-25 by the P3 backlog band._

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [kanzo](https://github.com/emanuele-em/kanzo) | tool | Self-hosted kanban for humans and agents (AGPL-3.0, ★1.3K, Rust) — one 4.7 MB binary, ~5 MB RAM, 3 ms start, MCP server + CLI so an agent claims and returns a card in 10–60 tokens | Agent task state lives in ad-hoc todo files nobody else can see; want one tiny shared board that agents and humans both read and write | agent-track, fleetpost, agentsview |
