# Agent VCS and workspace comparison — one branch, many agents

Scope: how several coding agents put changes onto a branch in one repository. Written
2026-10-31 to decide whether GitButler stays the version-control interface for
lenyas-apps or is replaced by a worktree-per-agent tool. Sources: `CATALOG.md` rows and
`evaluations/` verdicts, repository source and docs, GitHub API metadata fetched
2026-10-31, and the two public reviews cited per row. Star counts are as fetched; catalog
figures that disagree are noted because the disagreement is the finding.

## Shortlist

| Tool | Stars | License | Mechanism | Catalog verdict / Evidence |
|------|-------|---------|-----------|---------------------------|
| [gitbutler](https://github.com/gitbutlerapp/gitbutler) | 21,895 | Fair Source | One working tree; diffs assigned to virtual branches; ownership decided at commit time | CONDITIONAL / RUN (`evaluations/gitbutler.md`) |
| [git-ai](https://github.com/feder-cr/git-ai) | 1,030 | MIT (README; API reports NOASSERTION) | Server-centric VCS: sparse clones, compare-and-swap landing on one branch, changeset log | discovery-log / SOURCE-ONLY |
| [worktrunk](https://github.com/max-sixty/worktrunk) | 9,674 | MIT OR Apache-2.0 | One worktree + one real branch per task; `wt switch/list/merge`, hooks, CoW build caches | discovery-log / REVIEW |
| [claude-squad](https://github.com/smtg-ai/claude-squad) | 8,700 | AGPL-3.0 | tmux session + worktree per task, TUI over all sessions | CONDITIONAL / RUN |
| [h5i](https://github.com/h5i-dev/h5i) | 887 | Apache-2.0 | Sandboxed worktrees with prompt-aware commits (which prompt produced which change) | discovery-log / SOURCE-ONLY |
| [orca](https://github.com/stablyai/orca) | 111,636 | MIT | Desktop/mobile ADE; worktree per task, fan-out, native GitHub/Linear | discovery-log / REVIEW |

Not shortlisted: Nimbalyst/Crystal, agent-of-empires, diri, vibe-kanban (session managers;
branch policy stays yours; catalog SKIP or discovery-log), moire (15★) and succubus (17★)
(coordination overlays too immature), dmux, stargate, agentweaver, sigbound, buildd,
gastown (orchestration first), Sculptor (242★), uzi (582★), Terragon, Conductor
(uncatalogued, low stars or closed).

## Three architectures, one axis

The axis that decides the failure modes is *where ownership of a change lives*.

1. **Shared working tree, virtual lanes — GitButler.** Ownership lives in the operator's
   selection at commit time. Advantage: no second checkout, install, or build cache, which
   matters on a 3.8 GB host. Failure mode: the tool refuses changes it cannot trace to a
   lane ("depends on changes in another branch"), reports changes as unmodified when
   another lane holds them, and will happily commit files a human or agent did not mean to
   include — the docs-only commit that carried five application files onto main.
2. **Server-side landing onto one branch — git-ai.** Ownership lives in a per-agent token
   and a changeset log; concurrency is solved with compare-and-swap instead of a queue. It
   is the only design aimed at hundreds of agents at once. Blocker for this workflow:
   `doc/graft/LIMITATIONS.md` states it is not a hosting product — no web UI, no merge
   request review, no CI — so it replaces GitHub rather than sitting beside it. Version
   0.4.0, 1,030 stars after a peak above 2,000 in its first week (catalog row still reads
   2,370 from 2026-10-20), one open issue.
3. **Worktree plus one real branch per agent — worktrunk, claude-squad, h5i, orca.**
   Ownership lives in the filesystem: the branch *is* a directory. Cross-agent effects
   become ordinary merges a reviewer can see. Cost is a checkout and a dependency install
   per task; worktrunk softens that with copy-on-write build caches and per-worktree port
   templates, and is a single Rust binary.

## What this means for a memory-constrained box

The lightest option is not a new tool: it is the current one under discipline. Every
GitButler failure above is a consequence of concurrent uncommitted work in one tree, so
the mitigation is sequencing plus selection, not more software:

- one writing session per checkout at a time; commit before handing the workspace over
- always pass explicit change ids to `but commit`; never commit by path glob or by "all"
- treat "unmodified" as a query, not a fact — confirm against `but show <id>` / commits
- do moves of files whose sources live in another lane inside the lane that owns them, or
  after that lane lands

If serialization proves too slow, the next step is `worktrunk` (9,674★, single binary,
MIT/Apache) on one lane as a pilot, not `orca` (desktop app, 2 GB-class checkout state) or
`claude-squad` (tmux + TUI, AGPL). `git-ai` stays a watch item until it gains a review
surface.

## Evidence status

No arm of this comparison was measured on this repository. Tiers: claude-squad RUN
(installed, CLI surface exercised, TUI not drivable headless), gitbutler RUN (daily
production use, no protocol), worktrunk and orca REVIEW (docs/source read, not run),
git-ai and h5i SOURCE-ONLY. Promotion to a real verdict requires exercising the tool on
the lenyas-apps checkout and recording what happened.
