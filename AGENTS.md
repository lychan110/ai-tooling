# AI Tooling

Documentation-only repository; no default build, test, or deploy command.

## Purpose

Maintain a high-signal inventory and evaluation of AI tools, skills, agents, harnesses, workflows, and MCP servers. Evaluate tools for Correctness, Speed, Maintainability, Safety, Cost Efficiency, and Verifiability.

## Start here

- `PLAYBOOK.md` — one-page install/work/watch router.
- `CATALOG.md` — authoritative tool inventory.
- `WORKFLOW.md` — inner/outer dev loop and adoption guide.
- `STACK.md` — recommended installable stack.
- `STACK-LEDGER.md` — machine-readable ADOPT/KEEP exclusions.
- `evaluations/` — hands-on evaluations and discovery logs.
- `docs/agents/` — detailed agent procedures and rationale.
- `plugin/` — the distributable: the five installable skills plus the rendered docs; generated docs must not be edited directly.

## Source of truth

- Root `CATALOG.md`, `WORKFLOW.md`, and `evaluations/` are authoritative.
- `.agents/skills/` is canonical for repo skills; `skills/` is derived.
- `.opencode/agents/` is canonical for specialized agents.
- `plugin/docs/` is generated; `plugin/README.md` is hand-authored.
- Run `./sync-plugin-docs.sh` after changing root docs or plugin skills.

## Supported harness

opencode and Hermes both read this file as project context; neither needs wiring here. Keep instructions here current, concise, and executable. Enabling the Hermes harness is documented in `docs/agents/hermes-harness.md`. Put long explanations, postmortems, detector history, and issue-specific rationale in `docs/agents/` or ADRs.

## Catalog format

Catalog rows have six cells: Name, Type, One-liner, Problem it solves, Overlaps with, and Ships inside. `Ships inside` is empty unless the artifact is a component of an `owner/repo` package. Use stable slugs for identity; never infer identity from display names or basenames.

## Required invariants

- Do not hand-edit generated counts or summaries.
- Every new catalog row fills `Overlaps with` and all six cells.
- An evaluation must say how it was tested; a discovery log is not a hands-on evaluation.
- New evaluations use Verifiability; older evaluations are not retrofitted.
- Derived facts have one parser and one source of truth; do not duplicate extraction logic.
- Unknown/unreachable is not the same as absent/broken. Never fail a gate for external uncertainty.
- Every detector reports the population it examined; `0 findings` is not `0 examined`.
- Tests are end-to-end and deliberately few: exercise the real artifact against a
  throwaway target, then assert the result a user would see. No unit tests for internal
  helpers, no smoke tests, and no assertions of the obvious (a file exists because the
  previous line created it; a bad argument exits non-zero). The only test worth adding is
  one that would fail if the behaviour regressed.

## Canonical commands

- `make check` — full local/CI integrity gate.
- `make fix` — apply canonical repairs, then run `make check`.
- `uv run reconcile-counts.py --check` — validate generated counts and summaries.
- `uv run audit-evals.py --offline` — run offline evaluation detectors.
- `uv run triage.py` — regenerate `NEXT-EVALS.md`.
- `uv run refresh-metadata.py` — refresh GitHub metadata when needed.
- `bash install-harness.sh --check` — verify the opencode/Hermes skill install.

## Agent workflow

Use inner/outer loop vocabulary: Plan, Implement, Verify, Review, Ship, Reflect. Triage is eliminate-only outside the P0 measure band: unattended passes may write SKIP or leave `discovery-log`, never ADOPT/KEEP/CONDITIONAL. P2 names every resolved incumbent; P5 names its container. See `docs/agents/triage-labels.md` and `docs/agents/routines.md`.

## Skills and routines

- `/add-catalog-entry` runs the catalog, comparison, count, sync, and audit workflow.
- Issue tracker: GitHub Issues on `lychan110/ai-tooling`; see `docs/agents/issue-tracker.md`.
- Labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`.
- Scheduled routines land their own PR only after CI is green; eliminate-only still applies.

## Adding entries

Use `/add-catalog-entry`, resolve the canonical repository slug, place the row in the correct category, fill all six cells, and run `uv run reconcile-counts.py --check`. Never hand-edit mirrored counts or generated plugin docs.

## Evaluations

Copy `evaluations/TEMPLATE.md` for hands-on work. Discovery logs are historical bulk-triage records; new scans use GitHub Issues labeled `scan`. Include evidence from actual usage and keep verdicts honest.
