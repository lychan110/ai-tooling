#!/usr/bin/env bash
# Sync root documentation to plugin/docs/ so the installable plugin stays current.
# Also syncs root skills/ from plugin/skills/ (plugin is authoritative for skills).
# Run before publishing or via pre-commit hook.
#
#   ./sync-plugin-docs.sh                # apply: write the synced tree in place
#   ./sync-plugin-docs.sh --check        # verify only: exit 1 if plugin/docs or skills
#                                          would change; mutate nothing (CI/pre-commit gate)
#   ./sync-plugin-docs.sh --list-watched # print the watch set (one entry per line,
#                                          dirs with a trailing /) and exit; the
#                                          harness auto-sync hooks derive their trigger
#                                          predicate from this instead of restating it (#194)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DOCS="$REPO_ROOT/plugin/docs"
PLUGIN_SKILLS="$REPO_ROOT/plugin/skills"
ROOT_SKILLS="$REPO_ROOT/skills"

# The watch set — the one definition of what this script mirrors into plugin/docs/.
# The copy loop below iterates these arrays; adapters consume the same set via
# --list-watched (pinned by TestWatchListSeam). The apply-mode verify block at the
# bottom still spot-checks a hand-picked subset — it is a count sanity-check, not
# a second definition of the set.
WATCHED_FILES=(CATALOG.md WORKFLOW.md STACK.md STACK-LEDGER.md NEXT-EVALS.md WATCHLIST.md PLAYBOOK.md)
WATCHED_DIRS=(evaluations discovery methodologies)

CHECK=0
case "${1:-}" in
  --check) CHECK=1 ;;
  --list-watched)
    printf '%s\n' "${WATCHED_FILES[@]}"
    printf '%s/\n' "${WATCHED_DIRS[@]}"
    exit 0
    ;;
esac

# apply mode writes straight to the real destinations; --check exits above.
DEST_DOCS="$PLUGIN_DOCS"
DEST_SKILLS="$ROOT_SKILLS"

# --- Check mode: build the would-be-synced tree and compare it, entirely in Python ---
# rsync is not portable here (the Windows scoop build parses a C:/ path as an ssh
# host), and native Python cannot read MSYS-style paths handed in from bash, so the
# whole check runs in one Python process rooted at the repo: it builds the tree apply
# mode would write into a tempfile scratch dir, repoints links, strips the skill
# placeholder, and byte-compares against plugin/docs/ and skills/. Relative paths
# (cwd = repo root) keep it portable across POSIX and Windows.
if [ "$CHECK" = 1 ]; then
  (
    cd "$REPO_ROOT" || exit 1
    uv run python - "${WATCHED_FILES[@]}" -- "${WATCHED_DIRS[@]}" <<'PY'
import importlib.util, os, re, shutil, sys, tempfile

rest = sys.argv[1:]
sep = rest.index("--")
files, dirs = rest[:sep], rest[sep + 1:]
plugin_docs, root_skills, plugin_skills = "plugin/docs", "skills", "plugin/skills"

spec = importlib.util.spec_from_file_location(
    "rewrite_doc_links", os.path.abspath("rewrite-doc-links.py"))
rdl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rdl)


def tree(root):
    out = {}
    for dp, _, fns in os.walk(root):
        for fn in fns:
            full = os.path.join(dp, fn)
            out[os.path.relpath(full, root).replace(os.sep, "/")] = full
    return out


def same(a, b):
    ta, tb = tree(a), tree(b)
    if set(ta) != set(tb):
        return False
    for rel in ta:
        with open(ta[rel], "rb") as x, open(tb[rel], "rb") as y:
            if x.read() != y.read():
                return False
    return True


with tempfile.TemporaryDirectory() as tmp:
    dest_docs = os.path.join(tmp, "docs")
    dest_skills = os.path.join(tmp, "skills")
    os.makedirs(dest_docs)
    for f in files:
        shutil.copy2(f, os.path.join(dest_docs, f))
    for d in dirs:
        dst = os.path.join(dest_docs, d)
        os.makedirs(dst)
        shutil.copytree(d, dst, dirs_exist_ok=True)
    rdl.rewrite_tree(dest_docs, os.path.abspath("."))
    pat = re.compile(rb"\$\{AI_TOOLING_DOCS\}/")
    for name in sorted(os.listdir(plugin_skills)):
        src_dir = os.path.join(plugin_skills, name)
        if not os.path.isdir(src_dir):
            continue
        dst_dir = os.path.join(dest_skills, name)
        os.makedirs(dst_dir, exist_ok=True)
        with open(os.path.join(src_dir, "SKILL.md"), "rb") as fh:
            data = fh.read()
        with open(os.path.join(dst_dir, "SKILL.md"), "wb") as fh:
            fh.write(pat.sub(b"", data))
    ok = same(dest_docs, plugin_docs) and same(dest_skills, root_skills)

if ok:
    print("sync check: OK — plugin/docs/ and skills/ are in sync with root")
    sys.exit(0)
print("sync check: DRIFT — plugin/docs/ or skills/ is stale; run ./sync-plugin-docs.sh and commit the result", file=sys.stderr)
sys.exit(1)
PY
  )
  exit $?
fi

