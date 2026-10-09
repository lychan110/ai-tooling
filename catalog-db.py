"""
catalog-db.py — build the laptop-local search database the repo's docs never were:
a single SQLite file (`.generated/catalog.db`) with one row per catalog row and a
full-text index over its list, problem, overlaps, verdict, evidence, and
evaluation text.

Why: CATALOG.md is an inventory, not a query engine. This script turns the exact
markdown you already gate — CATALOG.md, COMPARISON.md, evaluations/*.md — into a
~11 MiB SQLite file so an agent or human can answer "what is recommended for
agentic memory?" in milliseconds, offline, without re-reading a ~5.4 MiB corpus
or inventing a second parser (parsing routes through catalog_lib — the shared
parser seam, ADR-0002).

The DB is a DERIVED artifact, like the generated counts: never commit it, never
hand-edit it. Rebuild with `make index-db`. It is deliberately NOT part of
`make check`'s gate set (see docs/catalog-db.md): like verify-installs' `--record`
(ADR-0006), a machine without the artifact must not fail CI — `--check` is the
report-only honesty contract for machines that HAVE rebuilt.

Identity and honesty invariants this script encodes:
- A database row is a catalog ROW, keyed by catalog_lib.name_key(name) — never
  the repo slug. 907 rows share 883 repo slugs (six to nine rows ship inside
  anthropics/claude-plugins-official or mattpocock/skills: the "Ships inside"
  cell #343 added), so a slug key collapses rows and multiplies their hits.
- Verdict and Evidence come from COMPARISON.md (the count-validated, detector-G
  -checked table), NOT from eval prose: a `## Verdict` paragraph that *mentions*
  ADOPT while concluding discovery-log must never surface as a false ADOPT.
- discovery-log is a LEAD, never a verdict (catalog_lib.REAL_VERDICTS); ask
  filters it out under --recommended but the row itself never lies about it.
- An eval `## Catalog entry` mirror is a ROW COPY, not the eval's text: it is
  stripped before indexing so a mirror never ranks one tool on another tool's
  verdict prose. (detector AD's rule, applied at ingestion.)

Usage:
  uv run catalog-db.py                          # build .generated/catalog.db
  uv run catalog-db.py --ask "agentic memory"
  uv run catalog-db.py --ask "code review" --recommended
  uv run catalog-db.py --card claude-mem
  uv run catalog-db.py --check                  # stale-artifact probe, no writes
"""
import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

import catalog_lib

ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH_REL = os.path.join(".generated", "catalog.db")
FTS_SCHEMA = """
CREATE VIRTUAL TABLE tools USING fts5(
  key UNINDEXED,
  name, type, section, one_liner, problem, overlaps,
  ships_inside, verdict UNINDEXED, evidence UNINDEXED, has_eval UNINDEXED,
  eval_body,
  tokenize='porter unicode61'
);
"""
# Column weights (FTS5 bm25 option): a name or one-liner hit IS the tool — an
# eval-body hit is a mention. Weight 0 drops a column from the MATCH haystack too
# (a column absent from the option string is not searched), which is why
# ships_inside stays at the tail with a low weight instead of being listed 0.
_BM25_OPTS = "bm25(tools, 8.0, 5.0, 2.0, 4.0, 2.0, 1.0, 0.5, 1.0)"
# Non-uniform verdict ladder added to bm25: ADOPT and KEEP are both "recommended"
# (ADR-0005) and sit two points apart; CONDITIONAL is a real but smaller gap
# (exercised-with-conditions); everything else (SKIP/DEFER/discovery-log) is far
# below — a 25-point hole, so a prose-dense SKIP can still edge a weak CONDITIONAL
# on relevance but never floats above the validated tools blanket. Cascade
# orderings both measured wrong live (verdict-first buried relevant KEEPs;
# relevance-first buried the canonical ADOPT pick under prose-dense SKIPs), and a
# uniform 5- or 15-point ladder measurably demoted KEEP/MEASURED rows: bm25 gaps
# between probe rows are small (single digits), so only a SMALL ADOPT/KEEP gap
# keeps the better-validated row winning. Measured on the three probe queries;
# retune only with a failing probe query pinned in
# TestCatalogDbEndToEnd.test_live_tree_ranks_the_canonical_pick.
VERDICT_LADDER = {"ADOPT": 0, "KEEP": 2, "CONDITIONAL": 10,
                  "SKIP": 25, "DEFER": 25, "discovery-log": 25}
_STOPWORDS = frozenset({
    "the", "a", "an", "is", "are", "of", "for", "to", "in", "on", "with", "and",
    "or", "what", "which", "how", "do", "i", "my", "me", "recommended",
    "recommend", "tool", "tools",
})


