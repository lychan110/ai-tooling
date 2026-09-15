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
