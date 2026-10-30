# Evaluation: graphicle

**Repo:** [Graphicle-AI/graphicle](https://github.com/Graphicle-AI/graphicle)
**Stars:** 427 | **Last updated:** 2026-10-28 (pushed) | **License:** Apache-2.0
**Last verified:** 2026-10-29
**Last triaged:** 2026-10-30  <!-- triaged: bulk -->
**Dev loop stage:** Plan
**Layer:** Tooling (code graph + agent memory)

---

## What it does

One Rust binary that indexes a repository into a tree-sitter code graph (files, functions,
classes, calls, imports — no model involved), holds project memory (docs, reviewed decisions,
and past Claude Code/Codex sessions) in a single SQLite file, and serves both to coding agents
over one MCP server alongside a CLI. `graphicle setup` indexes the repo, connects whichever
clients it finds (Claude Code, Codex, Cursor, VS Code, Claude Desktop), turns on session
capture, adds a two-line `AGENTS.md` section, and installs git hooks that keep the graph
current after each commit, merge and checkout; `graphicle disconnect` undoes all of it.

The differentiated part is that retrieval is *cited and budgeted*: `graphicle context` and the
MCP tools return excerpts naming file and line spans within a caller-set token budget and
without calling a model, and reviewed memories are anchored to the symbols they describe, so a
memory goes stale when that code changes. Optional extras hang off the same store —
`graphicle review` (branch-diff review restricted to comments whose citations hold, with a
GitHub Action), `graphicle fix` (patch an issue on a new branch and run the tests), and
`graphicle see` / `graphicle pixel` (screen-to-code via computer use).

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: GitHub repo
metadata (stars, pushed date, licence, fetched 2026-10-29) plus the README read at HEAD, and a
resolution check of the two install paths (`graphicle-ai/homebrew-tap` and
`graphicle-ai/graphicle/releases/latest` both resolve). Nothing was indexed, invoked or
benchmarked, and no run is claimed. Every performance and accuracy figure in the README —
speed and peak memory against Graphify, LoCoMo-10 accuracy against seven memory systems — is
the vendor's own, on the vendor's own pre-release builds; none of it is reproduced here.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at discovery-log
rather than SKIPped.

## Triage note

P2/P3 on arrival. The `Overlaps with` cell names `codegraph`, which is a STACK pick
(ADOPT, MEASURED) and therefore a real incumbent, so the redundancy question is not empty —
but the distinct claim here is the bundle, not the graph: a code graph plus code-anchored
memory plus cited, budgeted context in one install with no Python, Docker or database server.
`codegraph` alone does not cover memory, and the memory tools do not cover the graph. The repo
is also 15 days old and at `0.1.x`, which is a reason to keep it a lead rather than dispose of
it. Left for the P0/eval-runner lane to exercise; a hands-on comparison against `codegraph` on
the same repository is the deciding test.

**Triaged 2026-10-30 by the lead-triage band (P2 challenger):** left at `discovery-log`, stamped.
The incumbent a redundancy SKIP would have had to name is `codegraph` (STACK pick, ADOPT,
MEASURED), and it does not cover the claim: `codegraph` is a graph, not a graph plus code-anchored
memory plus cited token-budgeted excerpts. The other neighbours named in the catalog cell
(`graphify`, `code-review-graph`, `serena`, `codebase-memory-mcp`, `neuromesh`) are either graph
readers or memory stores; none ships both halves in one local binary. A `0.1.x` repo 15 days old
is a reason to keep looking rather than to dispose, so the row stays a lead and the deciding test
remains a measured run against `codegraph` — which is not this lane's call.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [graphicle](https://github.com/Graphicle-AI/graphicle) | tool | Single Rust binary (Apache-2.0) combining a tree-sitter code graph, code-anchored project memory and cited token-budgeted context over one MCP server, with `setup` wiring Claude Code/Codex/Cursor/VS Code and git hooks to keep it current | Agents re-explore the repo every session and memory sits apart from the code it describes; want one local store that returns cited excerpts from both inside a set token budget | codegraph, graphify, code-review-graph, serena, codebase-memory-mcp, neuromesh |
