# Evaluation: magpie

**Repo:** [yetone/magpie](https://github.com/yetone/magpie)
**Stars:** 22172 | **Last updated:** 2026-10-26 (pushed) | **License:** MIT
**Last verified:** 2026-10-26
**Last triaged:** 2026-10-27  <!-- triaged: bulk -->
**Dev loop stage:** Plan
**Layer:** Tooling

---

## What it does

Model router for coding agents (MIT, ★22K) — any agent on any provider or subscription from one local gateway and menu bar. Catalogued as the `magpie` row by the 2026-10-26 discovery pass.

One local gateway at `127.0.0.1:3425` speaks OpenAI Chat, OpenAI Responses, Anthropic Messages and Gemini, and translates between them (streaming, tool calls and reasoning included). The app rewrites the one key that matters in each agent's own config, so any installed agent — Claude Code, Codex, Gemini CLI, OpenCode, Pi, Hermes Agent, and 60+ more listed in the README — can run on any provider/model from one searchable picker. Subscriptions (Claude, ChatGPT, Copilot, Gemini, Grok…) become providers to every other agent; routing groups (`smart`, `order`, `rotate`, `usage`, `pace`) spread requests over accounts and fail over when a quota runs out, so the agent never sees the error. Profiles switch every agent's setup back in one move. Privacy masking (off by default) swaps keys/emails in prompts for placeholders on the machine before the request leaves it. Runs on macOS/Windows/Linux (menu bar app, window, TUI, web UI and CLI), in Docker, and on Termux.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: GitHub repo metadata (stars, licence, pushed date, fetched 2026-10-26) plus the README read at HEAD. All behaviour above is the author's own description, not measured here.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at discovery-log rather than SKIPped.

## Triage note

Sits in the same model-routing cluster as `claude-code-router`, `litellm`, `CLIProxyAPI` and `cc-switch`; not SKIPped on arrival: its mechanism is distinct from those proxy/account-rotation tools — it rewrites each agent's own config and fails over between subscriptions behind one local gateway. A real disposition needs a hands-on run against this machine's own agents, which is out of scope for an unattended discovery pass.

**Re-triaged 2026-10-27 (P3 backlog band).** Left at `discovery-log` and stamped. No redundancy SKIP
applies to this row: `claude-code-router`, `litellm`, `cc-switch` and `CLIProxyAPI` are catalogued
peers and none of the four is a STACK pick, so there is no incumbent it is redundant *with*. Rewriting
each agent's own config and failing over between subscriptions behind one gateway is a mechanism none
of them shares, so a real read is the honest disposition.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [magpie](https://github.com/yetone/magpie) | tool | Model router for coding agents (MIT, ★22K) — any agent on any provider or subscription from one local gateway and menu bar | A subscription or key works in one agent and nowhere else; want one local gateway that routes every coding agent to any model and fails over when a quota runs out | cc-switch, claude-code-router, litellm, CLIProxyAPI |