# --- Docs: root → plugin/docs (Windows-safe; replaces `cp` + `rsync -a --delete`) ---
# rsync on this Windows host parses a C:/ path as an ssh host, so the copy runs in
# Python rooted at the repo: watched files verbatim, watched dirs mirrored (extraneous
# entries removed — the shape `rsync -a --delete` had). Native Python cannot read MSYS
# paths, so the build uses repo-relative paths with cwd at the repo root.
(
  cd "$REPO_ROOT" || exit 1
  uv run python - "${WATCHED_FILES[@]}" -- "${WATCHED_DIRS[@]}" <<'PY'
import os
import shutil
import sys

rest = sys.argv[1:]
sep = rest.index("--")
files, dirs = rest[:sep], rest[sep + 1:]
dest_docs = "plugin/docs"

os.makedirs(dest_docs, exist_ok=True)
for f in files:
    shutil.copy2(f, os.path.join(dest_docs, f))
for d in dirs:
    if not os.path.isdir(d):
        continue
    dst = os.path.join(dest_docs, d)
    if os.path.isdir(dst):
        want = set()
        for dp, _, fns in os.walk(d):
            for fn in fns:
                want.add(os.path.normcase(os.path.normpath(
                    os.path.join(os.path.relpath(dp, d), fn))))
        for dp, _, fns in os.walk(dst):
            for fn in fns:
                rel = os.path.normpath(os.path.join(os.path.relpath(dp, dst), fn))
                if os.path.normcase(rel) not in want:
                    os.remove(os.path.join(dp, fn))
    shutil.copytree(d, dst, dirs_exist_ok=True)
PY
)

# --- Repoint links that leave the bundle (#437) ---
# The copies above are verbatim, so a relative link whose target is NOT in the watch
# set lands in a tree the target is not in — 16 were dead that way, 3 of them on the
# bundle's own front page. The rewrite is depth-only: a link broken at ROOT stays
# broken here, so check-links.py keeps reporting it where the fix belongs.
(
  cd "$REPO_ROOT" || exit 1
  uv run python - <<'PY'
import importlib.util
import os

spec = importlib.util.spec_from_file_location(
    "rewrite_doc_links", os.path.abspath("rewrite-doc-links.py"))
rdl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rdl)
print(f"link rewrite: {rdl.rewrite_tree('plugin/docs', os.path.abspath('.'))} file(s) repointed")
PY
) > /dev/null

# --- Skills: plugin/skills/ → DEST_SKILLS (strip ${AI_TOOLING_DOCS}/ paths) ---
(
  cd "$REPO_ROOT" || exit 1
  uv run python - <<'PY'
import os
import re

pat = re.compile(rb"\$\{AI_TOOLING_DOCS\}/")
src_skills = "plugin/skills"
if os.path.isdir(src_skills):
    for name in sorted(os.listdir(src_skills)):
        src_dir = os.path.join(src_skills, name)
        if not os.path.isdir(src_dir):
            continue
        dst_dir = os.path.join("skills", name)
        os.makedirs(dst_dir, exist_ok=True)
        with open(os.path.join(src_dir, "SKILL.md"), "rb") as fh:
            data = fh.read()
        with open(os.path.join(dst_dir, "SKILL.md"), "wb") as fh:
            fh.write(pat.sub(b"", data))
PY
)

# --- Verify (apply mode) ---
# Entry counts come from catalog_lib.catalog_count — the one implementation of
# "what counts as a catalog row" (#195). A grep here had subtly different
# whitespace rules and could silently diverge.
# Runs from REPO_ROOT so the repo's catalog_lib.py resolves first, wherever the
# caller's cwd is (a `-c` snippet puts cwd at the head of sys.path).
count_catalog_entries() {
  (cd "$REPO_ROOT" && uv run python -c '
import sys, catalog_lib
with open(sys.argv[1], encoding="utf-8") as f:
    print(catalog_lib.catalog_count(f.read()))' "$1")
}
root_entries=$(count_catalog_entries "CATALOG.md")
plugin_entries=$(count_catalog_entries "plugin/docs/CATALOG.md")
root_evals=$(ls "$REPO_ROOT/evaluations/"*.md 2>/dev/null | wc -l | tr -d ' ')
plugin_evals=$(ls "$PLUGIN_DOCS/evaluations/"*.md 2>/dev/null | wc -l | tr -d ' ')
root_discovery=$(ls "$REPO_ROOT/discovery/"*.md 2>/dev/null | wc -l | tr -d ' ')
plugin_discovery=$(ls "$PLUGIN_DOCS/discovery/"*.md 2>/dev/null | wc -l | tr -d ' ')
skill_count=$(ls -d "$PLUGIN_SKILLS"/*/ 2>/dev/null | wc -l | tr -d ' ')

echo "Synced: CATALOG.md ($plugin_entries entries), WORKFLOW.md, evaluations/ ($plugin_evals files), discovery/ ($plugin_discovery files), skills/ ($skill_count skills)"

if [ "$root_entries" != "$plugin_entries" ] || [ "$root_evals" != "$plugin_evals" ] || [ "$root_discovery" != "$plugin_discovery" ]; then
  echo "WARNING: count mismatch after sync — root has $root_entries entries/$root_evals evals/$root_discovery discovery, plugin has $plugin_entries/$plugin_evals/$plugin_discovery"
  exit 1
fi
