# Evaluation: goose

**Repo:** [aaif-goose/goose](https://github.com/aaif-goose/goose) (moved from block/goose to Linux Foundation AAIF)
**Stars:** 56,063 | **Last updated:** 2026-11-01 | **License:** Apache-2.0
**Last verified:** 2026-11-01
**Dev loop stage:** Implement
**Layer:** Tooling

---

## What it does

A general-purpose open-source AI agent — desktop app (macOS/Linux/Windows), full CLI, and embeddable REST API — built in Rust for performance and portability. Works with 15+ providers (Anthropic, OpenAI, Google, Ollama, OpenRouter, Azure, Bedrock, and more) via API keys or existing subscriptions through ACP (Agentic Context Protocol). Connects to 70+ extensions via MCP. Designed as a standalone agent runtime, not an enhancement to another harness — you use goose *instead of* your current harness, not alongside it.

The architecture is clean: a `goosed` server process exposes a REST API that any frontend (CLI, Electron desktop, custom web/mobile) can consume. Extensions are MCP servers. Providers are pluggable via a trait system. "Recipes" (YAML-based task definitions) enable guided workflows and multi-step automation. Custom distributions ("white labelling") let organizations ship preconfigured goose variants with their own providers, extensions, and branding.

## How we tested it

**Evidence:** MEASURED

> Scope: one measured task set (below), run 2026-11-01 against the v1.57.0 release binary. The
> provider-matrix, custom-distro and governance points carried over from the June 2026 review are
> review-grade notes, not measurements, and are labelled as such.

Downloaded the release binary (no build step), pointed it at an OpenAI-compatible gateway, and ran
it headless on three defect-repair tasks. Each task has its own `node test.js` oracle that prints
`RESULT k/N` and exits non-zero on failure, and I re-ran that oracle myself after every goose run
instead of trusting the agent's own summary.

```bash
curl -sLf -o goose.tar.bz2 \
  https://github.com/aaif-goose/goose/releases/download/v1.57.0/goose-x86_64-unknown-linux-gnu.tar.bz2
tar -xjf goose.tar.bz2 && ./goose --version     # 1.57.0 — 199 MB static binary, 54 MB download

# headless run: no `goose configure`, no keyring, config comes from the environment
GOOSE_PROVIDER=openai OPENAI_HOST=https://api.kilo.ai/api/gateway \
GOOSE_MODEL=deepseek/deepseek-v4.1-flash-1017 GOOSE_MODE=auto \
OPENAI_API_KEY=<gateway key> GOOSE_DISABLE_KEYRING=1 \
./goose run --no-session -q --max-turns 15 \
  -t "You are in a Node project directory whose test suite currently fails. Make 'node test.js'
      pass by fixing the source files. Do not modify test.js or SPEC.md. Verify by running the
      suite yourself and report the final RESULT line."

node test.js                                     # the oracle, run independently of goose's claim
```

## Test design

- **Task/corpus:** three throwaway Node fixtures, each a buggy module set plus a `SPEC.md` and a
  plain-`node` test script (`RESULT k/N` + exit code). **A** — 3 modules, 3 planted defects,
  8 assertions. **B** — the same repo, prompt only (no file contents in the prompt). **C** — 2
  modules, 2 planted defects, 5 assertions, prompt only.
- **Baseline (without the tool):** the *same* model (`deepseek/deepseek-v4.1-flash-1017`, pinned,
  same gateway, `temperature: 0`) given one turn and no tools. For task A the baseline gets the
  fixture files inlined — its best case. For B and C it gets the identical prompt goose got, so its
  only disadvantage is the one being measured: no file access.
- **Metric:** assertions passed `k/N` and the process exit code — a mechanical oracle — plus
  wall-clock per task. **Reproduce:** the commands above; fixtures are ~40 lines each.
- **Correctness:** `with 3/3 tasks` vs `without 1/3 tasks`.

| Task | Oracle | Without (one turn, no tools) | With goose |
|------|--------|------------------------------|------------|
| A — 3 defects, files inlined | `node test.js` | 8/8, exit 0 | 8/8, exit 0 (16.1 s) |
| B — same repo, prompt only | `node test.js` | 2/8, exit 1 — empty reply, it cannot see files | 8/8, exit 0 (17.1 s) |
| C — 2 defects, prompt only | `node test.js` | 3/5, exit 1 | 5/5, exit 0 (14.5 s) |

In both goose runs the test file stayed byte-identical to the original (`md5sum` unchanged), so it
fixed the code rather than the oracle.

## What worked

- **It actually runs headless.** One 54 MB download, no toolchain, no `goose configure` — provider,
  base URL and model come from four environment variables, and `goose run --no-session -q` returned
  a task result in a shell.
- **The harness delta is real and measured.** Where the model alone had no file access it produced
  nothing (2/8 and 3/5, exit 1); the same model through goose read the repo, edited the right
  modules, ran the suite itself and reached 8/8 and 5/5. That is 3/3 tasks solved with it, 1/3
  without.
- **It stayed inside the instruction.** Across all three runs it never touched `test.js` despite
  that being the shortest path to green, and it re-ran the suite and quoted the `RESULT` line.
- **Fixes were minimal.** Three files changed on task A, each a one-line-to-five-line edit at the
  offending expression; no scaffolding, no test rewrites.
- **Sane self-reporting.** On task A it flagged that the spec is silent on non-integer durations and
  `page = 0`, and declined to invent error semantics rather than adding defensive code.

## What didn't work or surprised us

- **`GOOSE_MODE=auto` is an unattended shell.** It executed shell commands and wrote files with no
  approval step, which is what makes headless runs useful and also what makes a live checkout a bad
  place to run it. Sandbox it; the curated alternative costs a permission prompt per call.
- **A provider account is the real prerequisite, not the binary.** The first attempt against a
  different OpenAI-compatible endpoint returned `402` — the install is trivial, the credits are not.
  Provider parity with Anthropic/Google/Bedrock is **untested here** (no keys available); only the
  OpenAI-compatible path was exercised.
- **Exit 0 is not success.** `goose run` returns 0 when the run completed, not when the work is
  right. The oracle has to be yours — the same trap as any agent harness.
- **Model routing is the gateway's.** With an alias model the upstream model varies per request; the
  measurement above pins a concrete model name precisely because of that.
- **It replaces the harness, it does not plug into one.** goose cannot be dropped into the
  opencode/Hermes install lists — using it means putting the current harness aside for that work.
- **Refreshed facts.** 56,063 stars (was 49,786), v1.57.0 published 2026-10-28 (was v1.38.0 in June),
  536 open issues (was 214), 6,530 forks.

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | + | 3/3 repair tasks solved vs 1/3 for the same model with no tools; the delta is file access plus self-verification |
| Speed | neutral | 14.5–17.1 s per task (median 16.1 s) for the agent loop; a no-tools turn is one request when it can answer at all, so the loop buys capability, not speed |
| Maintainability | neutral | Edits stayed at 3 files and a few lines each at the offending expression; no scaffolding or test rewrites |
| Safety | - | `GOOSE_MODE=auto` runs shell and edits files with no approval gate; the sandbox, not goose, has to contain it |
| Cost Efficiency | neutral | 212–479 output tokens per task on a cheap pinned model; the saving available is provider choice, not anything goose adds |
| Verifiability | + | It re-ran the oracle itself and its report matched an independent run; the `RESULT` line and exit code leave no room for a rosy summary |

## Verdict

**CONDITIONAL**

Adopt if you want an agent runtime you can point at any OpenAI-compatible endpoint and run headless
against a checkout — a one-shot repair loop in CI, or a provider-neutral runtime where the harness
must not be Hermes/opencode. It measured strictly better than the same model without tools (3/3
tasks vs 1/3) and never worse where one turn already sufficed. It is not a STACK install: it
replaces the harness rather than plugging into one, and `GOOSE_MODE=auto` hands it an unattended
shell — run it in a disposable checkout, never a live one.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [goose](https://github.com/aaif-goose/goose) | platform | Model-agnostic AI agent with desktop, CLI, API — Rust, 15+ providers, custom distros (56.1K stars) | Want a provider-neutral, extensible agent platform with enterprise governance | OpenHands, opencode, claude-squad |
