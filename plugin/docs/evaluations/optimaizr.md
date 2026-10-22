# Evaluation: optimaizr

**Repo:** [blendbunjaku/optimaizr](https://github.com/blendbunjaku/optimaizr)
**Stars:** 132 | **Last updated:** 2026-10-19 (pushed) | **License:** MIT
**Last verified:** 2026-10-22
**Dev loop stage:** Reflect
**Layer:** Tooling

---

## What it does

Local CLI (MIT) that shows where Claude Code, Codex and opencode waste tokens, and holds the expensive message before it is paid. Catalogued as the `optimaizr` row by the 2026-10-22 discovery pass.

It reads the session logs already on disk and attributes spend to the mechanism that caused it rather than to a tool: re-reading a long conversation on every call, and cache-expiry rewrites (a conversation idle past the hour cache is written in full again at up to twice the input price). Findings are split into clear waste, likely savings, and "up to, if you test" — the three are never summed into one number. `apply <rule>` makes a change it can measure (for example compacting at 200K), `results` compares the days after against the days before and marks every row that got worse, and `verify <rule>` replays the user's own requests on the cheaper option. `guard` uses Claude Code's own hooks to hold one message to an expiring conversation, showing what sending it would cost, and also blocks reading a large file whole or re-running a command that already failed twice. Reports and `live` cover Claude Code, Codex and opencode; `apply context-compaction` changes Claude Code and Codex only. Everything runs locally under `~/.optimaizr/`; network calls are limited to `verify` against the user's own provider, an optional third-party second opinion, and a daily npm version check.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: GitHub repo
metadata (stars, pushed date, licence, fetched 2026-10-22) plus the README, CLI reference and
CHANGELOG read at HEAD. The dollar figures quoted above are the author's own reported numbers
from their README, not measurements taken here.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at discovery-log rather than SKIPped.

## Triage note

Sits in the same outer-loop cost cluster as `ccusage` (ADOPT, MEASURED) and `codeburn` (ADOPT, MEASURED), so if a redundancy SKIP is ever considered, those two are the incumbents it must name. Not SKIPped on arrival: its mechanism is distinct from both — it does not just report spend, it gates the specific message that would pay for an expired cache and measures whether a change it applied actually helped. A real disposition needs a hands-on run on this machine's own logs, which is out of scope for an unattended discovery pass.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [optimaizr](https://github.com/blendbunjaku/optimaizr) | tool | Local CLI (MIT) that shows where Claude Code, Codex and opencode waste tokens, and holds the expensive message before it is paid | The bill shows a total but not that most of it is re-reading the same conversation, or that an expired cache re-wrote 162K tokens at up to 2x input price | ccusage, codeburn, peek, claude-monitor |
