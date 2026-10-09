# SQLite schemas — REVIEW (setup/setup_db.py @ HEAD)

Default paths: `~/.hermes/state.db`, `~/.hermes/memory_store.db`. Env overrides: STATE_DB_PATH, MEMORY_STORE_PATH. `--dry-run` prints SQL without executing (Docker NOT required).

## state.db (STATE_SCHEMA)
- `sessions` (id TEXT PK, source, user_id, model_config, system_prompt, parent_session_id FK→sessions, started_at, ended_at, end_reason, message_count, tool_call_count, input/output/cache_read/cache_write/reasoning tokens, billing fields, estimated/actual cost, handoff fields, rewind_count, archived)
- `messages` (id INTEGER PK AUTOINCREMENT, session_id FK, role, tool_call_id, tool_calls, tool_name, timestamp, token_count, finish_reason, reasoning, reasoning_content, reasoning_details, codex_reasoning_items, codex_message_items, platform_message_id, observed, active)
- `messages_fts` — VIRTUAL FTS5, `content=messages`, `content_rowid=id`
- `messages_fts_trigram` — VIRTUAL FTS5, `tokenize='trigram'`, `content=messages`
- `lineage` (lineage_id TEXT PK, retrieved_chunk_ids, generation_model, generation_context_hash, created_at)
- `reflection_budget` (hour_window TEXT PK, count, tokens_used)
- `compression_locks` (session_id TEXT PK, holder, acquired_at, expires_at)
- `schema_version` (version INTEGER)
- `state_meta` (key TEXT PK, value…)

## memory_store.db (MEMORY_SCHEMA)
- `entities` (entity_id INTEGER PK AUTOINCREMENT, entity_type, aliases, created_at)
- `facts` (fact_id INTEGER PK AUTOINCREMENT, content TEXT NOT NULL UNIQUE, category, trust_score REAL DEFAULT 0.5, retrieval_count, helpful_count, created_at, updated_at, …)
- `fact_entities` (fact_id FK, entity_id FK, PK(fact_id, entity_id)) — many-to-many junction
- `facts_fts` — VIRTUAL FTS5 (content, tags; `content=facts`, `content_rowid=fact_id`)
- `memory_banks` (bank_id INTEGER PK AUTOINCREMENT, bank_name TEXT NOT NULL UNIQUE, fact_count, updated_at) — HRR-composable fact groups

setup_db.py also prints the Qdrant collection bootstrap (`curl -X PUT :6333/collections/knowledge_base` with 4096d Cosine dense + sparse).
