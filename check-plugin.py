#!/usr/bin/env -S uv run --script
"""The distributable skills in `plugin/` must be structurally valid and internally consistent.

    uv run check-plugin.py            # report-only
    uv run check-plugin.py --check    # gate: exit 1 on any finding

Detector A gates every install command in `STACK.md`, `CATALOG.md` and `evaluations/`
because "a broken command means the tool was likely never run", and #416 sharpened that
to the page: STACK is the page whose whole purpose is to be executed. `README.md`'s
Install block is the only page here whose purpose is to be executed *by a stranger, on
this repo's own product*, and nothing checked it — neither of its two commands existed,
and `claude plugin validate ./plugin` failed outright on a missing manifest (#439).

This mirrors offline the parts of the package that are checkable from the tree. The
skills list in `plugin/README.md` is a fact restated in a hand-authored file with no
generator, which is the shape that put its eval count 87 behind (#302); the repo's own
rule is to gate the shared facts, not the file.


"""
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

Finding = collections.namedtuple("Finding", "kind detail")

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
# `plugin/README.md` lists each skill as "- `/name` — description".
_LISTED_SKILL = re.compile(r"^-\s*`/([a-z0-9][a-z0-9-]*)`", re.MULTILINE)


def skill_dirs(root):
    d = os.path.join(root, "plugin", "skills")
    if not os.path.isdir(d):
        return []
    return sorted(n for n in os.listdir(d) if os.path.isdir(os.path.join(d, n)))


def frontmatter_field(text, field):
    m = _FRONTMATTER.search(text)
    if not m:
        return None
    hit = re.search(rf"^{field}:\s*(.+)$", m.group(1), re.MULTILINE)
    return hit.group(1).strip() if hit else None


def audit_plugin(root=None):
    """Findings for the plugin package. Offline; reads only the tree."""
    root = root or ROOT
    findings = []

    on_disk = skill_dirs(root)
    for name in on_disk:
        path = os.path.join(root, "plugin", "skills", name, "SKILL.md")
        if not os.path.exists(path):
            findings.append(Finding("SKILL", f"{name}/ has no SKILL.md"))
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        declared = frontmatter_field(text, "name")
        if not declared:
            findings.append(Finding("SKILL", f"{name}/SKILL.md declares no `name:` frontmatter"))
        elif declared != name:
            findings.append(Finding("SKILL", f"{name}/SKILL.md declares name {declared!r}"))
        if not frontmatter_field(text, "description"):
            findings.append(Finding("SKILL", f"{name}/SKILL.md declares no `description:` frontmatter"))
        if "CLAUDE_PLUGIN_ROOT" in text:
            findings.append(Finding("HARNESS", f"{name}/SKILL.md names ${{CLAUDE_PLUGIN_ROOT}}, "
                                               "which exists only inside Claude Code"))

    # A `CLAUDE.md` back at the plugin root is the mistake returning, not a second
    # front door: `claude plugin validate` warns that Claude Code never loads it (#441).
    stray = os.path.join(root, "plugin", "CLAUDE.md")
    if os.path.exists(stray):
        findings.append(Finding("FRONT-DOOR", "plugin/CLAUDE.md is never loaded by Claude Code — "
                                              "the plugin's documented front door is plugin/README.md"))
    front = os.path.join(root, "plugin", "README.md")
    if os.path.exists(front):
        with open(front, encoding="utf-8") as fh:
            listed = sorted(set(_LISTED_SKILL.findall(fh.read())))
        for name in sorted(set(listed) - set(on_disk)):
            findings.append(Finding("FRONT-DOOR", f"plugin/README.md lists /{name}, which is not in plugin/skills/"))
        for name in sorted(set(on_disk) - set(listed)):
            findings.append(Finding("FRONT-DOOR", f"plugin/skills/{name}/ is not listed in plugin/README.md"))

    return findings


def main():
    check = "--check" in sys.argv
    findings = audit_plugin()
    label = "gate" if check else "report-only"
    print(f"== plugin package ({label}) — {len(findings)} finding(s) ==")
    for f in findings:
        print(f"  {f.kind} {f.detail}")
    if not findings:
        print("  OK — every skill's frontmatter names it and the front door lists every skill")
        return 0
    return 1 if check else 0


if __name__ == "__main__":
    sys.exit(main())
