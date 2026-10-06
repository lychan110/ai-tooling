# Catalog search database (`catalog-db.py`, `make index-db`)

A single SQLite file that makes the catalog **queryable**: ask it a question and get
the tools that answer it, ranked, with their verdict and evidence, in milliseconds
and offline. Built from the docs you already gate, never edited, never committed.

```bash
make index-db                                   # build .generated/catalog.db
uv run catalog-db.py --ask "agentic memory"     # ranked answer
uv run catalog-db.py --ask "code review" --recommended
uv run catalog-db.py --card claude-mem          # one tool's stored record
uv run catalog-db.py --check                    # is the built db still current?
```

## Why this exists

`CATALOG.md` answers "is X in the list?"; it does not answer "what should I use for
X?". The corpus is ~907 catalog rows plus ~934 evaluations and the root docs — about
**5.4 MiB**. Answering a recommendation question by reading it costs an agent a
context window; `catalog-db.py` turns it into one **~10 MiB** SQLite file whose
full-text index (FTS5, BM25) returns the ~8 relevant rows in **tens of
milliseconds**, with no dependency beyond the Python standard library the rest of
the repo already runs on.

The premise — that a lexical index is enough — was measured, not assumed. The three
probe queries this feature was built against all resolve to the right tool:

| Question | Top result (verdict/evidence) |
|---|---|
| recommended tools for agentic memory | claude-mem (ADOPT/MEASURED), then OMEGA and beads (KEEP) |
| code review | code-review (KEEP/MEASURED), pr-review-toolkit, security-guidance |
| browser automation testing | playwright (ADOPT/RUN) |

Retune the ranking only against a failing probe query — the queries are pinned in
`TestCatalogDbEndToEnd.test_live_tree_ranks_the_canonical_pick`, and the reason for
the current ladder is recorded at `VERDICT_LADDER` in the script.

## What it encodes

- **One parser.** Every row, verdict, and key comes from `catalog_lib.py` — the
  shared-parser seam (ADR-0002) — so the database cannot disagree with the docs about
  what a row says. There is no second catalog regex anywhere in this feature.
- **Identity is the row, not the repo.** Rows are keyed by
  `catalog_lib.name_key(name)`. Nine rows ship inside
  `anthropics/claude-plugins-official` and six inside `mattpocock/skills` (the
  `Ships inside` cell, #343); a repo-slug key collapses 907 rows to 883 and
  multiplies the shared container's hits. This is AGENTS.md's "never infer identity
  from display names or basenames", applied to the DB.
- **Verdict and Evidence come from `COMPARISON.md`**, the count-validated table
  (detector G), **not from eval prose**. A `## Verdict` paragraph can *mention*
  ADOPT while concluding `discovery-log`; scraping the prose was measured to surface
  that as a false recommendation. `discovery-log` is a lead, never a verdict
  (`catalog_lib.REAL_VERDICTS`), and `--recommended` filters it out.
- **Evidence is always shown next to a verdict**, so a recommendation never loses
  the fact that it rests on `REVIEW`/`SOURCE-ONLY` rather than a hands-on run.

## The gate posture: report-only, machine-local

The database is a **derived artifact**, like the generated counts — so it is
`gitignore`d (`.generated/`) and rebuilt, never hand-edited. It is deliberately
**not** a member of `check-data`, for the same reason `verify-installs.py --record`
is not (ADR-0006): it is machine-local, and a build must never fail because a laptop
has not rebuilt it. Instead:

- `--check` verifies the built db still agrees with the tree — row count equals
  `catalog_lib.catalog_count(CATALOG.md)`, and every ADOPT/KEEP row's `(verdict,
  evidence)` equals `COMPARISON.md`'s.
- It runs in `make check` and `make check-offline` as a **`-`-prefixed report-only
  trailer**, alongside the two staleness sweeps. A machine without the artifact
  reports `MISSING` and the gate still passes.

`--check` is deliberately **partial**: it proves the *rows and verdicts* are current,
not that every eval body was re-indexed. To catch a stale eval body, rebuild.

## Limits (stated, not hidden)

- **Lexical, not semantic.** FTS5 matches terms, stemmed by Porter. "stop my agents
  forgetting things" will not reach `claude-mem` unless those words appear. The
  catalog's own `section`/`overlaps` vocabulary is the cheap next step (map the query
  to a section) before reaching for embeddings.
- **`--check` is a freshness probe, not a content hash.** It catches the drift that
  matters (a new tool, a moved verdict) cheaply; it does not diff the full index.
