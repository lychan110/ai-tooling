# delx-memory (github.com/davidmosiah/delx-memory v0.4.1, MIT) — hands-on eval
Date: 2026-10-08 (EDT). Workspace: /home/lychan/.hermes/cache/scratch/eval-delx
Raw outputs: evidence/01-install.md … 07-http-memory-search.md (this dir)

## Verdict candidate
ADOPT — feasibility confirmed in keyless/local mode: installs without sudo/docker/go, one shared SQLite store readable/writable across distinct client processes over CLI, real MCP stdio (lite) and sessionless HTTP; secret-blocking, TTL and namespace isolation all verified with real outputs. Caveat: namespace isolation is opt-in key-prefixing, NOT storage-layer enforcement — REVIEW before multi-tenant use. Evidence class: MEASURED.

## Mode tested
- Posture: keyless / local-only. No accounts, no telemetry endpoints contacted, no sudo/docker/go.
- Host: Linux x86_64, node v26.7.0, npm 11.19.0, ~1.5GB free RAM (2GB swap used), 2 CPUs.
- Surfaces exercised: `delx-memory call <tool> --json` (CLI tool surface), MCP stdio (default lite transport, 15 tools), Streamable HTTP (--http, sessionless POST /mcp), direct SQLite artifact reads via better-sqlite3.
- Clients: each `call` invocation = fresh Node process; MCP stdio test used two independent client processes each spawning its own server process; HTTP used curl.

## Fixture & commands (exact, reusable)
Env: `export DELX_MEMORY_PATH=$PWD/data/db.sqlite` for every client below (same SQLite file).

1) INSTALL (no sudo/docker/go): in an empty dir with its own package.json:
   `npm install delx-memory@0.4.1` -> "added 130 packages" / 0 vulnerabilities; bin at node_modules/.bin/delx-memory.
   (Host gotcha: npm 11 resolves `local prefix` to the nearest package.json walking UP — first attempt landed in ~/.hermes; cleaned with `npm uninstall delx-memory` from ~/.hermes; a local package.json prevents this.)
2) CONTROL FACT — write client A, read client B (distinct processes):
   `bash scripts/client-a.sh`  (exec: delx-memory call memory_set --json '{"key":"eval-control-fact","value":{"fact":"hub org delegates provider selection to credential pools"},"tags":["eval","control"],"explicit_user_intent":true}')
   `bash scripts/client-b.sh`  (exec: delx-memory call memory_get --json '{"key":"eval-control-fact"}')
3) SECRET PROBE — expect refusal, exit 1, no row:
   `delx-memory call memory_set --json '{"key":"eval-aws-probe-2","value":"AKIAIOSFODNN7EXAMPLE","explicit_user_intent":true}'`
4) TTL PROBE:
   `delx-memory call memory_set --json '{"key":"eval-ttl-probe","value":{"note":"short-lived"},"ttl_seconds":2,"explicit_user_intent":true}'`
   then immediate `call memory_get`; `sleep 4`; `call memory_get` again; `call memory_list --json '{"prefix":"eval-ttl"}'`.
5) NAMESPACING PROBE:
   `DELX_MEMORY_NAMESPACE=eval-agent-A delx-memory call memory_set --json '{"key":"eval-ns-probe","value":{"scope":"written-by-A"},"explicit_user_intent":true}'`
   `DELX_MEMORY_NAMESPACE=eval-agent-B delx-memory call memory_get --json '{"key":"eval-ns-probe"}'`
6) MCP STdio (real protocol): `node scripts/mcp-client.mjs set eval-mcp-fact '{"fact":"written over MCP stdio by client A"}'` then `node scripts/mcp-client.mjs get eval-mcp-fact`.
7) HTTP: `bash scripts/measure-http.sh` (spawns --http on :3037 under /usr/bin/time -v, curls /health and sessionless /mcp).
8) ARTIFACT: `node scripts/dump-db.mjs data/db.sqlite` (better-sqlite3 readonly) -> schema objects + rows; `stat -c 'mode=%a path=%n' data data/db.sqlite`.

