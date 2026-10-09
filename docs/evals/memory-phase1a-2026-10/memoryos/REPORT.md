# Memory-OS Blocker-Probe Eval — REPORT
Date: 2026-10-08 · Host: Linux 7.0.0-29-generic, 3814 MB RAM (2347 available), user lychan · Repo: ClaudioDrews/memory-os @ HEAD

## VERDICT (blocker)
**YES — docker-group membership is the unblock.** The Docker socket is `root:docker` mode 0660 (`srw-rw---- 1 root docker /var/run/docker.sock`); the CLI error is a connect() EACCES on that socket; `id` shows lychan in groups `1000,27(sudo),100(users)` — no `docker` gid. Only paths: root runs `usermod -aG docker lychan` (an admin action this account cannot perform: sudo is deny-ruled at the agent level and unavailable per host facts). No workarounds attempted (newrootdedicated etc. out of scope); none exist that bypass socket perms for an unprivileged user.

## Blocker evidence (MEASURED)
- `id` → `uid=1000(lychan) gid=1000(lychan) groups=1000(lychan),27(sudo),100(users)`
- `docker info` → exit 1: `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock` (client 29.1.3 + compose 2.40.3 present)
- `ls -la /var/run/docker.sock` → `srw-rw---- 1 root docker 0 Aug 6 03:50 /var/run/docker.sock`
- `sudo -n true` → BLOCKED by deny rule 'sudo *'; no sudo on host
- Daemon liveness unverifiable (connect fails before server handshake). Raw: evidence/blocker.md

## Source-grounded addendum (REVIEW)
### Service list (docker/docker-compose.yml) — 3 services, 2 volumes
1. redis:7-alpine — 127.0.0.1:6379, maxmemory **512mb**, allkeys-lru, appendonly
2. qdrant/qdrant:v1.17.1 — 127.0.0.1:6333, volume qdrant_data:/qdrant/storage
3. worker — build ./worker, depends redis+qdrant healthy; remote embeddings (qwen/qwen3-embedding-8b via OpenRouter, EMBEDDING_DIMS=4096, COLLECTION_NAME=knowledge_base, ARQ_MAX_JOBS=10); mounts wiki:ro, hermes:rw, fabric:rw
Volumes: redis_data, qdrant_data. setup.sh hard-fails at Phase 2 (`docker info` check → exit 1); full detail evidence/services-compose.md

### SQLite schema (setup/setup_db.py)
state.db: sessions, messages, messages_fts (FTS5), messages_fts_trigram (FTS5 trigram), lineage, reflection_budget, compression_locks, schema_version, state_meta
memory_store.db: entities, facts, fact_entities, facts_fts (FTS5), memory_banks
Defaults ~/.hermes/{state,memory_store}.db; `--dry-run` works without Docker. Full detail evidence/schema-db.md

### Icarus plugin load (Hermes plugin entry format)
Directory plugin: `~/.hermes/plugins/icarus/` (setup.sh Phase 5 `cp -r`), manifest `plugin.yaml` (name/version/description + `provides_tools` 15: fabric_recall, fabric_write, fabric_search, fabric_pending, fabric_curate, fabric_export, fabric_train, fabric_train_status, fabric_models, fabric_eval, fabric_switch_model, fabric_rollback_model, fabric_telemetry, fabric_init_obsidian, fabric_report; `provides_hooks` 2: on_session_start, pre_llm_call) + python modules.
Fact-write paths: `fabric_write` → `state.write_entry()` → `$FABRIC_DIR/{agent}-{type}-{slug}-{4hex}.md` (markdown + YAML frontmatter; setup.sh sets FABRIC_DIR=$VAULT_PATH/fabric; default ~/fabric); plus .icarus-state.json / -models.json / -telemetry.jsonl under HERMES_HOME. Reads: state.db messages_fts, memory_store.db facts_fts, Qdrant via scripts/context_enhancer.py (all fail-open).
⚠️ Discrepancy: docs claim 16 tools (fabric_brief) / 4 hooks (post_llm_call, on_session_end); plugin.yaml declares 15/2 — tools.py does implement fabric_brief. Verify hands-on whether undeclared items load. Full detail evidence/icarus-plugin.md

### Non-Docker modes — NONE for infra; Ollama is backend-only
No `--no-docker` flag; setup.sh exits 1 without Docker. 'ollama' appears only as LLM/embedding backend (.env.example:48-52; embedding.py:3,54; llm.py:11-13 — host-side Ollama at host.docker.internal:11434; worker stays in Docker). The 4-level fallback (layers/05-qdrant.md: hybrid→dense→lexical→SQLite lineage→empty) is fail-open runtime degradation, not an install mode. Docker-free pieces: setup_db.py SQLite DBs, Icarus plugin, context_enhancer imports (fail-open), vault dirs. Full detail evidence/modes-footprint.md

### Footprint estimate (host 3814 MB total / 2347 available)
Redis capped 512mb (compose); Qdrant v1.17.1 with 4096d dense (16 KB/vector computed: 1k pts≈15 MB, 10k≈156 MB, 50k≈781 MB raw) + sparse BM25 index on_disk:false (in-memory); worker = Python ARQ + remote embeddings (no local LLM RAM) + fastembed BM25. Stack + daemon ≈ 1.5-2.5 GB RSS → <1 GB headroom on this host (1.9 GB already used, swap 2 GB in use). HIGH OOM RISK; local Ollama embedding would add ~0.5-1 GB.

## What the later hands-on eval needs (checklist)
1. **Unblock first (root/admin)**: `usermod -aG docker lychan` + re-login; then `docker info` + `docker compose ps`. Without it, skip to 3-7 only.
2. If unblocked: run setup.sh or manual install; watch Phase 2 pre-flight, worker build (5-10 min), healthchecks.
3. Docker-free: `python3 setup/setup_db.py --dry-run` (then for real in a THROWAWAY HERMES_HOME, e.g. `HERMES_HOME=$HOME/.hermes-eval` — do NOT touch live ~/.hermes DBs); verify tables via sqlite_master.
4. Plugin: copy icarus/ to a scratch plugins dir, `hermes plugins list`; test whether fabric_brief loads despite missing from plugin.yaml (declared 15 vs docs' 16) and whether post_llm_call/on_session_end hooks run (declared 2 vs docs' 4).
5. `fabric_write` → assert `{FABRIC_DIR}/{agent}-{type}-{slug}-{hex}.md` created with expected frontmatter; then fabric_recall/search/pending.
6. Smoke tests: `setup/smoke_test.sh --quick` (needs Redis+Qdrant up) and `icarus/scripts/test-plugin.sh`.
7. Ingestion E2E: `scripts/test_ingestion.py`, hourly cron `wiki_continuous_ingest.py`, then Qdrant `knowledge_base` collection check (4096d) + 4-level fallback behavior with qdrant down (hooks must fail-open).
8. RAM watch: `free -m` before/after stack start; expect <1 GB headroom — OOM kill is the likely failure mode on this box.

## Evidence class
- MEASURED: blocker probe only (`id`, `docker info`, `ls -la /var/run/docker.sock`, `free -m`, sudo-deny) — evidence/blocker.md
- REVIEW: all source reading (compose, setup.sh, setup_db.py, plugin.yaml, tools.py, state.py, hooks.py, layers/*, QUICKSTART, .env.example, smoke_test.sh) — evidence/services-compose.md, schema-db.md, icarus-plugin.md, modes-footprint.md
- ESTIMATE (labeled, arithmetic computed on terminal; no invented numbers).
