# Plan 018: Install on opencode and Hermes; delete the Claude Code marketplace

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected output before moving on. If a STOP condition fires,
> stop and report — do not improvise.
>
> **Drift check (run first)**:
> `git diff --stat a9af153..HEAD -- README.md plugin check-plugin.py sync-plugin-docs.sh rewrite-doc-links.py test_automation.py Makefile`
> Any change means the excerpts below are stale — re-read the live tree first.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: MEDIUM — deletes a published distribution path, then adds two new ones
- **Depends on**: 016 (landed), 017 (landed)
- **Category**: chore
- **Planned at**: commit `a9af153`, 2026-09-15
- **Decides**: plan 016's S5, which was a STOP ("keep shipping a Claude Code plugin, add a
  package for another harness, or drop `plugin/` entirely"). Owner decided 2026-09-15:
  drop the Claude Code marketplace; ship opencode + Hermes installs.

## Goal

Remove every Claude Code install path from this repo, and make the same five skills
installable by documented command on any machine running opencode or Hermes Agent.

## Current context / assumptions

Documentation-only repo: no build, no deploy. `make check` is the canonical gate; CI
(`.github/workflows/integrity.yml`, job `audit`) runs it verbatim.

### The Claude Code surface that still exists (verified at `a9af153`)

| Path | What it is |
|---|---|
| `README.md` "Install" block | `claude plugin marketplace add mattbutlerengineering/ai-tooling` + `claude plugin install ai-tooling@ai-tooling` + the `/plugin ...` in-session form |
| `plugin/README.md` lines 5-11 | the same two commands plus the in-session form |
| `.claude-plugin/marketplace.json` | Claude Code marketplace manifest (owner: Matt Butler) |
| `plugin/.claude-plugin/plugin.json` | Claude Code plugin manifest (homepage/repository → upstream repo) |
| `plugin/hooks/hooks.json` | SessionStart + PostToolUse wiring, both via `${CLAUDE_PLUGIN_ROOT}` |
| `plugin/skills/{audit-workflow,setup-workflow,update-catalog,evaluate-tool}/SKILL.md` | doc refs written as `${CLAUDE_PLUGIN_ROOT}/docs/<doc>` |
| `sync-plugin-docs.sh` | renders `plugin/skills/` into root `skills/`, stripping that prefix |
| `check-plugin.py` | validates the two manifests; wired into `check-data` (Makefile:96) |

**Not in scope — do not touch.** `STACK.md`, `CATALOG.md`, `COMPARISON.md` and
`evaluations/` contain many `claude plugin marketplace add anthropics/claude-plugins-official`
commands. Those install *catalogued third-party tools being evaluated*, not this repo's
own packaging; translating them would make accurate install commands wrong.
`plugin/hooks/{validate-counts.sh,check-freshness.sh}` also stay — both are portable
(`git rev-parse --show-toplevel`) and covered by `TestValidateCountsHook` and
`TestFreshnessHook`. Only `hooks.json`, the Claude wrapper, goes.

### What each harness actually reads (verified)

opencode (`opencode.ai/docs/skills`, `/docs/plugins`, `/docs/rules`):
- Rules: project `AGENTS.md`; global `~/.config/opencode/AGENTS.md`; plus an `instructions`
  array in `opencode.json` (paths, globs, or URLs).
- Skills, in search order: `.opencode/skills/`, `~/.config/opencode/skills/`,
  `.claude/skills/`, `~/.claude/skills/`, **`.agents/skills/`**, **`~/.agents/skills/`**.
  The last two are the "agent-compatible" locations, and the global one is what makes a
  machine-wide install possible. Frontmatter needs `name` + `description`, and `name` must
  equal the directory name.
- Plugins: `.opencode/plugins/` (project), `~/.config/opencode/plugins/` (global), or npm
  packages named in the config's `plugin` array.

Hermes Agent (verified against `hermes plugins --help` / `hermes skills --help`, v0.21.3):
- `hermes plugins install` — "from the curated catalog, a Git URL, or owner/repo".
- `hermes plugins validate <dir>` — the catalog-admission gate. `capabilities`, `doctor`,
  `compat`, and `pack` (`hermes-pack.yaml` plugin sets) also exist.
- `hermes skills trust <path>` — repo-local `.agents/skills/` needs a one-time trust;
  `hermes skills install` pulls skills from skills.sh / GitHub / ClawHub.
- `AGENTS.md` is loaded as project context with no wiring at all.

### The three skill trees (the thing that is easy to get wrong)

