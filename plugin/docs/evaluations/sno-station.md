# Evaluation: sno-station

**Repo:** [sno-ai/sno-station](https://github.com/sno-ai/sno-station)
**Stars:** 743 | **Last updated:** 2026-10-15 (pushed) | **License:** Apache-2.0
**Last verified:** 2026-10-16
**Last triaged:** 2026-10-16  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Tooling (multi-agent squad runtime)

---

## What it does

A local, open-source runtime (Apache-2.0) that turns several coding agents (Codex,
Claude Code, Cursor, Hermes, OpenClaw) into one cooperative squad: a shared encrypted
memory store, explicit work handoff between agents, and agents that review each
other's output.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only:
repo metadata plus the CATALOG "Overlaps with" cell. That is sufficient for the
triage decision below, which turns on overlap with a catalogued incumbent, not on
the tool's behaviour — a question the overlap answers directly. It would not
support an ADOPT, and this eval does not offer one.

## Triage note

Left at `discovery-log` (P2 challenger band, 2026-10-16). The band's listed
incumbent is `claude-squad` — the one STACK pick in the row's Overlaps cell
(`orca`, `succubus`, `hermes-conductor` are catalogued but not in STACK) — and a
redundancy SKIP against it would be dishonest: `claude-squad` multiplexes several
agent sessions, while sno-station's distinct value is what those sessions *share*
(squad-runtime layer with one encrypted memory store, handoffs and cross-agent
review across five heterogeneous harnesses). Significant standalone candidate —
deserves a real hands-on eval rather than a mechanical SKIP; left in the queue for
the P0/eval-runner lane.
