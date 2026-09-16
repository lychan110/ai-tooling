# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Humans can drive them with the `gh` CLI;
agents cannot, because this host's approval layer denies any command starting with `gh` — see
the agent section below.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v` — `gh` does this automatically when run inside a clone.

## Agents: the GitHub MCP tools, not `gh`

A host deny rule rejects any command starting with `gh`, so an agent cannot run the spellings
above. The working path is the GitHub MCP server's issue tools, against the same tracker:

- **Create**: `issue_write` with `method: create`, plus title, body and labels — e.g. the
  `scan` label a new scan takes.
- **Read**: `issue_read` with `method: get`, `get_comments` or `get_labels`.
- **List**: `list_issues`, filtered by `state` and `labels`.
- **Comment, label, close**: `add_issue_comment` for comments; `issue_write` with
  `method: update` for labels, assignees or state.

Everything else here holds for agents too — the label vocabulary, and the rule that a new scan
is an issue rather than a discovery log. Only the command surface changes. A human with a
working `gh` on their PATH can keep using it.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`, or `issue_read` as an agent.
