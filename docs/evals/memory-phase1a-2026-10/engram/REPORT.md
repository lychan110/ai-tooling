# engram feasibility eval — prebuilt Linux release binary path
Date: 2026-10-09 · Host: 2 CPU / ~3.8GB RAM (1.5GB free, 2GB swap used) · No Go, no sudo, no Docker · Node v26 + uv

## Verdict candidate
engram v3.2.1 — VERIFIED / FUNCTIONAL on the distributed-artifact path (prebuilt linux/amd64 binary, checksum-verified, real CLI + MCP stdio server exercised). Evidence class: MEASURED. No Go toolchain needed to adopt; store relocatable via ENGRAM_DATA_DIR; topic-key upsert (revision_count), dedup, compact progressive-disclosure search, timeline, and conflict relations all confirmed behaviorally. Caveats: CLI `conflicts scan` (structural) found 0 candidates on deliberately contradictory toy pairs and `--semantic` requires an external LLM CLI (ENGRAM_AGENT_CLI=claude|opencode); conflict verdicts persisted via MCP mem_compare; the automatic judgment_required flow did not trigger on plain saves.

## Mode tested
Hands-on CLI + MCP stdio server (JSON-RPC client script, uv run) against the v3.2.1 release binary. HTTP API (`serve`) started but exposes no discoverable route docs (404 on /, /openapi.json, /docs); not exercised beyond that probe.

## Fixture & exact commands
Workspace: /home/lychan/.hermes/cache/scratch/eval-engram (store kept INSIDE workspace via ENGRAM_DATA_DIR)
- Fetch: curl -sS -L -o engram_3.2.1_linux_amd64.tar.gz https://github.com/Gentleman-Programming/engram/releases/download/v3.2.1/engram_3.2.1_linux_amd64.tar.gz
- Verify: sha256sum tarball vs release checksums.txt -> c5e0bbf77b3c4b196713d64d68593966d30a94582fad8dafe8e458a182c155a8 MATCH
- Run: tar -xzf ...; ./engram --version -> "engram 3.2.1" (exit 0); ./engram --help (full CLI)
- Store: export ENGRAM_DATA_DIR=/home/lychan/.hermes/cache/scratch/eval-engram/data
- mem_save: ./engram save "<title>" "<content>" --project eval-engram-test --topic <key>   (--topic == topic_key)
- mem_search/timeline/conflicts/stats/export: ./engram search/timeline/conflicts/stats/export ...
- MCP: engram mcp --tools=all --project eval-engram-test, driven by mcp_drive.py + mcp_drive2.py (uv run)
- RSS: /usr/bin/time -v ./engram save ... ; /usr/bin/time -v ./engram search ...

## Observations per acceptance item
1. Binary acquired and invoked — PASS. linux_amd64 prebuilt exists in v3.2.1; checksum verified; --version and full CLI run (exit 0).
2. Topic-key upsert dedup via revision_count — PASS. Same --topic save returned SAME id (#1); export JSON shows revision_count 1->2, duplicate_count 1, exactly ONE row for the topic_key (2 obs total after two topics, no duplicate).
3. Search progressive-disclosure shape — PASS. CLI and MCP mem_search return compact "#id (type) — title / content snippet / timestamp | project | scope"; mem_get_observation (id) + engram export return full untruncated content; mem_timeline adds before/after context.
4. Conflict surfacing — PARTIAL (observed with caveat). MCP mem_compare persisted conflicts_with relation rel-f159e56251ddb06f between contradictory #4/#5; CLI conflicts list/stats read it back (judgment_status judged, source/target named). CLI structural conflicts scan: 0 candidates on toy pairs; --semantic blocked without ENGRAM_AGENT_CLI; mem_judge schema enforced; automatic judgment_required flow did NOT trigger on plain mem_save (response judgment_required:false).
5. RSS measured — PASS. save peak 19,596 KB; search peak 19,596 KB; ~0.07s wall each; exit 0.

## Weaknesses observed
- CLI `conflicts scan` (structural) returned 0 candidates on deliberately contradictory near-identical observations; `--semantic` gated behind external LLM CLI (ENGRAM_AGENT_CLI claude|opencode) — conflict DETECTION on the CLI path is effectively off unless such a CLI exists/authed.
- mem_judge/mem_compare are MCP-first; CLI offers scan/list/stats/show only (no per-pair judge command), and `conflicts show` wants an integer relation id, not the sync_id shown by list.
- HTTP API (`serve`) has no discoverable routes/docs (404 on /, /openapi.json, /docs) — adopters must read source or MCP config to use it.
- timeline/get_observation accept numeric obs id only; sync_id string rejected — minor API asymmetry.
- Same-topic contradiction is impossible via `save` (topic-key upsert replaces) — conflicts can only arise across distinct topic_keys.

## RAM/RSS pressure
~19.6 MiB peak per CLI op (save and search); no swap activity (Swaps: 0); MCP stdio server stable on a 2-CPU / 1.5GB-free host. Well within budget for this constrained box.

## Verdict scope
Single release (v3.2.1) linux/amd64; CLI + MCP modes on a small fixture (8 observations, 1 project, 1 persisted conflict relation). NOT tested: HTTP API routes, TUI, cloud sync, obsidian-export, setup integrations, multi-project merge/consolidate, `engram test` self-suite, performance at scale.

## Evidence class
MEASURED — every hands-on check above ran the real v3.2.1 binary; raw outputs in evidence/ (01_fetch, 02_upsert, 03_search_timeline, 04_conflicts, 05_rss, 06_mcp, export_after_upsert.json, release_latest.json, releases_list.json). No invented numbers.

