# Evaluation: Mintlify Index

**Repo:** [mintlify/index](https://github.com/mintlify/index)
**Stars:** 31 | **Last updated:** 2026-08-06 (pushed) | **License:** MIT
**Last verified:** 2026-08-08
**Last triaged:** 2026-10-30  <!-- triaged: bulk -->
**Dev loop stage:** Plan
**Layer:** Infrastructure (MCP server)

---

## What it does

A retrieval engine and MCP server from Mintlify for searching documentation, installed via
`npx mint index`.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo
metadata (README, topics, license) via the GitHub API, plus the CATALOG "Overlaps with" cell.

## Verdict

**SKIP** — archived (2026) with no successor. The repo README carries the vendor's own notice:
"Mintlify Index has been discontinued and this repo is no longer maintained. The hosted MCP
server and the `mint index` command have been shut down." Both install paths the row described
are gone, so nothing inherits this entry: the retrieval pipeline was a source release of a hosted
service (docs ingestion, the Chroma corpus and auth live in the Mintlify platform), not a
standalone tool. Its catalogued neighbours (`context7`, `ref-tools-mcp`, `docmd`) are independent
docs-lookup tools, not continuations of it, so there is no link to repoint.

## Triage note

P1 successor-check, disposed 2026-10-30. Successor check first: the README names no forwarding
repository and no replacement product, and `npx mint index` is switched off rather than moved —
so this is a SKIP, not a repoint. The earlier "worth a first-time eval on retrieval quality"
read (2026-08-08) described a service that no longer runs; an eval of a dead endpoint has nothing
to measure. Every other archived row in `repo-metadata.json` is already at `SKIP`, and this one
now joins them.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [Mintlify Index](https://github.com/mintlify/index) | MCP server | Retrieval engine and MCP server (MIT) from Mintlify for searching documentation — install via `npx mint index` | Agents need fast, accurate retrieval over docs without hand-rolling RAG or embeddings | context7, ref-tools-mcp, docmd |
