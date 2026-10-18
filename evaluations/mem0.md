# Evaluation: mem0

**Repo:** [mem0ai/mem0](https://github.com/mem0ai/mem0)
**Stars:** 58,871 | **Last updated:** 2026-06-18 | **License:** Apache-2.0
**Last verified:** 2026-10-18
**Dev loop stage:** Reflect
**Layer:** Infrastructure

---

## What it does

Universal memory layer for AI agents. Stores User, Session, and Agent state with entity linking and temporal reasoning. Retrieval fuses semantic search, BM25 keyword search, and entity matching scored in parallel. Available as a Python/Node SDK, self-hosted Docker server, managed cloud platform, or Claude Code plugin (v0.2.10 via `.claude-plugin/marketplace.json` in the repo).

The advertised differentiator is a research-backed algorithm with vendor-published benchmarks (91.6 LoCoMo, 94.8 LongMemEval, 64.1 BEAM at 1M tokens), plus the two behaviours that make it a memory *service* rather than a note store: entity linking across memories, and temporal reasoning ("what was X last month?" vs "what is X now?"). Those benchmark figures describe the hosted platform; the measured OSS-SDK behaviour on our own oracle is below, and the temporal claim did not reproduce there.

MCP server integration is community-maintained: `coleam00/mcp-mem0` (678 stars) is the most popular, with self-hosted options (`elvismdev/mem0-mcp-selfhosted`) bundling Qdrant + Neo4j + Ollama.

## How we tested it

**Evidence:** MEASURED

Measured, **hands-on** A/B in an isolated Python 3.12 venv: `mem0ai` 2.2.1 from PyPI (its own OSS
SDK), an embedded Qdrant collection with no server, local FastEmbed `BAAI/bge-small-en-v1.5` ONNX
embeddings (384-dim), and an OpenAI-compatible endpoint for fact extraction — the same gateway and
model this agent runs on (`kilo-auto/efficient`, routed to `deepseek/deepseek-v4.1-flash`), reached
through mem0's `llm.provider: openai` + `openai_base_url` path. Telemetry off for the whole run,
history in a throwaway SQLite file, everything under gitignored `.eval-work/mem0/`.

Two arms behind one interface. mem0 proper, and a hand-rolled memory of the shape a team writes in
an afternoon: append the raw turns to a per-user list and retrieve by token overlap — with
user/agent scoping, exact metadata filtering and delete wired up, so the delta is mem0's extraction,
dedup and retrieval rather than a feature either arm lacks.

```bash
uv venv --python 3.12 .eval-work/mem0/.venv
uv pip install mem0ai fastembed onnxruntime
MEM0_TELEMETRY=False ANONYMIZED_TELEMETRY=False MEM0_EVAL_RUN=r3 \
  .eval-work/mem0/.venv/bin/python .eval-work/mem0/oracle.py both
```

One clean run on a fresh collection — 13 planted turns, 13 objective steps:

| Arm | Steps | Load (13 turns) | add p50 / p95 | search p50 / p95 | memories | peak RSS |
|-----|-------|-----------------|---------------|------------------|----------|----------|
| mem0 2.2.1 | **10/13** | 40.5 s | 3.08 s / 5.43 s | 16.8 ms / 237.5 ms | 15 | 321 MB |
| hand-rolled baseline | 9/13 | <0.1 s | <0.1 s | 0.0 ms / 0.2 ms | 12 | 321 MB |

| Step | mem0 | baseline |
|------|------|----------|
| extract_fact_diet | PASS | PASS |
| scope_isolation_user | PASS | PASS |
| contradiction_update_rank1 | FAIL | FAIL |
| stale_fact_retired | FAIL | FAIL |
| duplicate_add_deduped | PASS | FAIL |
| metadata_filter_hit | PASS | PASS |
| metadata_filter_miss | PASS | PASS |
| scope_isolation_agent | PASS | PASS |
| delete_removes_memory | PASS | PASS |
| aggregation_recall_no_lexical_overlap | PASS | FAIL |
| recency_rank1 | FAIL | PASS |
| exact_token_retrieval | PASS | PASS |
| not_stated_no_fabrication | PASS | PASS |

An earlier run of the same harness scored mem0 11/13, with `contradiction_update_rank1` and
`recency_rank1` passing and only `stale_fact_retired` failing — that revision predated the metadata
pass-through, which is why `metadata_filter_hit` read 0 there. A first revision crashed on an
unscoped count, which mem0 rejects. Both were harness defects, fixed before the run above.

## Test design

- **Task/corpus:** `.eval-work/mem0/corpus.py` — 13 planted turns across seven users (`alice`,
  `bob`, `carol`, `dave`, `erin`, `frank`, `grace`) and two agents (`agentX`, `agentY`), carrying a
  contradiction ("Correction: I moved to Porto last month, I no longer live in Lisbon"), a verbatim
  duplicate turn, a recency pair ("Last week I biked 40 km" → "Today I biked 12 km"), a
  metadata-tagged turn (`{"topic": "billing", "project": "atlas"}`), a query whose answer is
  nowhere in the corpus, and a rare exact token.
- **Baseline:** the hand-rolled append-and-token-overlap store described above — same interface,
  same corpus, so the delta is mem0's extraction/dedup/retrieval and not a feature either arm lacks.
- **Metric:** pass rate over 13 steps whose expected sets are derived from the corpus text at run
  time, plus per-operation wall clock and peak RSS.
- **Reproduce:** the three commands above; `results.json` lands next to the harness.
- **Scope of this stack (declared):** extraction through a third-party gateway model, embeddings
  local ONNX rather than OpenAI's, vector store an embedded Qdrant collection rather than the
  Docker server, no graph store and no cloud platform, and the `mem0ai[nlp]` spaCy extra left out
  of the install (mem0 logged its enrichment path as unavailable at startup). The published
  LoCoMo/LongMemEval numbers describe the hosted platform; nothing here re-measures them.

## What worked

- **Extraction is real** — raw turns become atomic memories ("Alice is a vegetarian", "User works at a company called Northwind Systems"); the baseline can only hand back the whole turn it stored.
- **Scoping isolates cleanly** — a user-scoped query returned 5 memories with none of bob's leaking in; an agent-scoped query returned 1 and none of the other agent's.
- **Deduplication works** — the verbatim duplicate turn left dave with exactly 1 memory; the baseline's count doubled.
- **Metadata filtering works once metadata is passed through** — the `topic: billing` filter returned exactly the tagged memory, and a bogus topic returned 0.
- **Semantic recall beats keywords** — "summarise everything known about carol" returned both bakery memories with no lexical overlap; the token-overlap baseline returned 0.
- **Delete and history are real** — the memory left `get()` and `get_all()`, and `history()` recorded the DELETE event.
- **Cheap to stand up** — embedded Qdrant, no server, no Docker: 16.8 ms median search and 321 MB peak RSS for the whole process.

## What didn't work or surprised us

- **A contradicted fact was not retired** — after the Porto correction mem0 stored a correct update memory but kept "Alice lives in Lisbon" live, and then ranked that stale memory **first** for "where does alice live now". Two steps failed on this.
- **Recency ranking failed** — for "how far did I bike today" the 40 km memory outranked the 12 km one. The earlier run passed this step, so it is unstable rather than uniformly wrong.
- **One step of margin over a naive store** — 10/13 against 9/13. mem0's wins are structural (dedup, semantic aggregation); the two advertised differentiators, contradiction handling and temporal reasoning, were exactly what it failed.
- **Results are non-deterministic** — two runs of the same harness and corpus disagreed on three steps, which costs a verification pass each time you trust a stored fact.
- **No unscoped listing** — `get_all()` without a `user_id`/`agent_id`/`run_id` raises, so counting a store means iterating scopes.
- **~3 s per add** — extraction plus the update decision is LLM-bound and a 13-turn corpus took 40.5 s to load: fine for a background memory worker, slow inside an interactive turn.

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | + | 10/13 objective steps on a planted corpus — dedup, user/agent scoping, metadata filtering, semantic recall and delete/history all held; contradiction retirement and recency ranking failed |
| Speed | - | add p50 3.08 s / p95 5.43 s (LLM-bound); search p50 16.8 ms / p95 237.5 ms; the naive counter-arm answers in ~0 ms |
| Maintainability | neutral | memory is infrastructure; the SDK is one `pip install`, but the 2.x config surface (llm + embedder + vector store + history db) is a real amount of YAML |
| Safety | + | user/agent scoping leaked nothing in either isolation step; telemetry off for the whole run via env var |
| Cost Efficiency | - | every add is at least one LLM call (extraction + update decision); embeddings and the vector store run locally at no cost |
| Verifiability | + | `history()` records ADD/DELETE per memory id and the oracle's expected sets are derived from the corpus, so the whole measurement reruns from three commands |

## Verdict

**CONDITIONAL**

Use mem0 when you need a self-hosted, multi-tenant memory *service*: one shared store with
per-user and per-agent isolation, metadata-scoped retrieval, deduplication and semantic recall,
and you have an LLM endpoint to spend on extraction. Do not reach for it for single-user agent
notes — `claude-mem` (ADOPT) is the lighter fit — and do not depend on it to retire contradicted
facts or to rank by recency: both failed in this measured run, and its margin over a hand-rolled
append-and-search store was a single step (10/13 vs 9/13). Re-measure before adopting any
benchmark-shaped claim about it.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [mem0](https://github.com/mem0ai/mem0) | MCP server | AI memory layer with entity linking, temporal reasoning, and published retrieval benchmarks (58.8K stars) | Need cross-platform memory with relationship-aware retrieval that scales past thousands of entries | claude-mem, OMEGA, SimpleMem |
