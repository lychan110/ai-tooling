# Routines: unattended cloud agents

A **routine** is a scheduled, unattended agent run against this repo on its own (the daily
discovery-and-triage pass is the canonical one). Routines are scheduled outside this repo —
nothing here creates them; a Hermes cron job is the supported shape, and any harness that
can check out the repo and run the gates works the same way. Their only in-repo lever is
this file: every routine checks out the repo and reads `AGENTS.md`, which points here.

This doc is the branch-and-merge contract. For what a routine may *conclude*, see the
eliminate-only rule in `AGENTS.md` and `NEXT-EVALS.md` — that is unchanged and
independent of anything below.

## The rule: a routine lands its own PR

**A routine merges its own PR into `main` once CI is green.** It does not park the PR
for human review.

The old posture — open a PR, then self-check-in every 30–60 minutes until a human
merges it — produced the exact failure it was meant to avoid. PR #291 (discovery
2026-07-31) sat open ~24h across roughly a dozen check-in cycles and merged at
2026-08-01T20:03Z; PR #293 (discovery 2026-08-01) was closed one minute later at
20:04Z. Two catalog PRs cannot coexist — they both rewrite `CATALOG.md`,
`COMPARISON.md`, `NEXT-EVALS.md` and `WATCHLIST.md` — so the second day's work was
discarded rather than merged. Landing each pass before the next one starts is what
keeps that from recurring.

Review still happens; it happens *after* the merge, on a small dated commit that is
trivial to revert, instead of *before* it, on a branch that rots while it waits.

## The three lanes

The daily pass is split across three scheduled jobs, because no single agent run has the
budget for all of it. Each lane owns one half and refuses the other's work on purpose; a
lane that starts doing another lane's job is how the queue goes quiet.

| Lane | Cadence | Owns | May conclude |
|------|---------|------|--------------|
| Discovery | Mon, Thu | Intake (new candidates), catalog entries, the drift issue, the **full** `--maintenance` refresh | eliminate-only |
| Triage | Tue, Wed, Fri, Sat | The `NEXT-EVALS.md` queue, one day's worth, cheap `--stale` refresh | eliminate-only |
| P0 eval | Weekly | One **measured** evaluation of the `P0 measure` head | anything, including ADOPT/KEEP |

**Intake is a search of the ecosystem, not a read of this repo.** `find-gaps.py` (detector F
plus a hardcoded checklist) and `triage.py` (which re-bands leads already in
`COMPARISON.md`) can only see tools this repo already knows about — run alone they return
`0 candidates` by construction, and a report built on them alone measures the intake, not
the ecosystem. The discovery lane's real source is a GitHub search over the topics the
catalog covers (`claude-code`, `claude-skills`, `agent-skills`, `mcp-server`, `ai-agents`),
sorted by stars and restricted to a recent creation window, with `/sync-stars`'s
starred-but-uncatalogued comparison as a best-effort complement. Issue #608 (2026-09-14) is
the last run that used it, and the 10-add batch it produced is what the catalog has been
living on since.

**The drift issue is the discovery lane's.** The scheduled `link-archive-sweep` workflow
files it (Mondays, `.github/workflows/link-archive-sweep.yml`) and then stops — it reports,
it does not repair. The discovery lane reads it, resolves the MOVED and GONE classes, and
comments the residue back so the next sweep and the next pass read current state. MOVED is a
single class decision: repoint every row to its `resolved_name`, or decline every row at
once. The slug keys `repo-metadata.json`, so a repoint writes the destination as a new key
and orphans the old one — that cost is why the class moves together or not at all.

**`P0 measure` is nobody else's band, and that is why it needs its own job.** `NEXT-EVALS.md`
reserves it for "a human or `eval-runner` only — the one band that may reach ADOPT", and both
other lanes are eliminate-only: they may write `SKIP` or leave a lead at `discovery-log`,
never a positive verdict. So the band cannot move from either of them, and without a third
lane it moves only when a human sits down to it. It is drawn from what the structural bands
did not claim, none of its rows is stamped, so `sort_key` never sinks them and the same 25
leads hold the same scores pass after pass. A triage pass reporting "structurally settled"
is reporting the queue's floor accurately and its ceiling not at all.

**One measured eval per P0 run, and the verdict must be propagated.** `eval-runner`'s own
scope is one eval per run — install, build an objective oracle, plant defects, run the A/B.
An eval alone changes nothing downstream: the row's `COMPARISON.md` cell must take the
headline (detector D), an ADOPT/KEEP must be run-backed or disclaimed (detector K) and must
appear in `STACK.md` or in `STACK-LEDGER.md` with a reason (detector J). Honesty beats
coverage: when the tool cannot be installed or no oracle exists here, the honest not-run
review lands with a `discovery-log` headline, and the row stays a lead.

## Sequence

1. **Start from fresh `main`.** `git fetch origin main && git checkout -b routine/<lane>-<YYYY-MM-DD> origin/main`.
   Branch name is `routine/<lane>-<date>` (e.g. `routine/discovery-2026-08-01`). Nothing
   keys on the prefix mechanically — it is a convention that makes the lane greppable in
   `gh pr list` and obvious in the log.

2. **Check the lane is clear first.** `gh pr list --state open --json number,headRefName`.
   If a PR from the same lane is still open, resolve it before opening a second one —
   land it if it is green, or close it if this run supersedes it. **Never leave two PRs
   from the same lane open at once.** This is the rule that would have saved #293.

