# Evaluation: cognee

**Repo:** [topoteretes/cognee](https://github.com/topoteretes/cognee)
**Stars:** 17,903 | **Last updated:** 2026-06-19 | **License:** Apache-2.0
**Last verified:** 2026-06-22  <!-- backfilled from last git edit; not a hands-on re-check -->
**Dev loop stage:** Reflect / Retrospect
**Layer:** Infrastructure

---

## What it does

Open-source AI memory platform that builds a self-hosted knowledge graph from ingested data, giving agents persistent long-term memory across sessions. The core API is three operations — `remember` (ingest and graph-connect), `recall` (query with auto-routing between vector, graph, and hybrid search), and `forget` (delete). Under the hood, cognee combines vector embeddings, graph reasoning, and cognitive-science-grounded ontology generation to create a knowledge graph where documents are both searchable by meaning and connected by relationships that evolve.

The platform ships as a Python library (`pip install cognee`), CLI (`cognee-cli`), MCP server (`cognee-mcp` in the monorepo), Claude Code plugin (via separate `cognee-integrations` repo), and managed cloud service. The Claude Code plugin uses 6 lifecycle hooks (SessionStart, UserPromptSubmit, PostToolUse, Stop, PreCompact, SessionEnd) to automatically capture prompts, tool traces, and responses into session memory, inject relevant context on prompt submit, and sync to the permanent graph at session end.

## How we tested it

**Evidence:** MEASURED (keyless posture)

Two passes. First pass (2026-06-22): architecture-level REVIEW (see history below). Second pass (2026-10-05, this P0 eval): installed cognee 1.6.2 locally (`python3.14.7`) and ran a measured A/B against a TF-IDF cosine baseline on a 14-doc synthetic clinical-style corpus with a planted **three-hop entity chain** (Patient A1 → drug B1 → enzyme E1 ← inhibits − drug B2) that flat retrieval cannot cross. Cognee ran in its **keyless posture**: GLiNER-local demo extraction (its own shipped keyless route, no LLM key set, dotenv stubbed out, ~40 keys popped from env, telemetry disabled) + fastembed `BAAI/bge-small-en-v1.5` (384-d). This is the exact posture a break-glass user with no OpenAI key lands in by default.

```bash
# env hygiene (driver pops LLM_/EMBEDDING_/OPENAI_/* and stubs dotenv.load_dotenv)
python3 .eval-work/ab_driver.py       # A/B: TF-IDF baseline + cognee add/cognify/search
python3 /home/lychan/tmp/graph-probe.py   # direct Ladybug graph dump of the built graph
```

### Results (2026-10-05 run, 4 queries each)

| Query | TF-IDF | cognee CHUNKS | cognee GRAPH_COMPLETION |
|-------|--------|--------------|--------------------------|
| q1 direct pair (A1 took B1, S1) | ✓ | ✓ | — |
| q2 confusable (A2 took B2, never S1) | ✗ | **✓** | — |
| q3 2-hop jump (A1 at-risk via B2) | ✓ | ✓ | — |
| q4 3-hop jump (A1 harmed by B1+B2 combo) | ✓ | ✓ | — |

- cognee `add` 6.7 s, `cognify` 76.0 s (CPU), then CHUNKS 4/4 vs TF-IDF 3/4
- `GRAPH_COMPLETION` (its headline graph-aware retrieval): **raises `LLMAPIKeyNotSetError` 422 unconditionally in the keyless posture** — the feature is untestable without a real key, and this eval deliberately did not provide one
- Built graph: **17 nodes / 22 edges** (1 TextDocument, 1 DocumentChunk, 1 TextSummary, 10 Entity, 4 EntityType)
- **Direct Ladybug dump of the graph's edges: only `contains` (chunk→entity) and `is_a` (entity→type) exist.** The corpus's stated **relations are absent**: no `took` from A1 to B1, no `metabolized_by` from B1 to E1, no `inhibits` from B2 to E1 — the three-hop chain that the whole eval planted is **structurally impossible to cross** in the keyless build. GLiNER-local extracts entity *types* only, never the relation *between* entities; relation extraction on a real graph is exactly what prevented the q2/q3/q4 jump queries from being answered by traversal.

The graph build itself "succeeded" — it did not error, did not warn about missing relation extraction, and its node/edge count numbers look healthy in isolation. Only reading the actual edges exposed that it's a type-taxonomy graph, not a relation graph; the tool gave no signal a keyless user could act on short of directly dumping its Ladybug store (`MATCH (a)-[r]->(b) RETURN ...` via `ladybug.Connection(db)`).

## What didn't work or surprised us

Everything from the 2026-06-22 REVIEW stands; the measured pass adds:

- **Keyless graph is type-only, relations missing** — this is the summary finding
- **Keyless CHUNKS retrieval beat TF-IDF 4/4 vs 3/4** — that came from the `bge-small-en` embedding vector path, **not the graph**; it is a win for the embedding model choice, not for graph memory. A plain fastembed + LanceDB setup would score identically without any of cognee's graph build cost.
- **Trailing first-use cost** — first `cognify` auto-installed CPU-only PyTorch (~196 MB) plus gliner2 and its tokenizer deps (~17 s to fetch, ~800 MB on disk, ~98 s install) before any graph work started; the eval's first run crashed under disk pressure (root was 100%) and had to be deleted+retried on a recovered disk
- **No keyless on-ramp for graph retrieval**: `LLMAPIKeyNotSetError` surfaces only at query time (not at install or add time), after the ~90 s graph build has already happened
- **`cognee.search(query_type=SearchType.CODE)`** is not raw Cypher despite the name — it is a code/seed resolver that tries to interpret the string as a seed function name and errors out otherwise (`CodeSearchValidationError`); raw Cypher queries have to go via the graph engine directly through `ladybug.Connection`

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | − (keyless) | Built graph carries no relation edges — the differentiating feature is absent from its own keyless demo posture |
| Speed | neutral | graph build only ~76 s on CPU at this corpus size; not the bottleneck for small corpora |
| Maintainability | + | graph-backed store; this isn't the concern raised here |
| Safety | + | dataset isolation, tenant separation, audit traits (unchanged from REVIEW) |
| Cost Efficiency | − (keyless) | ~800 MB disk and GPU-free torch install for a graph that cannot traverse; the actual value paths require a paid LLM key |
| Verifiability | − (keyless) | a user cannot tell without dumping the store that edges never extracted — no warning, no surfaced signal |

## Verdict

**SKIP — keyless posture cannot deliver the platform's core value; keyed posture not exercised here.**

Three real findings, all measured, not review-inferred:

1. **Headline feature (graph-aware retrieval) is LLM-key-gated.** In its keyless demo posture, a new user who runs `cognify` on our eval and then queries `GRAPH_COMPLETION` gets `LLMAPIKeyNotSetError` — 422, every time, on every query type that requires an LLM.
2. **The graph it builds keylessly is a type taxonomy, not a relation graph.** Direct Ladybug dump shows `contains`/`is_a` edges only; the planted relations that should let the graph cross a 3-hop chain were not extracted. That is the specific reason to pick a graph-memory tool, and the keyless build cannot do it.
3. **The keyless retrieval win (CHUNKS, 4/4) is a vector-model win, not a graph win.** It is available anywhere by just picking a better embedding model — `claude-mem` or a plain vector store can match it without importing cognee.

**Keyed posture — disclosed not-run.** The A/B as designed could not exercise GRAPH_COMPLETION without a real OpenAI key, and this eval deliberately refused to add one (repo policy: no real keys in eval drives, no live secrets in the run file). An `adopt-if: you-have-an-llm-key` CONDITIONAL would be the natural verdict if the keyed route is ever measured — but that is an unexercised condition word on a feature we could not test, and a run where the tool's differentiating capability is the thing that was NOT measured should stay honest about its own boundary. The correct record here is that the keyless posture fails its own unique promise, the keyed posture is untested locally, and `claude-mem` (ADOPT, MEASURED) already holds this cluster pick. cognee as a keyed product remains promising (per its published HotPotQA benchmark) but is not measurable here without a key.

This verdict does not assert a real keyed user cannot extract more from cognee than the keyless demo can. It says we did not measure such a setup, and that is why it stands as SKIP (not ADOPT/CONDITIONAL) despite the tool's genuine quality signals.

## What worked

- **Published comparative benchmarks** — 45 evaluation cycles on HotPotQA against Mem0, Graphiti, and LightRAG. Only memory platform in the catalog with peer-reviewed competitive benchmarks (arXiv paper: 2505.24478). Cognee showed consistent improvements across EM, F1, and DeepEval Correctness.
- **Mature Claude Code integration** — 6-hook lifecycle with genuine architectural thought. PostToolUse captures tool traces (not just prompts), PreCompact preserves memory across context resets, SessionEnd bridges session data into the permanent graph. This is the deepest Claude Code hook integration of any memory tool in the catalog.
- **Minimal MCP API** — only 3 core tools (remember, recall, forget) vs mem0's larger surface. Auto-routing in `recall` picks the best search strategy (vector, graph, hybrid) without the user specifying. Session-aware memory with separate fast cache and permanent graph storage.
- **Research-backed architecture** — cognitive-science-grounded ontology generation is a genuine differentiator. The knowledge graph evolves its schema as knowledge grows, rather than using a fixed schema.
- **Deployment flexibility** — 6 one-click deployment options plus managed cloud. Docker Compose for local, Modal/Railway/Fly.io/Render for cloud, Daytona for sandboxes.

## What didn't work or surprised us

- **Heavy infrastructure for local use** — requires Python 3.10+, an LLM API key (OpenAI by default), and builds a local SQLite/graph database. Docker Compose setup adds PostgreSQL. This is significantly heavier than claude-mem (npm plugin, no external dependencies) or engram (single Go binary).
- **OpenAI dependency by default** — `LLM_API_KEY` defaults to OpenAI for graph construction. The remember operation uses LLM calls to build the knowledge graph, adding cost and latency. Other providers are documented but OpenAI is the happy path.
- **Claude Code plugin is in a separate repo** — `cognee-integrations`, not the main monorepo. Discovery is harder, and the plugin repo has lower visibility. Installation requires cloning the integrations repo and pointing `--plugin-dir` at it — not a marketplace install.
- **Commercial trajectory** — Cognee Cloud is the managed product; the OSS version is the on-ramp. The `serve()` API for cloud connection is prominent in docs. Apache-2.0 license is genuine, but the product incentives point toward cloud.
- **Benchmark limitations acknowledged** — the team notes that HotPotQA is a "benchmark mismatch" for memory systems and that LLM-as-judge evaluation carries inconsistencies. Honest, but means the competitive claims are weaker than they appear.

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | + | Graph-connected memory with relationship reasoning surfaces context that flat search misses |
| Speed | neutral | Graph construction adds latency to `remember`; `recall` auto-routing is fast but requires infrastructure |
| Maintainability | + | Knowledge graph evolves with the codebase; relationships between concepts are explicit |
| Safety | + | Dataset-level isolation, user/tenant separation, audit traits |
| Cost Efficiency | - | LLM calls for graph construction add cost; heavier infrastructure than lightweight alternatives |

## Verdict

**discovery-log — tentative read**

Use when you need relationship-aware memory that connects concepts across documents and sessions — the knowledge graph genuinely adds value for complex, multi-domain projects where flat text search misses relationships. The Claude Code integration is the deepest hook-based memory integration in the catalog. Choose claude-mem (ADOPT) for simpler setups where you want local-first memory without infrastructure overhead, or engram (CONDITIONAL) for portable cross-agent memory. Choose cognee when you need the knowledge graph layer, published benchmarks matter, or you're building a team-wide memory infrastructure.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [cognee](https://github.com/topoteretes/cognee) | platform | Open-source AI memory with self-hosted knowledge graph engine for persistent agent memory | Need structured knowledge graph memory that agents can query across sessions | claude-mem, OMEGA, SimpleMem |
