# Evaluation: langfuse

**Repo:** [langfuse/langfuse](https://github.com/langfuse/langfuse)
**Stars:** 35,515 | **Last updated:** 2026-10-08 | **License:** MIT (core, with EE-licensed enterprise features)
**Last verified:** 2026-10-11
**Dev loop stage:** Reflect
**Layer:** Infrastructure

---

## What it does

Self-hostable LLM/agent tracing and observability platform: applications emit traces (with nested spans/generations, scores, sessions, users, tags) via an OpenTelemetry-compatible SDK or raw API, and langfuse stores them in Postgres behind a Next.js web UI and query API. The job in an agent dev loop is *retrospection with accountability*: after a run, answer "what did the agent actually do, per session/user/trace, and was it good?" — the Reflect side of the loop that code-memory tools (engram, cognee) and cost counters (ccusage) do not cover.

Mechanically, in the version measured here (server v2.95.11 + Python SDK 2.61.1): the SDK batches trace/span events client-side and posts them to a single `/api/public/ingestion` endpoint; reads go through paginated `fetch_traces`/`fetch_observations`/`fetch_sessions` filter endpoints; scores are written through the same ingestion queue. One Postgres container is the only backing service at v2 — no ClickHouse/Redis/MinIO (that is the v3 architecture).

## How we tested it

**Evidence:** MEASURED

**hands-on** measured A/B on an isolated rootless-podman stack on 2026-10-11: `langfuse/langfuse:2` server **v2.95.11** (image digest `27c161e3979b`) + `postgres:16-alpine`, bound to `127.0.0.1:3210`, telemetry disabled and verified (`printenv` inside the container), against the Python SDK **2.61.1** on Python 3.12 in a throwaway venv. Keyless in the LLM sense (no LLM provider is involved anywhere; langfuse is tracing infrastructure, not a model call), with only throwaway per-run secrets produced by `env-gen.sh` (`openssl rand`, loopback-only, never committed; `.env.quill` lives in the repo's gitignored `.eval-work/`). First user/org/project/API keys are provisioned headlessly at boot via the documented `LANGFUSE_INIT_*` env-vars — the server's own supported primitive for this; no dashboard clicking, no pre-shared vendor secrets.

**Arm 1 — with-tool (langfuse):** instrument and ingest a 50-trace synthetic agent-workload corpus through the SDK, then retrieve through langfuse's own query API. Every oracle step's correct answer is derived programmatically from the planted corpus (shared single-source `planted.py`), with planted non-answers to catch false-positive query semantics and planted degradation dimensions:

- 50 traces across 6 fixed step names × 5 sessions × 10 service-like users × 6 tags, each with one child span (53 observations total); 3 chain traces carry a planted 3-hop entity chain (RUN-A1 → BND-B1 → ENZ-E1 ← BND-B2) folded across parent/child span payloads, so a 3-hop retrieval question can only be answered by crossing trace→observation→payload hops.
- 15 oracle steps (S0 smoke excluded from discrimination scoring): exact-ID set equality on single-dimension and planted-degradation queries (`llm_call ∧ session-02 →` exactly `trace-027`; `llm_call ∧ wrong-user →` empty), a true 4-way AND (name ∧ tag ∧ user ∧ session), aggregate entity correctness (5 sessions), observation-total count, parent/child topology linkage, payload-3-hop leg intactness, two-tag AND semantics on a deliberately false query, planted 2.5 s span-window respect, total-count consistency — plus one live **write-path** step: post a score mid-run and verify it becomes visible via the read API.

**Arm 2 — baseline (structured logging + grep/jq):** the same corpus emitted as JSON-lines by the same probes, with the 14 discriminating questions expressed as grep/jq filters. Grep answers are correct by construction where a field is greppable; the discriminating questions are (a) the per-question filter cost against raw files and (b) S7/S11, where the answer requires an aggregate reduction and a live write path that a flat log structurally lacks.

### Results (2026-10-11, all commands and full outputs in `.eval-work/langfuse/`, reproducible via `run_all.sh`)

| Oracle step | langfuse | baseline (grep/jq) |
|---|---|---|
| S1 single-dimension name (8 traces) | ✓ exact set | ✓ (one grep) |
| S2 4-way AND name∧tag∧user∧session | ✓ (correctly empty set here) | ✓ (3 chained greps) |
| S3 planted degradation: name ∧ session (1 trace) | ✓ exact set | ✓ |
| S4 planted non-answer: name ∧ wrong user → ∅ | ✓ returned ∅ | ✓ |
| S5 user dimension (5 traces) | ✓ exact set | ✓ |
| S6 tag dimension (8 traces) | ✓ exact set | ✓ |
| S7 aggregate: sessions visible as entities | ✓ 5/5 | ✗ (needs jq -s reduction + dedup; not one grep) |
| S8 observation-total count (53) | ✓ 53/53 | ✓ |
| S9 parent/child topology linkage (trace-045) | ✓ child.parentId == parent.id | ✓ |
| S10 payload 3-hop leg intact (BND-B1→ENZ-E1) | ✓ retrievable in 1 fetch | ✓ |
| S11 live score write→read | ✓ visible 0.3 s | ✗ (no such write path exists in a log file) |
| S12 planted 2.5 s span windows respected | ✓ (3/3) | ✓ |
| S13 trace total == 50 | ✓ | ✓ |
| S14 two-tag AND on false query → ∅ | ✓ returned ∅ | ✓ |

**Discriminated outcome: 15/15 oracle steps pass on langfuse's side; the baseline structurally fails 2 of the 14 discriminating steps** — an aggregate entity view (S7) and a live write path (S11) do not exist in a log file, and no number of greps adds them. Ingest-side numbers, both arms driven by the same SDK probe: enqueue wall 0.03 s for 50 traces (SDK batches client-side), flush wall 3.4 s, all 50 traces visible to the read API 0.07 s after flush. Ops footprint measured on this 2-CPU/4 GB host: web runtime RSS ≈ 198 MB + Postgres ≈ 44 MB; images 835 MB (web) + 297 MB (postgres); **unattended headless boot is a measured, bounded wait** — 271 Postgres migrations apply on first boot inside the web container, then `GET /api/public/health` returns `{"status":"OK","version":"2.95.11"}`.

Three defects found and fixed in **our own oracle** mid-run, all in the measurement, not the tool (recorded because they show the harness self-corrected honestly): a hand-derived intersection that ignored session modulo coupling (fixed by deriving every expected set programmatically from `planted.py`), a stale observation-count constant from an earlier 6-chain design, and an assumed-synchronous `score()` that is actually async-queued (measured visible 0.3 s after flush). None of the three involved the server answering incorrectly; the final run is all-green on the corrected harness.

## Test design

- **Task/corpus:** 50-trace synthetic agent-workload corpus (`planted.py` = single source of truth; 3 planted chain traces with a cross-payload 3-hop chain; planted non-answer dimensions), throwaway keys, loopback-only.
- **Baseline:** structured JSONL logging + grep/jq answerability baseline (same probes, same questions).
- **Metric:** oracle pass-rate k/N per arm (15 steps), plus ingest/flush/visibility wall-clock and container RSS/image-disk footprint.
- **Reproduce:** `sh .eval-work/langfuse/run_all.sh` (scratch harness, gitignored; regenerates `.env.quill` each run, recreates containers fresh).

```
sh .eval-work/langfuse/run_all.sh   # → {"verdict":"ALL_PASS","steps":15}, 15/15 lines
```

## What worked

- **15/15 oracle steps** — every filter dimension the SDK exposes behaves exactly as documented, including the planted-degradation and deliberately-false queries where the only correct answer is the empty set.
- **Genuine keyless onboarding** — `LANGFUSE_INIT_*` provisions org/project/user/API-keys at boot; a headless script drives the whole stack without touching the dashboard or a real vendor secret. Contrast measured directly on cognee 2026-10-05, whose keyless posture shipped a graph with zero relation edges and surfaced `LLMAPIKeyNotSetError` only at query time.
- **The introspection contract is wide** — parent/child observation topology with working `parentId` linkage (S9), payload-faithful spans (S10), session aggregates (S7), and a two-way write path (S11): enough for an agent to answer "what did I do and was it good" without clicking anything.
- **Fast batched ingestion and read-your-writes at this scale** — enqueue 0.03 s / flush 3.4 s / visibility 0.07 s for 50 traces on a 2-CPU host; score read-back 0.3 s.
- **Smaller than its reputation** — v2 single-container + Postgres, measured 242 MB combined RSS, UI reachable without exposing any non-loopback port.

## What didn't work or surprised us

- **`NEXTAUTH_URL` is load-bearing and deployment-shape-sensitive.** Kept at the container-internal address here, it made a loopback-only consumer work while the host-visible UI alias stays broken — the supported contract assumes the service genuinely owns a published interface (per upstream docs, `NEXTAUTH_URL` misconfiguration is the canonical self-hosting error). A loopback-only deployment must set it to the container-internal URL; a published deployment must set it to the public URL. This is the one deployment footgun the eval hit, and it is inherent to the service's own-goal-of-dashboard design rather than fixable by a flag.
- **Every write path is async-queued with no wait-for-visibility primitive** — `score()` returns long before the score exists; read-your-writes requires hand-rolled flush-and-poll (S11 measured the 0.3 s lag). Not a defect — an ingestion-server trade — but a real operational expectation to set.
- **Docker daemon access is a real setup step** (socket-group membership on this host denied it); rootless podman ran the published images unchanged, so the published-image default kept setup honest for either runtime.
- **No raw SQL/structured payload-search surface** — search beyond the exposed filters must be pulled-and-filtered client-side, which is exactly what the eval's grep baseline does for free and where it stays competitive per-question.

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | + | 15/15 oracle steps, including planted-degradation and false-query discrimination — no false positives, no silent wrong answers |
| Speed | + | enqueue 0.03 s / flush 3.4 s / read-visibility 0.07 s for 50 traces on a 2-CPU/4 GB rootless host |
| Maintainability | neutral | MIT core, one Postgres container at v2; the v3 migration path exists but was not exercised |
| Safety | + | telemetry verified disabled; throwaway per-run secrets; loopback-only port mapping |
| Cost Efficiency | + | 242 MB combined RSS measured; only cost is disk for images (1.13 GB) |
| Verifiability | + | version-string health endpoint, per-query exact-ID oracle, reproducible one-script `run_all.sh` |

## Verdict

**KEEP — measured, but scoped to where it fits.**

The eval's question — "does a self-hosted langfuse replace a structural-logging baseline for agent-run retrospection?" — took 15 oracle steps spanning every exposed retrieval dimension, planted non-answers, aggregate entity views, and a live write path, and langfuse answered all of them correctly while the grep baseline structurally cannot answer 2. It is the only tool of its kind in the catalog whose keyless posture was measured end-to-end here (server boot → headless key provisioning → instrumented ingest → read-back), with ops footprint measured, not estimated. That earns **KEEP** as the self-hosted agent-run retrospection pick of its cluster — **not ADOPT**: this is infrastructure a project adopts when it actually needs a hosted trace store, not a default every project should carry, and the eval measured the default keyless path only — no load testing, no v3 stack, no CI-integration surface. The grep/jq baseline stays competitive for single-run debugging where the two structural gaps (aggregates, live write path) do not bite.

Adopt-if: a project actually runs multi-session agent loops needing per-trace retrospection with accountability (scores/sessions/observation trees) and accepts the ~240 MB RSS + Postgres container. Skip-if: single-shot scripts where `jsonl + grep` already answers every question.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [langfuse](https://github.com/langfuse/langfuse) | platform | Self-hostable LLM/agent tracing with sessions, scores, and nested observation trees (SDK/OTel ingest; one Postgres container at v2) | Need per-trace agent-run retrospection with accountability (who/what/how-good) that flat logs cannot aggregate or score | ccusage, engram, Opik |