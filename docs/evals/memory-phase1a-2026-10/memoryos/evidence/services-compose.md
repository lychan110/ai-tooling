# Docker Compose service list — REVIEW (docker/docker-compose.yml @ HEAD)

Exactly 3 services + 2 named volumes. No other containers.

1. **redis** — image `redis:7-alpine`, restart unless-stopped
   - port `127.0.0.1:6379:6379`
   - redis.conf generated at start: `requirepass $REDIS_PASSWORD`, `bind 0.0.0.0`, `appendonly yes`, **`maxmemory 512mb`**, `maxmemory-policy allkeys-lru`
   - volume `redis_data:/data`; healthcheck: `redis-cli ping`
2. **qdrant** — image `qdrant/qdrant:v1.17.1`, restart unless-stopped
   - port `127.0.0.1:6333:6333`; volume `qdrant_data:/qdrant/storage`
   - env `QDRANT__SERVICE__HTTP_PORT=6333`, `QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY}`
   - healthcheck: `grep -q ':18BD' /proc/net/tcp` (6333 = 0x18BD; image lacks curl/python)
3. **worker** — build `./worker` (Dockerfile; gcc/build-essential), restart unless-stopped
   - depends_on: redis healthy + qdrant healthy
   - env: REDIS_HOST=redis, REDIS_PORT=6379, QDRANT_HOST=qdrant, QDRANT_PORT=6333, OPENROUTER_API_KEY, EMBEDDING_API_BASE=`https://openrouter.ai/api/v1`, EMBEDDING_MODEL=`qwen/qwen3-embedding-8b`, EMBEDDING_DIMS=`4096`, COLLECTION_NAME=`knowledge_base`, ARQ_JOB_TIMEOUT=300, ARQ_MAX_JOBS=10, ARQ_KEEP_RESULT=3600, LOG_LEVEL=INFO
   - volumes: `${MEMORY_OS_WIKI_PATH}:/wiki:ro`, `${MEMORY_OS_HERMES_HOME}:/hermes:rw`, `${MEMORY_OS_FABRIC_DIR}:/fabric:rw`
   - healthcheck: python redis ping with REDIS_PASSWORD

volumes: `redis_data`, `qdrant_data`.

## setup.sh behavior (REVIEW)
- Phase 2 pre-flight: `if docker info >/dev/null 2>&1; then ok; else fail "Docker is not run — install and start Docker first"; exit 1` — **hard-fails on this host.**
- Phase 7: `docker compose pull redis qdrant` → `docker compose build worker` (setup.sh notes 5-10 min first build) → `docker compose up -d` → expects "3 services (redis, qdrant, worker)" healthy.
- Phase 5: `cp -r icarus/` → `~/.hermes/plugins/icarus`. Phase 7b: installs hourly cron `wiki_continuous_ingest.py`. Phase 9: appends `modifications/execution-agent-protocol.md` to SOUL.md/rulebook. Phase 10: `hermes gateway restart`.
