# Plan 017: Support Hermes Agent alongside opencode

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected result before moving on. If anything in
> "STOP conditions" occurs, stop and report — do not improvise. When done, add the
> plan 017 row to `plans/README.md` (T8).
>
> **Drift check (run first)**:
> `git diff --stat c4e28e9..HEAD -- AGENTS.md .agents .opencode opencode.json test_automation.py Makefile`
> Any change there means the excerpts below are stale — re-read the live tree first.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: MEDIUM
- **Depends on**: none — plan 016's stages S1–S4 are already landed (`531b3ff`,
  `945aa19`, `85d2b26`, `934fe19`, `7b4fefc`). The tree is opencode-only today.
- **Category**: refactor
- **Planned at**: commit `c4e28e9`, 2026-09-15

## Goal

Make `ai-tooling` a first-class project for **both** harnesses — opencode *and*
Hermes Agent — with one canonical home per artifact and one implementation per gate.

## Current context / assumptions

The repo is **documentation-only** (see `AGENTS.md`: "No build, test, or deploy
commands"). Everything below was verified at `c4e28e9`.

### The opencode harness surface today

| Artifact | Home | Notes |
|---|---|---|
| Instructions | `AGENTS.md` | opencode's preferred project file |
| Repo skills (4) | `.agents/skills/` | `add-catalog-entry`, `find-catalog-gaps`, `find-skills`, `triage-lead` |
| Specialized agent | `.opencode/agents/eval-runner.md` | `mode: subagent` + permission block |
| Hook — commit gate | `.opencode/plugins/commit-gate.ts` | `tool.execute.before` → runs `make check-data`, rewrites the command on failure |
| Hook — auto-sync | `.opencode/plugins/auto-sync.ts` | `tool.execute.after` → runs `./sync-plugin-docs.sh` |
| Commands | `opencode.json` → `command.{check,fix,sync}` | prompt templates, `agent: build` |
| Permissions | `opencode.json` → `permission` | incl. `skill.add-catalog-entry: ask` |

### What Hermes already gets for free (no work)

- **Instructions** — Hermes loads `AGENTS.md` as project context (git root → cwd, then
  progressively into subdirectories). Nothing to configure.
- **Repo skills** — Hermes discovers `<project-root>/.agents/skills/`, documented as
  "the cross-tool convention (shared with other agent CLIs)". Works **after** a
  one-time `hermes skills trust` per machine, because Hermes does not auto-load
  procedures from an arbitrary clone.

### What Hermes does NOT get (this plan's work)

| Need | Hermes mechanism | Where it goes |
|---|---|---|
| `/check` `/fix` `/sync` | every project skill is auto-exposed as `/<skill-name>` | `.agents/skills/{check,fix,sync}/SKILL.md` |
| `eval-runner` | same — a skill (Hermes has no repo-local agent-definition file) | `.agents/skills/eval-runner/SKILL.md` |
| Commit gate | plugin middleware `tool_request` (rewrites tool args before approval + execution) | `.hermes/plugins/<name>/__init__.py` |
| Auto-sync | plugin hook `post_tool_call` | same file |
| Per-project permissions | ❌ no repo-level equivalent — user-level `config.yaml` only | documented, not shipped |

Two Hermes constraints shape the design and belong in the docs, not in code:

1. **Project plugins are opt-in.** `.hermes/plugins/` is only scanned when
   `HERMES_ENABLE_PROJECT_PLUGINS=true`, and the plugin only *loads* when its name is
   in `plugins.enabled` in `~/.hermes/config.yaml`. So the Hermes commit gate is a
   gate a machine must opt into, unlike opencode's auto-loaded plugin.
2. **Middleware failures are fail-open** and `tool_request` runs *before* approval
   checks. Both are correct for this use (a broken adapter must never brick a commit),
   but they mean the adapter needs *executed* tests, not a source pin.

### Environment (verified on this machine)

- `hermes` → v0.21.3, `/home/lychan/.local/bin/hermes`. `make`, `gh`, `node` present.
- `ruff` and `mypy` are **not** on PATH; the repo's pinned copies are in `.venv/bin/`.
  Every `make check*` below therefore passes `RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy`.
- `bun` is **not** installed → the two opencode behavioural tests skip. The Hermes
  adapter's tests are Python and always run — which is why they must be behavioural.
- Version control here is a **GitButler workspace** (`git log` HEAD is
  `c4e28e9 GitButler Workspace Commit`). Commit with `but`, never `git commit`.

### Baseline (measured before this plan was written — reproduce it)

```
$ cd /home/lychan/projects/ai-tooling
$ make check-offline RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy
...
Ran 734 tests in 31.643s

OK (skipped=2)
$ echo $?
0
```

`skipped=2` is the two `@unittest.skipUnless(shutil.which("bun"))` opencode adapter
tests. The tree is green; any failure after your first edit is yours.

## Architecture / proposed approach

Nothing about the *gates* changes — `make check` stays canonical and every adapter
keeps calling the same scripts it calls. What is added is a second **adapter** layer:
one Python plugin under `.hermes/plugins/ai-tooling-harness/` registering a
`tool_request` middleware (the commit gate) and a `post_tool_call` hook (auto-sync),
plus four project skills under `.agents/skills/` that *both* harnesses read.
`opencode.json` and `.opencode/plugins/*.ts` are **not** deleted: they are the opencode
half, and the repo's rule is one implementation of the *gate*, not of the *trigger*.

## Deliverables

| # | Path | What |
|---|---|---|
| 1 | `.agents/skills/check/SKILL.md` | `/check` for both harnesses |
| 2 | `.agents/skills/fix/SKILL.md` | `/fix` |
| 3 | `.agents/skills/sync/SKILL.md` | `/sync` |
| 4 | `.agents/skills/eval-runner/SKILL.md` | the eval procedure, harness-neutral |
| 5 | `.opencode/agents/eval-runner.md` | reduced to a wrapper naming #4 |
| 6 | `.hermes/plugins/ai-tooling-harness/plugin.yaml` | manifest |
| 7 | `.hermes/plugins/ai-tooling-harness/__init__.py` | commit gate + auto-sync |
| 8 | `test_automation.py` | `TestHermesHarnessAdapter` + 4 pin updates |
| 9 | `AGENTS.md` | harness section → both harnesses (3 exact edits) |
| 10 | `docs/agents/hermes-harness.md` | operator steps (trust / enable / verify) |
| 11 | `plans/README.md` | the plan 017 row |

## TDD rules for every task

RED → run → GREEN → run → commit. Never write the implementation before the test
fails. `python3 -m unittest -q test_automation.<Class>` is the narrow loop; if a local
deny rule blocks `python3` — on the authoring machine `*python*` is a user-level deny rule,
so **assume it is blocked** — use `make check-offline RUFF=.venv/bin/ruff
MYPY=.venv/bin/mypy` instead (it runs the same suite, and takes ~32 s).

**A green unittest class is not a green task.** GREEN means
`make check-offline RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy` exits 0, ruff and mypy
included. The first implementation run of this plan produced two lint errors — `RUF012` on
a class-level dict and `B007` on an unused loop variable — that reached a "verified" state
because the narrow class passed and the full gate was never run. Run the gate for every
task, and paste its **real exit code**: a pipe through `tail` reports the pipe's status and
hides the failure, so do not pipe the gate.

## T0 — Baseline (no commit, no edits)

```bash
cd /home/lychan/projects/ai-tooling
make check-offline RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy; echo "exit=$?"
```

Expected: `OK (skipped=2)` and `exit=0`. If it is not green, **STOP** — you are not
starting from the baseline this plan was written against.

Start the branch (GitButler workspace — do not create a worktree):

```bash
cd /home/lychan/projects/ai-tooling
but branch new --status-after feat/hermes-harness-support
```

## T1 — `/check` `/fix` `/sync` as project skills (both harnesses)

**Why**: opencode's copies live in `opencode.json` as prompt templates; Hermes has no
repo-level command file. A project skill is the one home both harnesses read.

### T1.1 RED — add the failing test

Open `test_automation.py`. Insert this block **immediately before** the line
`# ----------------------------------------------------------------- detector I (evidence field, #62)`
(line 2791 at `c4e28e9`), so it lands next to the other harness seams:

```python
# ----------------------------------------------------------------- harness skill surface
class TestHarnessSkillSurface(unittest.TestCase):
    """The harness-neutral half of the harness layer.

    `/check`, `/fix` and `/sync` are `opencode.json` prompt templates for opencode.
    Hermes exposes every project skill as `/<skill-name>` and reads the same
    `.agents/skills/` directory, so the three procedures live there once and both
    harnesses get the command. These tests pin that each skill still names the REAL
    command, so it cannot rot into a description of a gate that no longer exists.
    """

    COMMANDS = {
        "check": "make check",
        "fix": "make fix",
        "sync": "./sync-plugin-docs.sh",
    }

    def test_each_command_skill_exists_and_names_its_command(self):
        for name, command in self.COMMANDS.items():
            path = Path(ROOT, ".agents", "skills", name, "SKILL.md")
            self.assertTrue(path.is_file(), msg=f"missing {path}")
            text = path.read_text(encoding="utf-8")
            self.assertIn(command, text, msg=f"{name}/SKILL.md does not name `{command}`")

    def test_each_named_make_target_exists(self):
        # A skill describing a target the Makefile dropped would send the agent to a
        # command that fails for a reason no commit caused.
        body = Path(ROOT, "Makefile").read_text(encoding="utf-8")
        for name, command in self.COMMANDS.items():
            if not command.startswith("make "):
                continue
            target = command.split()[1]
            self.assertIn(f"\n{target}:", body, msg=f"Makefile has no `{target}:` target")
```

`shutil`/`os` are already imported by the file; `Path` and `unittest` are too.

### T1.2 RED — watch it fail

```bash
cd /home/lychan/projects/ai-tooling
python3 -m unittest -q test_automation.TestHarnessSkillSurface
```

Expected:
```
ERROR: test_each_command_skill_exists_and_names_its_command
AssertionError: missing .../.agents/skills/check/SKILL.md
```
plus `FAILED (failures=1)`. Two tests, at least one failing — good. (The Makefile test
passes already; that is the point: it constrains the *implementation*, not the RED.)

### T1.3 GREEN — create the three skills

Create `.agents/skills/check/SKILL.md`:

```markdown
---
name: check
description: Run the repo's canonical integrity gate (make check) exactly as CI does, and report the result. Use before review, commit, or push. Triggers - "/check", "run the gates", "is the tree green".
---

# Check

Run the repo's canonical integrity gate exactly as CI does:

    make check

If `ruff`/`mypy` are not on PATH, point the Makefile at the pinned copies:

    make check RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy

Report the result. If it fails, do NOT commit or push — read the diagnostic, fix the
underlying issue, and re-run until it exits clean. This is the same set
`.github/workflows/integrity.yml` enforces, so `make check` staying green means local
and CI agree.

`make check` hits the network (detector A's install resolver) and needs `gh` auth.
`make check-offline` is the same set minus that one gate — use it to iterate.
An `UNCHECKED`/`INCONCLUSIVE` line from detector A is a disclosed gap, not a failure.
```

Create `.agents/skills/fix/SKILL.md`:

```markdown
---
name: fix
description: Apply the repo's offline fixers then re-verify (make fix). Use when make check reports drift that has an apply-mode fixer. Triggers - "/fix", "fix the drift", "make the tree green".
---

# Fix

Run the repo's apply-mode fixers, then re-verify:

    make fix

A clean exit means the tree is actually green — the recipe ends by re-running
`make check`. Report which fixers applied and the final `make check` status.

Never hand-edit a derived page or a count: `make fix` is the canonical repair half.
```

Create `.agents/skills/sync/SKILL.md`:

```markdown
---
name: sync
description: Re-sync plugin/docs/ from the authoritative root docs (./sync-plugin-docs.sh). Use after editing CATALOG.md/WORKFLOW.md/STACK.md/PLAYBOOK.md or anything under evaluations/, discovery/, methodologies/.
---

# Sync

Re-sync the derived `plugin/docs/` copy from the authoritative root docs:

    ./sync-plugin-docs.sh

Then confirm no drift remains:

    ./sync-plugin-docs.sh --check

Expected on success: `sync check: OK — plugin/docs/ and skills/ are in sync with root`.

Root docs are authoritative; `plugin/docs/` is a synced copy — never edit it directly.
The syncable set is defined once, in the script's `WATCHED_*` arrays (ADR-0001's
allowlist is deliberate, so a new root doc is not auto-watched).
```

### T1.4 GREEN — watch it pass

```bash
cd /home/lychan/projects/ai-tooling
python3 -m unittest -q test_automation.TestHarnessSkillSurface
```

Expected: `Ran 2 tests` / `OK`.

Do **not** restate the `make fix` fixer chain (`ruff --fix` → … → `sync-plugin-docs`)
in any new doc. `TestIntegrityMakefile._prose_chain` scans `CHAIN_PROSE =
("AGENTS.md", "opencode.json")` for the anchor `apply-mode fixers in dependency order`;
a third copy of the chain elsewhere is unchecked drift. Point at the existing text.

### T1.4b — pin the opencode command templates to the new skills

`/check` `/fix` `/sync` are now defined in **two harness homes**: the `command` block of
`opencode.json` (`template` + `agent`, ~line 32 onward) and the project skills this task
just created. One fact, two definitions, coupled by nothing is this repo's #443/#469
defect shape, and it would have shipped here silently.

`opencode.json` **keeps** its templates: they carry `agent` and permission semantics a
skill cannot express, and rewriting a working harness's command shape is not this plan's
job. What this plan does is **gate the shared fact** — the way `plugin/README.md`'s rule
gates the facts it restates from root instead of freezing the file. Add to
`TestHarnessSkillSurface`:

```python
    def test_opencode_commands_and_the_skills_agree_on_the_command(self):
        # The procedure lives in the skill; opencode.json keeps only the wrapper. What
        # must not drift is the command each one names — one gate, named once.
        expected = self.COMMANDS  # one mapping — test 1 owns it, this test reuses it
        config = json.loads(Path(ROOT, "opencode.json").read_text(encoding="utf-8"))
        for name, command in expected.items():
            self.assertIn(command, config["command"][name]["template"],
                          msg=f"opencode.json's /{name} no longer runs `{command}`")
            skill = Path(ROOT, ".agents", "skills", name, "SKILL.md")
            self.assertIn(command, skill.read_text(encoding="utf-8"),
                          msg=f".agents/skills/{name} no longer runs `{command}`")
```

If `json` is not already imported at the top of `test_automation.py`, add it to the stdlib
import block (alphabetical, as ruff's `I` rules want it).

Verify:

```bash
cd /home/lychan/projects/ai-tooling
python3 -m unittest -q test_automation.TestHarnessSkillSurface
```

Expected: green immediately. It is a pin, not a RED step: both sides already exist, and
what it buys is that the next person to edit one of them finds out.

Then sanity-check that a template really does still carry the command (guards against a
pin that passes on an empty match):

```bash
cd /home/lychan/projects/ai-tooling
python3 -m json.tool opencode.json | grep -A1 '"check"'
```

Expected: the `/check` description line, i.e. the entry is present and non-empty — not a
bare `"check": {}`.

### T1.5 Commit

```bash
cd /home/lychan/projects/ai-tooling
but commit -b feat/hermes-harness-support -m "feat(skills): expose /check /fix /sync as project skills for both harnesses"
```

## T2 — `eval-runner` gets one home

**Why**: the P0 lane's procedure lives only in `.opencode/agents/eval-runner.md`, which
no other harness can read. The procedure moves to a project skill; the opencode file
becomes the thin subagent wrapper `mode: subagent` requires.

### T2.1 RED — add the single-home pin

Append these two methods to `TestHarnessSkillSurface` (inside the class body, after
`test_each_named_make_target_exists`):

```python
    def test_eval_runner_procedure_has_exactly_one_home(self):
        # The procedure used to live only in `.opencode/agents/eval-runner.md`. It lives
        # in the project skill now; the opencode agent is a wrapper that names it. Pinned
        # in both directions: the skill must keep the load-bearing steps, and the wrapper
        # must not grow a second copy of them.
        skill = Path(ROOT, ".agents", "skills", "eval-runner", "SKILL.md")
        self.assertTrue(skill.is_file(), msg=f"missing {skill}")
        text = skill.read_text(encoding="utf-8")
        for step in ("objective oracle", "A/B", "How we tested it",
                     "audit-evals.py --fabrication"):
            self.assertIn(step, text, msg=f"eval-runner skill lost the `{step}` step")

        agent = Path(ROOT, ".opencode", "agents", "eval-runner.md").read_text(encoding="utf-8")
        self.assertIn(".agents/skills/eval-runner/SKILL.md", agent,
                      msg="the opencode agent must point at the skill")
        self.assertNotIn("How we tested it", agent,
                         msg="the opencode agent has grown a second copy of the procedure")

    def test_eval_runner_is_still_removable_from_the_subagent_registry(self):
        # `mode: subagent` and the permission block are opencode's agent-file shape;
        # dropping them silently demotes the runner to a normal agent.
        agent = Path(ROOT, ".opencode", "agents", "eval-runner.md").read_text(encoding="utf-8")
        head = agent.split("---")[1]
        self.assertRegex(head, r"(?m)^mode:\s*subagent\s*$")
        self.assertRegex(head, r"(?m)^name:\s*eval-runner\s*$")
```

### T2.2 RED — watch it fail

```bash
cd /home/lychan/projects/ai-tooling
python3 -m unittest -q test_automation.TestHarnessSkillSurface
```

Expected: `FAILED` with `AssertionError: missing .../.agents/skills/eval-runner/SKILL.md`
(the T1 tests still pass).

> Rename that second test to `test_eval_runner_keeps_the_opencode_subagent_shape` —
> the name should say what it asserts.

### T2.3 GREEN — the skill, then the wrapper

Create `.agents/skills/eval-runner/SKILL.md`:

```markdown
---
name: eval-runner
description: Run ONE hands-on, MEASURED evaluation of a tool or skill and write it to evaluations/<name>.md following TEMPLATE.md. Use to graduate a review-based ADOPT skill eval to measured, or for a fresh evidence-based eval. One eval per run.
---

# Eval Runner

You produce ONE evidence-based evaluation for the tool/skill you are given, written to
`evaluations/<name>.md` following `evaluations/TEMPLATE.md` exactly. The bar is a
**measured** eval, not a README review. Honesty beats coverage: a disclosed not-run
review is acceptable; a fabricated run is not.

## The measured-eval pattern (what "measured" means here)

A measured eval rests on an **objective oracle** independent of your own judgement,
plus a **with-skill-vs-baseline or planted-defect A/B**. Proven examples in this repo:

- `web-quality-skills` — planted 8 defects in an HTML file; ran `html-validate` (a real
  a11y linter) as the oracle; showed it caught the basic ones but 0/4 WCAG 2.2 criteria
  the skill's checklist covers. The delta IS the skill's value.
- `resolving-merge-conflicts` — built a repo where a textually-clean merge is
  semantically broken; `node test.js` is the oracle; baseline ships 1/2 passing,
  with-skill reaches 2/2.

Find an external oracle for your target (a linter, type-checker, test runner, token
counter, schema validator). If none exists in this environment and you cannot install
one, say so and write an HONEST not-run review instead — do not invent a run.

## Steps

1. **Install / obtain the tool** (pip/npm/npx/gh).
   If it can't be installed here, record that plainly, and do not invent results.
2. **Design the A/B** around an objective oracle. Construct a minimal artifact
   (planted-defect file, broken merge, sample prompt) the oracle can score.
3. **Run baseline vs with-skill/with-tool**; capture real, reproducible output.
4. **Write `evaluations/<name>.md`** from `TEMPLATE.md`. The "How we tested it" section
   is mandatory and must either show the real run (commands + results) or disclose it
   was not run. Include a quality-signals table and a Verdict.
5. **Add the catalog row** (the table at the bottom of the template) and, if adding the
   tool to the catalog, defer the propagation to `/add-catalog-entry`.

## Self-check before finishing (must pass)

- `python3 audit-evals.py --fabrication` — your eval must NOT be flagged (no run-claim
  without an honesty disclaimer or a genuine verified run).
- If the target is an ADOPT *skill*, `python3 audit-evals.py --skills` should list it as
  MEASURED (detector E). Avoid HONEST-vocabulary words like "inspected" / "read" /
  "examined" in the How-we-tested section unless the eval really is a disclosed not-run
  review — those words flip the classifier to backlog.
- Return the eval path and a one-line verdict; do not edit COMPARISON/counts (that is
  `/add-catalog-entry`'s job).

## Scope

Evaluate dev-loop tooling only. Be specific and reproducible; vague "it works well"
prose is not evidence. One eval per run.
```

Then **replace the whole body** of `.opencode/agents/eval-runner.md` (everything after
the closing `---` of its frontmatter) with the pointer below, leaving the frontmatter
byte-for-byte as it is (`name`, `description`, `mode: subagent`, and the six
`permission:` keys):

```markdown
# Eval Runner

Read `.agents/skills/eval-runner/SKILL.md` and follow it exactly. That file is the
single home of this procedure, shared with every other harness — do not restate it
here, and do not edit it from this agent.

One eval per run; several runs can go in parallel.
```

### T2.4 GREEN — watch it pass

```bash
cd /home/lychan/projects/ai-tooling
python3 -m unittest -q test_automation.TestHarnessSkillSurface
```

Expected: `Ran 4 tests` / `OK`.

If the run fails with `AssertionError: the opencode agent has grown a second copy of the
procedure`, you left the old body in place; the wrapper must contain no "How we tested
it" text.

### T2.5 Commit

```bash
cd /home/lychan/projects/ai-tooling
but commit -b feat/hermes-harness-support -m "refactor(harness): move the eval-runner procedure to a project skill both harnesses read"
```

## T3 — the Hermes harness plugin: manifest + auto-sync half

**Why**: Hermes needs a counterpart for `.opencode/plugins/*.ts`. A project-local plugin
at `.hermes/plugins/ai-tooling-harness/` registers one `tool_request` middleware (used
in T4) and one `post_tool_call` hook. This task builds the manifest, the register
function, and the auto-sync half; T4 adds the gate.

### T3.1 RED — add the adapter test class

Insert this block **immediately before** the same
`# ----------------------------------------------------------------- detector I (evidence field, #62)`
line (it will sit directly after `TestHarnessSkillSurface`):

```python
# ----------------------------------------------------------------- Hermes harness adapter
class TestHermesHarnessAdapter(unittest.TestCase):
    """Pins the Hermes half of the harness layer.

    The opencode adapters are TypeScript: they are source-pinned here and executed only
    when `bun` happens to be installed. This adapter is Python in the same suite, so it
    is imported and executed against fixtures — the stronger pin, and the only one that
    can catch a fail-open bug in a plugin whose failures are silent by contract.
    """

    REL = os.path.join(".hermes", "plugins", "ai-tooling-harness", "__init__.py")

    def setUp(self):
        # _load() execs a fresh module per call and never registers it in sys.modules,
        # so mutating REPO below cannot leak between tests.
        self.mod = _load("ai_tooling_harness", self.REL)

    def _registered(self):
        """Run register() against a stub ctx and return {kind_or_hook_name: callback}."""
        seen = {}

        class Ctx:
            @staticmethod
            def register_middleware(kind, callback):
                seen[kind] = callback

            @staticmethod
            def register_hook(name, callback):
                seen[name] = callback

        self.mod.register(Ctx())
        return seen

    def _repo(self, watch=(), makefile=None, audit_exit=1):
        """A throwaway repo the adapter can run against. REPO is module-level on purpose
        — that is the seam these tests use."""
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        _write(d, "Makefile", makefile if makefile is not None
               else "check-data:\n\tpython3 audit-evals.py --offline\n")
        _write(d, "audit-evals.py",
               "import sys; sys.stderr.write('detector X: fail\\n'); "
               f"sys.exit({audit_exit})\n")
        _write(d, "sync-plugin-docs.sh",
               "#!/usr/bin/env bash\n"
               "set -euo pipefail\n"
               'if [ "${1:-}" = "--list-watched" ]; then\n'
               "  printf '%s\\n' " + " ".join(f"'{line}'" for line in watch) + "\n"
               "  exit 0\n"
               "fi\n"
               'echo ran >> "$(dirname "$0")/synced.log"\n'
               "exit 0\n")
        # The adapter calls it as `./sync-plugin-docs.sh`, as the Makefile does.
        os.chmod(os.path.join(d, "sync-plugin-docs.sh"), 0o755)
        self.mod.REPO = Path(d)
        return d

    def test_registers_the_commit_gate_and_the_auto_sync_half(self):
        seen = self._registered()
        self.assertIn("tool_request", seen, msg="no commit-gate middleware registered")
        self.assertIn("post_tool_call", seen, msg="no auto-sync hook registered")

    def test_the_commit_predicate_matches_the_opencode_adapter(self):
        # One predicate, two adapters. A cross-language literal share is not practical,
        # so this pin IS the single definition (TestHookTriggerSeam's rule).
        self.assertEqual(self.mod.COMMIT_PREDICATE, TestHookTriggerSeam.PREDICATE)
        self.assertFalse(re.search(r"[\\^$*+?()\[\]{}|]", self.mod.COMMIT_PREDICATE),
                         msg="metacharacters would diverge from the substring match")

    def test_the_plugin_resolves_the_repo_root_from_its_own_path(self):
        # `parents[3]` is load-bearing: <repo>/.hermes/plugins/<name>/__init__.py.
        # A shallower home would point every gate at the wrong tree, silently.
        self.assertEqual(self.mod.REPO, Path(ROOT))
```

Append these methods to the same class (after `test_the_plugin_resolves_the_repo_root_from_its_own_path`):

```python
    def _hook(self, **kwargs):
        self._repo(**kwargs)
        return self._registered()["post_tool_call"]

    def test_auto_sync_triggers_on_a_watched_root_doc(self):
        hook = self._hook(watch=("CATALOG.md", "evaluations/"))
        hook(tool_name="write_file", args={"path": "CATALOG.md"})
        self.assertTrue(os.path.exists(os.path.join(self.mod.REPO, "synced.log")),
                        msg="an edit to a watched root doc must re-sync plugin/docs/")

    def test_auto_sync_triggers_on_a_file_inside_a_watched_directory(self):
        hook = self._hook(watch=("CATALOG.md", "evaluations/"))
        hook(tool_name="patch", args={"path": "evaluations/aider.md"})
        self.assertTrue(os.path.exists(os.path.join(self.mod.REPO, "synced.log")))

    def test_auto_sync_skips_an_unwatched_path(self):
        hook = self._hook(watch=("CATALOG.md",))
        hook(tool_name="write_file", args={"path": "plans/017-hermes-harness-support.md"})
        self.assertFalse(os.path.exists(os.path.join(self.mod.REPO, "synced.log")),
                         msg="only the syncable set may trigger a sync")

    def test_auto_sync_skips_the_derived_copy_so_it_cannot_loop(self):
        hook = self._hook(watch=("CATALOG.md",))
        hook(tool_name="write_file", args={"path": "plugin/docs/CATALOG.md"})
        self.assertFalse(os.path.exists(os.path.join(self.mod.REPO, "synced.log")))

    def test_auto_sync_ignores_a_non_write_tool(self):
        hook = self._hook(watch=("CATALOG.md",))
        hook(tool_name="read_file", args={"path": "CATALOG.md"})
        self.assertFalse(os.path.exists(os.path.join(self.mod.REPO, "synced.log")))

    def test_auto_sync_fails_open_when_the_watch_set_cannot_be_read(self):
        # "could not run" is not "failed": a repo whose script is broken must not break
        # the session, and must not be read as a watch-everything.
        d = self._repo(watch=("CATALOG.md",))
        os.remove(os.path.join(d, "sync-plugin-docs.sh"))
        hook = self._registered()["post_tool_call"]
        hook(tool_name="write_file", args={"path": "CATALOG.md"})
        self.assertFalse(os.path.exists(os.path.join(d, "synced.log")))

    def test_both_hooks_accept_the_documented_payload(self):
        # The REAL contract, verbatim from the Hermes docs. Hermes calls plugin hooks by
        # KEYWORD from a fixed payload (`post_tool_call`: tool_name, args, result,
        # task_id, session_id, tool_call_id, turn_id, api_request_id, duration_ms,
        # status, error_type, error_message, middleware_trace) and tells plugins to
        # accept **kwargs. A hook naming its second parameter `params` instead of `args`
        # gets None and never fires — while a test passing its own `params=` stays
        # green. So this test passes what Hermes passes, and nothing of its own.
        hook = self._hook(watch=("CATALOG.md",))
        hook(tool_name="write_file", args={"path": "CATALOG.md"}, result="ok",
             task_id="t1", session_id="s1", tool_call_id="c1", turn_id="u1",
             api_request_id="a1", duration_ms=12, status="ok", error_type="",
             error_message="", middleware_trace=[],
             telemetry_schema_version="hermes.observer.v1")
        self.assertTrue(os.path.exists(os.path.join(self.mod.REPO, "synced.log")),
                        msg="the auto-sync hook did not fire on the documented payload")
        # `tool_request` middleware payload: tool_name, args, original_args.
        self.assertIsNone(self._registered()["tool_request"](
            tool_name="terminal", args={"command": "ls"}, original_args={"command": "ls"},
            middleware_schema_version="hermes.middleware.v1", session_id="s1"),
            msg="a non-commit must pass through the documented payload unchanged")

    # The "derives its trigger set from --list-watched" pin for THIS adapter lives in
    # TestWatchListSeam.test_adapter_derives_from_list_watched (T4.4), which loops over
    # every adapter: two copies of one assertion is the drift shape this repo fights.
```

### T3.2 RED — watch it fail

```bash
cd /home/lychan/projects/ai-tooling
python3 -m unittest -q test_automation.TestHermesHarnessAdapter
```

Expected: `ERROR` on every test in the class — `FileNotFoundError` from `_load` (the
plugin does not exist yet), so `FAILED (errors=N)` with `N` equal to the whole class.

> **Sequencing note**: `test_registers_the_commit_gate_and_the_auto_sync_half` cannot
> pass until T4 lands the gate — `register()` would name a callback that does not exist
> yet. **Cut that method out of the T3 block** and paste it into the T4 test block
> (T4.1). Per-step counts are deliberately not quoted in this plan; the two authoritative
> numbers are the class total (**15 tests**) and the suite total (**753**) in T4.5.

### T3.3 GREEN — create the plugin

Create `.hermes/plugins/ai-tooling-harness/plugin.yaml`:

```yaml
name: ai-tooling-harness
version: "1.0"
description: ai-tooling harness adapter — commit gate and plugin/docs auto-sync for Hermes Agent.
```

Create `.hermes/plugins/ai-tooling-harness/__init__.py`.

**Part 1 of 2** (T4 appends part 2):

```python
"""Hermes harness adapter for this repo — the counterpart of the opencode plugins.

Both halves call the SAME scripts CI (`make check`) calls, so no gate logic is
duplicated per harness: the commit gate runs `make check-data` (#459) and the auto-sync
half runs `./sync-plugin-docs.sh`. Only the *trigger* is harness-shaped; it is pinned by
TestHermesHarnessAdapter in test_automation.py.

Nothing here loads unless a human opts in, per machine:

    HERMES_ENABLE_PROJECT_PLUGINS=true
    hermes plugins enable ai-tooling-harness

Project-local plugins are disabled by default on purpose — see
docs/agents/hermes-harness.md.
"""

import subprocess
from pathlib import Path

# <repo>/.hermes/plugins/ai-tooling-harness/__init__.py -> <repo>. Resolved from the
# file rather than the process cwd, which may be anywhere. Module-level so the tests
# can point it at a fixture.
REPO = Path(__file__).resolve().parents[3]

_WRITE_HINTS = ("write", "edit", "patch")
_PATH_KEYS = ("path", "file_path", "filePath", "file")
_WATCH_CACHE = {}


def _run(argv):
    """A subprocess that never raises: a toolchain that cannot run must not break a
    session, and must never be read as a failed gate."""
    try:
        return subprocess.run(argv, cwd=REPO, capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None


def _watch_set():
    """The syncable set, DERIVED from `--list-watched` — the one definition (#194), never
    restated here. Cached only on success, so a transient failure does not disable
    auto-sync for the rest of the session."""
    if "watch" in _WATCH_CACHE:
        return _WATCH_CACHE["watch"]
    result = _run(["bash", "./sync-plugin-docs.sh", "--list-watched"])
    if result is None or result.returncode != 0:
        return (set(), ())  # fail-open: an empty watch set means "never trigger"
    files, dirs = set(), []
    for raw in (result.stdout or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.endswith("/"):
            dirs.append(line[:-1])
        else:
            files.add(line)
    _WATCH_CACHE["watch"] = (files, tuple(dirs))
    return _WATCH_CACHE["watch"]
```

**Part 2 of 2** — append to the same file:

```python
def _edited_path(params):
    if not isinstance(params, dict):
        return ""
    for key in _PATH_KEYS:
        value = params.get(key)
        if isinstance(value, str):
            return value
    return ""


def _is_syncable(path, watched):
    files, dirs = watched
    if not path:
        return False
    norm = path.replace("\\", "/")
    if "/plugin/docs/" in norm:
        return False  # already the derived copy — syncing it would loop
    if norm.rsplit("/", 1)[-1] in files:
        return True
    return any(f"/{d}/" in norm or norm.startswith(f"{d}/") for d in dirs)


def _auto_sync(tool_name=None, args=None, result=None, **kwargs):
    """`post_tool_call` hook: re-run `./sync-plugin-docs.sh` after an edit to a root doc
    it mirrors, so `plugin/docs/` never drifts during a session. Silent and fail-open —
    the same contract as the opencode adapter.

    The second parameter is `args`, NOT `params`: Hermes calls plugin hooks by KEYWORD
    with the documented `post_tool_call` payload (`tool_name`, `args`, `result`,
    `task_id`, `session_id`, `duration_ms`, ...). A hook that names it anything else
    receives None and silently never fires.
    """
    del result, kwargs
    if not any(hint in (tool_name or "").lower() for hint in _WRITE_HINTS):
        return
    if not _is_syncable(_edited_path(args), _watch_set()):
        return
    _run(["bash", "./sync-plugin-docs.sh"])


def register(ctx):
    ctx.register_middleware("tool_request", _commit_gate)
    ctx.register_hook("post_tool_call", _auto_sync)
```

Both invocations go through `bash` rather than `./sync-plugin-docs.sh` directly: the
script is executed that way by `TestWatchListSeam`, and it keeps the adapter working on
a checkout whose exec bit was lost (a zip download, some Windows checkouts).

> **Correction to T3.1**: the fixture comment
> `# The adapter calls it as ./sync-plugin-docs.sh, as the Makefile does.` is wrong —
> replace it with
> `# Harmless belt-and-braces: the adapter invokes the script through bash.`
> (the `os.chmod` line stays; it costs nothing and keeps the fixture faithful).

`register()` names `_commit_gate`, which does not exist until T4. **That is expected**:
this half is finished when the auto-sync tests pass, and the file does not import
cleanly until T4 lands — so do not run the full suite between T3 and T4.

### T3.4 GREEN — watch the auto-sync half pass

```bash
cd /home/lychan/projects/ai-tooling
python3 -m unittest -q \
  test_automation.TestHermesHarnessAdapter.test_auto_sync_triggers_on_a_watched_root_doc \
  test_automation.TestHermesHarnessAdapter.test_auto_sync_skips_an_unwatched_path
```

Expected: `Ran 2 tests` / `OK` if you temporarily comment the `tool_request` line in
`register()`, or `AttributeError: _commit_gate` — in which case land T4 first and verify
both halves together. Do not commit T3 on its own.

## T4 — the commit gate, and the pins that keep both adapters honest

**Why**: this is the half that actually gates. It mirrors `commit-gate.ts` exactly:
probe the three preconditions, run `make check-data`, and on failure rewrite the
command into a diagnostic echo so the agent reads the failure instead of retrying.

### T4.1 RED — the gate's tests

Paste the method you cut from T3 (`test_registers_the_commit_gate_and_the_auto_sync_half`)
into `TestHermesHarnessAdapter`, then append these five:

```python
    def _gate(self, **kwargs):
        self._repo(**kwargs)
        return self._registered()["tool_request"]

    def test_commit_gate_rewrites_a_failing_commit_into_a_diagnostic(self):
        gate = self._gate()
        out = gate(tool_name="terminal", args={"command": "git commit -m x"})
        self.assertIsNotNone(out, msg="a failing gate must rewrite the commit")
        command = out["args"]["command"]
        self.assertIn("BLOCKED by Hermes commit-gate", command)
        # The diagnostic must survive the shell round-trip intact: the opencode adapter
        # base64-encodes it for exactly this reason, and so does this one.
        m = re.search(r"printf '%s' '([A-Za-z0-9+/=]+)' \| base64 -d", command)
        self.assertIsNotNone(m, msg="the gate output is not carried in a decodable form")
        self.assertIn("detector X: fail", base64.b64decode(m.group(1)).decode())

    def test_commit_gate_leaves_a_non_commit_command_alone(self):
        gate = self._gate()
        self.assertIsNone(gate(tool_name="terminal", args={"command": "git status"}))

    def test_commit_gate_leaves_a_call_with_no_command_argument_alone(self):
        # Identifying by argument shape, not tool id, is what keeps this robust to a
        # differently-named shell tool.
        gate = self._gate()
        self.assertIsNone(gate(tool_name="read_file", args={"path": "AGENTS.md"}))

    def test_commit_gate_fails_open_when_the_gate_cannot_run(self):
        # A tree with no `check-data` target must let the commit through —
        # TestIntegrityMakefile pins the same rule for the opencode half; this is its
        # behavioural counterpart.
        gate = self._gate(makefile="all:\n\t@true\n")
        self.assertIsNone(gate(tool_name="terminal", args={"command": "git commit -m x"}))

    def test_commit_gate_allows_the_commit_when_the_tree_is_green(self):
        gate = self._gate(audit_exit=0)
        self.assertIsNone(gate(tool_name="terminal", args={"command": "git commit -m x"}))
```

Add `import base64` to `test_automation.py`'s stdlib import block (anywhere in it —
`make fix` runs `ruff check --fix`, which sorts it).

Also **delete** `test_the_adapter_derives_the_watch_set_from_list_watched` from
`TestHermesHarnessAdapter`: T4.3 extends the seam class that owns that pin to cover both
adapters, and two copies of one assertion is the drift shape this repo fights. That
leaves 8 auto-sync/predicate/depth tests plus 6 here = **14**.

### T4.2 RED — watch it fail

```bash
cd /home/lychan/projects/ai-tooling
python3 -m unittest -q test_automation.TestHermesHarnessAdapter
```

Expected: `ERROR` on the gate tests — `AttributeError: module 'ai_tooling_harness' has no
attribute '_commit_gate'` (raised inside `register()`), so `FAILED (errors=N)` for the class.

### T4.3 GREEN — implement the gate

In `.hermes/plugins/ai-tooling-harness/__init__.py`:

1. Change the import block to:

```python
import base64
import subprocess
from pathlib import Path
```

2. Add these constants directly under `_WATCH_CACHE = {}`:

```python
# The one commit predicate. Literal and metacharacter-free, so it is the same plain
# substring match as the opencode adapter's COMMIT_RE (TestHookTriggerSeam pins both).
COMMIT_PREDICATE = "git commit"

# Probed BEFORE the gate runs: `make` cannot signal "could not run" through its exit
# code — it exits non-zero for an absent target and for a real finding alike — so
# "could not run is not failed" is decided here, never inferred from the result.
_PROBE = (
    'command -v make >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1 '
    '&& grep -q "^check-data:" Makefile'
)

_DIAG_LIMIT = 4000
```

3. Insert this immediately **above** `def register(ctx):`:

```python
def _commit_gate(tool_name=None, args=None, **kwargs):
    """`tool_request` middleware: rewrite a `git commit` into a diagnostic echo when
    `make check-data` fails, so the agent reads the failure instead of retrying."""
    del tool_name, kwargs
    if not isinstance(args, dict):
        return None
    command = args.get("command")
    if not isinstance(command, str) or COMMIT_PREDICATE not in command:
        return None

    probe = _run(["sh", "-c", _PROBE])
    if probe is None or probe.returncode != 0:
        return None  # cannot run -> never block

    gate = _run(["make", "--no-print-directory", "check-data"])
    if gate is None or gate.returncode == 0:
        return None  # gates clean, or unrunnable -> allow the commit unchanged

    diag = ((gate.stderr or "") + (gate.stdout or ""))[:_DIAG_LIMIT]
    payload = base64.b64encode(diag.encode("utf-8", "replace")).decode("ascii")
    blocked = (
        "echo \"BLOCKED by Hermes commit-gate: 'make check-data' failed before "
        "'git commit' — fix the tree, then re-run the commit.\" ; "
        f"printf '%s' '{payload}' | base64 -d"
    )
    return {
        "args": {**args, "command": blocked},
        "source": "ai-tooling-harness",
        "reason": "make check-data failed before git commit",
    }
```

### T4.4 — the pins that hold both adapters together

**Edit 1.** In `TestIntegrityMakefile` (line 4466), replace:

```python
    COMMIT_HOOKS = (".opencode/plugins/commit-gate.ts",)
```

with:

```python
    COMMIT_HOOKS = (
        ".opencode/plugins/commit-gate.ts",
        ".hermes/plugins/ai-tooling-harness/__init__.py",
    )
```

This is the whole reason the Hermes file must literally contain `command -v make`,
`command -v python3`, `^check-data:` and `check-data`, and must not contain
`audit-evals.py --offline` outside a comment — the two existing tests
(`test_the_commit_hook_runs_the_shared_target`,
`test_the_commit_hook_fails_open_when_the_gate_cannot_run`) now cover the Hermes adapter
for free. If either fails, fix the plugin, not the test.

**Edit 2.** In `TestHookTriggerSeam`, add this method after
`test_opencode_gate_pins_the_commit_predicate`:

```python
    def test_hermes_gate_pins_the_same_commit_predicate(self):
        # The cross-language literal share is not practical, so this pin IS the single
        # definition of the predicate for the Python adapter (same rule as the TS half).
        source = self._source(".hermes/plugins/ai-tooling-harness/__init__.py")
        m = re.search(r'^COMMIT_PREDICATE = "(.+?)"$', source, re.MULTILINE)
        self.assertIsNotNone(m, msg="the Hermes adapter no longer defines COMMIT_PREDICATE")
        self.assertEqual(m.group(1), self.PREDICATE,
                         msg="the Hermes commit predicate drifted from the pin")
```

**Edit 3.** In `TestWatchListSeam`, replace the whole of
`test_adapter_derives_from_list_watched` (lines 2693–2704) with:

```python
    # Every adapter that triggers off the watch set. A new one goes here.
    ADAPTERS = (
        ".opencode/plugins/auto-sync.ts",
        ".hermes/plugins/ai-tooling-harness/__init__.py",
    )

    def test_adapter_derives_from_list_watched(self):
        # Each adapter consumes --list-watched rather than restating the watch set. The
        # sources are pinned here; the Hermes adapter is also executed behaviourally by
        # TestHermesHarnessAdapter, which the TS half cannot be without `bun`.
        for rel in self.ADAPTERS:
            with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("--list-watched", text,
                          msg=f"{rel} does not derive its trigger set from --list-watched")
            for name in sorted(self.WATCHED):
                self.assertNotIn(f'"{name.rstrip("/")}"', text,
                                 msg=f"{rel} hardcodes watched entry {name}")
```

### T4.5 GREEN — the whole suite, plus the lint gate

```bash
cd /home/lychan/projects/ai-tooling
make lint RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy
python3 -m unittest -q test_automation
```

Expected: `make lint` silent (exit 0) and `Ran 753 tests` / `OK (skipped=2)`.

`753` = 734 baseline + 19 new (**4** in `TestHarnessSkillSurface`: two from T1, two from
T2 — and **15** in `TestHermesHarnessAdapter`, listed below). If the count differs, a test
did not get added — check for a truncated paste.

The 15 in `TestHermesHarnessAdapter`: `test_registers_the_commit_gate_and_the_auto_sync_half`,
`test_the_commit_predicate_matches_the_opencode_adapter`,
`test_the_plugin_resolves_the_repo_root_from_its_own_path`,
`test_both_hooks_accept_the_documented_payload`, the six `test_auto_sync_*`, and the five
`test_commit_gate_*`.

Two ruff findings a first attempt can hit, and the fix for each:

- `BLE001` (blind `except Exception`) — you widened an except clause. Use
  `except (OSError, subprocess.SubprocessError):` as written.
- `B603`/`B602` (subprocess) — only if you changed the call shape. Keep the literal
  list form; if it still fires, add `# noqa: B603` **with a one-line reason** beside it.

`mypy` does not see this file: `pyproject.toml` sets `files = ["*.py"]` and excludes
`plugin/`/`skills/`, so `*.py` means top level only. That gap is declared in the plan's
risks, not fixed here — widening a gate is its own change.

### T4.6 Commit

```bash
cd /home/lychan/projects/ai-tooling
but commit -b feat/hermes-harness-support -m "feat(harness): add the Hermes adapter — commit gate and plugin-docs auto-sync"
```

This commit carries T3 and T4 together: the plugin's two halves are one file and one
`register()`, and splitting them would leave a commit whose tests cannot pass.

## T5 — documentation: `AGENTS.md`, the operator page, the plan row

**Why**: a harness that is supported but undocumented is a harness nobody enables. The
`AGENTS.md` harness section is also **stale in a second way** — line 100 still says the
plugins call `audit-evals.py --offline`, which they stopped doing in #459.

### T5.1 — rewrite the harness section in `AGENTS.md`

Replace lines 90–101 (from `### Supported harness (opencode)` through the
`Deterministic gates` bullet) with:

```markdown
### Supported harnesses (opencode, Hermes Agent)

Two harnesses are supported. Each artifact has **one canonical home** that both read
wherever the formats allow (ADR-0002):

- **Instructions** → `AGENTS.md` — opencode's preferred project file, and the file
  Hermes loads as project context (git root → cwd, then progressively into
  subdirectories).
- **Repo skills** → `.agents/skills/` canonical. opencode reads it; Hermes reads it as
  its project-local skill directory (the cross-tool convention) after a one-time
  `hermes skills trust`. Whatever either harness ships, `/check`, `/fix`, `/sync` and
  `/eval-runner` come from here.
- **Specialized agent (`eval-runner`)** → `.agents/skills/eval-runner/SKILL.md`
  canonical. `.opencode/agents/eval-runner.md` is the thin subagent wrapper that names
  it — opencode needs the `mode: subagent` shape, and Hermes has no agent file at all.
- **Hook logic** → two adapters over one gate: opencode plugins in `.opencode/plugins/`
  (`commit-gate.ts`, `auto-sync.ts`) and the Hermes plugin in
  `.hermes/plugins/ai-tooling-harness/` (a `tool_request` middleware plus a
  `post_tool_call` hook). Both call the **same** `make check-data` (#459) and
  `./sync-plugin-docs.sh` that CI's `make check` calls — one implementation of the gate,
  nothing duplicated per harness.
- **Deterministic gates** → `/check` `/fix` `/sync` (both harnesses, from
  `.agents/skills/{check,fix,sync}/`) and `make check`/`make fix`/`./sync-plugin-docs.sh`
  directly.

Hermes needs two one-time opt-ins per machine — project skills are not auto-trusted and
project plugins are not auto-loaded. See `docs/agents/hermes-harness.md`.
```

### T5.2 — the lockstep paragraph

Immediately below that section, replace:

```markdown
**Single implementation:** any change to a hook behavior must keep the opencode
plugins and `.github/workflows/integrity.yml` in lockstep — they all gate against
the same coupled scripts, so they must not drift.
```

with:

```markdown
**Single implementation:** any change to a hook behavior must keep the opencode
plugins, the Hermes plugin (`.hermes/plugins/ai-tooling-harness/`) and
`.github/workflows/integrity.yml` in lockstep — they all gate against the same coupled
scripts, so they must not drift. Every one of them is pinned by `test_automation.py`:
`TestIntegrityMakefile` requires each commit hook to run `make check-data` and to probe
the same three preconditions, and `TestHookTriggerSeam` pins the one commit predicate
for both adapters.
```

### T5.3 — the stale Sources line

Line 70 still lists `~/.claude/plugins/` and `~/.claude/skills/` as sources, but the
Claude Code runtime was dropped in `945aa19`. Replace:

```markdown
- Locally installed: `~/.claude/plugins/`, `~/.claude/skills/`, MCP servers in settings.json
```

with:

```markdown
- Locally installed: `~/.claude/plugins/` and `~/.claude/skills/` (still live — see below),
  repo skills under `.agents/skills/`, harness config (`opencode.json`,
  `~/.hermes/config.yaml`, `~/.hermes/plugins/`, `~/.hermes/skills/`) — verify the current
  list before adding a tool that claims to read one of them
```

**This edit is additive on purpose.** The first draft of this plan *deleted* the
`~/.claude/…` locations as stale after #016, and that is the wrong call: `audit-evals.py`'s
detector Y still reads `~/.claude/plugins/installed_plugins.json` (`PLUGIN_RECORD`, line
2827), and `plugin/` is still a Claude Code marketplace package, so Claude-local installs
remain part of what this catalog inventories. The Sources line is catalog *provenance*,
not harness config — removing a live source to look tidy loses real information. What this
task adds is the Hermes half of the same sentence.

`audit-evals.py`'s detector Y still reads `~/.claude/plugins/installed_plugins.json`
(`PLUGIN_RECORD`, line 2827). **Do not touch it here**: it is opt-in, report-only,
local-only, and it is a detector's data source rather than a doc. Noted as a finding in
this plan instead.

### T5.4 — the operator page

Create `docs/agents/hermes-harness.md`:

```markdown
# Hermes Agent harness support

Hermes Agent is a second supported harness for this repo, alongside opencode. Both read
one instruction file (`AGENTS.md`), one skill directory (`.agents/skills/`) and drive one
gate set (`make check`/`make fix`/`./sync-plugin-docs.sh`). This page is the operator
half: the one-time opt-ins a machine needs, and how to verify each.

## 1. Instructions — already on

Hermes loads `AGENTS.md` as project context with nothing to configure.

**Watch the size — this already bites.** `AGENTS.md` is 175 158 chars. Hermes caps a
context file at `context_file_max_chars` when set, otherwise at a value that scales with
the model's context window (floor 20 000, ceiling 500 000 chars), keeping 70% head + 20%
tail with a marker between them. **Measured on the authoring machine, in the session that
reviewed this plan:** `kept 22400+6400 of 175158 chars` — a 32 000-char budget, so ~83% of
the file, the entire middle, never reaches the agent.

    hermes chat --query 'reply with the single word ok'
    grep -rn "truncated AGENTS.md" ~/.hermes/sessions/   # or search it with your own tools

A match is the expected case here, not a surprise. Two honest fixes — a larger-context
model, or an explicit `context_file_max_chars` — and one thing that is **not** a fix:
forking a Hermes-only copy of `AGENTS.md`. One instruction surface is the point of this
plan; a second copy is exactly the drift #443 and #451 spent their effort closing.

## 2. Repo skills — one-time trust

Hermes discovers `<repo>/.agents/skills/` but does **not** auto-load procedures from a
cloned repo. The first run prints a notice naming the skills it found and did not load.
Then:

    cd <repo>
    hermes skills trust

Trusted roots are recorded in `skills.trusted_project_dirs` in `~/.hermes/config.yaml`.
Every project skill is security-scanned before it enters the index; a `dangerous`
verdict quarantines it (it disappears from the index and refuses to load by name).

Expected after trusting: `check`, `fix`, `sync`, `eval-runner`, `add-catalog-entry`,
`find-catalog-gaps`, `find-skills` and `triage-lead` are all available as `/<name>`.

Cron jobs, subagents and other non-interactive surfaces **inherit** this trust decision —
they never prompt and never auto-trust, so trust once, here, from an interactive session.
Project skills are also the highest-precedence tier (`project → ~/.hermes/skills/ →
external dirs`): inside this repo, `/check` is this repo's `check` skill.
```

Continue the same file:

```markdown
## 3. The harness plugin — two opt-ins

`.hermes/plugins/ai-tooling-harness/` provides the commit gate (a `tool_request`
middleware that rewrites a failing `git commit` into a diagnostic) and the
`plugin/docs/` auto-sync (a `post_tool_call` hook). Project-local plugins are disabled
by default, deliberately — a plugin is arbitrary code in the agent's process.

    export HERMES_ENABLE_PROJECT_PLUGINS=true    # per shell, or in your environment
    hermes plugins enable ai-tooling-harness     # writes plugins.enabled in config.yaml

Confirm discovery (discovery is independent of enablement):

    HERMES_ENABLE_PROJECT_PLUGINS=true hermes plugins list

Keep **one** `HERMES_HOME` for the enablement command and for the run: `hermes plugins
enable` records `plugins.enabled` *in that home*, and middleware only runs for enabled
plugins — so enabling under one home and running under another silently runs unguarded.

    export HERMES_HOME=/tmp/hermes-aitooling    # the same value for both commands
    export HERMES_ENABLE_PROJECT_PLUGINS=true

After any edit to the plugin, check it against the installed build's import paths (the Sep
2026 module decomposition retired the old ones on 2026-09-14):

    hermes plugins compat .hermes/plugins/ai-tooling-harness    # exits 0 when clean

Nothing in the plugin re-implements a gate: it runs `make check-data` and derives its
sync triggers from `./sync-plugin-docs.sh --list-watched`, the same definitions CI uses.

## 4. What Hermes has no repo-level equivalent for

- **Permissions.** `opencode.json`'s `permission` block — including
  `skill.add-catalog-entry: ask` — is opencode-only. Hermes' equivalents are user-level:
  `command_allowlist` / `approvals.deny` in `~/.hermes/config.yaml`. The repo cannot ship
  them; set them per machine if you want the same confirmation gate.
- **A published package.** `plugin/` is a Claude Code marketplace package. Hermes
  distributes skills through hubs and taps; publishing a Hermes tap is a separate
  decision, not part of this harness support.

## 5. Verifying end to end

With the plugin enabled, in a checkout whose gates are red:

    make check-data          # expect non-zero (make the tree red first, e.g. with a
                             # hand-edit to a derived page — `make fix` restores it)
    hermes chat --query 'Run `git commit -m test` in this repo and report exactly what happened.'

Expected: the agent reports `BLOCKED by Hermes commit-gate: 'make check-data' failed
before 'git commit' — fix the tree, then re-run the commit.`, followed by the gate's own
output — and no commit is created.

Then restore the tree (`make fix`) and confirm `make check-data` exits 0.
```

### T5.5 — keep the harness's own scratch out of the repo

Hermes writes plan-mode output to `.hermes/plans/` inside the active workspace. This plan
makes `.hermes/plugins/` a **tracked** directory, so that scratch would start appearing as
untracked noise in every `git status` and can be swept into a commit by accident.

Append to `.gitignore` (after the `.venv/` line):

```
# Hermes harness scratch — plan-mode output. The tracked .hermes/plugins/ adapter stays.
.hermes/plans/
```

Verify — no file has to be created for this:

```bash
cd /home/lychan/projects/ai-tooling
git check-ignore -v .hermes/plans/2026-01-01-example.md; echo "exit=$?"
```

Expected: one line naming `.gitignore:8:.hermes/plans/` (the line number may differ) and
`exit=0`. `exit=1` with no output means the pattern is wrong — fix the pattern; never
commit the scratch file instead.

### T5.6 — commit

```bash
cd /home/lychan/projects/ai-tooling
but commit -b feat/hermes-harness-support -m "docs(harness): document Hermes support and refresh the harness section"
```

## T6 — prove Hermes actually loads it

Nothing so far has been executed *by Hermes*. The unit suite proves the adapter's logic;
this task proves the wiring.

### T6.1 — do the instructions reach the agent?

```bash
cd /home/lychan/projects/ai-tooling
hermes chat --query 'reply with the single word ok'
```

Expected: `ok`, then **a match** — the expected case here, not a surprise. This machine
already reports `kept 22400+6400 of 175158 chars` for this file: a 32 000-char budget, 70%
head / 20% tail (~83% of the file, the whole middle, dropped). Search your session store
for the marker (`ctx_search` over `~/.hermes/sessions/`, or `grep -rn` in a shell) and
**record the exact `kept N+M of TOTAL chars` line in the PR body** — it is what tells a
maintainer how much of this repo's instructions a Hermes agent really sees (~17% today).

The installed `hermes-agent` skill's project-context reference describes the shape:
`context_file_max_chars` when set, otherwise a dynamic cap of floor 20 000 / ceiling
500 000 characters split 70% head / 20% tail. **T6.1's measurement is the authority, not
that sentence.** Do **not** fork a Hermes-only copy of `AGENTS.md`: a larger-context model
or an explicit `context_file_max_chars` are the two honest fixes. The real follow-up —
splitting `AGENTS.md` into a small front door plus references the agent reads on demand —
is a separate decision and should not be smuggled in here.

### T6.2 — do the project skills load?

```bash
cd /home/lychan/projects/ai-tooling
hermes skills trust
hermes skills list
```

Expected: `hermes skills trust` reports the repo as trusted; `hermes skills list`
includes `check`, `fix`, `sync`, `eval-runner`, `add-catalog-entry`, `find-catalog-gaps`,
`find-skills`, `triage-lead`. `hermes skills trust <path>` does the same from anywhere.

`hermes skills check` is **not** a validator for these — it reports which *hub* skills
changed upstream. The check that matters is that a project skill loads **by name**:

### T6.2b — does a project skill actually load?

```bash
cd /home/lychan/projects/ai-tooling
hermes chat --query '/sync Do not run anything. Reply with the exact command your instructions tell you to run, and nothing else.'
```

Expected: `./sync-plugin-docs.sh` (the script's own `--check` mode may be named too). This
proves three things at once — the project skill was discovered and trusted, its content is
the file you wrote, and the harness reached it by name — and it executes nothing. A
missing skill, a rejected frontmatter or a quarantine gives a different answer here, which
is exactly what makes it worth running.

If a skill is missing, it was either quarantined by the security scanner (Hermes prints
the verdict and refuses to load it by name) or its frontmatter was rejected. Report the
exact loader message — **do not** edit the skill to work around a scanner verdict.

### T6.3 — does the plugin load, and does the gate actually block?

```bash
export HERMES_HOME=/tmp/hermes-aitooling-smoke
export HERMES_ENABLE_PROJECT_PLUGINS=true
mkdir -p "$HERMES_HOME"
cd /home/lychan/projects/ai-tooling
hermes plugins compat .hermes/plugins/ai-tooling-harness
hermes plugins enable ai-tooling-harness
hermes plugins list
```

Expected: `hermes plugins compat` exits **0** first. The Sep 2026 module decomposition
retired the old Hermes import paths on **2026-09-14**; this plugin imports only the
standard library, so it should already be clean — a non-zero exit names each `file:line`
to fix. Then `ai-tooling-harness` is listed and enabled.

**Keep this shell.** Plugin enablement and the run must share **one** `HERMES_HOME`: a
fresh shell with a different (or unset) `HERMES_HOME` silently runs without the plugin.
Every block below re-exports both variables so it is self-contained if you do open one.

Now make the tree red **with a normal edit** (never hand-patch a derived page — use the
tool an agent would use), confirm the gate sees it, then let the gate itself tell you:

```bash
# 1. introduce drift in a derived page
#    (append a stray line to WATCHLIST.md; `make fix` restores it)
make check-data; echo "check-data exit=$?"
```

Expected: a non-zero exit, e.g.
`watchlist check: DRIFT — WATCHLIST.md is stale; run ./sync-plugin-docs.sh` and
`check-data exit=2`.

```bash
export HERMES_HOME=/tmp/hermes-aitooling-smoke
export HERMES_ENABLE_PROJECT_PLUGINS=true
cd /home/lychan/projects/ai-tooling
make check-data; echo "still red: exit=$?"
hermes chat --query 'Run the shell command `git commit -m test` in this repository and report exactly what you saw.'
```

Expected: the agent reports the `BLOCKED by Hermes commit-gate:` line and the gate
output, and `git log -1 --oneline` is unchanged. A commit that lands here means the
middleware is not registered — check `plugins.enabled` in that `HERMES_HOME` and that
both variables were exported in **this** shell, then re-run T6.3.

Restore and confirm green:

```bash
cd /home/lychan/projects/ai-tooling
make fix
make check-data; echo "check-data exit=$?"
```

Expected: `check-data exit=0`.

> If `hermes chat` cannot use a terminal tool in this environment, this step is a
> **disclosed gap**, not a pass: say so in the PR body and leave the unit suite as the
> evidence. Do not claim the live path was verified.

## T7 — the full gate, the plan row, the PR

### T7.1 — the canonical gate

```bash
cd /home/lychan/projects/ai-tooling
make fix RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy
make check RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy; echo "check exit=$?"
```

Expected: `check exit=0`. Detector A may print `UNCHECKED`/`INCONCLUSIVE` lines when a
registry is unreachable — per `docs/agents/routines.md` that is a **disclosed gap, not a
failure**; only `BROKEN` (a real 404) fails. If detector A reports `BROKEN`, fix the
install command it names.

### T7.2 — register the plan

In `plans/README.md`, add a run note after the **Run 3** paragraph:

```markdown
**Run 4** — harness parity, 2026-09-15 (audit at commit `c4e28e9`). Focus: make Hermes
Agent a second supported harness without duplicating a single gate. Plan 017 — four
project skills both harnesses read, one Python adapter over the same `make check-data` /
`sync-plugin-docs.sh` the opencode adapters call, and the docs to enable it.
```

and this row at the end of the status table:

```markdown
| [017](../docs/plans/017-hermes-harness-support.md) | Support Hermes Agent alongside opencode | P1 | M | — | TODO |
```

Run `./sync-plugin-docs.sh --check` afterwards: `plans/` is not in the watch set, so the
check must still report `OK`. If it reports drift, something else edited a watched doc.

### T7.3 — commit, push, PR

```bash
cd /home/lychan/projects/ai-tooling
but commit -b feat/hermes-harness-support -m "docs(plans): add plan 017 for Hermes harness support"
but pr new feat/hermes-harness-support -m "$(cat <<'PRBODY'
## What

Adds Hermes Agent as a second supported harness beside opencode, with one implementation
per gate.

- `.agents/skills/{check,fix,sync,eval-runner}/SKILL.md` — the four procedures live in the
  directory BOTH harnesses read; `/check` `/fix` `/sync` now work in Hermes too.
- `.opencode/agents/eval-runner.md` — reduced to the subagent wrapper `mode: subagent`
  requires; the procedure has one home.
- `.hermes/plugins/ai-tooling-harness/` — a `tool_request` middleware (commit gate, same
  `make check-data`) and a `post_tool_call` hook (auto-sync, same `./sync-plugin-docs.sh`).
- `test_automation.py` — `TestHermesHarnessAdapter` (14 tests, executed, not source-pinned)
  and the pins that hold both adapters to one predicate and one watch-set definition.
- `AGENTS.md` + `docs/agents/hermes-harness.md` — the harness mapping and the two
  one-time opt-ins; also removes a stale `~/.claude/` source line and a stale claim that
  the plugins run `audit-evals.py --offline` (they run `make check-data` since #459).

## Verification

<PASTE the exact commands and their observed output for: make lint, the unit suite
count, make check exit code, T6.2 skills list, T6.3 blocked-commit smoke test>

## Disclosed gaps

<PASTE any step you could not run, e.g. the live T6.3 smoke test, and the AGENTS.md
context-file truncation result from T6.1>

Closes #<issue>
PRBODY
)"
```

> The heredoc delimiter is **quoted** (`<<'PRBODY'`) — that is what keeps the backticks
> and `$` in the body literal. Never inline this body as `-m "…backticks…"` on zsh:
> there the substitutions are live and the message is silently mangled.

The PR body must carry the real command output. If a verification step was not run, say
so there rather than omitting it.

## Tests / validation — the whole matrix

| What it proves | Command | Expected |
|---|---|---|
| Baseline before any edit | `make check-offline RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy` | `OK (skipped=2)`, exit 0 |
| The four skills exist and name real targets | `python3 -m unittest -q test_automation.TestHarnessSkillSurface` | `Ran 4 tests` / `OK` |
| The procedure has one home | same class | `OK`; the wrapper carries no "How we tested it" |
| The adapter's auto-sync behaviour | `python3 -m unittest -q test_automation.TestHermesHarnessAdapter` | `Ran 15 tests` / `OK` |
| Both hooks accept the documented Hermes payload | same class (`test_both_hooks_accept_the_documented_payload`) | `OK` |
| The gate rewrites, passes through, fails open | same class | `OK` |
| Both adapters share one predicate | `python3 -m unittest -q test_automation.TestHookTriggerSeam` | `OK` |
| Both adapters derive the watch set | `python3 -m unittest -q test_automation.TestWatchListSeam` | `OK` |
| Both adapters run `make check-data` and probe before blocking | `python3 -m unittest -q test_automation.TestIntegrityMakefile` | `OK` |
| Ruff + mypy over the new Python | `make lint RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy` | exit 0 |
| The whole tree | `make check RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy` | exit 0 |
| Hermes loads instructions, skills, plugin | T6.1–T6.3 | see each step |

## Risks and tradeoffs

1. **`AGENTS.md` is 176 KB and Hermes truncates context files.** A small-context model
   silently loses the middle of the file. Mitigation: T6.1 measures it; the operator page
   documents `context_file_max_chars`. Accepted because the alternative — a second
   instruction file — breaks the one-surface rule.
2. **The Hermes gate is opt-in, so parity is weaker than opencode's.** opencode
   auto-loads `.opencode/plugins/*.ts`; a Hermes user who never sets
   `HERMES_ENABLE_PROJECT_PLUGINS` and never enables the plugin gets no commit gate.
   CI and `make check` remain the real backstop, and the operator page says so plainly.
3. **Middleware is fail-open, by contract.** A bug in the adapter silently stops gating
   rather than breaking a session. That is the right failure direction here, and it is
   exactly why `TestHermesHarnessAdapter` *executes* the adapter instead of pinning its
   source text.
4. **`tool_request` runs before approval checks.** The rewritten command is what the
   approval layer sees. The rewrite is a diagnostic echo, never a different command, so
   the blast radius is bounded — but anyone extending the gate must keep that property.
5. **Two adapters, one gate.** The repo's rule is one implementation of the gate, not of
   the trigger; a second trigger is unavoidable across two harnesses. The pins in T4.4
   are what keep the pair honest.
6. **`mypy` does not type-check `.hermes/**`** (`pyproject.toml` has `files = ["*.py"]`).
   The executed tests cover more than mypy would here; widening the gate is deliberately
   left out of scope.
7. **`REPO = parents[3]`** is load-bearing. The depth is pinned by a test, but a future
   Hermes change to how project plugins are discovered (one level deeper, say) would
   break it — the pin fails loudly rather than silently gating the wrong tree.
8. **`/check`, `/fix`, `/sync` are generic skill names** that outrank any global skill of
   the same name *inside this repo* (project skills are the highest tier). Intended, and
   worth knowing before naming a future skill.
9. **`opencode.json` still holds the three command templates.** Declared duplication of
   prose, not of behaviour; both sides name the same real commands and the hermetic test
   pins the skills.

10. **Plugin callbacks receive the documented payload by KEYWORD, and a renamed parameter
    fails silently.** Found in review of this plan: the first draft named the auto-sync
    hook's second parameter `params`, while Hermes passes `args` — the hook would have
    received `None` and done nothing, and **every test would still have passed**, because
    the tests passed `params=` too. That is the repo's #443 defect in a new place ("two
    extractors for one fact, coupled by nothing … the test passed more easily the more
    broken it got"). Fixed by T3.1's `test_both_hooks_accept_the_documented_payload`, which
    passes Hermes' exact payload and nothing of its own; any future hook here gets the same
    shape.

11. **`ctx.state` is the documented home for plugin bookkeeping** ("plugin-owned cursors,
    caches, and deduplication data … rather than placing runtime bookkeeping in
    `config.yaml`"). This adapter keeps its watch-set memo in a module global instead,
    deliberately: it is a per-process read-through cache of a value the script owns, not
    durable state, and a module global is what makes it testable — each `_load()` hands
    the tests a fresh module. Recorded so the deviation is a decision, not an oversight.
12. **Middleware and hook names are version-coupled to the installed build.** The
    contracts live in `hermes_cli/middleware.py`'s `VALID_MIDDLEWARE` and
    `hermes_cli.plugins.VALID_HOOKS`; the Sep 2026 module decomposition retired the old
    Hermes import paths on 2026-09-14, which is why T6.3 runs `hermes plugins compat`
    before anything else. This plugin imports only the standard library, so it is clean
    today — but a future edit that reaches into Hermes internals must re-run that check.

**The load-bearing risk — measured, not predicted.** `AGENTS.md` is **175 158 chars** and
Hermes keeps **`22400+6400`** of it on this machine: 70% head + 20% tail, ~83% of the file
dropped, including the middle where most of the operating rules live. Everything else in
this plan is plumbing; this is what decides how well a Hermes agent actually works here.
It is **not** solved by this plan, and deliberately not solved by forking the file. The two
honest options are a larger-context model and an explicit `context_file_max_chars`; both
are per-machine settings this repo cannot ship. Put the measured `kept N+M of TOTAL chars`
line in the PR body, and treat "split `AGENTS.md` into a small front door plus references
the agent reads on demand" as the real follow-up — that is the shape `PLAYBOOK.md` already
uses for humans, it is a larger decision than harness support, and it should not be
smuggled in here.

## Open questions

- Should `opencode.json`'s `command` templates be reduced to one-line pointers at the new
  skills, so the prose exists once? That changes opencode behaviour, so it is a follow-up
  decision, not part of this plan.
- Should `plugin/` gain a Hermes distribution (a skills tap)? Separate product decision.
- Should the adapter ship as a **Portable Agent Plugins v1** package instead of a
  Hermes-shaped directory plugin? The Hermes plugin guide documents that format (a
  supported subset, explicitly "not a claim of full Agent Plugins conformance"), and it is
  the only path here that could serve a **third** harness without a third adapter. Out of
  scope now: this repo needs two harnesses, and YAGNI says do not pay for portability
  nothing has asked for — but it is the right answer the day a third harness arrives.
- `audit-evals.py`'s detector Y still reads `~/.claude/plugins/installed_plugins.json`.
  It is opt-in, report-only and local-only, and it reads a data source rather than
  restating a doc — left alone here.
- Should a bot profile ("eval-runner" as a Hermes Bot) replace `delegate_task` for the P0
  lane? Not needed: the skill plus delegation covers it.

## STOP conditions

- `make check` reddens in a file this plan does not list — the surface list is
  incomplete. Stop and report rather than widening the diff.
- Hermes rejects a project skill's frontmatter (`disable-model-invocation` is a
  Claude/opencode field with no Hermes meaning) — report the exact loader message. Do not
  delete the field from the existing skills without deciding what it should mean.
- `ctx.register_middleware` or `ctx.register_hook` is absent on the installed Hermes'
  `ctx` — the plugin contract moved. Stop; the adapter shape needs re-deriving from the
  current developer guide.
- `HERMES_ENABLE_PROJECT_PLUGINS` does not surface the plugin at all — report the
  discovery output before working around it.
- Anything requires editing `plugin/` (the published package) — that is a product
  decision.
- A gate needs a `# noqa` **without** a stated reason, or the fix would widen a gate
  (`mypy` files, ruff `select`). Stop and report.
- The installed Hermes rejects `tool_request` / `post_tool_call` as unknown names,
  `hermes plugins compat` exits non-zero, or a callback arrives with fields the adapter
  does not expect. Read the installed build's `hermes_cli/middleware.py`
  (`VALID_MIDDLEWARE`) and `hermes_cli.plugins` (`VALID_HOOKS`), plus the Event Hooks
  reference, before changing the adapter shape. Do not guess a name from a blog post.

## Findings considered and rejected

- **Add `.hermes.md`.** It takes precedence over `AGENTS.md` (first match wins), so Hermes
  would stop loading the real instruction file and the repo would gain a second one to
  keep in sync. Rejected.
- **Delete `.opencode/` or `opencode.json`.** opencode is not being dropped; this plan
  adds a harness, it does not remove one.
- **Port `opencode.json`'s `permission` block to Hermes.** Hermes has no repo-level
  permission file; the equivalents are user-level `config.yaml` settings. Documented
  rather than shipped.
- **Use Hermes' `pre_tool_call` block directive instead of `tool_request` middleware.**
  Both can stop a commit, and `block` is the purpose-built guardrail shape — `pre_tool_call`
  is Directive/control, where "first valid `block` or `approve` directive wins". Rejected
  for **parity**: the opencode adapter *rewrites* the command (`tool.execute.before`
  mutating `output.args.command`), so in both harnesses the agent reads the gate's
  diagnostic as command output — one agent-visible shape, not two. A block directive
  produces a refusal instead. If that parity ever stops mattering, `pre_tool_call` is the
  simpler adapter, and this entry is the note that says so.
- **A `.pre-commit-config.yaml` git hook instead of a harness plugin.** It would be a
  third trigger for the same gate, with its own drift risk, and it would fire for every
  contributor regardless of harness. The repo's precedent is harness plugins over the
  shared `make check-data`.
- **Generate the Hermes adapter from the opencode one.** Two ~120-line files in two
  languages; a generator is more machinery than the thing it removes.
- **Widen `mypy` to `.hermes/**`.** Real, but it is a gate change; it belongs in its own
  plan with its own rationale.
- **Fix detector Y's `~/.claude/` record path.** Out of scope — a detector's data source,
  opt-in and report-only, not a harness mapping.

## Definition of done

- [ ] `make check RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy` exits 0.
- [ ] `Ran 753 tests` / `OK (skipped=2)` — or a documented explanation of any difference.
- [ ] `hermes skills trust && hermes skills list` shows the eight project skills.
- [ ] The T6.3 smoke test blocks a `git commit` on a red tree, or the gap is disclosed in
  the PR body.
- [ ] The plan 017 row is in `plans/README.md` and `plans/README.md` is committed.
- [ ] No secret, token, or credential appears in the diff.

## Review log — 2026-09-15, against the installed harness and the live tree

This plan was reviewed after its first draft, against **authoritative sources** rather than
against memory. Everything below was re-checked; what changed is listed separately from
what was confirmed, so a reader can tell the two apart.

**Verified correct — no change:**

- `ctx.register_middleware("tool_request", cb)`, return shape `{"args": {...}}` (plus
  optional `source` / `reason` trace fields) — Hermes developer guide, *Middleware*.
- `ctx.register_hook("post_tool_call", cb)` — Event Hooks reference and Plugins guide.
- Middleware runs **before** guardrails, approvals and hooks; middleware failures are
  **fail-open** — *Middleware*, "Execution Order" and "Safety Notes". Risks 3 and 4 quote
  these; they are documented behavior, not inferences.
- Project-local plugins live in `./.hermes/plugins/` and are **disabled by default**,
  enabled by `HERMES_ENABLE_PROJECT_PLUGINS=true` — Plugins guide.
- `plugin.yaml` needs `name` / `version` / `description` — Plugins guide.
- `<project-root>/.agents/skills/` is the documented cross-tool project skill directory;
  `hermes skills trust`; `skills.trusted_project_dirs`; project skills are the
  highest-precedence tier; each is security-scanned — Skills guide, "External Skill
  Directories".
- `TestWatchListSeam.WATCHED`, `TestHookTriggerSeam.PREDICATE` and `._source(rel)`,
  `_load()`, `_write(d, name, text)`, `ROOT` — read from `test_automation.py` at the lines
  the tasks name. `_load()` does **not** register in `sys.modules`, so the fresh-module
  assumption the tests rely on holds.
- `make lint`, `make check`, `make check-data`, `make check-offline` and `make fix` all
  exist (`Makefile:57`, the `.PHONY` line).
- `.gitignore` does **not** ignore `.hermes/`, so the adapter is committable.

**Changed by this review — each was a real defect:**

1. **`params` → `args`** in the auto-sync hook and its six test call sites. Hermes passes
   the documented payload **by keyword**, so the hook would have received `None` and never
   fired — while the tests, which passed `params=` too, stayed green. This is the most
   important correction in the plan, and risk 10 keeps the lesson.
2. **`hermes chat -q` → `hermes chat --query`**, in all four places — including the two
   inside the operator page this plan ships. A wrong flag in a doc that ships is a defect
   that outlives the plan; the review caught two of the four only after the first fix.
3. **The smoke test's environment.** Enablement and the run must share one `HERMES_HOME`
   (they did not — the run's block could open a fresh shell), and `hermes plugins compat`
   now runs first, because the Sep 2026 module decomposition retired the old Hermes import
   paths on **2026-09-14**, the day before this review.
4. **`.gitignore` gained `.hermes/plans/`** (new T5.5). Making `.hermes/plugins/` tracked
   without it would have let Hermes' own plan-mode scratch appear in every `git status`.
5. **Test counts corrected** — 750 → **753** (734 + 4 + 15) — and the per-step counts that
   could not honestly be pinned are gone, replaced by the two that can.
6. **T6.2 no longer implies `hermes skills check` validates project skills** — it reports
   which *hub* skills changed upstream. T6.2b loads a project skill **by name** instead,
   which is the property that actually matters.
7. **`pre_tool_call` (the block directive) is recorded as the considered alternative** to
   the `tool_request` middleware, with the parity reason for not using it.
8. **Portable Agent Plugins v1** added as the open question that decides the third-harness
   case.

**Not verified here:** that the Hermes build **installed on this machine** accepts these
names and payloads. The docs are the contract; T6.3 is the empirical check, and its first
command is the one that fails loudly if the contract has moved.






















