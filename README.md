# ai-tooling

An operating manual for AI-assisted development that produces high-quality code — and keeps getting better.

Evaluates tools against six quality signals (Correctness, Speed, Maintainability, Safety, Cost Efficiency, Verifiability) across the dev loop stages where they intervene.

## Install

This repo's agent surface is written for opencode and Hermes Agent:

- **opencode** reads `AGENTS.md` and `.agents/skills/` from the checkout — nothing to wire.
  `opencode.json` carries the permission block and the `check` / `fix` / `sync` commands.
- **Hermes Agent** loads `AGENTS.md` as project context and discovers `.agents/skills/`, but
  does not auto-trust procedures from a cloned repo — run `hermes skills trust` once in the
  checkout. The project-local plugin (`.hermes/plugins/ai-tooling-harness/`) carries the
  commit gate and the `plugin/docs/` auto-sync; see
  [docs/agents/hermes-harness.md](docs/agents/hermes-harness.md).

Both harnesses drive the same gates: `make check`, `make fix`, `./sync-plugin-docs.sh`.

The same five skills are also packaged as a Claude Code marketplace:

```bash
claude plugin marketplace add mattbutlerengineering/ai-tooling
claude plugin install ai-tooling@ai-tooling
```

Or from inside a Claude Code session: `/plugin marketplace add mattbutlerengineering/ai-tooling`
then `/plugin install ai-tooling@ai-tooling`.

The five skills:

- `/setup-workflow` — bootstrap the recommended AI workflow in any repo
- `/evaluate-tool` — evaluate a new tool before adopting it (checks stage fit, quality signals, overlap)
- `/audit-workflow` — audit your current setup against the recommended workflow
- `/update-catalog` — sync the catalog with current GitHub stars and local installs
- `/sync-stars` — find starred repos not in CATALOG.md and generate ready-to-paste entries

## Contents

- [PLAYBOOK.md](PLAYBOOK.md) — **start here**: how to use AI for development in one page — what to install, how to work, what to watch
- [WORKFLOW.md](WORKFLOW.md) — the dev loop (inner + outer), tools per stage, quality signals, adoption guide
- [CATALOG.md](CATALOG.md) — flat inventory of 913 tools with definitions, problem statements, and overlap markers
- [COMPARISON.md](COMPARISON.md) — all tools at a glance with evaluation status by dev loop stage
- [STACK.md](STACK.md) — the 30 tools worth installing, distilled from 941 evaluations
- [LEARNING.md](LEARNING.md) — curated AI/AI-coding learning resources: YouTube channels, talks, and web references (passive learning, not catalogued tools)
- [evaluations/](evaluations/) — 941 evaluation files: 345 carrying a verdict (ADOPT/KEEP/CONDITIONAL/SKIP/DEFER), 282 still at `discovery-log` — leads, not verdicts — and 314 stubs and comparison documents

## Integrity

The catalog is kept honest by `audit-evals.py` (install resolver, fabrication classifier, verdict sync, COMPARISON/CATALOG consistency) and `reconcile-counts.py --check`. These run automatically in CI (`.github/workflows/integrity.yml`) on every push and pull request — a PR that introduces a verdict mismatch, count drift, or fabrication-pattern eval fails its checks. See `AGENTS.md` for the full detector list and the opt-in detectors.

## Quick Start

After installing, run `/setup-workflow` in any repo to bootstrap the recommended workflow. It creates an `AGENTS.md` with quality-producing rules, checks your global tool installation, and identifies gaps.

## The Workflow

Two loops, three layers, six signals — Plan → Implement → Verify → Review → Ship with Reflect feeding back, wrapped by an outer Discover → Architect → Decompose → Integrate → Retrospect loop.

New here? Read [PLAYBOOK.md](PLAYBOOK.md) — the one-page front door to what to install, how to work, and what to watch. For the full stage-by-stage map, see [WORKFLOW.md](WORKFLOW.md).
