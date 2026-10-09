## delx-memory eval — install evidence
Date: 2026-10-08 (UTC-04:00)

### Attempt log
- ATTEMPT 1 (FAILED placement): `cd eval-delx && npm install delx-memory@0.4.1`
  -> npm 11.19.0 resolved `npm local prefix = /home/lychan/.hermes` (nearest package.json walking up from scratch dir = Hermes' own package.json).
  -> "added 119 packages, audited 268 packages in 1m" but files landed in /home/lychan/.hermes/node_modules/delx-memory; ~/.hermes/package.json + package-lock.json modified.
  -> Cleanup: `cd /home/lychan/.hermes && npm uninstall delx-memory` (exit 0). Verified REMOVED: node_modules/delx-memory, node_modules/.bin/delx-memory. `npm ls delx-memory` from ~/.hermes -> "(empty)".
- ATTEMPT 2 (SUCCESS, isolated): created eval-delx/package.json {"name":"delx-memory-eval","private":true,"version":"0.0.0"} so npm stops walking up; then `npm install delx-memory@0.4.1` from eval-delx.
  -> "added 130 packages, and audited 131 packages in 5s" / "found 0 vulnerabilities"
  -> Probes OK: node_modules/delx-memory/package.json, node_modules/.bin/delx-memory, node_modules/better-sqlite3/build/Release/better_sqlite3.node
  -> npm warn install-scripts: better-sqlite3@12.11.1 install script not covered by allowScripts (prebuild-install || node-gyp rebuild) — native binding file still present, runtime confirmed working.

### Runtime check
`./node_modules/.bin/delx-memory version` -> 0.4.1 (exit 0)
`DELX_MEMORY_PATH=<eval>/data/db.sqlite ./node_modules/.bin/delx-memory doctor --json` -> {"ok":true,"version":"0.4.1","rss_kb":67432,"checks":{"node_supported":true,"db_writable":true,"permissions_ok":true}}

### Environment notes
- node v26.7.0, npm 11.19.0, no sudo/docker/go used anywhere.
- ~/.hermes restored to pre-install state (npm ls -> (empty)).
