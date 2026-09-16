# Installing on opencode or Hermes

`bash install-harness.sh <harness>` renders the five skills in `plugin/skills/` into that
harness's global skill directory, and the reference docs into one shared location.

| | opencode | Hermes |
|---|---|---|
| Skills | `~/.agents/skills/<name>/SKILL.md` | `~/.hermes/skills/<name>/SKILL.md` |
| Docs | `~/.local/share/ai-tooling/docs/` | the same directory |
| Discovery | automatic — opencode loads global agent-compatible skills | automatic |
| Commit gate | `.opencode/plugins/` (repo-local, auto-loaded) | copy `.hermes/plugins/ai-tooling-harness/` into `~/.hermes/plugins/`, then `hermes plugins enable ai-tooling-harness` |

${AI_TOOLING_DOCS} is the placeholder that makes this work. It appears in
`plugin/skills/*/SKILL.md`; the repo-local render strips it (so `STACK.md` resolves at the
repo root), and the installer replaces it with the absolute docs directory. That is the one
substitution point — never hand-write an absolute path into a skill.

Verify with `bash install-harness.sh --check`: exit 0 and one `OK <dir>` line per installed
harness. To remove an install, delete the skill directories it created plus
`~/.local/share/ai-tooling/`.