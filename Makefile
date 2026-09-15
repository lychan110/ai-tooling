# Single entrypoint for the catalog integrity gates (#114).
#
#   make check   verify mode — runs exactly what .github/workflows/integrity.yml
#                enforces, in --check order, exiting non-zero on the first failure.
#   make fix     apply mode — runs the apply-mode fixers in dependency order, then
#                re-runs `check` so a clean exit means the tree is actually green.
#   make check-offline
#                `check` minus the network install resolver — the fast local loop.
#                NOT the canonical gate: it cannot catch a broken install command,
#                so CI runs the full `check` and so should you before pushing.
#
# CI's `audit` job calls `make check`, so the two cannot drift. Keep this target in
# lockstep with the gate set: a gate added to integrity.yml must be added here (and
# test_automation.py's TestIntegrityMakefile pins that they stay in sync).
#
# `check`'s install resolver (audit-evals.py --installs) hits the network and uses
# `gh`, so it needs gh auth / GH_TOKEN. `fix`'s fixers are offline, but its trailing
# `check` re-run inherits that same network/gh requirement. The final `-`-prefixed
# staleness lines are report-only trailers (both offline) — the `-` prefix keeps a
# stale eval or a stale metadata cache from failing the gate. Only **Last verified:**
# field presence is gated; L (evals) and R (repo-metadata.json) age on the calendar,
# and their only fix needs the network CI must not depend on.
#
# `check-stars.py --check` has no counterpart in `fix`, and that is deliberate (#377): a missing **Stars:** value cannot be generated, only declared — the
# author knows whether the file has one subject, several contenders, or none. Dropping
# `--check` there turns it report-only in one word, which is how the gate-vs-report call
# stays reversible; TestStarConvention pins both modes regardless of which is wired.
#
# `verify-installs.py --check` likewise has none, for a different shape of reason
# (#382/ADR-0006): it validates that every ADOPT/KEEP ledger row DECLARES a well-formed
# `Install evidence` value, never that the value is still true. The apply side
# (`--record`) reads one laptop's install records, so it is deliberately absent from
# `fix` — CI has no lockfile, and a build that failed because a machine changed would be
# worse than the drift it caught.
#
# Which gates have no fixer is DECLARED, not counted in prose: TestIntegrityMakefile's
# NO_APPLY_MODE holds the set with a reason each, and derives from this file which gates
# must have one (#461). The three ordinals that used to live here and in AGENTS.md gave
# three different answers for a set of four.
#
# `uv` owns the interpreter and the environment. `python3` is not on every machine's
# shell allowlist, so every recipe below reaches the scripts through `$(UV) run`. The
# two non-stdlib gates — ruff and mypy (#388) — are the only ones that need packages,
# and they are pinned EXACTLY in pyproject.toml's `dev` dependency group: an unpinned
# linter turns an upstream rule addition into a red build on an unrelated PR. uv.lock is
# committed, so there is nothing to install by hand:
#
#   uv run ruff check
#
# and the tool itself stays overridable: `make check UV=/path/to/uv`.
#
# They run FIRST in both check targets: a syntax error should surface before twelve
# data gates parse the tree with it.
UV ?= uv
RUFF ?= ruff
MYPY ?= mypy

.PHONY: check check-data check-offline fix lint lint-preflight

# A missing `uv` must say what to install, not "command not found: uv". Nothing else is
# probed: ruff and mypy come from the locked `dev` group, so they cannot be absent on
# their own — there is no venv to build and no requirements file to keep in sync.
lint-preflight:
	@command -v $(UV) >/dev/null 2>&1 || { \
	  echo "uv not found — install it (https://docs.astral.sh/uv/). It provides the"; \
	  echo "pinned ruff/mypy from pyproject.toml's dev group."; exit 1; }

# Runnable alone while iterating on a script.
lint: lint-preflight
	$(UV) run $(RUFF) check
	$(UV) run $(MYPY)

# The data gates alone — every offline `--check`, minus the two linters (they need the
# pinned dev packages, and a contributor must be able to commit without syncing them) and
# minus the unit suite (15.9s of regression net for the *scripts*, not a check on the
# *tree*). Median 4.0s over 5 runs against 0.55s for the one gate the hooks used to run,
# so full coverage costs ~3.5s per commit — the reason the two heavy exclusions above are
# exclusions rather than an oversight.
#
# This is the ONE definition of that set, and the commit hook calls it
# (`.opencode/plugins/commit-gate.ts`). Before #459 it ran
# `audit-evals.py --offline` alone — 1 of these 13 — while it described itself
# as running "the offline subset of make check", so every gate added since #153 silently
# widened the hole: a stale NEXT-EVALS.md, a desynced plugin/docs/, a missing **Stars:**
# line, a dead relative link and a stale WATCHLIST.md all passed the commit gate and
# failed CI. A gate added here now reaches the Makefile, CI and the hook at once, which
# is what the single-implementation rule asks for and what nothing enforced.
check-data:
	$(UV) run audit-evals.py --offline
	$(UV) run audit-evals.py --selftest
	$(UV) run reconcile-counts.py --check
	$(UV) run backfill-evidence.py --check
	$(UV) run backfill-lastverified.py --check
	$(UV) run check-stars.py --check
	$(UV) run check-links.py --check
	$(UV) run check-plugin.py --check
	$(UV) run verify-installs.py --check
	$(UV) run tier-stack.py --check
	$(UV) run triage.py --check
	$(UV) run watchlist.py --check
	./sync-plugin-docs.sh --check

check: lint-preflight
	$(UV) run $(RUFF) check
	$(UV) run $(MYPY)
	@$(MAKE) check-data
	$(UV) run -m unittest -q test_automation
	$(UV) run audit-evals.py --installs
	-$(UV) run audit-evals.py --staleness
	-$(UV) run audit-evals.py --metadata-staleness

# Everything in `check` except the network install resolver (A) — the fast local loop.
# `check` remains the canonical gate; this is for iterating without paying ~22s of
# network round trips per run. CI always runs the full `check`.
# TestIntegrityMakefile pins that this stays `check` minus exactly that one line.
check-offline: lint-preflight
	$(UV) run $(RUFF) check
	$(UV) run $(MYPY)
	@$(MAKE) check-data
	$(UV) run -m unittest -q test_automation
	-$(UV) run audit-evals.py --staleness
	-$(UV) run audit-evals.py --metadata-staleness

fix: lint-preflight
	$(UV) run $(RUFF) check --fix
	$(UV) run reconcile-counts.py
	$(UV) run backfill-evidence.py
	$(UV) run backfill-lastverified.py
	$(UV) run tier-stack.py
	$(UV) run triage.py
	$(UV) run watchlist.py
	./sync-plugin-docs.sh
	@$(MAKE) check