| Tree | Contents | Role |
|---|---|---|
| `.agents/skills/` (8) | `add-catalog-entry`, `check`, `eval-runner`, `find-catalog-gaps`, `find-skills`, `fix`, `sync`, `triage-lead` | canonical repo skills; read by **both** harnesses |
| `plugin/skills/` (5) | `audit-workflow`, `evaluate-tool`, `setup-workflow`, `sync-stars`, `update-catalog` | the **distributable** skills — what a machine installs |
| `skills/` (5) | the same five, prefix stripped | derived repo-local rendering written by the sync |

`./sync-plugin-docs.sh` copies root docs → `plugin/docs/` and renders `plugin/skills/` →
root `skills/`. Never hand-edit `plugin/docs/` or `skills/`.

Environment (verified on this machine):

- `hermes` v0.21.3; `make`, `uv`, `git` present; `bun` absent, so the two opencode adapter
  tests skip. `ruff`/`mypy` are not on PATH — pass `RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy`.
- Version control is a **GitButler workspace**: commit with `but`, never `git commit`.
- `python*` and `gh` are deny-ruled on this host, so the narrow loop is
  `uv run -m unittest -q test_automation.<Class>`.

### Baseline (reproduce before editing)

    cd /home/lychan/projects/ai-tooling
    make check-offline RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy; echo "exit=$?"
    # → Ran 755 tests ... OK (skipped=2)   and   exit=0

## Architecture / proposed approach

`plugin/` stops being a Claude Code marketplace package and becomes the harness-neutral
**distributable**: `plugin/skills/` + `plugin/docs/`, plus one installer that renders them
into whichever harness's global directories exist on the machine. The placeholder that
today names a Claude-only variable becomes a harness-neutral token, `${AI_TOOLING_DOCS}`,
and each renderer substitutes the path it knows: the repo-local render strips it (bare
`STACK.md`, correct at the repo root), while an install replaces it with the absolute
installed docs directory. No gate changes — opencode and Hermes keep calling the same
`make check` and `./sync-plugin-docs.sh`.

Two decisions an implementer would otherwise have to guess:

1. **`plugin/` keeps its name.** Renaming it would churn `plugin/docs/` (1,100+ files),
   `sync-plugin-docs.sh`, `check-plugin.py`, both adapter suites and the Makefile for zero
   user-visible gain. What changes is its *contents*: the two Claude manifests and the
   Claude hook wrapper go, and the install story is rewritten.
2. **Docs ship with the skills, into one shared directory.** The 5 skills reference
   CATALOG.md / WORKFLOW.md / STACK.md, which are large and single-sourced. A machine-wide
   install renders the docs once to `~/.local/share/ai-tooling/docs/` and points every
   installed skill at it — no per-skill duplication, no live network dependency.

### Install targets

| Harness | Skills land in | Docs land in | Extra step |
|---|---|---|---|
| opencode | `~/.agents/skills/<name>/SKILL.md` | `~/.local/share/ai-tooling/docs/` | none — global skills are auto-discovered |
| Hermes | `~/.hermes/skills/<name>/SKILL.md` | same directory | `hermes plugins install` for the commit-gate adapter |

Both are installed by one script, `install-harness.sh`, so the substitution logic lives in
exactly one place.

## Conventions this plan must follow

These override anything below that contradicts them. If a later step seems to want more
tests, this section wins.

### Testing — lean, end-to-end only

- **One real end-to-end acceptance per task.** Run the actual artifact against a throwaway
  HOME and read the actual result. Nothing mocked, nothing simulated.
- **No unit tests for internal helpers.** `skills_dest_for`, `render_skills` and
  `install_docs` get no direct tests — the installer's e2e test covers them through the real
  script.
- **No smoke tests, no assertions of the obvious.** Do not test that: a file exists because
  the previous line created it, a bad argument exits non-zero, help text names a harness, or
  `--check` reports "no install found" on an empty HOME. All self-evident from the code.
- **No test stacking.** T2 and T4 each *replace* a deleted pin 1:1, so the net count does not
  grow. The only added test in this plan is the single e2e case in T3.
- **Isolation, then cleanup.** Per the `real-subprocess-e2e-testing` skill: each run gets its
  own `tempfile.TemporaryDirectory()`, the install target is asserted to be inside that temp
  path *before* the script is invoked, and teardown runs on failure as well as success.
- **The gate is the arbiter.** GREEN means `make check` exits 0. Never pipe `make check` — a
  pipeline reports the pipe's status, not the gate's.

### UI — shadcn conventions, and why there is nothing to migrate here

This repository has **no UI**, verified at `a9af153`: zero `package.json`, `components.json`,
`registry.json` or `tsconfig.json` across 2,800 files, and the only HTML artifact
(`presentations/development-process/Development process.dc.html`) is a self-contained deck
with no React, Tailwind, Radix or Vite markers. Every file this plan touches is bash, Python
or Markdown. **There is nothing to migrate to shadcn, and inventing a UI to satisfy the
instruction would be the wrong change.**

