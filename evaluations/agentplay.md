# Evaluation: agentplay

**Repo:** [Entelligence-AI/agentplay](https://github.com/Entelligence-AI/agentplay)
**Stars:** 314 | **Last updated:** 2026-10-26 (pushed) | **License:** Apache-2.0
**Last verified:** 2026-10-26
**Dev loop stage:** Review
**Layer:** Tooling

---

## What it does

Local replay of coding-agent sessions (Apache-2.0) — every session as a map and timeline: what it read, edited, failed, and shipped. Catalogued as the `agentplay` row by the 2026-10-26 discovery pass.

`uvx agentplay` finds the agent sessions already on disk (`~/.claude/projects/**/*.jsonl`, `~/.codex/sessions`, Cursor SQLite stores, Copilot, OpenCode, Kiro, Gemini CLI, Antigravity), builds a redacted map per session (`agentplay/v1` JSON), and serves a local viewer at `127.0.0.1:7317`. The map is a radial tree of everything the session touched (files read/edited, shell verbs, MCP servers, skills, subagents, models, errors, commits/PRs); the timeline plays the session back at 1x/4x/16x with lanes for prompts, errors, edits, tokens, cost and context size, with compactions marked. Maps deliberately exclude prompt/assistant text, tool inputs/outputs, file contents and command arguments (a shell command is recorded as its verb only); `--path-mode dirs_only|hashed` further strips paths before sharing. No runtime dependencies beyond the Python stdlib, no account and no API key; the only network call is an optional email signup in the viewer, disabled with `AGENTPLAY_NO_NETWORK=1`.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: GitHub repo metadata (stars, licence, pushed date, fetched 2026-10-26) plus the README read at HEAD. The viewer screenshots and session counts quoted above are the author's own, not measurements taken here.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at discovery-log rather than SKIPped.

## Triage note

Sits in the same session-observability cluster as `Tracely`, `agentsview` and `tracecrate`; not SKIPped on arrival: its mechanism is distinct — a redacted, replayable map/timeline of what a session touched, built locally from transcripts the agent already wrote, rather than a cost report, a cross-session search index, or a CI regression gate. A real disposition needs a hands-on run against this machine's own transcripts, which is out of scope for an unattended discovery pass.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [agentplay](https://github.com/Entelligence-AI/agentplay) | tool | Local replay of coding-agent sessions (Apache-2.0) — every session as a map and timeline: what it read, edited, failed, and shipped | Agent transcripts sit unread in ~/.claude and ~/.codex; want to see what a session actually did — files read before edits, failed commands, context-window fills, shipped PRs | Tracely, agentsview, tracecrate |
