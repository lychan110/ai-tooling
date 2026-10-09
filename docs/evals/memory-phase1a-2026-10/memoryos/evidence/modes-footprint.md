# Non-Docker modes + footprint — REVIEW (source-cited)

## Non-Docker install mode: NONE exists.
- setup.sh Phase 2: exits 1 on `docker info` failure ("Docker is not run — install and start Docker first"). No `--no-docker` flag anywhere.
- README Requirements: "Hermes Agent + Docker (Qdrant + Redis + ARQ Worker) + Python 3.11+". QUICKSTART: "Requires: Docker, Python 3.11+, Hermes Agent (v0.14.0+)".
- **'ollama' appears ONLY as an LLM/embedding backend choice — never as infra replacement:**
  - `.env.example:48-52` — OLLAMA_BASE_URL=http://localhost:11434, OLLAMA_EMBEDDING_MODEL=nomic-embed-text ("If both are set, Ollama takes priority (local, zero cost)") — i.e. Ollama runs on the HOST; the worker still runs in Docker.
  - `docker/worker/services/embedding.py:3,54` — EMBEDDING_API_BASE points at "local Ollama/vLLM/llama.cpp"; :54 dimensions ignored by those backends.
  - `docker/worker/services/llm.py:2,11-13,23-29` — `ollama_chat()` for reflection; default OLLAMA_BASE_URL `http://host.docker.internal:11434` (host Ollama).
  - `setup/install.md:12` — local providers need no API key.
- **4-level fallback (layers/05-qdrant.md)** hybrid → dense → lexical (vault md search) → SQLite `lineage` → empty is a fail-open RUNTIME degradation when Qdrant is offline — NOT an install mode. Redis + ARQ worker still required for ingestion.
- Docker-free pieces: SQLite DBs (`setup/setup_db.py`), Icarus plugin copy, `context_enhancer.py` imports (fail-open), wiki vault dirs. Everything vector/queue-related needs Docker.

## RAM footprint estimate (host: 3814 MB total, 2347 MB available, swap 4095/1976 used)
Documented in repo:
- Redis: `maxmemory 512mb` cap (docker-compose.yml redis.conf)
- Qdrant v1.17.1, collection `knowledge_base`: dense 4096d Cosine + sparse BM25; **sparse index `on_disk: false` = in-memory** (layers/05-qdrant.md collection schema; local_qdrant.py)
- Worker: Python ARQ (ARQ_MAX_JOBS=10) with REMOTE embeddings (qwen3-embedding-8b via OpenRouter API — no local model RAM) + local fastembed BM25
Computed (terminal, `4096*4` bytes): 1 dense vector = 16,384 B → 1k pts ≈ 15 MB, 10k ≈ 156 MB, 50k ≈ 781 MB raw vector bytes, plus Qdrant index/RSS + 3 containers + Docker daemon (~0.5-1 GB typical on this class).
Estimate: full stack ≈ **1.5-2.5 GB RSS** → on this host that leaves <1 GB headroom (1.9 GB already used, swap 2 GB in use). HIGH OOM RISK. Local Ollama embedding (nomic-embed-text) would add ~0.5-1 GB more.
