# Evaluation: export-md

**Repo:** [yussufs/export-md](https://github.com/yussufs/export-md)
**Stars:** 9  <!-- repo-metadata.json, fetched 2026-10-22 -->
**License:** MIT | **⚠️ Archived**  <!-- archived by the owner 2026-10-20 -->
**Last verified:** 2026-08-18
**Last triaged:** 2026-10-23  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Tooling

---

## What it does

A `/export-md` slash command for Claude Code — saves any session as clean, readable markdown.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo metadata
plus the CATALOG "Overlaps with" cell (cli-continues, claude-hud). That is sufficient to place
the lead and note none of its named overlaps are STACK incumbents, not to support an ADOPT —
this eval offers none.

## Triage note

Left at `discovery-log`: neither cli-continues (cross-tool session handoff) nor claude-hud
(in-session HUD) does what export-md does — a one-shot session-to-markdown export for sharing
or archiving. Small, single-purpose utility; not clearly dominated by an incumbent. Left for the
P0/eval-runner lane.

_Triaged 2026-07-31 by today's discovery lead; re-confirmed 2026-08-18 — still a small,
undominated single-purpose utility._

## Successor

none — the owner's other repositories are unrelated (a Flutter dictionary fork, an LLM-gateway
fork, a 2025 side project), the README names no successor, and the repository was archived
without a forwarding note. Claude Code's built-in `/export` (raw `.txt` transcript) is a
pre-existing partial substitute, not a lineage successor: it shipped before this tool and does
not do this tool's job of rendering turns and code fences as readable markdown.

## Verdict

**SKIP** — archived by its owner on 2026-10-20 with no successor to repoint to. It is a
single slash command plus one Python script (six commits, last push 2026-07-30) that reads the
on-disk JSONL transcript and renders it as markdown; read-only, it cannot follow Claude Code's
internal transcript format, which the README itself names as the thing that breaks it. Nothing
here to adopt.

_Triaged 2026-10-23 by the P1 successor-check band. The 2026-08-18 read left it a lead on the
assumption the repository was live; the archival is what changed, not the tool._