def _match_expr(question):
    """Free-text question -> an FTS5 MATCH expression, OR-joined.

    Relevance-first ordering (bm25 ascending, verdict as tiebreaker):
    a tool whose NAME matches is the answer to "tools for X"; verdict rank
    only breaks ties. --recommended is the recommendation filter, not the
    sort. bm25(): smaller (more negative) is better, so ascending rank is
    best-first. Recall-first on purpose: a missed match matters more than
    an over-broad one.

    Terms are split EXACTLY as the indexer splits text (unicode61: on every
    non-alphanumeric), so no query token can carry FTS5 query syntax into
    MATCH. Keeping `+`/`-` inside a token is not harmless: `long-term` reaches
    MATCH raw and FTS5 reads `-` as a column filter ("no such column: term"),
    and `c++` dies with `fts5: syntax error near "+"` (both live, 2026-10-08).
    Splitting also lets a `c++` query reach the C++ row: the index holds the
    bare token `c` (unicode61 keeps no punctuation), so the bare token is the
    one that matches. A single-char term is still dropped by the length guard
    below, so a lone `c++` degrades to the no-term fallback rather than a
    crash — widening that guard is a ranking change, not this fix."""
    terms = [w for w in re.findall(r"[a-z0-9]+", question.lower())
             if w not in _STOPWORDS and len(w) > 1]
    return " OR ".join(terms) if terms else "ai"


def _rows_for_build(catalog_text):
    """(row, section) for every CATALOG body row — catalog_lib's own body-row
    predicate walking a text whose `## ` headings carry the section, so the
    section column is read from the same text the parser read (no line-number
    bookkeeping, no second body parser)."""
    out, section = [], ""
    for line in catalog_text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not catalog_lib.is_body_row(line):
            continue
        parsed = catalog_lib.parse_catalog_rows(line)
        if parsed:
            out.append((parsed[0], section))
    return out


def build(db_path):
    """Parse catalog/comparison/evals and write one fresh FTS5 database."""
    catalog_text = Path(ROOT, "CATALOG.md").read_text(encoding="utf-8")
    comparison_text = Path(ROOT, "COMPARISON.md").read_text(encoding="utf-8")
    vermap = {}
    for v in catalog_lib.comparison_verdict_rows(comparison_text):
        # ComparisonRow is (tool, verdict, cells): the Evidence level is a trailing
        # cell, located the same way backfill-evidence rebuilds it — by its closed
        # vocabulary, not a fixed offset, so a column shift cannot mis-key it.
        evidence = next((c for c in v.cells[1:]
                         if c in ("MEASURED", "RUN", "REVIEW", "SOURCE-ONLY")), "")
        vermap[catalog_lib.name_key(v.tool)] = (v.verdict, evidence)
    evals = {}
    eval_dir = Path(ROOT, "evaluations")
    for p in sorted(eval_dir.glob("*.md")):
        if p.name == "TEMPLATE.md":
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        cut = text.find("## Catalog entry")  # the mirror row, not the eval text
        if cut != -1:
            text = text[:cut]
        text = catalog_lib.strip_html_comments(text)
        # Register an eval under every identity key its filename claims
        # (identity_keys, the #201 seam): playwright.md-s debate aside, the live
        # corpus keys `playwright`'s eval at `playwright-mcp.md` — a stem-only
        # map orphans exactly the rows PLAYBOOK.md links by hand.
        for k in catalog_lib.identity_keys(p.stem):
            evals.setdefault(k, text)

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    Path(db_path).unlink(missing_ok=True)  # a fresh DB, not an upsert
    db = sqlite3.connect(db_path)
    try:
        db.executescript(FTS_SCHEMA)
        for r, section in _rows_for_build(catalog_text):
            key = catalog_lib.name_key(r.name)
            verdict, evidence = vermap.get(key, ("", ""))
            body = evals.get(key, "")
            db.execute(
                "INSERT INTO tools VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (key, r.name, r.type, section, r.one_liner or "",
                 # CatalogRow carries no `problem` field (name/url/type/one_liner/
                 # overlaps/cells/ships_inside) — the Problem cell is row.cells[3]
                (r.cells[3] if len(r.cells) > 3 else ""),
                 r.overlaps or "", r.ships_inside or "", verdict, evidence,
                 1 if body else 0, body))
        db.commit()
        db.execute("INSERT INTO tools(tools) VALUES('optimize')")
        db.commit()
        n = db.execute("SELECT COUNT(*) FROM tools").fetchone()[0]
    finally:
        db.close()
    return n


def _require_db(db_path):
    if not Path(db_path).exists():
        print(f"catalog-db: MISSING {db_path} — build it with `make index-db`")
        return False
    return True


