# Evaluation: GitButler

**Repo:** [gitbutlerapp/gitbutler](https://github.com/gitbutlerapp/gitbutler)
**Stars:** 21,895 | **Last updated:** 2026-10-31 (pushed) | **License:** Fair Source (source-available; becomes MIT after two years)
**Last verified:** 2026-10-31
**Dev loop stage:** Ship
**Layer:** Tooling

---

## What it does

A Git client — Rust/Tauri desktop GUI plus the `but` CLI — that replaces branch
switching with *virtual branches*. One working tree holds several applied branches at
once; every uncommitted change is assigned to one of them by file or hunk, and the
assignment is decided at commit time.

Mechanically: `but status` lists uncommitted changes with stable short ids; `but commit -b
<branch> <id>...` records exactly those ids as a commit on that branch; `but` keeps an
operations log so any operation can be undone, restacks stacked branches automatically,
and treats conflicts as first-class state rather than a blocked rebase. The GUI and the
CLI read and write the same workspace state, and agents are expected to drive the CLI.

## How we tested it

**Evidence:** RUN

Production use, not a benchmark. GitButler is the only version-control interface used
for the lenyas-apps monorepo (`~/projects/lenyas-apps`); agent sessions invoke the CLI
many times a day. The commands actually exercised include `but status`, `but diff`,
`but show <id>`, `but branch new --status-after <name>`, `but commit -b <branch> -m
"..." <ids...>`, `but land <branch> --yes`, and `but pr new`.

```bash
but status
but diff
but show <id>
but commit -b agent/<topic> -m "feat(scope): subject" <id> <id>   # ids are required to scope
but land agent/<topic> --yes                                       # fast-forward onto target
```

**What this is not.** No with/without arm, no wall-clock or token metric, no concurrent
agent benchmark. The failure observations below come from production sessions whose
results are on disk: the cross-lane refusal and the misattributed commit are recorded in
the workspace's own history and in the agent memory store (rows for the rename-dependency
refusal, the docs-only commit that carried application source, and the shared-workspace
revert). They are reported observations, not a protocol run.

## Test design

Not applicable — this eval is `RUN` without a measurement protocol. A MEASURED version
would serialize two agent sessions on one workspace and one worktree-based arm on the
same task set, counting misattributed commits and cross-lane refusals per arm.

## What worked

- **One working tree, no per-task setup cost.** Parallel tasks do not pay for a second
  `node_modules`, build cache, or dev-server port. On a 3.8 GB host this is the whole
  argument for the tool.
- **Commit surgery without `rebase -i`.** Uncommit, reword, amend, move, split, squash by
  change id; the operations log makes every one reversible.
- **Conflict handling that does not stop work.** A rebase always completes; commits can be
  marked conflicted and resolved later, in any order.
- **`but commit` with explicit ids is precise** when the operator selects the ids: the
  commit carries exactly the named changes.
- **Forge integration is enough to ship:** branch listing, PR creation and CI status from
  the CLI, no second tool.

## What didn't work or surprised us

- **Ownership is inferred at commit time, not held by the filesystem.** A rename whose
  source path was created by another lane's commit is refused — `Cannot commit: 4 changes
  could not be applied ... depends on changes in another branch` — and forcing it through
  the lane's bases fails with `Failed to merge bases while cherry picking ... was/were
  conflicted when merging`. Observed 2026-10-31 on a five-document move where four sources
  lived only in other lanes' commits.
- **A commit can carry content its subject does not describe.** `6a9548a2 docs(repo):
  consolidate planning docs into per-app thoughts trees` also changed five chimera web
  source files belonging to an in-flight lane, and main stopped compiling. Selecting
  changes by path/id is a manual step and a mis-selection is invisible in the subject.
- **Phantom "unmodified".** Wiring edits present in the tree were reported unmodified
  because another lane's commit already held them; the operator cannot tell "already
  committed elsewhere" from "never changed".
- **Workspace-global operations cross lanes.** Another session's edit-mode, unstack, or
  undo reverts uncommitted work in *every* lane, not just its own.
- **No runtime isolation, by design.** The project's own parallel-agent documentation
  states that parallel branches share one filesystem, dependency install, generated files,
  and app state; GitHub discussion #12228 raises the resulting races, and the Trigger.dev
  write-up quotes maintainers confirming that overlapping edits cause races and
  interference.

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | − | Cross-lane refusals and misattributed commit contents put the wrong change on a branch |
| Speed | + | No worktree creation or per-task install; branch context switches instantly |
| Maintainability | neutral | Organizes history; does not change code structure |
| Safety | − | One mutable workspace shared by all sessions; undo/edit operations affect every lane |
| Cost Efficiency | + | Single install and build state — decisive on a 3.8 GB host |
| Verifiability | + | Per-change ids and an operations log make every commit and conflict inspectable |

## Verdict

**CONDITIONAL — adopt-if: one writer at a time per checkout.** GitButler is the right
choice when parallel work must share one checkout (memory-constrained host, expensive
installs) and the tasks are serialized or touch disjoint paths. It is the wrong choice
when independent agents hold uncommitted work in the same tree: ownership is inferred at
commit time, so the failures are misattributed commits and cross-lane refusals, not merge
conflicts a reviewer would see.

The lighter mitigation is discipline — serialize lanes, commit before handing the
workspace to another session, and always pass explicit ids to `but commit` — rather than
adding a worktree manager whose per-worktree install cost this host cannot absorb.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with | Ships inside |
|------|------|-----------|-------------------|---------------|--------------|
| [gitbutler](https://github.com/gitbutlerapp/gitbutler) | tool | Git client (Rust/Tauri GUI + `but` CLI) keeping parallel work in one working tree by assigning file and hunk changes to virtual branches | Several tasks need branch-per-task organization in one checkout without a worktree and dependency install per task; virtual branches give that but infer change ownership at commit time | worktrunk, h5i, moire, weave |  |
