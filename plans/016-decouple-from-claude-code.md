# Plan 016: Decouple from Claude Code — make the harness layer agnostic

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected result before moving on. If anything in
> "STOP conditions" occurs, stop and report — do not improvise. When done, update
> this plan row in `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat ddd343e..HEAD -- .claude .claude-plugin CLAUDE.md plugin .opencode test_automation.py`
> Any change there means the excerpts below may be stale — re-read the live tree first.

## Status

- **Priority**: P1
- **Effort**: L
- **Risk**: MEDIUM
- **Depends on**: none
- **Category**: refactor
- **Planned at**: commit `ddd343e`, 2026-09-14

## Why this matters

The goal is to drop the Claude Code dependency and make the repo agent-harness
agnostic. Today the repo is Claude-Code-first at three layers, with opencode as a
supported second harness kept in lockstep by duplicated implementations:

1. **Instructions** — `CLAUDE.md` (176 KB) is the only instruction file. opencode
   reads it as a "rules fallback"; there is intentionally no `AGENTS.md` fork
   (documented in `CLAUDE.md`, section "Supported harnesses").
2. **Runtime** — `.claude/` is a first-class harness dir: `settings.json` wiring two
   bash hooks, three repo-maintenance skills, and a symlinked agent file.
3. **Distribution** — `plugin/` *is* a Claude Code marketplace package
   (`.claude-plugin/plugin.json`, `${CLAUDE_PLUGIN_ROOT}` paths).

The maintainability cost of the current shape is the **lockstep invariant**:
`.claude/hooks/{audit-gate,auto-sync}.sh` and `.opencode/plugins/{commit-gate,auto-sync}.ts`
are two implementations of one gate, coupled by two tests and a prose invariant.
`TestHookTriggerSeam` and `TestWatchListSeam` exist only to hold the two halves
together. Deleting the Claude Code half removes the duplication, both tests, and the
invariant — a net simplification, not a loss.

## Current state (verified at `ddd343e`)

`.claude/`:
- `settings.json` — PreToolUse Bash -> `$CLAUDE_PROJECT_DIR/.claude/hooks/audit-gate.sh`;
  PostToolUse Edit|Write -> `.../auto-sync.sh`
- `hooks/audit-gate.sh`, `hooks/auto-sync.sh`, `hooks/hook-field.py` (the one JSON
  helper both bash hooks share)
- `agents/eval-runner.md` — symlink -> `.opencode/agents/eval-runner.md`
- `skills/add-catalog-entry/SKILL.md`, `skills/find-catalog-gaps/{SKILL.md,find-gaps.py}`,
  `skills/triage-lead/SKILL.md`
- `skills/find-skills` — symlink -> `.agents/skills/find-skills`

Claude-named / Claude-coupled elsewhere:
- `.claude-plugin/marketplace.json`; `plugin/.claude-plugin/plugin.json`
- `plugin/hooks/hooks.json` (uses `${CLAUDE_PLUGIN_ROOT}`);
  `plugin/hooks/{validate-counts.sh,check-freshness.sh}`
- `plugin/README.md`, `plugin/skills/*/SKILL.md` — `${CLAUDE_PLUGIN_ROOT}/docs/` paths
- `docs/agents/routines.md` — Claude Code cloud routines
- `check-plugin.py`, `sync-plugin-docs.sh`, `rewrite-doc-links.py`

`CLAUDE.md` is read by **8 scripts/tests**, not just the harnesses:
`test_automation.py`, `audit-evals.py`, `check-plugin.py`, `reconcile-counts.py`,
`freshness.py`, `check-links.py`, `check-stars.py`, `rewrite-doc-links.py`.
Any rename is a coordinated edit across all eight.

## The deletion hazard: test seams pin `.claude/`

All in `test_automation.py`; all run by `make check` (CI job `audit`):

