# Plan 019 — Harness-parity gaps: install-verb coverage and tiers vs dropped picks

**Run 6**, 2026-09-16 (audit at commit `ff6f7a0`). Source: the *known gaps and evidence
notes* comment on [PR #11](https://github.com/lychan110/ai-tooling/pull/11#issuecomment-5701208758).

## Goal

Close the five gaps that comment records — each one either gated by a test or a generator,
or documented as a decision — so the harness column PR #11 added stops being a surface no
detector can see.

## Current context / assumptions

Read-only recon on 2026-09-16 against branch `gitbutler/workspace` @ `ff6f7a0`. PR #11 is
**open, not merged** (head `f30a7c7`, branch `docs/stack-opencode-hermes-install`); its
changes are already in this working tree, so every task below can be built and verified
locally. Nothing here edits PR #11's files except STACK.md's hand-written prose.

Facts this plan relies on, each verified in the tree:

- `audit-evals.py:783` `extract_installs()` recognises exactly six forms: `pip install`
  and `npm install|i|add` (both multi-package), `cargo install`, `npx <pkg>`, and
  `claude plugin marketplace add <owner/repo>`. `hermes plugins install …`,
  `npx skills add …`, `brew install …` and `uv tool install git+…` are invisible to it.
- `uv run audit-evals.py --installs` today prints
  `== A. install resolver — 97/97 target(s) checked ==` and `OK — every install target resolves`.
  Detector A **gates** CI (`integrity.yml` → `make check` → `audit-evals.py --installs`).
- Detector AL (`audit-evals.py:4364-4459`, flag `--claude-verbs`) is the pattern to copy: a
  frozen verb snapshot, backtick-span extraction, `NEGATION` reuse, report-only.
- The verb snapshots are live, not guessed: `hermes --help`, `hermes mcp --help` and
  `hermes plugins --help` on **v0.21.3 (2026.9.14)** — the version PR #11 verified against.
  CI has **no `hermes` and no `brew` binary**, so no gate may depend on one.

### Testing convention this plan must obey

`AGENTS.md`: *"Tests are end-to-end and deliberately few: exercise the real artifact against
a throwaway target, then assert the result a user would see. No unit tests for internal
helpers, no smoke tests, and no assertions of the obvious (a file exists because the previous
line created it; a bad argument exits non-zero). The only test worth adding is one that would
fail if the behaviour regressed."*

So this plan adds **two** e2e cases — one class, `TestHarnessGapDetectors` — and **no** unit
tests: nothing for `extract_installs`, `stack_pick_harness` or `stack_tiers`, and no structural
page check. Each case runs the shipped script as a subprocess against a throwaway tree and
asserts the headline, the finding and the exit code. Existing tests are edited only where an
interface changes, as Task 3 does.

The pattern to copy is `TestInstallHarness` (`test_automation.py:3054-3090`): guard the temp
target, run the real script, then assert what it produced — including the closing comment
there about the cases a unit-minded author would add and it deliberately does not.

## Architecture / proposed approach

Grow the existing apparatus instead of adding a parallel one: detector A learns the four
install forms that have a **resolvable public artifact** (a GitHub repo, a Homebrew
formula); a new report-only detector **AM** checks `hermes <verb>` the way AL checks
`claude <verb>`; and `tier-stack.py` gains a third bucket for the picks the Harness column
marks `dropped`, reading that column through one new `catalog_lib` parser. Prose that code
cannot settle (the empty CI-review slot, the opencode-only picks) is recorded with its
evidence, never guessed.

### Task 0 — preflight (5 min, no code)

```bash
cd /home/lychan/projects/ai-tooling
git log --oneline -5
make check          # baseline: expect exit 0 and "A. install resolver — 97/97"
```

`git show` is denied on this host — use `git log -p -- <path>`, never `git show`.

Branch (GitButler workspace; never a worktree):

```bash
but branch new feat/harness-gap-detectors
```

If PR #11 has merged by the time you start, fetch/rebase first. If it has not, stack on it
and say so in the PR body (`Base: docs/stack-opencode-hermes-install`). **STOP** if
`make check` is red before you touch anything: report the pre-existing failure instead of
debugging it inside this plan.

### Task 1 — detector A: resolve `hermes plugins install`, `npx skills add`, `brew install`, `uv tool install`

**RED.** One e2e case, in a new class appended at the end of `test_automation.py` (the file
currently ends at ~line 9032). It runs the shipped script as a subprocess against a throwaway
tree and reads what a user reads — headline, findings, exit code — instead of calling
`extract_installs` directly. Two traps make the shape non-obvious, and both are handled below:

- `audit-evals.py` sets `ROOT = os.path.dirname(os.path.abspath(__file__))` and `main()`
  builds `DetectorContext(ROOT)`, so the throwaway tree only becomes the target if the script
  **and `catalog_lib.py`** are copied into it (the pattern this module's own docstring names);
- the fixture targets are deliberately non-existent, so a form the extractor still does not
  recognise shows up as a **missing BROKEN line and a smaller denominator**, never as a
  passing run — detector A's own rule, `0 findings` is not `0 examined`.

```python
class TestHarnessGapDetectors(unittest.TestCase):
    """The two behaviours this PR adds, through the real CLI against a throwaway tree.

    Needs `gh` on PATH and authenticated, and a working HTTPS client — the same requirement
    `make check`'s `audit-evals.py --installs` already carries.
    """

    def _run(self, d, argv, stack):
        _write(d, "STACK.md", stack)
        for script in ("audit-evals.py", "catalog_lib.py"):
            shutil.copy(os.path.join(ROOT, script), d)
        return subprocess.run([sys.executable, *argv], capture_output=True, text=True,
                              check=False, cwd=d)

    def test_the_new_install_forms_are_resolved_by_the_gate(self):
        """One fabricated target per new form: four unique targets, four findings, exit 1."""
        with tempfile.TemporaryDirectory() as d:
            # Guard the target before running anything (real-subprocess-e2e-testing).
            self.assertTrue(os.path.realpath(d).startswith(os.path.realpath(tempfile.gettempdir())))
            r = self._run(d, ["audit-evals.py", "--installs"],
                          "# Stack\n\n"
                          "`hermes plugins install owner/aitooling-nope-plugins`\n"
                          "`npx skills add owner/aitooling-nope-skills -g -y`\n"
                          "`brew install aitooling-nope-formula`\n"
                          '`uv tool install "git+https://github.com/owner/aitooling-nope-uv"`\n'
                          "`brew install --cask aitooling-nope-cask`\n"
                          "`brew install owner/aitooling-nope-tap/formula`\n"
                          "`brew install --cask --no-quarantine owner/aitooling-nope-casktap/cask`\n")
            self.assertIn("7/7 target(s) checked", r.stdout, msg=r.stdout + r.stderr)
            self.assertIn("BROKEN [brew] aitooling-nope-formula", r.stdout)
            self.assertIn("BROKEN [cask] aitooling-nope-cask", r.stdout)
            self.assertIn("BROKEN [tap] owner/aitooling-nope-tap/formula", r.stdout)
            self.assertIn("BROKEN [tap] owner/aitooling-nope-casktap/cask", r.stdout)
            self.assertIn("BROKEN [gh] owner/aitooling-nope-plugins", r.stdout)
            self.assertIn("BROKEN [gh] owner/aitooling-nope-skills", r.stdout)
            self.assertIn("BROKEN [gh] owner/aitooling-nope-uv", r.stdout)
            self.assertEqual(r.returncode, 1, msg=r.stdout)
```

Run it:

```bash
uv run -m unittest test_automation.TestHarnessGapDetectors -v
```

**Expect one failure**: the output reads `0/0 target(s) checked` with no BROKEN lines and
exit 0 — none of the four forms is extracted yet (they were invisible to the gate, which is
the whole gap).

**GREEN — the extractor** (`audit-evals.py`, inside `extract_installs`, ~lines 745-816).

1. Add a shared multi-form pattern beside `_NPM_INSTALL` / `_PIP_INSTALL` (~line 751), so
   brew reuses `_install_packages` — which already handles version pins, quotes,
   placeholders and multi-target tails:

```python
# `brew install a b c` installs three formulae and the single-token form would check only
# `a`. Homebrew's formula API is one HTTPS GET, so this needs no brew binary on the runner.
_BREW_INSTALL = re.compile(r"^brew +(?:install|reinstall) +(.*)$")
```

2. Add it to the multi list (~line 792):

```python
        multi = ((_PIP_INSTALL, "pypi"), (_NPM_INSTALL, "npm"), (_BREW_INSTALL, "brew"))
```

3. Add three single-form patterns to the list below it, **above** `cargo install`. Leave the
   loop's no-`break` shape alone and leave `skills` in `PLACEHOLDER`: the generic `npx`
   pattern still matches `npx skills add …`, yields the placeholder `skills`, and yields
   nothing — the new pattern is what yields the repo, so no command mints two targets.

```python
            # `hermes plugins install owner/repo` — the argument is a GitHub repo, exactly
            # like the claude marketplace form below; `plugins` is the declared verb.
            (r"hermes +plugins? +install +([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)", "gh"),
            # The skills CLI is the install unit for skills, and `skills` is in
            # PLACEHOLDER, so every `npx skills add owner/repo` in the corpus was invisible
            # to a gate whose headline read "every install target resolves".
            (r"npx +(?:-y +)?skills add +([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)(?:@[A-Za-z0-9._-]+)?", "gh"),
            # `uv tool install git+https://github.com/owner/repo[.git][@ref]` — anchored on
            # `$` so the non-greedy repo group cannot stop after a single character.
            (r"uv +tool +install +['\"]?git\+https://github\.com/([A-Za-z0-9._-]+/[A-Za-z0-9._-]+?)(?:\.git)?(?:@[A-Za-z0-9._-]+)?['\"]?\s*$", "gh"),
```

4. Add the Homebrew checker beside `crates_exists` (~line 730) and register it:

```python
def brew_formula_exists(pkg):
    return http_status(f"https://formulae.brew.sh/api/formula/{pkg}.json")
```

```python
    checkers = {"pypi": pypi_exists, "crates": crates_exists, "npm": npm_exists,
                "gh": gh_repo_exists, "brew": brew_formula_exists}
```

Verified 2026-09-16: `claude-squad` → 200, `nosuchformula-xyz` → 404 — so the formula API
splits OK/DEAD the way the other kinds do and a 429/5xx stays UNCHECKED.

5. Update detector A's section comment (line 732) and its `audit_installs` docstring to say
   which forms are resolvable and which are not: a **catalog name** (`hermes mcp install
   context7`) has no offline authority, so it is checked by detector AM's verb snapshot and
   never looked up as a package.

> **Correction at implementation (2026-09-16).** The single brew pattern above is incomplete.
> The census this plan asked for found one `--cask` line and three `owner/tap/name` lines in
> `evaluations/`, and the core formula API answers all four with 404 — four false `BROKEN`
> lines on four correct pages, gate exit 1. Shipped instead: three mutually exclusive brew
> patterns plus two kinds — `cask` (`https://formulae.brew.sh/api/cask/<pkg>.json`, verified
> 200 for `ping-island`) and `tap` (the target stays the page's `owner/tap/name` token and the
> checker delegates to the existing `gh_repo_exists("<owner>/homebrew-<tap>")`; all three tap
> repos were verified to exist). One command still yields exactly one target, and the real-tree
> population is unchanged at **128** — the fix reclassifies four existing targets and discovers
> nothing new. The e2e fixture below therefore carries three brew lines as well, which is where
> the one-target-per-command rule gets pinned.

**Verify (GREEN).**

```bash
uv run -m unittest test_automation.TestHarnessGapDetectors -v   # expect: OK, 0 failures
uv run audit-evals.py --installs
```

Expected: `== A. install resolver — 128/128 target(s) checked ==` — the value measured at
implementation, 31 new targets over the 97 baseline, every one reachable — then
`OK — every install target resolves`. If a `BROKEN` line appears, **STOP and report it**: a
real 404 means the page tells a reader to install something that does not exist. Do not
loosen a pattern to make it go away — a false 404 from the wrong registry is fixed by fixing
the registry (see the correction note above), never by widening the pattern back.

Commit: `feat(audit): resolve the hermes, skills-CLI, brew and uv-tool install forms`

### Task 2 — detector AM: `hermes <verb>` (report-only, offline)

**RED.** One more e2e case in the class Task 1 created — not a class of cases over
`audit_hermes_verbs`'s internals. The file's own precedents are `TestInstallHarness`
(`test_automation.py:3054-3090`: "run the real script, then follow the pointer it wrote") and
`test_check_flag_gates_and_bare_run` (~line 9015, which already shells out to a repo script
with `sys.executable`).

Add to `TestHarnessGapDetectors`:

```python
    def test_a_fabricated_hermes_verb_is_named_without_gating(self):
        """The user-visible contract of `--hermes-verbs`: the bad command is printed, the good
        one is not, and the flag never changes the exit code (report-only, exactly like AL)."""
        with tempfile.TemporaryDirectory() as d:
            # Guard the target before running anything (real-subprocess-e2e-testing).
            self.assertTrue(os.path.realpath(d).startswith(os.path.realpath(tempfile.gettempdir())))
            r = self._run(d, ["audit-evals.py", "--hermes-verbs"],
                          "# Stack\n\n"
                          "Run `hermes plugins install obra/superpowers` in your project.\n\n"
                          "Then `hermes plugin install obra/superpowers` does the same thing.\n\n"
                          "Per-harness views: `ccusage opencode daily`, `ccusage hermes daily`.\n")
            self.assertEqual(r.returncode, 0, msg=r.stdout + r.stderr)
            self.assertIn("— 1 of 2", r.stdout, msg=r.stdout)
            self.assertIn('"plugin" is not a `hermes` subcommand', r.stdout)
            self.assertNotIn('"plugins" is not a `hermes` subcommand', r.stdout)
            self.assertNotIn('"daily" is not a `hermes` subcommand', r.stdout)
```

Run it:

```bash
uv run -m unittest test_automation.TestHarnessGapDetectors -v
```

**Expect one failure** — this new case, on `returncode == 0`, with `unknown argument(s):
--hermes-verbs` on stderr (the flag does not exist yet). Task 1's case in the same class must
already be green at this point.

**GREEN — the detector.** Add a new section to `audit-evals.py` immediately after AL
(~line 4460):

```python
# ---------------------------------------------------------------- AM. hermes verb (report-only)
# `hermes mcp install <name>` and `hermes plugins install <owner>/<repo>` are the install
# forms STACK.md teaches since PR #11, and detector A checks an install's ARGUMENT and never
# its VERB — the defect AL documents for `claude` (#487). A *catalog name* has no offline
# authority at all (the Hermes catalog belongs to the CLI, and CI has no hermes binary:
# detector R's rule), so this detector checks the verb and leaves the name to the reader.
#
# Snapshot of `hermes --help`'s "Command to run" column plus `hermes mcp --help` and
# `hermes plugins --help`, taken 2026-09-16 on v0.21.3 (2026.9.14) — the version PR #11
# verified its commands against. Re-derive it by running those three commands and reading
# the left column.
HERMES_VERBS = frozenset({
    "acp", "approvals", "auth", "backup", "browser", "bundles", "chat", "checkpoints",
    "claw", "completion", "computer-use", "config", "console", "cron", "curator",
    "dashboard", "debug", "desktop", "doctor", "dump", "egress", "fallback", "gateway",
    "gui", "hooks", "import", "import-agent", "insights", "journey", "kanban", "learning",
    "logs", "login", "logout", "lsp", "mcp", "memory", "memory-graph", "migrate", "moa",
    "model", "monitoring", "pairing", "pause", "peer", "pets", "plugins", "portal",
```

```python
    "profile", "project", "prompt-size", "proxy", "resume", "secrets", "security", "send",
    "serve", "sessions", "setup", "skin", "skills", "slack", "status", "sync", "tools",
    "uninstall", "update", "vault", "verify", "webhook", "whatsapp", "whatsapp-cloud",
    "worktree",
})

# Same page list as AL: the pages a reader or an agent EXECUTES. AGENTS.md, audit-evals.py
# and test_automation.py all name fabricated verbs ON PURPOSE — documenting a defect is not
# committing it — and plugin/docs/ is a synced MIRROR of these same root files (#437's
# split), so walking it would double every finding.
HERMES_VERB_PAGES = ("STACK.md", "WORKFLOW.md", "CATALOG.md", "README.md", "PLAYBOOK.md")

# Anchored at the START of the backticked span, then `hermes` + whitespace. The span anchor
# is what keeps a tool NAMED hermes in argument position out: STACK.md's `ccusage hermes
# daily` is a per-harness view of ccusage and would otherwise donate the verb `daily`, while
# `caveman hermes` donates nothing only because no argument follows it. The `\s+` requirement
# plus the anchor also rule out `hermes-agent` (a hyphen, not whitespace) and `.hermes` (the
# config directory).
_HERMES_CMD = re.compile(r"^\s*hermes\s+(\S+)")

HermesVerbFinding = collections.namedtuple("HermesVerbFinding", "rel line verb command")
```

```python
def audit_hermes_verbs(ctx):
    """(findings, walked) — every backticked `hermes <word>` command whose word resolves to
    neither a declared subcommand nor a flag.

    Same three exclusions and the same NEGATION window as AL, for the same reason: a command
    framed as the WRONG one in surrounding prose is a correction note, not a claim to check.
    Extraction runs on `` `...` `` spans that START with `hermes` — prose describing the CLI
    ("the Hermes CLI") carries no verb, and a tool *named* hermes in argument position
    (`ccusage hermes daily`, a per-harness view of ccusage) is not a hermes subcommand.

    Nested forms are read at the TOP level (`hermes mcp install …` is the verb `mcp`,
    `hermes plugins install …` is `plugins`), which is what the one-word match gives: a
    sub-verb is never checked on its own, exactly as `claude auth login` never flags `login`.

    Report-only, AL's own call: the pages are mid-migration between harnesses, and the
    remedy for a live finding is a human's — guessing at a replacement is how a fix launders
    a wrong command into a plausible-looking one.
    """
    files = [*HERMES_VERB_PAGES,
             *sorted(glob.glob("evaluations/*.md", root_dir=ctx.root)),
             *sorted(glob.glob("discovery/*.md", root_dir=ctx.root))]
    findings, walked = [], 0
    for rel in files:
        if not os.path.exists(ctx.path(rel)):
            continue
        for i, line in enumerate(ctx.read(rel).splitlines(), 1):
            for m in re.finditer(r"`([^`]*)`", line):
                cmd = m.group(1)
                cm = _HERMES_CMD.search(cmd)
                if not cm:
                    continue
                word = cm.group(1)
                if word.startswith(("-", '"', "'")):
                    continue
                walked += 1
                if word.lower() in HERMES_VERBS:
                    continue
                window = line[max(0, m.start() - 70):m.end() + 60]
                if NEGATION.search(window):
                    continue
                findings.append(HermesVerbFinding(rel, i, word, cmd.strip()))
    return findings, walked
```

**Wiring** — four places in the same file:

1. `REPORT_FLAGS` (~line 4474): append `"--hermes-verbs"` to the tuple. It must **not**
   enter `OFFLINE_GATES` or `DEFAULT_GATES`, so it never touches the exit code.
2. `main()`'s flag block (~line 4546), directly under `do_claudeverb`:

```python
    do_hermesverb = "--hermes-verbs" in want  # opt-in report (does not affect exit code)
```

3. `main()`'s print block, immediately after AL's (~line 5226):

```python
    if do_hermesverb:
        hv = audit_hermes_verbs(ctx)
        print(f"== AM. hermes verb (report-only) — {len(hv[0])} of {hv[1]} "
              f"`hermes <word>` command(s) name an unrecognized subcommand ==")
        if not hv[1]:
            print("  no `hermes <word>` commands found — nothing to check")
        elif not hv[0]:
            print("  OK — every `hermes <word>` command names a declared subcommand or a flag")
        for f in hv[0]:
            print(f"  UNRECOGNIZED  {f.rel}:{f.line} — `{f.command}`: "
                  f"\"{f.verb}\" is not a `hermes` subcommand")
```

4. The module docstring's `Usage:` block (~line 570), beside the `--claude-verbs` entry:
   `uv run audit-evals.py --hermes-verbs  # hermes-verb report (offline, report-only)`.

**Verify.**

```bash
uv run -m unittest test_automation.TestHarnessGapDetectors -v   # expect: OK, 2 tests
uv run audit-evals.py --hermes-verbs
```

Expected: `== AM. hermes verb (report-only) — 0 of M `hermes <word>` command(s) name an
unrecognized subcommand ==` with **M = 7** on the current tree, then
`OK — every `hermes <word>` command names a declared subcommand or a flag`. The census this
plan first published (`M ≥ 8`, eight STACK.md lines) was **wrong**: extraction runs on
backticked spans only, and STACK.md's Quick Start block (lines 17, 28, 32) writes its three
`hermes …` commands as `#` comments inside a ```` ```bash ```` fence — no backticks, no spans.
The real population is the six span-initial commands in STACK.md (lines 5, 57, 58, 60, 81,
155) plus one in `evaluations/`.

> **Known coverage limit, deliberately out of scope.** Those three fenced Quick Start commands
> are outside AM's population, so a fabricated verb written there would go unreported.
> Extending extraction to ```` ```bash ```` fence bodies is a detector-design change (it would
> move AL's population too), so it is recorded here rather than smuggled into this task.

Two ways this run can be wrong, both diagnosable from its own output:

- **0 findings is required.** A finding naming `daily` means the span anchor is missing and
  `ccusage hermes daily` (STACK.md:119) is being read as a `hermes` command;
- **`M == 0`** means the page list or the regex is wrong.

Any other `UNRECOGNIZED` line: **STOP and report it**. Disposition is a human's call (that is
why AM is report-only), and deleting the command to silence the report is forbidden.

Commit: `feat(audit): add AM, the hermes-verb report detector`

### Task 3 — tier-stack.py: stop calling a `dropped` pick installable

Gap 3 of the comment. `Tier 1 — measured (29): install with confidence` currently lists all
seven picks the Harness column marks `dropped` — feature-dev, code-review, pr-review-toolkit,
security-guidance, claude-code-action, claude-reflect and skill-creator — so a count that
reads "install with confidence" covers seven things nobody can install. The population stays
30 (so `reconcile-counts.py`'s sentence and every number derived from it are untouched); only
the bucketing changes.

**RED.** No new test class: the invariant this change needs already exists and must be
widened, not duplicated. **Four** existing call sites in `test_automation.py` need edits — the
arity change from two return values to three breaks every unpacking, not only the one in
`TestTierStack` — and a unit case over hand-built rows is deliberately **not** added
(`AGENTS.md`: no unit tests for internal helpers; the only test worth adding is one that would
fail if the behaviour regressed).

1. `test_tiering_split_derived_from_evidence` (~line 4164) unpacks two values — make it three:

```python
        t1, t2, dropped = tier.stack_tiers(self.STACK, amap)
        self.assertEqual(t1, [("foo", "MEASURED")])           # MEASURED/RUN -> Tier 1
        self.assertEqual(t2, [("bar", "REVIEW"), ("baz", "SOURCE-ONLY")])  # rest -> Tier 2
        self.assertEqual(dropped, [])   # no Harness cell -> installable, never guessed
```

2. `test_live_tree_prose_count_equals_the_generated_tiers_block` (~line 4236) reads the real
   STACK.md; replace the two lines that collect `tiers` with:

```python
        tiers = [int(x) for x in re.findall(
            r"\*\*(?:Tier \d+ — [a-z-]+|Dropped — [^*]+?) \((\d+)\)", text)]
        self.assertEqual(len(tiers), 3, "STACK.md should render two tiers plus the dropped group")
        self.assertEqual(sum(tiers), n)
```

3. `TestStackCount.test_the_two_consumers_render_the_same_population` (~line 4256) unpacks the
   same two values; unpack three and keep summing every group, so the population assertion
   still holds.
4. `TestWorkflowDrift.test_every_consumer_reads_one_definition` (~line 5162) unpacks them too;
   unpack three and flatten `[*t1, *t2, *dropped]` so the one-definition claim survives.

Leave that test's `assertIn(f"The {n} tools worth installing", text)` line alone — it is the
reason the population must not shrink.

`uv run -m unittest test_automation.TestTierStack -v` → **expect two failures**: the live
invariant (`2 != 3`) and a `ValueError` from unpacking three values into two names. Both are
GREEN-step work below.

**GREEN.**

1. `catalog_lib.py` — one new parser directly after `distinct_stack_picks` (~line 607),
   reading the closed set the harness key declares:

```python
HARNESS_TOKENS = ("both", "opencode", "Hermes", "dropped")


def stack_pick_harness(stack_text):
    """{display text: harness token} for the rows `distinct_stack_picks` returns.

    The cell is found by TOKEN, never by position: the stage tables are five columns
    (… | Install | Harness | Signal) and the Conditional table is four (Tool | Install when
    | Install | Harness), so `cells[-2]` is right for one shape and wrong for the other. A
    row with no token is simply absent from the map — the caller reads that as "installs
    everywhere" rather than guessing a harness out of an Install cell.
    """
    out = {}
    for line in stack_text.splitlines():
        row = line.lstrip()
        if not row.startswith("|"):
            continue
        m = _STACK_PICK.match(row)
        if not m:
            continue
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        tok = next((c for c in reversed(cells) if c in HARNESS_TOKENS), None)
        if tok:
            out.setdefault(m.group(1), tok)
    return out
```

2. `tier-stack.py` — `stack_tiers` reads the map once and returns a third list. Update its
   docstring: it now returns `(tier1, tier2, dropped)`.

```python
    hmap = catalog_lib.stack_pick_harness(text)
    tier1, tier2, dropped = [], [], []
    for pick in catalog_lib.distinct_stack_picks(text):
        ev = catalog_lib.evidence_lookup(amap, pick.text, pick.url)
        if hmap.get(pick.text) == "dropped":
            dropped.append((pick.text, ev))
        else:
            (tier1 if ev in TIER1 else tier2).append((pick.text, ev))
    return tier1, tier2, dropped
```

3. `render(tier1, tier2, dropped)` — insert one line between the Tier 2 block and the
   closing marker, and update the function's docstring:

```python
        f"**Dropped — Claude Code only ({len(dropped)}): not installable on opencode or "
        "Hermes.** The Harness column above says why for each one; this block still reports "
        "how well validated it is.\n\n"
        f"{fmt(dropped)}\n"
```

`apply()` already calls `render(*stack_tiers(text, amap))`, so the third value flows through
untouched — no other call site needs an edit.

4. `STACK.md` line 5 — the harness key is hand-written and sits outside the markers. After
   "The Evidence tiers below answer *how well validated* a pick is, not *what runs on your
   harness* — the Harness column answers that." add:

   `Picks marked `dropped` are grouped separately at the end of that block.`

5. Regenerate, mirror, verify:

```bash
uv run tier-stack.py            # rewrites between the TIERS markers
./sync-plugin-docs.sh           # plugin/docs/ is generated — never hand-edit it
uv run -m unittest test_automation.TestTierStack -v     # expect: OK, 0 failures
uv run reconcile-counts.py --check                      # expect: stack picks = 30
```

Expected in STACK.md: `Tier 1 — measured (22)`, `Tier 2 — review-based (1)` and
`Dropped — Claude Code only (7)` — the three counts sum to 30, and the dropped count is the
same seven STACK.md's *What's NOT here* section already names.
`reconcile-counts.py --check` must still report **30 stack picks**: the population is
unchanged on purpose, only the bucketing is. If `sync-plugin-docs.sh --check` reports drift after the regen, commit the
mirror too.

Commit: `fix(tier-stack): separate dropped picks from the measured tiers`

### Task 4 — dropped: no table-shape test (the testing convention forbids it)

Gap 5 of the comment is a *verification*, not a defect: all 11 tables were checked
structurally by hand and every delimiter row matched its header. The obvious next move is a
test that pins it, and that test is the wrong one. `AGENTS.md` requires tests to "exercise the
real artifact against a throwaway target, then assert the result a user would see" and rules
out "assertions of the obvious". A delimiter-width check on a hand-edited page is exactly
that: nothing a user sees, and nothing that fails unless the page is already visibly broken —
`stack_pick_harness` stops resolving the moment a row loses a cell, and the tier block is
regenerated byte-exact by `tier-stack.py --check`.

Action: **none**. The hand verification stands as evidence in the PR body, and no test is
added.

### Task 5 — the empty CI-review slot (gap 2): record it, do not fill it

1. `STACK.md`, in the `## Ship` section after its table (~line 97):

```markdown
> **CI review on opencode or Hermes is an open slot.** `claude-code-action` is dropped
> above: it installs and runs Claude Code in CI, and no equivalent runner is documented for
> either harness this page supports. Nothing is guessed into the gap — a candidate has to be
> evaluated hands-on first (WORKFLOW.md's adoption rule), so the slot stays visibly empty
> rather than filled with a plausible-looking action nobody has run.
```

2. A `scan`-labelled tracking issue, per `AGENTS.md` (new scans are GitHub Issues). Create
   it with the GitHub MCP `issue_write` tool — **not** `gh`, which a `gh *` deny rule blocks
   for the agent on this host:
   - title: `Discovery: CI-review runner for opencode and Hermes (claude-code-action equivalent)`
   - labels: `scan`
   - body: the reason above, the two harnesses, and the bar — it must be run hands-on before
     it can touch STACK.md.

Then `./sync-plugin-docs.sh`, and commit:
`docs(stack): name the empty CI-review slot`.

### Task 6 — the two opencode-only picks (gap 4): check the evidence, not the claim

`STACK.md` marks `claude-mem` and `abtop` `opencode`, with the reason in the Install cell
("its installer covers …; Hermes is not one of its hosts"). That is a claim about a
third-party installer, and the evals should carry the census it rests on:

1. Read the installer's host list from its own source (`ctx_url_read` on the tool's
   README/installer, or `ctx_git_read` on the repo) and count the hosts.
2. If `evaluations/claude-mem.md` and `evaluations/abtop.md` do not already record that
   census, append one line to each eval's "How we tested it": the count, the hosts, and the
   date read — an honest SOURCE-ONLY note, not a re-evaluation.
3. **STOP** if the source cannot be fetched: leave the eval alone and say so. An
   unfetchable installer is not evidence that the claim is wrong.
4. `make check`, then commit:
   `docs(evals): record the host census behind the opencode-only picks`.

### Validation — after every task, and the full gate before the PR

```bash
make check          # ruff + mypy + 13 data gates + unittest + detector A + staleness
make fix            # apply-mode fixers, then re-runs check — the tree must end green
```

`make check` is exactly what CI runs (`integrity.yml` → `make check`), so a green local run
is the bar. PR #11's body records the baseline: **97/97** install targets and **748** unit
tests. The target count goes **up, 97 → 128**, and every new target must still resolve (that is the
point of Task 1); the suite grows by exactly **two** cases — the e2e pair in
`TestHarnessGapDetectors` — plus two edits to existing tests in Task 3. Nothing is added for an internal helper, and the structural page check a
first draft would add is deliberately dropped (Task 4).

## Risks, tradeoffs, and open questions

- **A false `BROKEN` now fails CI.** The four new forms turn previously unchecked lines into
  gating targets: a renamed repo or a removed formula goes red on a page that looks healthy.
  That is the intended behaviour (it is how `obra/superpowers` was caught), but the remedy is
  to fix the page — never to widen a pattern back.
- **`brew install --cask …` is a different registry — the census proved it, and the guard is in.**
  The plan's first cut resolved every brew token against the core formula API, which turned four
  correct pages into false `BROKEN` lines (`ping-island`, `humanlayer/humanlayer/codelayer`,
  `Kilo-Org/tap/kilo`, `esengine/reasonix/reasonix` — exit 1). Verified at implementation:
  `api/formula/ping-island.json` is 404 while `api/cask/ping-island.json` is 200, and the three
  `owner/tap/name` forms map to `owner/homebrew-<tap>` GitHub repos that all exist. The shipped
  fix is two extra kinds — `cask` (the cask API) and `tap` (the tap's GitHub repo, delegating to
  the existing `gh_repo_exists`) — with mutually exclusive patterns so one command still yields
  exactly one target. This is why the census line below mattered: the plan asserted no `--cask`
  line existed, and the corpus contained one plus three tap forms.
- **`stack_tiers`' arity changes from 2 to 3.** Its docstring claimed two tiers, `apply()`
  splats it, and **four** call sites unpack it — `TestTierStack`'s split test, the live-tree
  invariant, `TestStackCount`'s two-consumers test and `TestWorkflowDrift`'s one-definition
  test. All four are named in Task 3, and the module docstring documents the third group now.
  The alternative — filtering the population instead of bucketing it — would move the page's
  "30 tools" sentence through `reconcile-counts.py` and every count derived from it.
- **AM is report-only and stays that way until it is quiet**, following the `--overlaps`
  lifecycle: report first, gate once the findings are dispositioned. Do not add it to
  `DEFAULT_GATES` in this plan, and do not wire it into CI here.
- **Gap 3 may be a documented decision rather than a defect.** The harness key already says
  the two axes answer different questions. Task 3 keeps that reading intact and only stops
  the word "install" from covering a pick with no install path — if the key-only reading is
  preferred, drop Task 3 and leave the block untouched.
- **The two new e2e cases are the only tests in the suite that need the network.** They live
  in `make check`'s unit-suite step, which is otherwise offline: `gh` must be on PATH and
  authenticated and `formulae.brew.sh` reachable, or a case fails on its denominator
  (`3/3` instead of `4/4`) rather than on a defect. The remedy for that is a
  skip-when-unavailable guard, never a relaxed assertion — and the dependency is documented in
  the test class docstring, since `audit-evals.py --installs` already carries it four lines
  later in the same target.

## Open questions (answer before starting)

1. **Stack or wait on PR #11?** Its Harness column is what Tasks 3-5 read; it is open, not
   merged. Stacking keeps the work verifiable now; waiting keeps the PR diff small.
2. **One PR or three?** Tasks 1-2 (the two e2e cases and the detectors they gate), Task 3
   (the generated block plus the two edited tests), Tasks 5-6 (prose and evidence notes) touch
   different files but all of them edit STACK.md. Recommended: 1-2 first, then 3, then 5-6 —
   never two at once. Task 4 is a decision, not a commit.
3. **File the Task 5 issue now?** It is the only external write in this plan.
4. **Is the `dropped` bucket the wanted fix for gap 3**, or should the block keep listing
   every pick with the key sentence as the only explanation?
5. **Who dispositions AM's first findings**, and what makes it quiet enough to gate?

## Out of scope (YAGNI, deliberately)

- No snapshot of the Hermes MCP **catalog** names — the verb is checkable offline, the name
  is not, and a 60-entry snapshot would rot between Hermes releases.
- No parsing of the `opencode.json` JSON blocks: they are configuration, not commands, and
  have no artifact to resolve.
- No gating of `--hermes-verbs` in `make check` or CI (see the AM risk above).
- No re-derivation of the `claude` verb snapshot in AL, and no migration of AL's page list.

## Registration and shipping

1. `plans/README.md` — add a **Run 6 — harness-parity gaps, 2026-09-16 (audit at commit
   `ff6f7a0`)** paragraph beside Runs 1-5, and one row in the execution table:

```markdown
| [019](../docs/plans/019-harness-parity-gaps.md) | Check the install verbs and the dropped picks the harness column introduced | P1 | M | 11 | TODO |
```

2. Commit atomically, one task per commit — five commits, matching the `Commit:` lines above,
   plus the `plans/README.md` registry row.
3. Open the PR:

```bash
but pr new feat/harness-gap-detectors -m "feat(audit): gate the install verbs the harness column introduced"
```

   `-m` sets the **title** only. Set the body afterwards through the GitHub MCP
   `update_pull_request` tool — no heredocs, no backticks in the shell string — and state
   there which PR this stacks on, the before/after target count, and the tier counts.
4. The PR opens as ready, with `make check` green and every number from PR #11's body re-run
   and re-stated. The user merges; the agent never does.
