# Hermes harness support

The Hermes Agent harness can drive this repository the way opencode does. Support ships as a project-local plugin at `.hermes/plugins/ai-tooling-harness/` (one module plus `plugin.yaml`), mirroring the two opencode plugins in `.opencode/plugins/`.

## Enable it - one time per machine

Project-local plugins are deliberately off by default: a plugin that can rewrite a commit should never be enabled by accident.

```bash
export HERMES_ENABLE_PROJECT_PLUGINS=true   # makes repo-local plugins discoverable
hermes skills trust "$PWD"                 # trust repo-local skills under .agents/skills/
```

Both halves are needed, and both are deliberate:

```yaml
# ~/.hermes/config.yaml
plugins:
  enabled:
    - ai-tooling-harness     # discovered is not loaded
```

`hermes plugins list` never shows a repo-local plugin and `hermes plugins enable` refuses it
("not installed or bundled" - that path manages bundled and user plugins), so the
`plugins.enabled` entry is added by hand. `hermes skills trust` also takes the project root
explicitly - bare, it trusts the enclosing git checkout of the *process* working directory,
which is not always the repo you are standing in. With only the environment variable set the adapter
is discovered but never loaded, and the gate stays silent - observed live on this repo.
`hermes plugins compat .hermes/plugins/ai-tooling-harness` is the pre-flight check for a
directory you are about to trust: it exits non-zero and names each file:line when an import
has been retired.

`AGENTS.md` needs no Hermes-specific wiring - Hermes loads it as project context on its own.

## What it does

Two halves, mirroring the opencode plugins in `.opencode/plugins/`:

| Half | Trigger | Effect |
|---|---|---|
| Commit gate | `tool_request` middleware | A `git commit` whose `make check-data` probe fails is rewritten into a diagnostic echo, with the diagnostic base64-preserved so shell quoting cannot mangle it. |
| Auto-sync | `post_tool_call` hook | After a write, edit, or patch touching a root doc that `./sync-plugin-docs.sh --list-watched` reports, the sync re-runs so `plugin/docs/` cannot drift. It never fires for `plugin/docs/` itself, which is what stops a sync loop. |

**Fail-open is the contract.** Only a non-zero `check-data` blocks a commit. If `make`, `uv`, or the `check-data` target cannot be probed, or the gate cannot run at all, the commit passes unchanged - the repository rule that unknown and unreachable are not the same as absent and broken.

**The hook second parameter is `args`, not `params`.** Hermes calls plugin hooks by keyword with the documented payload. Any other name means the hook silently never fires.

**The blocked rewrite emits its diagnostic with `echo`, never `printf`.** `printf` is deny-listed in the operator's config, and a rewritten command the deny layer refuses explains nothing; the payload is base64, so neither quoting nor a deny layer can mangle it.

## One implementation, two triggers

Neither harness owns gate logic. Both call the same two scripts - `make check-data` and `./sync-plugin-docs.sh` - and `test_automation.py` pins the agreement so the adapters cannot drift apart: `TestHermesHarnessAdapter` covers this adapter, and `TestHookTriggerSeam` pins the single commit predicate both adapters must match.

## When it misbehaves

Silence is the normal state, because the plugin is fail-open by design. The tests are the specification:

```bash
uv run -m unittest -q test_automation.TestHermesHarnessAdapter
```

Related: `.opencode/plugins/` (the opencode twins), `docs/plans/017-hermes-harness-support.md` (design and rationale), and `AGENTS.md` (the project rules both harnesses read).
