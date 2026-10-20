# Evaluation: Tracely

**Repo:** [jwuthri-cloud/Tracely-ai](https://github.com/jwuthri-cloud/Tracely-ai)
**Stars:** 1,068 | **Last updated:** 2026-10-15 (pushed) | **License:** MIT
**Last verified:** 2026-10-20
**Last triaged:** 2026-10-20  <!-- triaged: bulk -->
**Dev loop stage:** Outer Loop
**Layer:** Tooling

---

## What it does

Trace-native CI/CD for AI agents (MIT) — grades every agent trace, clusters failures into issues, freezes bad runs into hermetic replayable regression cases that gate PRs. Catalogued as the `Tracely` row by the 2026-10-19 discovery pass.

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
has no incumbent to name: its overlap list (langfuse, opik, promptfoo, phoenix) is unsettled
leads, not incumbents. Left at discovery-log for a real hands-on eval — promoting failing
production traces into regression cases that gate PRs is a distinct mechanism worth
measuring, not a mechanical-disposition candidate.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with | Ships inside |
|------|------|-----------|-------------------|---------------|--------------|
| [Tracely](https://github.com/jwuthri-cloud/Tracely-ai) | platform | Trace-native CI/CD for AI agents (MIT) — grades every agent trace, clusters failures into issues, freezes bad runs into hermetic replayable regression cases that gate PRs | Observability stops at the dashboard: want failing production traces promoted into deterministic regression tests that block the PR that would ship them again | langfuse, opik, promptfoo, phoenix |  |
