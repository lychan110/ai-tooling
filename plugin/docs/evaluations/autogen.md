# Evaluation: autogen

**Repo:** [microsoft/autogen](https://github.com/microsoft/autogen)
**Stars:** 61,965 | **Last updated:** 2026-11-12 (pushed) | **License:** CC-BY-4.0
**Last verified:** 2026-11-25
**Last triaged:** 2026-11-25  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Process (framework)

---

## What it does

Microsoft's programming framework for agentic AI — conversational multi-agent orchestration with a
layered API (Core, AgentChat, Extensions) and a no-code Studio for prototyping.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo metadata
plus the CATALOG "Overlaps with" cell (microsoft/agent-framework, langchain, crewAI, LangGraph,
semantic-kernel). That is sufficient to place the lead, not to support an ADOPT — this eval offers
none.

## Successor

`microsoft/agent-framework` — Microsoft's own successor, and already a catalogued row in its own
right (CATALOG: `microsoft/agent-framework`, itself at SKIP for this catalog's scope). The archived
AutoGen README names it for new users and links the AutoGen → Agent Framework migration guide.

One caveat on that successor, recorded because a reader will follow the link: on 2026-11-25
`microsoft/agent-framework` answered a GitHub API request with **404** (its own cached metadata
record already reads unreachable, fetched 2026-11-23), while `microsoft/agent-framework-go` — live,
701★, pushed 2026-11-25 — still points at that upstream repository as the place the .NET and Python
implementations live. That successor-link problem belongs to the `microsoft/agent-framework` row and
to the drift lane, not to this row's disposition; this row's own fact is that AutoGen is archived
and the project names its successor.

## Verdict

**SKIP** — archived, and superseded by `microsoft/agent-framework`. The project moved rather than
died: the repo is archived and read-only, and Microsoft's own README directs new users to Agent
Framework and ships a migration guide. The successor is already catalogued, so there is nothing to
repoint this row at and nothing to add.

The earlier leave-decision rested on different ground — that a ★60K first-party framework is too
significant to SKIP as *redundant* — and the P1 reason is factual rather than a redundancy call:
archived, with the successor named by the project itself.

_Triaged 2026-11-25 by the P1 successor-check band. Archived is never an automatic SKIP: a repo is
far more often archived because it **moved** than because it died, so each one gets a successor
check before disposal. This one got that check._
