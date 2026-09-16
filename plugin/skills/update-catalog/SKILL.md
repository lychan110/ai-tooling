---
name: update-catalog
description: Sync the AI tooling catalog with current GitHub stars and locally installed tools
---

# Update Catalog

Refresh the catalog by checking for new GitHub stars, newly installed local tools, and stale entries.

## Trigger

`/update-catalog`

## Workflow

### 1. Get current sources

```bash
# Current GitHub stars
gh api user/starred --paginate --jq '.[].full_name'

# Current harness plugins, skills, MCP servers
hermes plugins list 2>/dev/null
ls .agents/skills/ ~/.hermes/skills/ 2>/dev/null
cat opencode.json ~/.config/opencode/opencode.json 2>/dev/null
```

### 2. Diff against catalog

Read `${AI_TOOLING_DOCS}/CATALOG.md`. Compare:
- **New stars not in catalog** — research each one and classify as AI_DEV_TOOL or NOT_RELEVANT
- **Unstarred repos still in catalog** — flag but don't remove (may still be relevant)
- **New local installs not in catalog** — add them
- **Removed local installs still in catalog** — update if they were marked as installed

### 3. Research new entries

For each new AI_DEV_TOOL:

```bash
gh api repos/{owner}/{repo} --jq '.description'
```

Determine: name, type, category, one-liner, problem it solves, overlaps with.

### 4. Update

- Add new entries to the correct category table in `${AI_TOOLING_DOCS}/CATALOG.md`
- Fill "Overlaps with" by checking existing entries in the same category
- If a new entry overlaps with a tool in `${AI_TOOLING_DOCS}/WORKFLOW.md`, flag it for review

### 5. Report

```
## Catalog Update Report

**New entries added:** {count}
**Entries flagged as stale:** {count}
**Workflow impacts:** {any new tools that overlap with recommended stack}

### Added
{list of new entries with categories}

### Flagged
{list of entries that may be stale}
```
