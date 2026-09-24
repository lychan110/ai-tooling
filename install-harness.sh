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
    *)        printf 'unknown harness: %s (expected opencode or hermes)\n' "$1" >&2 ; exit 2 ;;
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
        printf 'next: enable the repo-local plugin for this checkout — HERMES_ENABLE_PROJECT_PLUGINS=true plus an `ai-tooling-harness` entry in plugins.enabled (see docs/agents/hermes-harness.md). Do NOT copy it to ~/.hermes/plugins/: REPO = parents[3] would then resolve to your HOME and the gate fails open, silently.\n'
      fi
      ;;
    *) printf 'usage: bash install-harness.sh opencode|hermes|--check\n' >&2 ; exit 2 ;;
  esac
}

main "$@"
