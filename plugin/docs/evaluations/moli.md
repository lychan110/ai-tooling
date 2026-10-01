# Evaluation: moli

**Repo:** [lexmount/moli](https://github.com/lexmount/moli)
**Stars:** 119 | **Last updated:** 2026-08-12 (pushed) | **License:** Apache-2.0 OR MIT (dual-licensed: LICENSE-APACHE + LICENSE-MIT)
**Last verified:** 2026-08-12
**Last triaged:** 2026-08-12  <!-- triaged: bulk -->
**Dev loop stage:** Verify
**Layer:** Tooling

---

## What it does

A browser built in Rust specifically for AI agents to navigate, automate, and script the web,
rather than automation bolted onto a human-first browser.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this. Source-grounded only: repo metadata plus the CATALOG
"Overlaps with" cell. Enough to place it against nearby browser-automation tools, not enough for
any verdict, and none is offered.

## Triage note

Left at `discovery-log` — re-checked 2026-10-01, when the repo carried both `LICENSE-APACHE` and
`LICENSE-MIT` at HEAD (dual MIT/Apache-2.0, both permissive and clear of this catalog's licence
bar). The row stays a lead on its own merits; no licence gap remains. The original 2026-08-12 note
recorded the opposite because the repo was two days old and GitHub reported no detected LICENSE
file — a still-forming metadata state it was not worth disposing on.

_Triaged 2026-08-12 by the P3 backlog band._

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [moli](https://github.com/lexmount/moli) | tool | Rust-built browser for AI agents (Apache-2.0 OR MIT, dual-licensed) — navigate, automate, and script the web natively | Browser automation bolted onto a human-first browser is fragile; want one built agent-first from the ground up | agent-browser, playwright-skill, opencli, browser-act/skills |
