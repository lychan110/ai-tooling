# Icarus Hermes plugin — REVIEW (icarus/ @ HEAD)

## Install path (setup.sh Phase 5)
`cp -r icarus/` → `~/.hermes/plugins/icarus` (HERMES_HOME=`~/.hermes`).

## Hermes plugin entry format
`icarus/plugin.yaml` manifest + Python modules in the same dir:
- `plugin.yaml`: name: icarus, version: 0.3.0, description, author: esaradev
  - `provides_tools` (15): fabric_recall, fabric_write, fabric_search, fabric_pending, fabric_curate, fabric_export, fabric_train, fabric_train_status, fabric_models, fabric_eval, fabric_switch_model, fabric_rollback_model, fabric_telemetry, fabric_init_obsidian, fabric_report
  - `provides_hooks` (2): on_session_start, pre_llm_call
- Modules: __init__.py, hooks.py, tools.py, state.py, collapse.py, parsing.py, schemas.py, obsidian.py, export-training.py, fabric-retrieve.py

⚠️ Doc/source discrepancy to verify hands-on: README + layers/04 claim "16 tools (…fabric_brief…)" and "4 hooks (…post_llm_call, on_session_end)". plugin.yaml declares 15 tools / 2 hooks; tools.py DOES implement fabric_brief (16th). Whether Hermes loads undeclared tools/hooks is untested (blocked by Docker gate only indirectly — plugin load is Docker-free, but installing it into the live ~/.hermes was out of scope).

## Fact-write paths (tools.py `fabric_write` → state.py `write_entry`)
- Writes markdown + YAML frontmatter to `$FABRIC_DIR` (env; default `~/fabric`; setup.sh sets `FABRIC_DIR=$VAULT_PATH/fabric`):
  `{FABRIC_DIR}/{agent}-{entry_type}-{slug}-{4hex}.md` — atomic `.tmp` write
- Entry types: decision, resolution, note, code-session, session, review, research, task
- Frontmatter fields: id, agent, platform, timestamp, type, tier, summary, project_id, session_id, tags, status, outcome, review_of, revises, customer_id, assigned_to, training_value, verified, evidence, source_tool, artifact_paths
- Returns `{"status":"written","path":...}`
- Optional Obsidian post-format if `ICARUS_OBSIDIAN=1`
- Other files under HERMES_HOME: `.icarus-state.json`, `.icarus-training-job.txt`, `.icarus-models.json`, `.icarus-telemetry.jsonl`

## Read paths (fail-open)
- `_search_sessions` → FTS5 `messages_fts` in `~/.hermes/state.db` (read-only URI)
- `_search_facts` → FTS5 `facts_fts` in `~/.hermes/memory_store.db`
- `_search_qdrant` → `scripts/context_enhancer.py` `search_with_fallback()` (needs Qdrant + remote embedding API)
