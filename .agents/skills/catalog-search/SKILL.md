---
name: catalog-search
description: Answer "what should I use for <X>?" from the catalog search database (catalog-db.py) instead of reading the 5.4 MiB corpus. Use for recommendation questions and single-tool lookups. Triggers - "/catalog-search", "what tools for X", "recommended tools for X".
---

# Catalog Search

Answer a recommendation question from the built catalog database, not from reading
`CATALOG.md` / `COMPARISON.md` / `evaluations/` (a ~5.4 MiB corpus).

```bash
make index-db                                # once per machine / after a large doc change
uv run catalog-db.py --ask "<question>"       # ranked answer
uv run catalog-db.py --ask "<question>" --recommended
uv run catalog-db.py --card <name>            # one tool's stored record
uv run catalog-db.py --check                  # is the built db still current?
```

## Rules

- **Quote the verdict AND the evidence** from every result. `ADOPT/MEASURED` is a
  recommendation; `ADOPT/SOURCE-ONLY` is "catalogued but never exercised". Never
  present a `discovery-log` row as a recommendation — `--recommended` filters those
  out, and `discovery-log` is a lead, not a verdict (ADR-0005).
- **Rebuild before trusting a recommendation.** If `--check` prints `STALE`, or no
  db exists (`MISSING`), run `make index-db` first — a stale snapshot can name a tool
  the catalog has since dropped, or quote a verdict that has since moved.
- **The database is derived.** `.generated/catalog.db` is machine-local and
  gitignored; never commit it, never hand-edit it. The markdown is the source of
  truth, and `catalog_lib.py` is the one parser that reads it.
- **Lexical, not semantic.** FTS5 matches terms (Porter-stemmed), so a question whose
  words appear in no row returns nothing — fall back to reading `COMPARISON.md` by
  `## section`. Do not claim a semantic match the index cannot make.

Design and gate posture: `docs/agents/catalog-db.md`; decision record: `docs/adr/0007-catalog-search-db.md`.
