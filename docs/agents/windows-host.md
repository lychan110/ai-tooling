# ai-tooling on Windows: running the gates

`make` is installed on this Windows host (GNU Make 4.4.1 via scoop), so `make check`,
`make fix` and `make check-offline` run directly. The `uv run` equivalents below are kept as
a reference for a host without make, or for running one gate in isolation. The Makefile is
the source of truth for the exact command list.

## `make check` (full CI gate, in order)

```
uv run ruff check
uv run mypy
uv run audit-evals.py --offline
uv run audit-evals.py --selftest
uv run reconcile-counts.py --check
uv run backfill-evidence.py --check
uv run backfill-lastverified.py --check
uv run check-stars.py --check
uv run check-links.py --check
uv run check-plugin.py --check
uv run verify-installs.py --check
uv run tier-stack.py --check
uv run triage.py --check
uv run watchlist.py --check
./sync-plugin-docs.sh --check        # now rsync-free on Windows (see sync-plugin-docs.sh)
uv run -m unittest -q test_automation
uv run audit-evals.py --installs      # network + gh auth; UNCHECKED/INCONCLUSIVE without network
-uv run audit-evals.py --staleness    # report-only trailer
-uv run audit-evals.py --metadata-staleness  # report-only trailer
-uv run catalog-db.py --check         # report-only trailer (.generated/catalog.db)
```

## `make check-offline` (local loop, no network resolver)

```
uv run ruff check
uv run mypy
<all 13 offline --check gates above, same as check-data>
uv run -m unittest -q test_automation
-uv run audit-evals.py --staleness
-uv run audit-evals.py --metadata-staleness
-uv run catalog-db.py --check
```

## `make fix` (apply-mode fixers, then re-run `make check`)

```
uv run ruff check --fix
uv run reconcile-counts.py
uv run backfill-evidence.py
uv run backfill-lastverified.py
uv run tier-stack.py
uv run triage.py
uv run watchlist.py
./sync-plugin-docs.sh
<then re-run the full `make check` list above>
```

## `sync-plugin-docs.sh --check` on Windows

The `--check` branch no longer uses `rsync` (scoop rsync parses `C:/` paths as ssh hosts).
It builds the would-be-synced tree in a scratch dir via a Python inline script, runs
`rewrite-doc-links.py` on it, strips `${AI_TOOLING_DOCS}/` from skills, then `diff -rq`
against `plugin/docs/` and `skills/`. Apply mode is unchanged.

## cronjobs

The 5 ai-tooling cronjobs already carry Windows `workdir` paths
(`C:\Users\lycha\cheshire\projects\ai-tooling`). Agent-based lanes (discovery, triage,
P0 eval, maintenance PR) run `make fix && make check` per `docs/agents/routines.md` — on
this host they should use the `uv run` equivalents above instead of `make`.

## Line endings

`refresh-metadata.py` writes `repo-metadata.json` with CRLF on this host; `but status` then
shows it modified even when `git diff` is empty. After a maintenance refresh, rewrite the file
back to LF so the tree stays clean.

## Windows quirks, resolved

- `uv run mypy` used to fail with `error: uv trampoline failed to canonicalize script path`
  (a stale venv shim, not a type error). Fix: `uv sync --dev --reinstall-package mypy`.
  `uv run python -m mypy` also works around it. Both `ruff` and `mypy` now pass.
- `sync-plugin-docs.sh` apply mode is now rsync-free, using the same Python build as
  `--check`; both modes run on this host (the scoop `rsync` parsed a `C:/` path as an ssh
  host).
- `install-harness.sh` is rsync-free (`rm -rf` + `cp -R`) and forward-slashes `DOCS_DEST`
  so the `sed` render cannot eat a Windows path's backslashes.
- The detectors resolve `gh` via `shutil.which`, so a PATHEXT shim (`gh.cmd`) is found; a
  bare `gh` goes through CreateProcess, which only ever appends `.exe`.
- The markdown-walking detectors report `rel` with `/` (a shared `_md_files` helper), so
  Windows separators cannot leak into findings.

## Known `but` limitation

- Some generated docs (`STACK.md`, `NEXT-EVALS.md`, `COMPARISON.md`, `README.md`, and the
  `plugin/docs` copies of `STACK.md`/`NEXT-EVALS.md`) are committed with CRLF blobs that
  `but` normalises against, so a pure CRLF→LF rewrite is not committable through `but`
  ("no effective change"); the file only picks up LF when a real content change is committed.


