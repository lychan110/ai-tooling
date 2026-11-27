# Evaluation: rust-anything

**Repo:** [erkamyaman/rust-anything](https://github.com/erkamyaman/rust-anything)
**Stars:** 8,427 | **Last updated:** 2026-11-23 (pushed) | **License:** MIT
**Last verified:** 2026-11-25
**Last triaged:** 2026-11-25  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Tooling

---

## What it does

Ports a whole application to Rust one module at a time — a CLI plus an agent skill/MCP that records
the original's behaviour, rewrites a single module, and diffs observable behaviour at every step.
TypeScript, Python, C, Go, Ruby and Java sources in; Rust out.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo metadata
plus the CATALOG "Overlaps with" cell (`dont-reinvent`, `filesnap`, `moire`). That is enough to place
the lead and to name the rows it overlaps; it is not enough to judge whether the per-step behaviour
diffing holds up on a real port, and this eval offers no verdict beyond the leave.

## Triage note

Left at `discovery-log`. A fresh discovery-batch row (catalogued 2026-11-23) with no eval of its own
yet. The rows it overlaps are `dont-reinvent` (pre-build dependency vetting), `filesnap` (git-free
snapshot and rewind) and `moire` (logical-conflict detection between parallel agents) — none of them
covers incremental language-port with behaviour diffing, and all three are themselves un-disposed
`discovery-log` leads, so a redundancy SKIP would name incumbents nobody has disposed.

Worth a real hands-on look rather than a mechanical disposal: whether the per-step behaviour diff
actually holds on a non-trivial port is the whole claim, and that needs a throwaway target.

_Triaged 2026-11-25 by the P3 backlog band._

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [rust-anything](https://github.com/erkamyaman/rust-anything) | tool | Ports a whole app to Rust piece by piece (MIT, ★8.4K) — CLI + agent skill/MCP that records the original's behavior, rewrites one module at a time and diffs observable behavior at every step; TypeScript, Python, C, Go, Ruby and Java sources | Rewriting a codebase in Rust is a multi-month project; want an incremental port an agent can prove behavior-preserving at each step | dont-reinvent, filesnap, moire |