Recorded so the convention is on file for the day a UI does appear — a catalog browser is the
plausible one:

- Any new or touched front-end surface follows shadcn/ui conventions: start from the `shadcn`
  and `shadcn-ui-patterns` skills, add components from a registry instead of hand-rolling
  primitives, and never introduce a second styling system beside shadcn.
- Match the repo's existing design tokens rather than inventing colours, spacing or type scale.
- A UI for this repo is its own plan; it is out of scope here.

## T0 — Baseline and branch (no edits)

    cd /home/lychan/projects/ai-tooling
    make check-offline RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy; echo "exit=$?"

Expected: `OK (skipped=2)` and `exit=0`. If it is not green, **STOP** — you are not starting
from this plan's baseline.

    but branch new --status-after chore/opencode-hermes-install
    but status

Expected: the new branch, empty, sitting directly on the common base.

## T1 — One harness-neutral docs token

**Why**: `${CLAUDE_PLUGIN_ROOT}` exists only inside Claude Code. Every other renderer needs
a token it can substitute, and there must be exactly one.

### T1.1 RED — flip the token in the four skills, leave the renderer stale

No new test here: the existing gate already owns this behaviour, so the RED comes from
breaking it. Edit the four SKILL.md files with the lean-ctx patch tool using
`op=replace_all`, `find: ${CLAUDE_PLUGIN_ROOT}/docs/`,
`replace: ${AI_TOOLING_DOCS}/`:

- `plugin/skills/audit-workflow/SKILL.md`
- `plugin/skills/setup-workflow/SKILL.md`
- `plugin/skills/update-catalog/SKILL.md`
- `plugin/skills/evaluate-tool/SKILL.md`

(`replace_all` is safe on these — plain Markdown, no exec bit. Never `replace_all` an
executable file: it rewrites at mode 600 and drops the exec bit, and `chmod` is deny-ruled
on this host.)

### T1.2 RED — the existing renderer test now fails

    uv run -m unittest -q test_automation.TestSyncPluginDocs

Expected: FAILED. The sync still strips a prefix that no skill writes any more, so the
repo-local `skills/*/SKILL.md` copies no longer match what `plugin/skills/` renders to.
That failure is the RED — do not paper over it by editing `skills/` by hand.

### T1.3 GREEN — update the renderer

`sync-plugin-docs.sh` is executable, so use `op=replace_unique` (never `replace_all`) for
both edits:

    old: # --- Skills: plugin/skills/ → DEST_SKILLS (strip ${CLAUDE_PLUGIN_ROOT}/docs/ paths) ---
    new: # --- Skills: plugin/skills/ → DEST_SKILLS (strip ${AI_TOOLING_DOCS}/ paths) ---

    old: sed 's|\${CLAUDE_PLUGIN_ROOT}/docs/||g' "$skill_dir/SKILL.md" > "$DEST_SKILLS/$skill_name/SKILL.md"
    new: sed 's|\${AI_TOOLING_DOCS}/||g' "$skill_dir/SKILL.md" > "$DEST_SKILLS/$skill_name/SKILL.md"

`rewrite-doc-links.py` line 13 mentions the old prefix in a docstring — `op=replace_unique`,
same substitution. (`check-plugin.py` and `plugin/README.md:34` are handled in T2.)

### T1.4 GREEN — re-render and verify

    ./sync-plugin-docs.sh && ./sync-plugin-docs.sh --check
    # → sync check: OK — plugin/docs/ and skills/ are in sync with root
    rg -n 'CLAUDE_PLUGIN_ROOT' plugin/skills/ skills/ sync-plugin-docs.sh
    # → no output
    rg -n 'STACK\.md' skills/setup-workflow/SKILL.md
    # → the bare filename: stripped here, absolute after an install

Then the full gate: `make check-offline RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy; echo "exit=$?"`
→ `exit=0`.

### T1.5 Commit

    but commit -b chore/opencode-hermes-install -m "refactor(plugin): name the docs token after the harness, not Claude Code"

## T2 — Delete the Claude Code install path

### T2.1 RED — pin the absence

In `TestPluginPackage`, replace `test_the_plugin_ships_a_readme` (it asserts the Claude
command exists) with:

```python
    CLAUDE_ONLY = (".claude-plugin", "plugin/.claude-plugin", "plugin/hooks/hooks.json")

    def test_no_claude_install_path_remains(self):
        for rel in self.CLAUDE_ONLY:
            self.assertFalse(os.path.exists(os.path.join(ROOT, rel)), msg=rel)
```

The README/documentation pin belongs with the doc rewrite (T4) — adding it here would leave
two tasks fighting over one green gate.

