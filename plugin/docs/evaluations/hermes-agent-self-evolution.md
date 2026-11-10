# Evaluation: hermes-agent-self-evolution

**Repo:** [NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution)
**Stars:** 5650 | **Last updated:** 2026-06-17 (pushed) | **License:** MIT (README states MIT; no LICENSE file in the repo)
**Last verified:** 2026-11-10
**Last triaged:** 2026-11-10  <!-- triaged: bulk -->
**Dev loop stage:** Build
**Layer:** Process

---

## What it does

DSPy + GEPA loop (by Nous Research) that mutates Hermes Agent skills, tool descriptions, and prompts, scores variants on synthetic or session-history evals, gates on tests and size limits, then opens a PR. Self-improving tooling for an agent's own skill library.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo metadata plus the CATALOG "Overlaps with" cell (SkillOpt, SkillAdam, evolver, dspy). That is sufficient to place the lead; it is not sufficient for a positive verdict, and none is offered.

## Triage note

Left at `discovery-log` by the P3 backlog band. This is the band's head and it has never been triaged — no eval file and no `**Last triaged:**` stamp existed before this pass. Its `Overlaps with` cell names no STACK incumbent, so there is no incumbent to SKIP against, and this lane may not write ADOPT/KEEP/CONDITIONAL. Stamped and left; a hands-on read of a self-mutating framework is P0/eval-runner lane work, not a bulk disposition.

_Triaged 2026-11-10 by the P3 backlog band._

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| hermes-agent-self-evolution | framework | DSPy + GEPA loop (by Nous Research) that mutates Hermes Agent skills, tool descriptions, and prompts, scores variants on synthetic or session-history evals, gates on tests and size limits, then opens a PR | Skills and prompts are hand-written and never measurably improve; want trace-driven variants that must pass the test suite and size caps before a human reviews | SkillOpt, SkillAdam, evolver, dspy |
