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