### T2.2 RED — watch it fail

    uv run -m unittest -q test_automation.TestPluginPackage

Expected: `FAILED (failures=2)` — `test_no_claude_install_path_remains`, plus
`test_live_package_is_clean`, which still sees the Claude manifests.

### T2.3 GREEN — delete the three Claude-only files

    cd /home/lychan/projects/ai-tooling
    rm .claude-plugin/marketplace.json plugin/.claude-plugin/plugin.json plugin/hooks/hooks.json
    rmdir .claude-plugin plugin/.claude-plugin
    ls plugin/hooks/

Expected: `check-freshness.sh  validate-counts.sh` — both stay. Whole-file `rm`/`rmdir` is
the one file operation allowed on the native terminal; lean-ctx has no equivalent.

**`make check` is red at this point, and that is expected.** `check-plugin.py` is wired into
`check-data` (Makefile:96) and now reports the missing manifests as MANIFEST findings.
Repoint it in T2.4 before running the gate — do not "fix" this by softening the gate or by
re-adding a manifest.

### T2.4 GREEN — repoint `check-plugin.py` at the harness-neutral package

It existed to validate Claude manifests; with those gone it must be repointed in the same
commit, because `check-data` runs it with `--check`.

Edits to `check-plugin.py`:

1. Delete `import json` — after step 2 nothing uses it, and ruff flags it.
2. Delete `_load_json()` entirely.
3. In `audit_plugin()`, delete the whole manifest block: both `_load_json` calls, the
   `market`/`manifest`/`entry`/`src` block, the `NAME` check, and the `VERSION` block
   (including the `plugin/package.json` probe). Rewrite the module docstring's first
   paragraph to match — the package is no longer a marketplace entry.
4. Keep `skill_dirs()`, the per-skill frontmatter loop, the `plugin/CLAUDE.md` FRONT-DOOR
   check and the `plugin/README.md` list-parity check unchanged.
5. In the per-skill loop, after the `description` check, add:

<pre>
        if "CLAUDE_PLUGIN_ROOT" in text:
            findings.append(Finding("HARNESS", f"{name}/SKILL.md names ${{CLAUDE_PLUGIN_ROOT}}, "
                                               "which exists only inside Claude Code"))
</pre>

6. In `main()`, delete the closing
   `print("  run \`claude plugin validate ./plugin\` for the upstream check too")` line.

Kinds in play afterwards are `SKILL`, `FRONT-DOOR`, `HARNESS`. Delete `TestPluginPackage`'s
tests for `MANIFEST`, `SOURCE`, `NAME` and `VERSION` (five test methods) with them.

### T2.5 GREEN — drop the hooks.json assertion

`test_automation.py:2448` reads `plugin/hooks/hooks.json` inside `TestFreshnessHook`. Delete
that assertion only; the rest of the class invokes the script by path and stays.

    uv run -m unittest -q test_automation.TestFreshnessHook
    uv run -m unittest -q test_automation.TestPluginPackage

Both → `OK`.

### T2.6 Verify and commit

    uv run check-plugin.py            # → == plugin package (report-only) — 0 finding(s) ==
    uv run check-plugin.py --check; echo "exit=$?"    # → exit=0
    make check-offline RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy; echo "exit=$?"   # → exit=0
    but commit -b chore/opencode-hermes-install -m "chore(plugin): delete the Claude Code marketplace packaging and repoint its validator"

## T3 — `install-harness.sh`: one renderer, two harnesses

**Why**: `claude plugin marketplace add` was a server-side install. Nothing replaces it yet,
so "installable on any machine with opencode or Hermes" is still untrue after T2.

### T3.1 RED — pin the renderer's contract

Add **one** test class to `test_automation.py`, after `TestHermesHarnessAdapter`. It is the
only new test this plan adds, and deliberately the only case:

