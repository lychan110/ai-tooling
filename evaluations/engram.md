# Evaluation: Engram

**Repo:** [Gentleman-Programming/engram](https://github.com/Gentleman-Programming/engram)
**Stars:** 4,493 | **Last updated:** 2026-06-18 | **License:** MIT
**Last verified:** 2026-10-09  <!-- hands-on re-run on the box; see How we tested it -->
**Last triaged:** 2026-10-09  <!-- triaged: human -->
**Dev loop stage:** Reflect
**Layer:** Infrastructure

---

## What it does

Persistent memory for AI coding agents. A single Go binary with SQLite + FTS5 full-text search, exposed via MCP tools, an HTTP API, a CLI, and a TUI. Works with any MCP-capable agent — Claude Code, OpenCode, Gemini CLI, Codex, VS Code, Cursor, Windsurf. The agent decides what's worth remembering and saves with structured content; the store deduplicates by topic key.

Ships as a proper Claude Code plugin with hooks for session lifecycle (start, stop, compaction recovery, subagent stop, user prompt submit) and an MCP server config. Also has first-class plugins for Pi, OpenCode, and Obsidian.

## How we tested it

**Evidence:** MEASURED (prebuilt-binary posture, v3.2.1)

Two passes. First pass (2026-06-22, history in <details> below): architecture REVIEW — did not run (Go build dependency). Second pass (2026-10-09, this eval): installed the checksum-verified prebuilt linux/amd64 release binary (no Go toolchain, no sudo, no Docker) and exercised the real CLI + MCP stdio server on a 2-CPU / 1.5 GB-free constrained host. Full reports + evidence captures: [`docs/evals/memory-phase1a-2026-10/engram/`](../docs/evals/memory-phase1a-2026-10/engram/REPORT.md). Follow-up on top of this eval: the auto-brain memory facade — engine selected by the engram-vs-delx fork in [ai-tooling#49](https://github.com/lychan110/ai-tooling/issues/49) Phase 2; 10 facade tests green against this binary; E2E over real MCP stdio (`mem_remember` upsert + conflict digest, `mem_recall` progressive disclosure, `mem_forget`, `mem_status`).

- **Install:** tarball (sha256 vs checksums.txt), `./engram --version` → `engram 3.2.1`. Store relocatable via `ENGRAM_DATA_DIR`.
- **Upsert/dedup (decisive behavior):** two saves to the same `--topic` → ONE row, `revision_count` incremented, content = updated version, prior revision kept in `observation_versions`. Verified via independent SQLite reads + `engram export` JSON.
- **Dedup-key correction (vs the June REVIEW):** the dedup key is the **`topic_key`, NOT the title** — differential probe: same topic + different title revises in place; same title + different topic creates two rows. June's "dedup via hash + project + scope + type + title" line is wrong as written.
- **Progressive disclosure (MEASURED):** compact `#id (type) — title / snippet / timestamp | project | scope` rows; `mem_get_observation`/`export` return full content; `mem_timeline` adds before/after context.
- **Conflict surfacing — weaker than June reviewed.** MCP `mem_compare` DOES persist a `conflicts_with` relation (read back); but CLI `conflicts scan` found **0 candidates** on deliberately contradictory pairs, `--semantic` requires an authed external LLM CLI (`ENGRAM_AGENT_CLI`), and the automatic `judgment_required` flow never fired on plain saves. Same-topic contradiction is impossible by design (topic upsert replaces).
- **Footprint (measured):** ~19.6 MB peak RSS per CLI op, ~0.07 s wall, 0 swaps; stdio server stable on the constrained box.

> **FTS5 caveat:** hyphenated query terms (e.g. `long-term`) parse as FTS5 column-filter syntax and miss records — same failure family as catalog-db #48 (merged PR #51). Identity lookups must not ride the text-search path.

## What worked

- **Topic-key upserts (MEASURED)** — the "100 versions of the same decision" problem dies at the data model.
- **Prebuilt-binary install (MEASURED)** — zero deps, no Go, no sudo; ~20 MB RSS on a 1.5 GB-free box.
- **Progressive disclosure (MEASURED)** — compact rows, full content one call away.
- **Agent-agnostic**: `engram setup <agent>` one-liner for 7+ agents; MCP + CLI + HTTP.
- **Git sync**: chunked export/import via git; cloud replication opt-in, local authoritative.

## What didn't work or surprised us

- **Conflict detection materially weaker than the June REVIEW** — auto-detection effectively off; `mem_compare` works but CLI scan finds nothing without a semantic pass backed by another LLM CLI. Treat as beta-at-best; a facade built on engram owns this mechanic.
- **Update banner on every run** (3.2.1→3.3.0 nit) — stderr noise on every invocation; wrappers must strip it.
- **Cloud complexity** (June REVIEW, unchanged): multi-step upgrade flow + repair scripts; local-only path is clean and is what we verified.
- **v3.3.0 available but unmeasured** — this eval pins 3.2.1; upgrade is a tracked follow-up (auto-brain#25).

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | + | Topic-key upsert + revision_count proven on real saves; dedup key = topic_key (June review corrected) |
| Speed | + | ~0.07 s wall per op; progressive disclosure holds |
| Maintainability | + | Zero-dep binary; store = one SQLite file; upgrade = swap the binary |
| Safety | + | Local-first; single file on disk; no telemetry observed |
| Cost Efficiency | + | ~20 MB RSS; ~100 tokens per compact search row |
| Verifiability | + | `engram export` JSON + SQLite reads make every claim independently checkable |

## Verdict

**CONDITIONAL** — adopt-if: you want durable agent memory as a storage ENGINE behind a thin facade you own, on constrained hardware, agent-agnostic. Proven: topic-key dedup, progressive disclosure, tiny footprint, prebuilt install. Conflict surfacing is NOT fire-and-forget — own it in the calling layer (ours does). For wire-as-is shared stores with secret-blocking, see `delx-memory` (MEASURED same week); for Claude-Code-native capture, `claude-mem` stays the incumbent pick.

<details>
<summary>Historical: 2026-06-22 architecture REVIEW (pre-hands-on)</summary>

### What worked (review-only)

- **20 MCP tools with progressive disclosure**; **topic-key upserts** keeping one memory per decision with `revision_count`; **agent-agnostic** `engram setup <agent>` for 7+ agents; **conflict surfacing** via `mem_judge`/`mem_compare` (beta, architecturally sound — no other catalog memory tool does this); **zero dependencies** (`brew install`); **git sync** (compressed chunks); **memory lifecycle** with `review_after` + `mem_review`.

### What didn't work (review-only)

- Not hands-on tested (Go build dependency). Cloud-complexity surface (4-step upgrade flow, repair scripts, transport failure modes). Large repo (1,176 files) = scope creep beyond simple memory. claude-mem (ADOPT) simpler for Claude-Code-only users.

_Triaged 2026-08-04 by the P2 challenger band ([#264](https://github.com/mattbutlerengineering/ai-tooling/issues/264)). Re-triaged 2026-10-03 by the P2 challenger band: no change._

</details>

**2026-10-09 — hands-on MEASURED re-eval (this file):** evidence promoted `discovery-log` → `MEASURED`; human-attended run. Verdict now `CONDITIONAL` on the measured posture. Engine selected for the auto-brain memory facade ([ai-tooling#49](https://github.com/lychan110/ai-tooling/issues/49) Phase 2).

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [engram](https://github.com/Gentleman-Programming/engram) | tool | Agent-agnostic persistent memory — Go binary with SQLite, FTS5, MCP, CLI, and TUI | Need a single portable binary for memory that works with any AI coding agent | OMEGA, claude-mem, SimpleMem, agentmemory |
