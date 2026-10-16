# Evaluation: OpenAgentCore

**Repo:** [MiniMax-AI/OpenAgentCore](https://github.com/MiniMax-AI/OpenAgentCore)
**Stars:** — (no `repo-metadata.json` record for this repo) | **Last updated:** unknown | **License:** MIT
**Last verified:** 2026-10-16
**Last triaged:** 2026-10-16  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Tooling (self-hosted agent runtime)

---

## What it does

An open-source, self-hosted implementation of the OpenAI Agents API by MiniMax-AI
(MIT): the OpenAI agent-runtime contract without the proprietary control plane, with
multiple native harnesses to swap in.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only:
the CATALOG row — `repo-metadata.json` carries no record for this repo — plus the
row's "Overlaps with" cell. That is sufficient for a triage stamp; it would not
support an ADOPT, and this eval does not offer one.

## Triage note

Left at `discovery-log` (P3 backlog band, 2026-10-16). The row's Overlaps cell
(`strands-agents (harness-sdk)`, `eca`, `aster`) cites no STACK pick, so P3's rule
is a stamp, not a verdict. Gap flagged for the discovery lane: there is no
`repo-metadata.json` record for MiniMax-AI/OpenAgentCore, so the metadata sweep
never sees this repo; the cheap `--stale` refresh cannot fetch it either.
