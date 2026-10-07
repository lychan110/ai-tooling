# Evaluation: mcp-audit-tool

**Repo:** [graygnatconsole/mcp-audit-tool](https://github.com/graygnatconsole/mcp-audit-tool)
**Stars:** 115 | **Last updated:** 2026-09-26 (pushed) | **License:** MIT
**Last verified:** 2026-10-07
**Last triaged:** 2026-10-07  <!-- triaged: bulk -->
**Dev loop stage:** Review
**Layer:** Tooling

---

## What it does

Catalog one-liner: "Security-audit CLI for MCP servers (MIT, ★106, pure Python) — scans
agent configs for tool poisoning, rug pulls, hardcoded secrets, command injection, and
supply-chain risk; SARIF- and CI-ready." A static analyser that reads the MCP servers your
agent is configured to connect to and reports the risk classes named above, emitting
SARIF so the result can gate a CI job. Its job is to audit the *config surface* an agent
trusts before the agent connects, rather than to run the servers.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo
metadata plus the CATALOG "Overlaps with" cell. That is enough to place the lead, not to
judge the scanner's detection behaviour hands-on, so it would not support a positive
verdict — and none is offered.

## Triage note

Left at `discovery-log`. Zero overlap pressure (P3 backlog): its cited peers — `trustmcp`,
`agent-scan`, `agentshield`, `skill-scanner` — are all `discovery-log` leads themselves,
with no STACK pick among them, so there is no incumbent to call this redundant against. A
maintained (pushed 2026-09-26), MIT-licensed, pure-Python MCP-config auditor that emits
SARIF for CI is a distinct tool in the agent-security cluster, and the detection quality
of a scanner is exactly the kind of claim only a hands-on eval can support. The
eliminate-only triage lane cannot run one, so it is left here for a human or `eval-runner`.

_Triaged 2026-10-07 by the P3 backlog band._

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [mcp-audit-tool](https://github.com/graygnatconsole/mcp-audit-tool) | tool | Security-audit CLI for MCP servers (MIT, ★106, pure Python) — scans agent configs for tool poisoning, rug pulls, hardcoded secrets, command injection, and supply-chain risk; SARIF- and CI-ready | MCP servers and agent configs ship with no independent audit before an agent connects; want a scanner you can gate in CI | trustmcp, agent-scan, agentshield, skill-scanner |