## Observations (claim -> artifact that proved it)
- Install w/o sudo/docker/go: PASS — `npm install delx-memory@0.4.1` in eval-delx: "added 130 packages", 0 vulns; bin + better-sqlite3 native binding present; doctor --json {"ok":true,"rss_kb":67432}. Evidence: 01-install.md.
- Control-fact cross-process roundtrip: PASS — process 1836153 (memory_set, action:created) -> distinct process 1836160 (memory_get, found:true, value verbatim "hub org delegates provider selection to credential pools"). Evidence: 02-roundtrip-cli.md.
- Secret probe blocked: PASS — memory_set with value "AKIAIOSFODNN7EXAMPLE" refused: "value at '<value>' matches AWS access key pattern" (exit 1); nested field 'credentials' also refused; get/list show no rows. Evidence: 03-secret-blocked.md.
- TTL: PASS — ttl_seconds=2 -> ttl_expires_at = created+2000ms; get at +242ms found:true; after 4s found:false and list count 0 (lazy sweep). Evidence: 04-ttl.md.
- Namespacing: PASS w/ caveat — eval-agent-B cannot see eval-agent-A's key (found:false, list 0); A reads it back; at rest stored as "eval-agent-A::eval-ns-probe"; DEFAULT scope lists it (prefix scheme, no storage-layer enforcement). Evidence: 05-namespace.md.
- Cross-tool shared store (decisive): PASS twice — (a) MCP stdio: client 1839199+server 1839207 wrote, client 1839214+server 1839222 read; 15 tools over initialize/tools/list/tools/call JSON-RPC. (b) HTTP sessionless POST /mcp returned the control fact. Evidence: 06-mcp-stdio.md, 07-http-memory-search.md.
- Artifact (acceptance #5): PASS — readonly better-sqlite3 dump of data/db.sqlite: table memory(key,value,created_at,updated_at,ttl_expires_at,tags,metadata) + memory_fts (FTS5: config/data/docsize/idx) + indexes idx_memory_ttl/tags/updated_at + triggers memory_fts_ai/ad/au; 3 rows at rest (control, ns-probe, mcp-fact); TTL row absent (swept), secret rows absent; data dir mode 700, db file mode 600.

## Weaknesses observed (scoped: keyless/local mode)
1. Namespace isolation is opt-in key-prefixing: unscoped/default clients read ALL namespaced keys (proved: default list shows "eval-agent-A::eval-ns-probe"). Fine for same-trust multi-agent; NOT multi-tenant security.
2. Key-name secret filter is substring-based and aggressive: any key containing "secret"/"token"/"password"/"credential"/"session_id" is refused (probe: key "eval-secret-probe" blocked even though it was the VALUE that mattered); nested field names (e.g. "credentials") blocked even with benign values. Legit keys can false-positive.
3. Value detector is regex-only on known shapes: an AKIA key split across two fields or otherwise obfuscated would pass; no entropy/heuristic layer. Documented as high-specificity by design.
4. Store is unencrypted SQLite; README admits other local users can read the 0600 file (root/housemate) and no durability promise (no VACUUM, lazy TTL means expired pages linger on disk).
5. Mutation gate `explicit_user_intent: true` is a schema-required flag an agent can always set — a soft convention, not user verification.
6. npm 11 needs install-scripts approval for better-sqlite3's postinstall; without it the native binding may not build (prebuilt present here). Host gotcha: bare `npm install <pkg>` in a dir without package.json resolves prefix to nearest package.json walking up (~/.hermes) — always create a local package.json first.
7. Baseline RSS ~67MB even in "lite" mode; ~96MB with --http (Express+SDK). On a 1.5GB-free host, one persistent server per agent adds up; the `call` CLI avoids it (process exits) but stdio/HTTP servers stay resident.

## Memory/CPU pressure observed (host: 1.5GB free, 2GB swap in use, 2 CPUs)
- Lite/CLI one-shot call (memory_stats, fresh process): /usr/bin/time -v -> user 0.18s, sys 0.05s, wall 0.20s, Max RSS 68,892 KB, minor faults 6,844, major 0, swaps 0. doctor self-report rss_kb=67,432 (consistent).
- HTTP server (--http, Express+SDK, measured under /usr/bin/time -v while serving /health + 2 MCP calls): user 0.61s, sys 0.12s, Max RSS 96,404 KB, exit 0.
- No OOM, no swap growth during eval; ~69MB peak per resident process is the dominant footprint.

## Verdict scope (what remains untested)
- SDK transport (--sdk prompts/resources) and DELX_MEMORY_LEAN variants — only lite stdio + HTTP exercised.
- Batch/export/forget tools (memory_set_batch, memory_export, memory_forget, memory_forget_by_tag) — registered (15 tools) but not driven.
- Multi-writer concurrency: WAL + busy_timeout 5000 present; no concurrent-writer stress test run.
- Durability: no kill -9 / power-loss test; TTL long-expiry persistence not observed beyond 2s case.
- Boundary behavior: 64KB value cap, 512-char key cap, 32-tag cap, FTS5 porter/diacritic edge cases not probed.
- Windows/WSL, node 20-24 (tested only on node 26.7.0), and cross-machine use (none claimed).
- Zero-telemetry claim: no outbound traffic observed during eval, but no network capture was run — treat as partially verified.

## Evidence class
MEASURED — every acceptance check backed by real command output saved under evidence/01..07 and the SQLite artifact itself (schema + rows read back with better-sqlite3, not tool-printed text). No invented numbers; anything unmeasured is marked untested above.

## Acceptance checklist (all 5 PASS)
1. Install w/o sudo/docker/go: PASS (npm local install, 130 pkgs, 0 vulns, runtime OK).
2. Control fact roundtrip across two distinct client processes: PASS (CLI A->B, MCP stdio A->B, HTTP read).
3. Secret probe visibly blocked: PASS (AWS-key value refused, exit 1, no row persisted).
4. TTL behavior confirmed: PASS (created+2000ms, retrievable before, swept after).
5. SQLite artifact inspected: PASS (schema objects + 3 persisted rows read back from file; perms 700/600).
