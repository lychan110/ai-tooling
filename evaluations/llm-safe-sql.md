# Evaluation: llm-safe-sql

**Repo:** [hyuga611/llm-safe-sql](https://github.com/hyuga611/llm-safe-sql)
**Stars:** 0 | **Last updated:** 2026-09-02 (pushed) | **License:** MIT | **⚠️ Archived**
**Last verified:** 2026-08-09
**Last triaged:** 2026-09-21  <!-- triaged: bulk -->
**Dev loop stage:** Implement (safe database mutations)
**Layer:** Infrastructure

---

## What it does

Lets an LLM propose an UPDATE/DELETE, runs it for real inside a database transaction, measures the actual before/after diff, and always rolls back — so a human approves a measured fact instead of the model's claim about what the mutation would do. MySQL + PostgreSQL, MCP server, no runtime dependencies. The repository is now archived and read-only: its README banner says development continues in the **airframe** monorepo under `packages/llm-safe-sql`, with `@hyuga/llm-safe-sql` 0.10.1 and later published from there and this repo stopping at 0.9.x so older links keep working.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: it rests on GitHub repo metadata (the `archived` flag, last push, licence), on the project's own README banner, and on its npm registry record. Archived status and the successor lineage came from those three; the MCP server was never installed or exercised.

That is sufficient for the verdict below, because the verdict turns on *maintenance status and succession*, not on the tool's behaviour — a question metadata answers directly. It would not be sufficient to support an ADOPT, and this eval does not offer one.

## Successor

`hyuga611/airframe` — `packages/llm-safe-sql` (npm `@hyuga/llm-safe-sql`, 0.10.1+; 0.11.2 current). Not a standalone row in CATALOG.md: the continuation lives inside a monorepo package, so there is no successor *repo* for this row to repoint at.

## Verdict

**SKIP** — archived, and superseded by `hyuga611/airframe` (`packages/llm-safe-sql`). The project moved rather than died: the archived repo is a read-only mirror frozen at 0.9.x, and the live code is the monorepo package the npm releases come from. The successor is a package inside a monorepo rather than a repo of its own, so there is nothing to repoint this row at — and nothing to add, since this row already describes what the package is.

_Triaged 2026-09-21 by the P1 successor-check band. Archived is never an automatic SKIP: a repo is far
more often archived because it **moved** than because it died, so each one gets a successor check
before disposal. This one got that check._
