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