- L2000 `HOMES = (".agents/skills", ".claude/skills")` — `TestRepoInstallRecord`
- L2693-2699 `_run_claude_hook` copies `.claude/hooks/{auto-sync.sh,hook-field.py}` and
  sets `CLAUDE_PROJECT_DIR` — `TestWatchListSeam`
- L2740 `adapters = (".claude/hooks/auto-sync.sh", ".opencode/plugins/auto-sync.ts")`
- L2793-2869 `TestHookTriggerSeam`: `GATE`/`HELPER` constants plus
  `test_bash_hooks_share_the_json_helper`
- L4605 `COMMIT_HOOKS = (".claude/hooks/audit-gate.sh", ".opencode/plugins/commit-gate.ts")`
  — `TestIntegrityMakefile`

Deleting `.claude/` without editing these reddens `make check` and CI.

## Steps (each stage must end with `make check` green)

**S1 — Repo skills to `.agents/` (independent, safe first step).** Move
`add-catalog-entry`, `find-catalog-gaps`, `triage-lead` from `.claude/skills/` to
`.agents/skills/`; leave `.claude/skills/<name>` as symlinks if Claude Code support
is retained during the transition. Update `TestRepoInstallRecord` `HOMES` only if the
`.claude/skills` entry goes away. Update the "Repo skills" line in `CLAUDE.md`.
Verify: the `test_automation` unit suite, `-k RepoInstallRecord` only.

**S2 — Instructions to `AGENTS.md`.** Rename `CLAUDE.md` -> `AGENTS.md`; if Claude
Code is still supported during the transition, add a thin `CLAUDE.md` containing
`@AGENTS.md` (Claude Code import syntax) so both harnesses read one source. Update
the 8 readers listed above. Verify: `make check` — this is the stage most likely to
surface a `reconcile-counts.py` pattern.

**S3 — Delete the bash hook half.** Remove `.claude/hooks/*` and `.claude/settings.json`;
delete `TestHookTriggerSeam` and `TestWatchListSeam`; drop the `.claude` entry from
`TestIntegrityMakefile.COMMIT_HOOKS`; rewrite the "Lockstep invariant" prose.
Verify: `make check` green with 2 fewer tests.

**S4 — Delete the Claude-shaped agent symlink.** Remove `.claude/agents/eval-runner.md`;
keep `.opencode/agents/eval-runner.md` canonical. Verify: `make check`.

**S5 — Decide the `plugin/` question (STOP: needs a human).** `plugin/` is a
*published Claude Code marketplace artifact*, not a dependency. Removing the
dependency does not require removing distribution. Decide: keep shipping a Claude
Code plugin, add a package for another harness, or drop `plugin/` entirely. Do not
guess — see STOP conditions.

## Verification

- `make check` is the canonical gate (CI job `audit` calls it). Run it after every stage.
- The `test_automation` unit suite covers the seam edits in S1 and S3.
- `./sync-plugin-docs.sh --check` if anything under `plugin/` changes.

## STOP conditions

- A stage turns on whether `plugin/` keeps shipping a Claude Code package — ask; this
  is a product decision, not a refactor.
- `make check` reddens in a file this plan does not list — the seam list here is
  incomplete; stop and report it rather than widening the diff.
- `CLAUDE.md` -> `AGENTS.md` breaks a `reconcile-counts.py` pattern (`EVAL_PATTERNS` /
  `TOTAL_PATTERNS`) — report the pattern; never hand-edit counts.
- The intent is to drop Claude Code support *entirely* (no shim at all) — confirm before S2.

## Findings considered and rejected

- Deleting `.github/workflows/integrity.yml` — already harness-agnostic (`make check`),
  no Claude coupling.
- `plugin/hooks/{validate-counts.sh,check-freshness.sh}` — already portable
  (`git rev-parse --show-toplevel`); only `hooks.json` wrapper is Claude-specific.
- `.opencode/` — a second harness, not a Claude dependency; out of scope.