def run_ask(db_path, question, limit, recommended):
    if not _require_db(db_path):
        return 1
    where = ""
    if recommended:
        where = "AND verdict IN ('ADOPT', 'KEEP', 'CONDITIONAL')"
    sql = ("""
        SELECT name, type, section, verdict, evidence, has_eval,
               one_liner, problem, overlaps, ships_inside,
               """ + _BM25_OPTS + """ AS rank
        FROM tools
        WHERE tools MATCH ? """ + where + """
        ORDER BY (CASE verdict WHEN 'ADOPT' THEN 0 WHEN 'KEEP' THEN 2
                  WHEN 'CONDITIONAL' THEN 10 ELSE 25 END) + rank
        LIMIT ?
    """)
    db = sqlite3.connect(db_path)
    try:
        rows = db.execute(sql, (_match_expr(question), limit)).fetchall()
    finally:
        db.close()
    for (name, typ, section, verdict, evidence, has_eval, one_liner, problem,
         overlaps, ships_inside, _rank) in rows:
        print(f"{name} ({typ}, {section}) — {verdict or 'no-verdict'}/"
              f"{evidence or 'SOURCE-ONLY'}" + ("" if has_eval else " [no eval file]"))
        print(f"    {one_liner}")
        print(f"    problem: {problem}")
        if overlaps:
            print(f"    overlaps: {overlaps}")
        if ships_inside:
            print(f"    ships inside: {ships_inside}")
    return 0


def run_card(db_path, name):
    if not _require_db(db_path):
        return 1
    keys = catalog_lib.alias_keys(name)
    placeholders = ",".join("?" * len(keys))
    db = sqlite3.connect(db_path)
    try:
        rows = db.execute(
            "SELECT key, name, type, section, verdict, evidence, has_eval,"
            " one_liner, problem, overlaps, ships_inside"
            f" FROM tools WHERE key IN ({placeholders})",
            tuple(keys),
        ).fetchall()
    finally:
        db.close()
    if not rows:
        print(f"no tool matching {name!r}")
        return 1
    if len(rows) > 1:
        print(f"ambiguous: {len(rows)} tools under key(s) {sorted({r[0] for r in rows})}")
        return 1
    row = rows[0]
    print(json.dumps(dict(zip(
        ("key", "name", "type", "section", "verdict", "evidence", "has_eval",
         "one_liner", "problem", "overlaps", "ships_inside"), row, strict=True)),
        indent=2))
    return 0


def run_check(db_path):
    """Honest iff built from THIS tree: the catalog row count must match
    reconcile-counts' count, and every ADOPT/KEEP row's (verdict, evidence)
    must equal COMPARISON.md's. Partial by design — see docs/catalog-db.md."""
    if not Path(db_path).exists():
        print(f"catalog-db: MISSING {db_path} — machine-local artifact; build it "
              "with `make index-db` (not a tree defect)")
        return 1
    catalog = catalog_lib.catalog_count(
        Path(ROOT, "CATALOG.md").read_text(encoding="utf-8"))
    db = sqlite3.connect(db_path)
    try:
        db_rows = db.execute("SELECT COUNT(*) FROM tools").fetchone()[0]
        rec = db.execute(
            "SELECT key, name, verdict, evidence FROM tools"
            " WHERE verdict IN ('ADOPT', 'KEEP')").fetchall()
    finally:
        db.close()
    if db_rows != catalog:
        print(f"catalog-db STALE: db has {db_rows} rows, catalog has {catalog} — "
              "rebuild (`make index-db`)")
        return 1
    comp = {}
    for v in catalog_lib.comparison_verdict_rows(
            Path(ROOT, "COMPARISON.md").read_text(encoding="utf-8")):
        evidence = next((c for c in v.cells[1:]
                         if c in ("MEASURED", "RUN", "REVIEW", "SOURCE-ONLY")), "")
        comp[catalog_lib.name_key(v.tool)] = (v.verdict, evidence)
    for key, name, verdict, evidence in rec:
        want = comp.get(key)
        if want != (verdict, evidence):
            print(f"catalog-db STALE: {name!r} db={verdict}/{evidence} but "
                  f"comparison says {want} — rebuild (`make index-db`)")
            return 1
    print(f"catalog-db OK: {db_rows} rows match CATALOG.md; all {len(rec)} "
          "recommended rows agree with COMPARISON.md")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Build / query / verify the laptop-local catalog search db.")
    ap.add_argument("--db", default=os.path.join(ROOT, DB_PATH_REL),
                    help=f"sqlite path (default: {DB_PATH_REL} under the repo)")
    ap.add_argument("--ask", metavar="QUESTION",
                    help="query a built db instead of building")
    ap.add_argument("--recommended", action="store_true",
                    help="--ask: keep only ADOPT/KEEP/CONDITIONAL rows")
    ap.add_argument("--limit", type=int, default=8, help="--ask result count")
    ap.add_argument("--card", metavar="NAME",
                    help="print one tool's stored record by name")
    ap.add_argument("--check", action="store_true",
                    help="verify db freshness against the current tree; no write")
    args = ap.parse_args()
    if args.check:
        return run_check(args.db)
    if args.ask:
        return run_ask(args.db, args.ask, args.limit, args.recommended)
    if args.card:
        return run_card(args.db, args.card)
    n = build(args.db)
    size = os.path.getsize(args.db) if os.path.exists(args.db) else 0
    print(f"ingested {n} tools into {args.db} ({size / 1024:.0f} KiB). "
          "It is derived — never commit it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

