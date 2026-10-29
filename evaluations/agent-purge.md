# Evaluation: agent-purge

**Repo:** [ZiChuanLan/agent-purge](https://github.com/ZiChuanLan/agent-purge)
**Stars:** 861 | **Last updated:** 2026-10-29 (pushed) | **License:** MIT
**Last verified:** 2026-10-29
**Dev loop stage:** Implement
**Layer:** Tooling (harness system-prompt control)

---

## What it does

An npm CLI (Node ≥ 20, zero runtime dependencies) that unifies the per-harness entry points for
a coding agent's system prompt behind one set of persona files in `~/.agent-purge/personas/`.
Every harness exposes a different lever — a launch flag, a config file, a plugin hook, or a
runtime object — and agent-purge normalises them into three channels (`install` writes a
managed config block/hook/plugin into the harness, `shim` puts a same-named wrapper on `PATH`,
`slash` hot-switches inside a session via `/purge on|off|status`) across four modes (`replace`,
`strict` persona-only, `append`, `off`).

The claimed property is reversibility: `--mode off`, `disarm` or `uninstall <h>` restores the
harness byte-for-byte. A local web console on `127.0.0.1:7788` selects and edits personas, and
an optional magpie gateway plugin rewrites the system segment of any request routed through
that gateway instead of per-harness installs. The README tabulates 13 harnesses with
before/after system-prompt sizes; two (qoder, workbuddy) are declared unsupported because the
prompt lives server-side, and closed desktop clients are launched as-is rather than faked.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: GitHub repo
metadata (stars, pushed date, licence, fetched 2026-10-29) plus the README read at HEAD, and an
existence check that the `agent-purge` package resolves on the npm registry. Nothing was
installed, injected or measured, and no run is claimed. The before/after prompt sizes in the
README are the author's own measurements against a local fake provider; they are not
reproduced here.

Two facts about the repository itself belong in the record rather than in a footnote. First,
it was created 2026-10-25 — four days before this evaluation — so the whole "tested versions"
matrix describes harness versions current this week, not a track record. Second, it shows 633
forks against 861 stars, an unusual ratio for a four-day-old CLI that reads as star/fork
farming until explained; it is a reason to look before installing, not proof of anything.
The README, console and CLI are Chinese-language, and the repo carries a long
legal-disclaimer section.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at discovery-log
rather than SKIPped.

## Triage note

The `Overlaps with` cell names only config-surface tools (`capa`, `ai-rules-sync`, `gentle-ai`)
and none of them is a STACK pick, so a redundancy SKIP has no incumbent to name. The mechanism
is also genuinely uncatalogued: the other cross-harness tools share *skills, rules and
commands* between editors, while this one rewrites the *system prompt itself* — which is the
layer those tools all leave alone. Two supported harnesses are the ones this workspace runs
(Hermes, via a temporary `HOME` with a swapped `SOUL.md`, and opencode, via an in-place
`output.system` plugin), so exercising it here is cheap. Left for the P0/eval-runner lane.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [agent-purge](https://github.com/ZiChuanLan/agent-purge) | tool | npm CLI (MIT, Node ≥ 20, zero deps) that replaces, appends, strictly overrides or disables the system prompt of 13 coding harnesses from one persona file, with install/shim/slash channels, a local web console, and reversible uninstall | Each harness exposes its system prompt behind a different lever (launch flag, config file, plugin hook, runtime object), so keeping one persona across codex/claude/opencode/hermes/pi means per-harness hacks with no undo | capa, ai-rules-sync, gentle-ai, magpie, system-prompts-and-models |
