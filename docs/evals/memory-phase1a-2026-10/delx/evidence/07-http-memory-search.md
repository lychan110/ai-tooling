## Evidence 07 — HTTP surface, memory pressure, FTS5 search
HTTP (server under /usr/bin/time -v, DELX_MEMORY_PORT=3037):
- GET /health -> {"ok":true,"name":"delx-memory","version":"0.4.1"}
- POST /mcp sessionless tools/list -> 15 tools
- POST /mcp sessionless tools/call memory_get eval-control-fact -> found:true, exact control value
- /usr/bin/time -v: User 0.61s, System 0.12s, Maximum resident set size 96404 KB, Exit 0. No lingering process after kill.
Lite/CLI call (fresh process, memory_stats): /usr/bin/time -v -> User 0.18s, System 0.05s, wall 0:00.20, Max RSS 68892 KB, minor faults 6844, major 0, swaps 0. doctor --json self-report rss_kb=67432 (consistent).
FTS5 search: memory_search query="credential pools" -> engine:"fts5", count 1, result eval-control-fact score 1.889 with snippet.
