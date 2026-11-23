# Plan: ai-tooling Windows migration

**Goal:** Make the ai-tooling repo's scripts, gates, and cronjobs runnable on this Windows host, and resolve the MOVED-repo drift without repointing to the repurposed curriculum.

**Workstreams (independent, parallel):**

A. `audit-evals.py` MOVED tombstoned suppression
- Extend the `tombstoned()` suppression to cover `moved:` results so an already-tombstoned row (awesome-hermes-agent → SKIP) prints `tombstoned <slug> — already recorded in the entry` instead of actionable `MOVED <slug> -> <resolved_name>`.
- Add a test pinning that a tombstoned+moved row is not actionable.
- Do NOT repoint awesome-hermes-agent to `Anil-matcha/open-agent-email` (content-monetization curriculum — the #437 defect). Repointing is a whole-class decision, never unilateral.

B. Windows line-ending normalization
- Normalize the 12 dirty `plugin/docs/` files (and `repo-metadata.json` if refreshed by maintenance) from CRLF to LF so `but status` is clean.
- Content is byte-identical except line endings; `git diff` shows only CRLF warnings.

C. `sync-plugin-docs.sh` Windows compatibility
- `rsync` breaks on Windows paths (`ssh: Could not resolve hostname c:`). Add a `--check` mode that works without rsync: copy watched files/dirs to a scratch dir, run `rewrite-doc-links.py`, strip `${AI_TOOLING_DOCS}/` from skills, byte-compare against `plugin/docs/` and `skills/`.

D. Cron gate alternatives (`uv run` equivalents)
- `make` is missing on this host. Document/provide the `uv run` equivalents of `make check`/`make fix`: ruff, mypy, the 13 offline `--check` gates, `python -m unittest -q test_automation`, staleness trailers.
- Point the 5 ai-tooling cronjobs at these instead of `make check`/`make fix`.

**Constraints:**
- No `git` or `gh`; use `but` for branch/commit.
- Commit work in hunks (atomic, per workstream).
- Do not touch parallel workstreams' files.
- No MOVED repoint without explicit, whole-class approval.