3. **Do the work, then gate it.** `make fix && make check`.
   **Every red gate is a blocker.** There is no exception, including detector A.

   This step used to carve one out — *"a detector-A-only failure is not a blocker … note
   it in the PR body and continue"* — because the network install resolver reported
   *could not check* as `BROKEN`, so an unreachable sandbox failed the build. #448 ended
   that: only a 404 is `BROKEN` now, and an unreachable registry is `UNCHECKED`. With no
   network the detector reports its gap and exits 0, so `make check` is simply green:

   ```
   == A. install resolver — 52/85 target(s) checked ==
     UNCHECKED [pypi] markitdown  (STACK.md) — URLError
     UNCHECKED …and 23 more target(s)
     INCONCLUSIVE — 33 target(s) could not be checked; not a gate failure (no commit caused it)
   ```

   That block is a **disclosed gap, not a failure** — do not read `UNCHECKED` or
   `INCONCLUSIVE` as red, and do not re-add the exception on seeing them. What is left
   under `BROKEN` is a real 404, which is the one thing this detector exists to catch and
   which this lane is least able to notice: a discovery pass writes install commands into
   `CATALOG.md` and `evaluations/`, the files detector A reads. The old carve-out named a
   *detector* rather than a *cause*, so it excused that too.

   Expect it to be **slow** rather than fast when the network is unreachable —
   `TIMEOUT = 15` across 85 targets means tens of seconds. Slow is not hung.

4. **Open the PR, and close the scan issue with it.** Conventional-commit title, body
   stating what changed and the gate result, and a **`Closes #<scan-issue>`** line in the
   PR body so the merge closes the issue the pass was opened against.

   The keyword is the whole of it. GitHub closes an issue only on one of its
   [closing keywords](https://docs.github.com/articles/closing-issues-using-keywords) —
   `Closes`, `Fixes`, `Resolves` — and `Scan issue: #<n>` is **not** one of them. That was
   the live shape until #522: every pass wrote the reference, every PR merged green, and
   **13 scan issues from 2026-08-09 to 2026-08-23 sat open** while the work each described
   had landed the same day. Nothing was wrong with the passes; the word did not close.

   `discovery/README.md` had stated the intended lifecycle the whole time — a scan issue
   "is closed by the pull request that catalogs those findings" — and nothing coupled that
   sentence to this file, the one a routine actually reads. That is the two-copies-of-one-
   fact shape `AGENTS.md` names for the count extractors, in prose.

   A reference that does not close is worse than no reference: it reads as bookkeeping
   already handled, so nobody checks it. Put the keyword in the **PR body** — a commit
   trailer also works, but on a squash merge the subject is the part a routine controls
   least.

5. **Queue the merge.** `gh pr merge <n> --auto --squash --delete-branch`.
   `main` requires the `audit` check (`.github/workflows/integrity.yml`, which runs
   `make check`), so GitHub holds the merge until that check is green and then lands it.
   CI is the authority here, not the sandbox run. Prefer `--auto` over watching: the
   routine can exit instead of burning check-in cycles, and the wait is enforced
   server-side rather than by the agent's own judgment.

   Use `gh pr checks <n> --watch` only when the routine needs to *see* the result — for
   example to fix a red build in the same run.

6. **Reconcile with `main` if it moved.** Do not act on `mergeStateStatus` alone — a
   `main` that has moved flips it to `unknown` while GitHub lazily recomputes, which is
   not a conflict. Confirm with a trial merge:

   ```sh
   git merge-tree --write-tree origin/main origin/routine/<lane>-<date>
   ```

   On a real conflict: `git fetch origin main && git merge origin/main`, resolve,
   re-run `make fix && make check`, push. The queued auto-merge survives the push and
   re-waits on the new head.

7. **Confirm it landed** before ending the run — `gh pr view <n> --json state,mergedAt`.
   A queued auto-merge that never fires is a stuck lane, and step 2 of tomorrow's run
   will trip over it.

Protection on `main` is `enforce_admins: false`, so an admin token can still merge past
a red `audit`. That is deliberate — it keeps direct-to-main commits working for routines
that don't branch, and keeps the repo owner unblocked. It also means the required check
is a guardrail plus the mechanism that makes `--auto` wait, not an unbypassable gate for
an agent running with owner credentials. The do-not-merge list below is still binding.

## When a routine must NOT merge

Leave the PR open, comment on it with the reason, and notify. Do not merge if:

- **`make check` is red.** Any gate, no exceptions — see step 3 for why detector A no longer has one.
- **CI is red.** Check whether it reproduces on `main` first: if it does, say so once in
  the thread and wait for recovery — it is not this PR's fault. If it is the PR's, fix
  and push.
- **A conflict is not mechanically resolvable** — anything needing a judgment call about
  which side wins.
- **The diff reaches outside the lane's declared scope.** A discovery pass touches
  `CATALOG.md`, `COMPARISON.md`, `evaluations/`, `NEXT-EVALS.md`, `WATCHLIST.md`,
  `discovery/` and the derived `plugin/` mirrors. A change to `Makefile`, `audit-evals.py`,
  `STACK.md`, a detector, or CI is out of scope for an unattended pass and needs a human.
- **The pass wrote an `ADOPT`/`KEEP`/`CONDITIONAL` verdict.** Detector Q gates this
  mechanically; if it somehow passes, self-merge is still off. Auto-merge changes how a
  routine's work *lands*, not what it is allowed to *conclude*.

## Reverting

Every routine merge is one squashed, dated commit. `git revert <sha>` undoes a bad pass
cleanly — that reversibility is the premise the whole policy rests on. If a merged pass
turns out to be wrong, revert it and file an issue; do not hand-patch main.
