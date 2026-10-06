# ADR-0007: a derived, machine-local catalog search database

- **Status:** Accepted
- **Date:** 2026-10-05
- **Context:** issues and docs assume an agent answers "what should I use for X?"
  by reading `CATALOG.md`/`COMPARISON.md`/`evaluations/` — a ~5.4 MiB corpus.

## Decision

Add `catalog-db.py` (built by `make index-db`) which derives a single SQLite file,
`.generated/catalog.db`, with one row per catalog row and an FTS5 index over its
listing fields, verdict, evidence, and evaluation text. The database is:

1. **Derived** — rebuilt from the tracked docs on demand, never hand-edited.
2. **Uncommitted** — `gitignore`d under `.generated/`, like the other derived
   artifacts the repo generates and does not store.
3. **Never a gate** — not in `check-data`; its `--check` runs report-only
   (`-`-prefixed) in `check` and `check-offline`.

## Why derived-and-uncommitted, not a committed artifact

The counts in `README.md`/`COMPARISON.md` are committed because a human reads them in
a diff. A binary SQLite file is read in a diff by no one; committing it would add
~10 MiB of churn to every catalog PR and to `sync-plugin-docs.sh`'s surface. The
repo's rule is one parser and one source of truth — the markdown is the truth, and
this is a projection of it, so it is rebuilt, not stored.

## Why it is not a gate

Membership in `check-data` would fail CI (`make check`) on a machine that has not
built the artifact, since the artifact is machine-local. That is exactly the shape
`verify-installs.py --record` was excluded for (ADR-0006): the *fact* that a
derived, machine-local artifact is fresh cannot be required of every checkout. CI
therefore never depends on it; the developer builds it locally with `make index-db`
and `--check` runs as a report-only trailer so a machine without it is unaffected.
We extended the trailer set, not the gate set — see `docs/agents/catalog-db.md`.

## Consequences

- A laptop that never builds it is unaffected: `--ask`/`--card`/`--check` report a
  one-line `MISSING` message, not a traceback.
- Recommendation answers must carry `verdict` **and** `evidence`, so a review-based
  or source-only row is never presented with the authority of a measured one.
- The ranking lives in the script and is pinned by an e2e test on the three probe
  queries; it is retuned only against a failing query, never by taste.
