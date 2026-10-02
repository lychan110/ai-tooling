# Evaluation: jevgrep

**Repo:** [dzhng/jevgrep](https://github.com/dzhng/jevgrep)
**Stars:** 2,028 | **Last updated:** 2026-10-02 (pushed) | **License:** MIT
**Last verified:** 2026-10-02
**Last triaged:** 2026-10-02  <!-- triaged: bulk -->
**Dev loop stage:** Plan
**Layer:** Tooling

---

## What it does

A CLI (`jg`) that answers a repository question — "how are telemetry events recorded and sent?" — with the relevant files, reading leads, and verbatim source excerpts in one stdout response, using the Jev model to judge relevance across folders, files, and declarations. It ships with its own agent skill plus an install command (`jg skill`) so a coding agent learns to reach for it; requires Node 22+ and a gateway key (Vercel AI Gateway, OpenRouter, TypeSafe-compatible endpoints). Self-reported: matched the baseline on 8 of 10 SWE-bench tasks at ~30% lower cost by cutting file-discovery turns.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only:
README plus repo metadata plus the CATALOG "Overlaps with" cell. That is sufficient for a SKIP
that turns on *redundancy with a catalogued STACK incumbent*, not on the tool's behaviour —
a question the overlap answers directly. It would not support an ADOPT, and this eval
offers none.

## Verdict

**SKIP** — redundant with [`serena`](https://github.com/oraios/serena) (MEASURED STACK pick for semantic code retrieval and symbol-level context; both exist so an agent starts from relevant source instead of grepping whole directories — a second retrieval path for the same job earns nothing, and jevgrep's differentiator is a hosted relevance model behind a required gateway key, a cost and dependency the incumbent does not carry).

_Triaged 2026-10-02 by the P3 backlog band — significant enough to note the differentiation, but the retrieval job is already covered in STACK; left for the P0/eval-runner lane if gateway-keyed relevance search ever needs a hands-on look._
