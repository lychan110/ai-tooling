# Evaluation: uncut

**Repo:** [Balanov/uncut](https://github.com/Balanov/uncut)
**Stars:** 504 | **Last updated:** 2026-11-02 (pushed) | **License:** MIT
**Last verified:** 2026-11-02
**Last triaged:** 2026-11-02  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Tooling (headless agent harness)

---

## What it does

A deliberately tiny coding-agent harness: one statically linked Go binary (~7 MB, 837 lines
of implementation across four tools), no TUI, no telemetry, no plugin system, no automatic
retries, no context compaction. The whole conversation is sent on every model call, file
contents and combined command output are never truncated, and if the provider cuts a response
at its output limit UNCUT exits with an error (code 3) instead of presenting a partial answer
as success. Final text goes to stdout; `--json` emits NDJSON events (`user`, `assistant`,
`assistant_meta`, `tool`, `done`/`error`); `--session` resumes an append-only JSONL session.
Works with any OpenAI-compatible Chat Completions endpoint (including local servers and
Ollama). The four tools are `read_file`, `write_file`, `replace` (exactly one occurrence;
zero or multiple matches fail) and `run_command`, all scoped to the workspace directory.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: GitHub repo
metadata (stars, pushed date, licence, fetched 2026-11-02) plus the README read at HEAD. The
repo is 1 day old (created 2026-11-01) at `v0.1.1`, and its lossless contract is verified by
the vendor's own `bench/proof.py` driving the real binary against a deterministic local
provider — a transport proof we did not re-run. No model call, session or measurement is
claimed here.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at discovery-log
rather than SKIPped.

## Triage note

The `Overlaps with` cell names `opencode` (a STACK pick, ADOPT, MEASURED), which is therefore a
real incumbent — but the distinct claim here is not "another harness", it is the lossless
contract: no silent summarization, pruning, sliding windows or output caps, and an explicit
error instead of a partial answer. `opencode` compacts and truncates by design; `smallcode`
budgets context for small models; `jcode` targets RAM efficiency; `durable-harness` wraps
other harnesses for crash-resumability. None of the four ships the lossless-by-default loop as
its headline, so a redundancy SKIP has no incumbent whose claim it fully covers. The repo being
one day old at `0.1.x` is a reason to keep it a lead rather than dispose of it; the deciding
test would be the vendor's own `bench/proof.py` (large-file and large-output round trips,
exact session resume, explicit truncation failure) run here on a local model. Left for the
P0/eval-runner lane.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [uncut](https://github.com/Balanov/uncut) | harness | Lossless headless coding-agent harness (MIT, Go) — one 7 MB static binary, four tools, plain stdin/stdout, no TUI/telemetry/plugin system/context cuts; if the provider truncates a response it exits with an error rather than presenting a partial answer as success | Harnesses silently summarize, prune, or cap context and output, corrupting what an agent actually saw; want a minimal auditable lossless loop for pipelines, CI, containers, and experiments | opencode, jcode, smallcode, durable-harness |
