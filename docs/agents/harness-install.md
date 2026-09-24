# Installing on opencode or Hermes

`bash install-harness.sh <harness>` renders the five skills in `plugin/skills/` into that
harness's global skill directory, and the reference docs into one shared location.

| | opencode | Hermes |
|---|---|---|
| Skills | `~/.agents/skills/<name>/SKILL.md` | `~/.hermes/skills/<name>/SKILL.md` |
| Docs | `~/.local/share/ai-tooling/docs/` | the same directory |
| Discovery | automatic — opencode loads global agent-compatible skills | automatic |
| Commit gate | `.opencode/plugins/` (repo-local, auto-loaded) | **repo-local only**: `HERMES_ENABLE_PROJECT_PLUGINS=true` plus a hand-added `ai-tooling-harness` entry in `plugins.enabled` — enable this checkout, never copy it to `~/.hermes/plugins/` (see the warning below) |

${AI_TOOLING_DOCS} is the placeholder that makes this work. It appears in
`plugin/skills/*/SKILL.md`; the repo-local render strips it (so `STACK.md` resolves at the
repo root), and the installer replaces it with the absolute docs directory. That is the one
substitution point — never hand-write an absolute path into a skill.

Verify with `bash install-harness.sh --check`: exit 0 and one `OK <dir>` line per installed
harness. To remove an install, delete the skill directories it created plus
`~/.local/share/ai-tooling/`. `--check` covers the **skills and docs only** — it cannot see the
commit gate, so a green `--check` is not evidence the gate is active.

## The commit gate is repo-local by construction — do not copy it to `~/.hermes/plugins/`

`ai-tooling-harness` derives its target from its own path:
`REPO = Path(__file__).resolve().parents[3]`, which is `<repo>` only for
`<repo>/.hermes/plugins/ai-tooling-harness/__init__.py`. Copied to
`~/.hermes/plugins/ai-tooling-harness/`, the same expression resolves to your **HOME**: the
`make check-data` probe fails, and because the adapter is deliberately fail-open
("cannot run is not failed") the commit gate and the `plugin/docs` auto-sync both go **silently
inert** — no error, no warning. Enable the repo-local plugin instead, exactly as
[`hermes-harness.md`](hermes-harness.md) describes. Verified 2026-09-24: repo-local probe exit 0,
user-copy probe exit 2 with no `Makefile` at the resolved root.