```python
class TestInstallHarness(unittest.TestCase):
    """install-harness.sh renders plugin/skills/ into a harness's global dirs.

    HOME is redirected to a temp dir, so this is offline and touches nothing real.
    """

    def _run(self, *args, home):
        # `bash <script>` rather than `./<script>`: chmod is deny-ruled on the authoring
        # host, so a file created through ctx_patch has no exec bit.
        return subprocess.run(["bash", os.path.join(ROOT, "install-harness.sh"), *args],
                              capture_output=True, text=True, check=False,
                              env={**os.environ, "HOME": home})

    def test_install_renders_both_harnesses_and_the_pointer_resolves(self):
        """The one e2e case: run the real script, then follow the pointer it wrote."""
        with tempfile.TemporaryDirectory() as home:
            # Guard the target before mutating anything (real-subprocess-e2e-testing).
            self.assertTrue(os.path.realpath(home).startswith(os.path.realpath(tempfile.gettempdir())))

            for harness, rel in (("opencode", ".agents/skills"), ("hermes", ".hermes/skills")):
                r = self._run(harness, home=home)
                self.assertEqual(r.returncode, 0, msg=r.stderr)

                text = Path(home, rel, "setup-workflow", "SKILL.md").read_text(encoding="utf-8")
                self.assertNotIn("${AI_TOOLING_DOCS}", text, msg="token left unresolved")

                # Follow the rendered pointer: the doc the skill names must exist on disk.
                pointer = re.search(r"\S+/ai-tooling/docs/STACK\.md", text)
                self.assertIsNotNone(pointer, msg="no resolved docs pointer in the skill")
                self.assertTrue(Path(pointer.group(0)).is_file(), msg=pointer.group(0))

    # The other cases a unit-minded author would write — a bad argument exiting non-zero,
    # --check on an empty HOME, per-harness destination paths — are self-evident from the
    # script and are deliberately not tested. See the Conventions section.
```

### T3.2 RED — watch it fail

    uv run -m unittest -q test_automation.TestInstallHarness

Expected: 1 error — `bash: .../install-harness.sh: No such file or directory`.

### T3.3 GREEN — write `install-harness.sh`

Create it at the repo root with `ctx_patch op=create`. `chmod +x` is deny-ruled for the agent
on this host, so the tests and the docs invoke it as `bash install-harness.sh`; a human can
make it executable if they want the `./` form.

```bash
#!/usr/bin/env bash
# Render the distributable in plugin/ into a harness's global directories.
#
#   bash install-harness.sh opencode     # ~/.agents/skills + <XDG_DATA_HOME>/ai-tooling/docs
#   bash install-harness.sh hermes       # ~/.hermes/skills + the same docs dir
#   bash install-harness.sh --check      # exit 1 unless every installed harness is complete
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="$REPO_ROOT/plugin/skills"
DOCS_SRC="$REPO_ROOT/plugin/docs"
DOCS_DEST="${XDG_DATA_HOME:-$HOME/.local/share}/ai-tooling/docs"

skills_dest_for() {
  case "$1" in
    opencode) printf '%s\n' "$HOME/.agents/skills" ;;
    hermes)   printf '%s\n' "$HOME/.hermes/skills" ;;
    *)        printf 'unknown harness: %s (expected opencode or hermes)\n' "$1" >&2; exit 2 ;;
  esac
}

render_skills() {
  local dest="$1" dir name
  mkdir -p "$dest"
  for dir in "$SKILLS_SRC"/*/; do
    name="$(basename "$dir")"
    mkdir -p "$dest/$name"
    sed 's|\${AI_TOOLING_DOCS}|'"$DOCS_DEST"'|g' "$dir/SKILL.md" > "$dest/$name/SKILL.md"
  done
}

install_docs() {
  mkdir -p "$DOCS_DEST"
  rsync -a --delete "$DOCS_SRC/" "$DOCS_DEST/"
}
```

Then the second half of `install-harness.sh`:

```bash
check_installed() {
  local found=0 incomplete=0 dest dir name f
  for dest in "$HOME/.agents/skills" "$HOME/.hermes/skills"; do
    [ -d "$dest" ] || continue
    found=1
    for dir in "$SKILLS_SRC"/*/; do
      name="$(basename "$dir")"
      f="$dest/$name/SKILL.md"
      if [ ! -f "$f" ]; then
        printf 'MISSING %s\n' "$f"; incomplete=1
      elif grep -q 'AI_TOOLING_DOCS' "$f"; then
        printf 'UNRESOLVED %s\n' "$f"; incomplete=1
      fi
    done
    [ "$incomplete" = 0 ] && printf 'OK %s\n' "$dest"
  done
  if [ "$found" = 0 ]; then
    printf 'no harness install found (looked in ~/.agents/skills and ~/.hermes/skills)\n'
    return 1
  fi
  return "$incomplete"
}

main() {
  case "${1:-}" in
    --check) check_installed ;;
    opencode|hermes)
      render_skills "$(skills_dest_for "$1")"
      install_docs
      printf 'installed %s: %s + %s\n' "$1" "$(skills_dest_for "$1")" "$DOCS_DEST"
      if [ "$1" = hermes ]; then
        printf 'next: hermes plugins install lychan110/ai-tooling && hermes plugins enable ai-tooling-harness\n'
      fi
      ;;
    *) printf 'usage: bash install-harness.sh opencode|hermes|--check\n' >&2; exit 2 ;;
  esac
}

main "$@"
```

### T3.4 GREEN — run it, then prove the real path

    uv run -m unittest -q test_automation.TestInstallHarness
    # → Ran 1 test ... OK

