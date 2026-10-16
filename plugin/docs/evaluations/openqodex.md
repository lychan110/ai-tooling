# Evaluation: openqodex

**Repo:** [openqodex/openqodex](https://github.com/openqodex/openqodex)
**Stars:** 708 | **Last updated:** 2026-10-15 (pushed) | **License:** Apache-2.0
**Last verified:** 2026-10-16
**Last triaged:** 2026-10-16  <!-- triaged: bulk -->
**Dev loop stage:** Review
**Layer:** Tooling (in-agent pre-push code review)

---

## What it does

Pre-push code review inside the coding agent (Apache-2.0): scanners plus a separate
AI reviewer, gating before code leaves the machine — under the developer's own login
rather than a hosted review service.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only:
repo metadata plus the CATALOG "Overlaps with" cell. That is sufficient for a
triage stamp; it would not support an ADOPT, and this eval does not offer one.

## Triage note

Left at `discovery-log` (P3 backlog band, 2026-10-16). P3's rule is a stamp, not a
verdict: the row's Overlaps cell cites no STACK pick (`PR-Agent`, `open-code-review`,
`kodus-ai`, `vet` — `vet` is catalogued but the row does not challenge a STACK pick),
so no redundancy SKIP is available to write. Nearest catalogued neighbour is `vet`,
itself the P0 measure head; whether the in-agent pre-push gate actually beats
post-push review is a real eval's question, not a stamp's.
