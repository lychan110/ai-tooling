# Evaluation: Memory OS (Hermes Agent)

**Repo:** [ClaudioDrews/memory-os](https://github.com/ClaudioDrews/memory-os)
**Stars:** 1,170 | **Last updated:** 2026-06-10 (pushed; created 2026-05-31) | **License:** MIT | **Install:** one-command `setup.sh`
**Last verified:** 2026-06-22  <!-- backfilled from last git edit; not a hands-on re-check -->
**Last triaged:** 2026-08-04  <!-- triaged: bulk -->
**Dev loop stage:** Memory & Context (memory infrastructure for a specific agent)
**Layer:** Infrastructure (local Docker + Qdrant + SQLite, as a Hermes Agent plugin)

---

## What it does

Memory OS is a **7-layer memory operating system for [Hermes Agent](https://github.com/NousResearch/hermes-agent)** — local memory infrastructure that gives Hermes persistent long-term memory. It provides automatic, intelligent context injection; **structured facts with trust scoring**; a **self-curating wiki pipeline**; and **semantic search across every conversation you've ever had**, backed by Qdrant + SQLite. It's **API-provider-agnostic** (OpenRouter, OpenAI, Anthropic, Ollama, or local models), runs **entirely on your machine**, and has no memory subscription / vendor lock-in. v0.2.0 added a one-command installer (`setup.sh`) that brings up the Docker services, databases, and the "Icarus" plugin.

## How we tested it

**Evidence:** REVIEW

**Source-grounded inspection — not installed, not run.** No stack set up, no Hermes session run, no recall measured. Behavior comes from the README and metadata, not observed usage.

```bash
gh api repos/ClaudioDrews/memory-os --jq '{stars,license:.license.spdx_id,pushed:.pushed_at}'   # 1.2K, MIT
gh api repos/ClaudioDrews/memory-os/readme --jq '.content' | base64 -d | head -15   # 7 layers, Qdrant, trust scoring, self-curating wiki, local
```

## What worked

- **Purpose-built for Hermes Agent.** It's the dedicated memory layer for a specific (and newly popular) own-it agent — tight integration rather than a generic bolt-on, which the catalog's Hermes Agent entry can pair with.
- **Trust-scored structured facts + self-curating wiki** is a more disciplined memory model than raw recall — it tries to keep memory accurate and organized, not just large.
- **Local-first, provider-agnostic, no subscription.** Qdrant + SQLite on your machine with any LLM provider is the right privacy/cost posture.
- **One-command install,** MIT, healthy fork ratio (~111 forks / 1.2K stars).

## What didn't work or surprised us

- **Tied to Hermes Agent.** Its value is conditional on using Hermes; it's not a general drop-in memory layer for Claude Code/Codex (those have their own options in this catalog).
- **Operational footprint.** Docker services + Qdrant + SQLite is more infrastructure to run than a single-binary or plugin memory tool.
- **Young (created late May 2026).** Promising but early; trust-scoring/self-curation efficacy is unverified here.
- **Overlaps the memory cluster conceptually** (MemOS, OMEGA) but is Hermes-scoped.

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | + | Trust-scored structured facts + self-curating wiki + semantic recall keep the right, accurate context available to Hermes. |
| Speed | + | Automatic context injection avoids re-explaining; "surgically token-efficient" per its pitch. |
| Maintainability | neutral / − | Disciplined memory model, but Docker + Qdrant + SQLite is a stack to run and maintain. |
| Safety | + | Runs entirely local, provider-agnostic — memory data stays on-box. |
| Cost Efficiency | + | No memory subscription; local infra; token-efficient context injection. |

## Verdict

**SKIP** — built for a harness this catalog does not run. The tentative read above states the
condition exactly: *"Adopt it **if Hermes Agent is your agent**"*, and *"If you're on Claude
Code/Codex, use this catalog's harness-native memory tools instead."*

That is a disposition, not a caveat. The supported harnesses here are Claude Code and opencode
(ADR-0002), memory for those is held by `claude-mem` (ADOPT, installed) and `OMEGA`, and a seven-layer
memory OS wired into a different agent's internals is dead weight next to them — worse than neutral,
because a second memory MCP alongside claude-mem risks the split-brain context the `guild` and
`agentic-stack` evals both warn about.

Nothing here is a quality judgement. MIT, local-first, trust-scored facts on Qdrant + SQLite with no
subscription is a sound design, and Hermes Agent users should find this row — which is what keeping
it catalogued does.

Re-open if Hermes Agent enters the supported-harness set.
_Triaged 2026-08-04 by the P3 backlog band ([#268](https://github.com/mattbutlerengineering/ai-tooling/issues/268))._

## 2026-10-09 addendum — hands-on deployment attempt (BLOCKED on this host); Evidence: MEASURED (blocker) / REVIEW (capability)

The re-open trigger above has now FIRED for this fleet: Hermes Agent IS in the supported-harness set here. A deployment eval was attempted on the constrained box (2 CPU, 1.5 GB free, no sudo, agent deny-ruled). Full report + captured source details: [`docs/evals/memory-phase1a-2026-10/memoryos/`](https://github.com/mattbutlerengineering/ai-tooling/blob/main/docs/evals/memory-phase1a-2026-10/memoryos/REPORT.md).

- **Blocking (measured):** `setup.sh` exits 1 without Docker; no non-Docker install mode exists. The docker socket is `root:docker 0660` and user `lychan` holds no `docker` gid (1000, 27(sudo), 100) — unblocking needs root (`usermod -aG docker lychan` + re-login), outside agent authority.
- **Footprint (ESTIMATE, labeled):** 3 services (redis 512 MB cap, qdrant v1.17.1, ARQ worker with remote 4096-d embeddings) ≈ **1.5–2.5 GB RSS vs <1 GB headroom → HIGH OOM risk** on this box even unblocked.
- **Source addendum captured for a future eval with zero rediscovery cost:** compose service list, SQLite schemas (`state.db`/`memory_store.db`), Icarus plugin load path (declares 15 tools/2 hooks vs docs' 16/4 — `fabric_brief` implemented but undeclared), fact-write path shape, 8-step resume checklist.

**Verdict unchanged: SKIP (harness-disposition stands; the row keeps its catalog place).** The capability review is unchanged REVIEW; the deployment blocker is MEASURED on this hardware. Not disqualified on merit — blocked on (a) a root action this agent cannot perform and (b) a footprint this host cannot carry. Re-re-open when either changes: bigger host, or Docker gid granted.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [memory-os](https://github.com/ClaudioDrews/memory-os) | tool | Local-first 7-layer memory OS for Hermes Agent (MIT) — Qdrant + SQLite, trust-scored structured facts, self-curating wiki, semantic search over all conversations; provider-agnostic, no subscription | Hermes Agent forgets across sessions; want disciplined, on-box long-term memory with accuracy controls | MemOS, OMEGA, Hermes Agent |