Then on this machine, using one temp HOME twice:

    H="$(mktemp -d)"; HOME="$H" bash install-harness.sh opencode
    # → installed opencode: $H/.agents/skills + $H/.local/share/ai-tooling/docs
    HOME="$H" bash install-harness.sh --check; echo "exit=$?"
    # → OK $H/.agents/skills      ...      exit=0
    ls "$H/.agents/skills"
    # → audit-workflow  evaluate-tool  setup-workflow  sync-stars  update-catalog
    grep -c 'AI_TOOLING_DOCS' "$H/.agents/skills/setup-workflow/SKILL.md"
    # → 0        (every occurrence was resolved)
    ls "$H/.local/share/ai-tooling/docs/STACK.md"
    # → the file

### T3.5 Gate and commit

    make check-offline RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy; echo "exit=$?"   # → exit=0
    but commit -b chore/opencode-hermes-install -m "feat(dist): render the distributable into opencode and Hermes global dirs"

## T4 — Rewrite the two install front doors

### T4.1 RED — pin the new front door

Add to `TestPluginPackage` (this is the pin deferred out of T2), and delete
`test_readme_install_commands_use_real_subcommands` (lines 9041-9048):

```python
    def test_the_public_docs_teach_harness_installs_not_a_marketplace(self):
        for rel in ("README.md", "plugin/README.md"):
            text = Path(ROOT, rel).read_text(encoding="utf-8")
            self.assertNotIn("claude plugin marketplace add", text, msg=rel)
            self.assertNotIn("claude plugin install", text, msg=rel)
            self.assertNotIn("CLAUDE_PLUGIN_ROOT", text, msg=rel)
            self.assertIn("install-harness.sh", text, msg=rel)
```

### T4.2 RED — watch it fail

    uv run -m unittest -q test_automation.TestPluginPackage
    # → FAILED (failures=1) on the new test

### T4.3 GREEN — replace the `README.md` Install section

Replace everything from `## Install` up to (not including) `The five skills:` with:

```markdown
## Install

Built for opencode and Hermes Agent — there is no marketplace and no account.

**opencode** reads `AGENTS.md`, `.agents/skills/` and `opencode.json` straight from the
checkout. To use the five distributable skills from any project on the machine:

    bash install-harness.sh opencode

**Hermes Agent** loads `AGENTS.md` as project context and discovers `.agents/skills/` after a
one-time trust:

    bash install-harness.sh hermes
    hermes skills trust "$PWD"      # only needed to use the repo-local skills in place

Both harnesses drive the same gates: `make check`, `make fix`, `./sync-plugin-docs.sh`. See
[docs/agents/harness-install.md](docs/agents/harness-install.md) for exactly what each
installer writes, how to verify it, and how to remove it.
```

### T4.4 GREEN — rewrite the top of `plugin/README.md`

Replace lines 1-11 (the `# ai-tooling Plugin` heading through the opencode/Hermes note) with:

```markdown
# ai-tooling skills

Five skills for bootstrapping and maintaining an AI-assisted workflow, installable on
opencode or Hermes Agent. No marketplace, no account, no plugin registry.

    git clone https://github.com/lychan110/ai-tooling && cd ai-tooling
    bash install-harness.sh opencode     # or: bash install-harness.sh hermes

Each skill reads the reference documents in `docs/`; the installer renders them once to
`~/.local/share/ai-tooling/docs/` and points every installed skill at that directory, so the
skills work from any project without the checkout being your working directory.
```

Also replace the closing line of "Reference Documents" —
`Skills reference these docs via \`${CLAUDE_PLUGIN_ROOT}/docs/\` paths.` — with:

    Skills reference these docs through the installer-resolved `~/.local/share/ai-tooling/docs/` path.

Leave the `## Skills` list exactly as it is: `check-plugin.py` gates it against the
directories on disk, so a missing or extra bullet is a finding.

### T4.5 GREEN — add `docs/agents/harness-install.md`

New file, kept short and factual:

