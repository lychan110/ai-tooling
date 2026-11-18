# Evaluation: stalemap

**Repo:** [Umair/stalemap](https://github.com/Umair/stalemap)
**Stars:** 109 | **Last updated:** 2026-11-01 (pushed) | **License:** MIT
**Last verified:** 2026-11-16
**Last triaged:** 2026-11-18  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Tooling

---

## What it does

A coding agent's idea of a library is frozen at its training cutoff, while the project's lockfile
points at something newer — so the agent writes `maxSteps` against AI SDK 7, `required_error`
against zod 4, or a `middleware.ts` against Next 16. stalemap closes that gap in three channels.
**Notes:** it diffs the pinned versions against the cutoff, ranks the changes, and writes a short
block between `<!-- stalemap:start -->` and `<!-- stalemap:end -->` in `AGENTS.md` or `CLAUDE.md`
(text outside the markers is never touched). **Edit-time guard:** a PostToolUse hook runs the
project's own type-check after each write and, when the code hits a changed API, returns the
compiler error together with the release-note or upgrade-guide passage that explains it.
**`search_changes`:** an MCP tool the agent can query in its own words. The package ships as
`npx stalemap` (npm `stalemap` 0.4.1, verified in the registry 2026-11-16), a Claude Code plugin
with SessionStart/PostToolUse hooks, and a GitHub Action for the same check in CI.

Scope is JavaScript and TypeScript projects only, and the README says so plainly. The author's
pre-registered benchmark (66 tasks drawn from changes released after June 2026) reports 89% of
sessions passing with stalemap against 68% with no help and 73% with a bare `tsc --noEmit` hook.
Those are the author's numbers; nothing here reproduces them.

## How we tested it

**Evidence:** SOURCE-ONLY

**Source-grounded review — not run hands-on.** We did not install the plugin, run the hooks, or
execute the benchmark. What was checked: GitHub repo metadata fetched 2026-11-16 (stars, licence,
push date), the README at HEAD, the repository file list (a real `src/`, `test/`, `bench/`,
`server.json`, `action.yml`, `.claude-plugin/`), and the npm registry entry for `stalemap`
(0.4.1, four published versions, last modified 2026-10-20). No run is claimed and the benchmark
figures above are the vendor's.

Two properties are worth naming because they decide the next step rather than the verdict. The
project is early and single-maintainer by its own statement, and its value depends on a moving
external input — the model's cutoff date and the release notes it can reach — so a stale or
unreachable notes source silently degrades it to a plain type-check hook.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at
`discovery-log` rather than SKIPped.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [stalemap](https://github.com/Umair/stalemap) | tool | npm CLI + MCP server + Claude Code plugin (MIT) that finds dependencies changed after the model's training cutoff and writes a ranked note block into AGENTS.md/CLAUDE.md, with an edit-time type-check guard | Coding agents code against APIs from their training cutoff while the project pins newer versions, so the fix is a compile-error round trip the agent cannot interpret | opensrc, reporails/cli |
