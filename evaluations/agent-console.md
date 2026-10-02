# Evaluation: agent-console

**Repo:** [LockedinLabs-AI/agent-console](https://github.com/LockedinLabs-AI/agent-console)
**Stars:** 785 | **Last updated:** 2026-10-02 (pushed) | **License:** MIT
**Last verified:** 2026-10-02
**Last triaged:** 2026-10-02  <!-- triaged: bulk -->
**Dev loop stage:** Reflect
**Layer:** Infrastructure

---

## What it does

Local-first observability for AI coding agents: parses Claude Code and Codex session logs on the machine for tokens, cache, models, and cost per session, with an optional self-hosted team hub to aggregate sessions across machines. Ships policy hooks, presenting mode, and signed/notarized macOS builds with attested releases.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only:
README plus repo metadata plus the CATALOG "Overlaps with" cell. That is sufficient for a SKIP
that turns on *redundancy with a catalogued STACK incumbent*, not on the tool's behaviour —
a question the overlap answers directly. It would not support an ADOPT, and this eval
offers none.

## Verdict

**SKIP** — redundant with [`ccusage`](https://github.com/ccusage/ccusage) (ADOPT, MEASURED — the STACK's Outer Loop cost pick parses the same local Claude Code/Codex session logs into token and cost reports; agent-console's extras — a per-session TUI, a self-hosted team hub, signed macOS builds — are packaging over the same job `ccusage` already covers, and the multi-machine aggregation use case is `codeburn`'s recorded note in STACK-LEDGER, not a new job).

_Triaged 2026-10-02 by the P2 challenger band._