```markdown
# Installing on opencode or Hermes

`bash install-harness.sh <harness>` renders the five skills in `plugin/skills/` into that
harness's global skill directory, and the reference docs into one shared location.

| | opencode | Hermes |
|---|---|---|
| Skills | `~/.agents/skills/<name>/SKILL.md` | `~/.hermes/skills/<name>/SKILL.md` |
| Docs | `~/.local/share/ai-tooling/docs/` | the same directory |
| Discovery | automatic — opencode loads global agent-compatible skills | automatic |
| Commit gate | `.opencode/plugins/` (repo-local, auto-loaded) | `hermes plugins install lychan110/ai-tooling`, then `hermes plugins enable ai-tooling-harness` |

`${AI_TOOLING_DOCS}` is the placeholder that makes this work. It appears in
`plugin/skills/*/SKILL.md`; the repo-local render strips it (so `STACK.md` resolves at the
repo root), and the installer replaces it with the absolute docs directory. That is the one
substitution point — never hand-write an absolute path into a skill.

Verify with `bash install-harness.sh --check`: exit 0 and one `OK <dir>` line per installed
harness. To remove an install, delete the skill directories it created plus
`~/.local/share/ai-tooling/`.
```

### T4.6 Verify and commit

    uv run -m unittest -q test_automation.TestPluginPackage    # → OK
    uv run check-plugin.py --check; echo "exit=$?"            # → exit=0
    grep -rn 'claude plugin' README.md plugin/README.md plugin/skills/    # → no output
    make check-offline RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy; echo "exit=$?"   # → exit=0
    but commit -b chore/opencode-hermes-install -m "docs(dist): document the opencode and Hermes install paths"

## T5 — Verify the install for real, on this machine

The unit tests use a temp HOME and prove the renderer. This task proves the *harness* accepts
what it writes — the part no unit test can reach.

### T5.1 opencode

    H="$(mktemp -d)"; HOME="$H" bash install-harness.sh opencode
    ls "$H/.agents/skills"/*/SKILL.md | wc -l        # → 5
    head -3 "$H/.agents/skills/evaluate-tool/SKILL.md"
    # → ---
    # → name: evaluate-tool
    # → description: ...

Then install into your own HOME if you want it there:

    bash install-harness.sh opencode && bash install-harness.sh --check; echo "exit=$?"
    # → OK /home/<you>/.agents/skills          exit=0

opencode's loader requires frontmatter `name` + `description` with `name` equal to the
directory — exactly what `check-plugin.py` gates, so a green gate means the loader accepts it.

### T5.2 Hermes — validate the adapter before trusting it

    hermes plugins compat .hermes/plugins/ai-tooling-harness; echo "exit=$?"
    # → exit=0; non-zero would name each file:line whose import the Sep 2026 decomposition retired
    hermes plugins validate .hermes/plugins/ai-tooling-harness; echo "exit=$?"
    # → exit=0 if catalog-admissible, otherwise a finding per line

### T5.3 Hermes — the machine-wide plugin install

`hermes plugins install` accepts a Git URL or `owner/repo`. This repo's adapter lives at a
nested path (`.hermes/plugins/ai-tooling-harness/`), so **verify before documenting it**:

    hermes plugins install --help

Read the accepted forms; look specifically for a subdirectory/path argument.

- **If a nested path is supported**, run it and record the exact command in
  `docs/agents/harness-install.md`.
- **If it is not**, do not invent one. Document the manual path instead:

      cp -r .hermes/plugins/ai-tooling-harness ~/.hermes/plugins/
      hermes plugins enable ai-tooling-harness

**STOP** if the only honest instruction would be `hermes plugins install lychan110/ai-tooling`
and that command does not resolve the nested plugin. Report it rather than shipping a command
you could not run — detector A exists in this repo precisely because "a broken command means
the tool was likely never run".

## T6 — Cross-references and the plan index

### T6.1 `AGENTS.md`

- "Start here": change the `plugin/` bullet from "Claude Code marketplace packaging for the
  same skills" to "the distributable: the five installable skills plus the rendered docs".
  The two "Source of truth" bullets about `plugin/docs/` and `plugin/README.md` stay.
- "Canonical commands": add `bash install-harness.sh --check` — verify the opencode/Hermes
  skill install.

### T6.2 `plans/README.md`

Add after the 017 row in the execution table:

```markdown
| [018](../docs/plans/018-opencode-hermes-distribution.md) | Install on opencode and Hermes; delete the Claude Code marketplace | P1 | M | 016 | IN PROGRESS <date> |
```

And a Run 5 paragraph above the table:

    **Run 5** — distribution, 2026-09-15 (audit at commit `a9af153`). Focus: finish the
    decoupling plan 016 started. Plan 018 — the Claude marketplace packaging goes, and one
    `install-harness.sh` renders the same five skills into opencode's and Hermes's global
    skill directories.

### T6.3 Record the S5 decision in plan 016

In `plans/016-decouple-from-claude-code.md`, replace S5's "Do not guess" sentence with one
line recording that the owner decided, linking plan 018.

### T6.4 `AGENTS.md` — write the testing convention down

The convention must live in the repo, not only in this plan, so the next implementer
inherits it. Add to `AGENTS.md` under `## Required invariants` (already a bulleted list):

    - Tests are end-to-end and deliberately few: exercise the real artifact against a
      throwaway target, then assert the result a user would see. No unit tests for internal
      helpers, no smoke tests, and no assertions of the obvious (a file exists because the
      previous line created it; a bad argument exits non-zero). The only test worth adding is
      one that would fail if the behaviour regressed.

