# Evaluation: easel

**Repo:** [The-Sentience-Company/easel](https://github.com/The-Sentience-Company/easel)
**Stars:** 47 | **Last updated:** 2026-08-17 (pushed) | **License:** Apache-2.0
**Last verified:** 2026-08-18
**Last triaged:** 2026-09-28  <!-- triaged: bulk -->
**Dev loop stage:** Plan
**Layer:** Tooling

---

## What it does

A local review board for work an agent wants a human to look at: the agent publishes,
a human annotates in the browser, and the feedback flows back to the agent as JSON.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo
metadata plus the repo's own `LICENSE` file at HEAD, read directly for the license claim
below. That is not enough to judge whether a human review board in the browser actually
beats a blocking chat prompt. It would not support an ADOPT, and this eval offers none.

## Triage note

The 2026-08-18 `SKIP` is withdrawn. It was a `P4` mechanical skip whose recorded reason was
the license and nothing else — "license is the reason, not quality" — and that license does
not exist. `LICENSE` at HEAD is the **Apache License 2.0**, the permissive side of this
catalog's bar, and `repo-metadata.json` records `license_spdx: Apache-2.0` independently. A
mechanical skip is only as sound as its fact, so with the fact gone the route back is the
queue: the row returns to `discovery-log` as an unexamined lead. Whether a human-in-the-loop
review board beats a blocking chat prompt — and how it compares to `facet` and `plannotator`
— is a behaviour question no license can answer, and this catalog has not tested it.

_Triaged 2026-09-28 by the discovery lane — unsound `P4` skip withdrawn after license verification._

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [easel](https://github.com/The-Sentience-Company/easel) | tool | Local review board where an agent publishes work, a human annotates in-browser, and feedback returns as JSON | Agents need human sign-off mid-task but only have blocking chat prompts, not a structured review surface | facet, plannotator, hubo |
