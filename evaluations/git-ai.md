# Evaluation: git-ai

**Repo:** [feder-cr/git-ai](https://github.com/feder-cr/git-ai)
**Stars:** 2,370 | **Last updated:** 2026-10-18 (pushed) | **License:** MIT
**Last verified:** 2026-10-20
**Last triaged:** 2026-10-20  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Infrastructure

---

## What it does

Git designed for AI agents (MIT) — a server-centric VCS (Scion-style): sparse clones, agent-first compare-and-swap landing, server-side history, changeset log. Catalogued as the `git-ai` row by the 2026-10-19 discovery pass.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo
metadata (via `repo-metadata.json`, fetched 2026-10-19) plus the CATALOG row. Nothing here
was installed, invoked, or benchmarked, and no run is claimed.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at discovery-log rather than SKIPped.

## Triage note

P3 backlog. The row arrived with the 2026-10-19 discovery pass and no eval file existed, so
it could never carry a stamp and headed P3 on every pass. Nothing structural bands it — it
sits in P3, which means its `Overlaps with` cell cites no STACK pick, so a redundancy SKIP
has no incumbent to name. Left at discovery-log for a real hands-on eval: a server-centric
VCS built around thousands of short-lived agent changes is a differentiated mechanism, not a
mechanical-disposition candidate.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with | Ships inside |
|------|------|-----------|-------------------|---------------|--------------|
| [git-ai](https://github.com/feder-cr/git-ai) | tool | Git designed for AI agents (MIT) — server-centric VCS (Scion-style): sparse clones, agent-first compare-and-swap landing, server-side history, changeset log | Classic Git hosting assumes humans — full clones, merge queues, client-side history walks — and bottlenecks thousands of short-lived concurrent agent changes | re_gent, worktrunk, h5i, weave |  |
