# Evaluation: delx-memory

**Repo:** [davidmosiah/delx-memory](https://github.com/davidmosiah/delx-memory)
**Stars:** 1 | **Last updated:** recent (exact push date not captured from the repo page; checked 2026-09-04) | **License:** MIT
**Last verified:** 2026-09-04
**Last triaged:** 2026-10-09  <!-- triaged: human -->
**Dev loop stage:** Memory & Context
**Layer:** Tooling

---

## What it does

A shared, local-first SQLite memory store any MCP-speaking agent (Claude Desktop, Cursor, Hermes, OpenClaw, Codex) can read and write, so context survives across sessions **and** across tools. Ships 15 MCP tools, secret-blocking, TTL support, multi-agent namespacing, and zero telemetry.

## How we tested it

**Evidence:** MEASURED (keyless-local posture, v0.4.1)

Two passes. First pass (2026-09-04, history below): SOURCE-ONLY. Second pass (2026-10-09, this eval): installed v0.4.1 locally (npm, no sudo/docker/go) and verified the cross-process store claim three ways, plus secret-block, TTL, and namespace behavior. Full report + evidence: [`docs/evals/memory-phase1a-2026-10/delx/`](../docs/evals/memory-phase1a-2026-10/delx/REPORT.md).

- **Install:** local npm install (130 pkgs, 0 vulns) — needs a local package.json (npm 11 upward-prefix-resolution quirk).
- **Cross-process shared store (the core claim) — VERIFIED 3 WAYS:** CLI proc A→B, two independent MCP stdio client+server pairs (15 tools), and sessionless HTTP POST /mcp all read one verbatim control fact from the same SQLite file.
- **Secret-block:** AWS-key-shaped value refused at write, exit 1, no row. Key-NAME filter is aggressive substring (`*secret*`/`*token*` false-positives possible).
- **TTL:** expiry computed at write; readable before, swept after.
- **Namespace isolation — PASS with a material caveat:** scoping is opt-in key-prefixing, NOT storage-layer enforcement — a default/unscoped client reads ALL namespaced keys. Same-trust multi-agent only; this is not multi-tenant security.
- **Footprint (measured):** ~69 MB RSS (lite/CLI one-shot) / ~96 MB (HTTP server resident). Materially heavier than engram (~19.6 MB) on a 1.5 GB-free box.
- Store: unencrypted SQLite (0600 file / 0700 dir). `explicit_user_intent: true` is a soft convention a client can always set.

## What worked

- Cross-harness shared store exactly as pitched — the only MEASURED candidate in the cluster whose "one store, many agents" claim is verified end-to-end, and verified without any harness-specific wiring.
- Secret-blocking at write time + TTL sweep, both behaviorally confirmed.
- Zero cloud; zero embedder; plain SQLite a human can inspect.

## What didn't work or surprised us

- **No dedup/upsert model** — key overwrite only; revision history or topic-key semantics absent. A facade needing "one fact, many revisions" owns that mechanic itself (ours sided with engram for exactly this).
- **Isolation is prefix-cosplay** — same-trust only; don't point untrusted tenants at one store.
- **Heavier resident footprint** than the single-binary alternative on constrained hardware.

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | + | Shared-store read/write verified across 3 transports; TTL + secret-block behaviorally confirmed |
| Speed | neutral | Not benchmarked; latency unremarkable in smoke use |
| Maintainability | + | Plain SQLite; npm-managed; no external services |
| Safety | neutral | Secret-block real but name-filter overbroad; unencrypted store; prefix-only isolation |
| Cost Efficiency | − | 69–96 MB resident vs ~20 MB for the engine cluster alternative |
| Verifiability | + | Store is plain SQLite — every claim above re-verifiable with sqlite3 |

## Verdict

**CONDITIONAL** — adopt-if: you want a cross-harness shared memory store wired in AS-IS (the facade shrinks toward zero) and your hosts can carry ~96 MB resident; accept no-dedup + prefix-only isolation, same-trust tenants only. For ours the fork chose engram as engine + a thin auto-brain facade (dedup at the data model, 3.5× smaller) — but delx-memory remains the pick if no-facade simplicity wins a future re-eval.

## Triage note

Left at `discovery-log`. `triage.py` bands this P2 (challenges `claude-mem`), but claude-mem is a Claude Code-specific plugin while delx-memory's core pitch is cross-tool interoperability — one SQLite store shared across five different agent clients. That's a genuine differentiator, not obviously redundant. Tiny (★1) and unproven; leaving for a real eval to check whether the cross-tool claim holds up.

_Triaged 2026-09-04 by the P2 challenger band (daily discovery pass)._

**2026-10-09 — hands-on MEASURED re-eval (this file, above):** evidence promoted `SOURCE-ONLY` → `MEASURED`; human-attended run; the cross-tool claim held (3 transports). Verdict `CONDITIONAL` on the measured posture. Evaluated in the engram-vs-delx fork (ai-tooling#49 Phase 2) — not selected as engine, revisit trigger recorded.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [delx-memory](https://github.com/davidmosiah/delx-memory) | MCP server | Shared local SQLite memory store (MIT) any MCP-speaking agent (Claude, Cursor, Hermes, OpenClaw, Codex) can read/write — context survives across sessions and across tools, with secret-blocking and TTL support | Each tool/session keeps its own throwaway context; want one local, cross-tool memory store with zero telemetry | claude-mem, mex, opencontext |
