# ai-tooling skills

Five skills for bootstrapping and maintaining an AI-assisted workflow, installable on
opencode or Hermes Agent. No marketplace, no account, no plugin registry.

    git clone https://github.com/lychan110/ai-tooling && cd ai-tooling
    bash install-harness.sh opencode     # or: bash install-harness.sh hermes

Each skill reads the reference documents in `docs/`; the installer renders them once to
`~/.local/share/ai-tooling/docs/` and points every installed skill at that directory, so the
skills work from any project without the checkout being your working directory.

AI workflow toolkit organized around inner/outer dev loop stages and six quality signals (Correctness, Speed, Maintainability, Safety, Cost Efficiency, Verifiability).

Under opencode or Hermes Agent the marketplace is not needed: clone the repo and the skills
load from `.agents/skills/` (run `hermes skills trust` once, for Hermes).

## Skills

- `/setup-workflow` — bootstrap the recommended AI workflow in any repo (creates AGENTS.md, checks global tools, identifies gaps)
- `/evaluate-tool` — evaluate a new AI tool before adopting it (checks catalog overlap, quality signal fit, dev loop stage)
- `/audit-workflow` — audit current setup against the recommended dev loop tool stack
- `/update-catalog` — sync the AI tooling catalog with current GitHub stars and local installs
- `/sync-stars` — find starred repos not in CATALOG.md and generate ready-to-paste entries

## Reference Documents

The plugin includes reference documents under `docs/`:
- `CATALOG.md` — flat inventory of 914 tools across 13 categories with overlap markers
- `WORKFLOW.md` — inner/outer dev loop stages, tools per stage, quality signals, adoption guide
- `evaluations/` — 941 evaluation and comparison files

Skills reference these docs through the installer-resolved `~/.local/share/ai-tooling/docs/` path.

## Hooks

Two portable scripts in `hooks/` remain for harnesses that wire hooks up:

- `check-freshness.sh` — surfaces catalog maintenance: evaluations past their threshold,
  and starred repos missing from the catalog, using the repo's own `freshness.py`.
- `validate-counts.sh` — runs the repo's own count and sync gates after an edit, and
  surfaces whatever they report.

Both resolve the repo root with `git rev-parse --show-toplevel` and stay a silent no-op in a
repo that carries neither script. Nothing here runs them automatically: the SessionStart and
PostToolUse wiring was deleted with the Claude Code package.