Then check nothing in the repo contradicts it — and fix only statements about *this* repo's
own tests, not prose describing other tools' testing:

    rg -n 'smoke test|unit test|test coverage' AGENTS.md README.md WORKFLOW.md docs/agents/

## T7 — Final gate and PR

    make check RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy; echo "exit=$?"   # → exit=0 (network: detector A)
    ./sync-plugin-docs.sh --check                                       # → sync check: OK
    bash install-harness.sh --check                                     # → OK / exit 0
    but push chore/opencode-hermes-install
    but pr new chore/opencode-hermes-install -m "chore(dist): install on opencode and Hermes, delete the Claude marketplace"

`-m` sets the PR **title** only; set the body afterwards through the GitHub MCP and read it
back before reporting success.

## Deliverables

| # | Path | What |
|---|---|---|
| 1 | `install-harness.sh` | renders `plugin/skills/` + `plugin/docs/` into a harness's global dirs |
| 2 | `plugin/skills/*/SKILL.md` (5; four edited) | `${AI_TOOLING_DOCS}` replaces `${CLAUDE_PLUGIN_ROOT}/docs/` |
| 3 | `.claude-plugin/`, `plugin/.claude-plugin/`, `plugin/hooks/hooks.json` | **deleted** |
| 4 | `check-plugin.py` | repointed: `SKILL` + `FRONT-DOOR` + `HARNESS`, no manifest checks |
| 5 | `sync-plugin-docs.sh` | strips `${AI_TOOLING_DOCS}/` instead of the Claude prefix |
| 6 | `README.md`, `plugin/README.md` | install sections teach opencode + Hermes |
| 7 | `docs/agents/harness-install.md` | new: targets, verification, removal |
| 8 | `test_automation.py` | `TestInstallHarness` added; Claude pins replaced |
| 9 | `AGENTS.md`, `plans/README.md`, `plans/016-decouple-from-claude-code.md` | cross-refs, the S5 decision, and the testing convention |

## Tests / validation

| Check | Command | Expected |
|---|---|---|
| renderer contract | `uv run -m unittest -q test_automation.TestInstallHarness` | 1 test, OK |
| package structure | `uv run check-plugin.py --check; echo $?` | 0 |
| full gate | `make check RUFF=.venv/bin/ruff MYPY=.venv/bin/mypy; echo $?` | 0, `OK (skipped=2)` |
| no self-install left | `rg -n 'marketplace add mattbutlerengineering' .` | no output |
| install works | `H=$(mktemp -d); HOME=$H bash install-harness.sh opencode; HOME=$H bash install-harness.sh --check` | `OK`, exit 0 |
| token resolved | `rg -c 'AI_TOOLING_DOCS' "$H/.agents/skills/setup-workflow/SKILL.md"` | no match (all resolved) |
| Hermes adapter | `hermes plugins compat .hermes/plugins/ai-tooling-harness; echo $?` | 0 |

## Risks, tradeoffs, and open questions

- **Removing a published install path is one-way for existing users.** Anyone who already ran
  `claude plugin marketplace add mattbutlerengineering/ai-tooling` keeps a cached copy; this
  plan only stops the repo from advertising and maintaining it. If Claude Code users should
  keep getting updates, that needs a separately-published copy — a product call, out of scope.
- **A git clone is still the install unit for the skills.** `hermes plugins install owner/repo`
  can fetch the adapter, but the *skills* come from a local clone through `install-harness.sh`.
  Registry-published skills (`hermes skills publish`, an npm package for opencode's `plugin`
  array) are deliberately out of scope — YAGNI until someone actually needs them.
- **The shared docs directory is a machine-level singleton.** `~/.local/share/ai-tooling/docs/`
  is overwritten by every install, so two checkouts of different vintages will fight over it.
  Fine for one user with one clone; revisit if that stops being true.
- **Open question**: does opencode read `~/.agents/skills/` per session or cache it at startup?
  The docs describe startup loading. If it caches, re-installing needs a restart — worth one
  line in `docs/agents/harness-install.md` once observed.
- **Open question**: whether `hermes plugins validate` requires the plugin to be *installed*
  rather than merely present on disk. T5.2 answers it; if it needs an install, run T5.3 first.
- **Do not reintroduce `plugin/package.json`.** `#439` deleted one on purpose: a second version
  declaration is a second place for the number to drift, and nothing here publishes to npm.
- **`test_live_package_is_clean` is the tripwire for a half-finished migration.** It fails
  until the manifests are gone *and* `check-plugin.py` has been repointed, which is why T2 does
  both in one commit. If it is still red at the end of T2, something in the deletion is partial.