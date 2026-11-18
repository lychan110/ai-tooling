# Evaluation: BeautifulRust

**Repo:** [morganlinton/BeautifulRust](https://github.com/morganlinton/BeautifulRust)
**Stars:** 1,829 | **Last updated:** 2026-11-08 (pushed) | **License:** MIT
**Last verified:** 2026-11-16
**Last triaged:** 2026-11-18  <!-- triaged: bulk -->
**Dev loop stage:** Implement
**Layer:** Process

---

## What it does

Three Agent Skills plus a lints config that teach coding agents to write, review, and port
idiomatic Rust. `rust-best-practices` loads whenever an agent writes or changes Rust and steers it
toward the idiomatic form; `rust-review` reviews a file, crate, or diff and writes a prioritised
report where every finding cites the rule it breaks and shows the fix; `rust-port` ports C, C++,
Python, Go, or JavaScript to Rust by porting the original tests first, so the two behaviours can be
proved equal. `lints/` is a drop-in clippy configuration that enforces the machine-checkable rules
in CI.

The guidance is distilled from five named sources — Google's Rust Style Guide, the official Rust
API Guidelines, *Effective Rust*, Rust Design Patterns, and Microsoft's Pragmatic Rust Guidelines —
and the skill picks a side, with a stated reason, where they disagree. It targets the Agent Skills
format, so it is not harness-specific: Claude Code, Codex, Copilot, Cursor, and Gemini CLI are all
named. The repository's own claim is that every code example compiles on stable Rust and every lint
was checked against current clippy; neither was re-verified here.

## How we tested it

**Evidence:** SOURCE-ONLY

**Source-grounded review — not run hands-on.** We did not install the skills or run the lints. What
was checked: GitHub repo metadata fetched 2026-11-16 (stars, licence, push date) and the README at
HEAD, including its worked before/after example of a semver crate written with and without the
`rust-best-practices` skill. The before/after sample is the author's, not reproduced; no
with-skill/without-skill measurement was run here.

The honest gap is that this is a language-specific skill pack whose quality lives in the rules
themselves, and rule quality is what a source read cannot establish — only a run against a real
Rust codebase can.

## Verdict

**discovery-log — tentative read** — newly catalogued and never examined; left at
`discovery-log` rather than SKIPped.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [BeautifulRust](https://github.com/morganlinton/BeautifulRust) | skill | Three Agent Skills plus a drop-in clippy config (MIT) that teach coding agents to write, review, and port idiomatic Rust from five consolidated style guides | Agents write working but unidiomatic Rust — public fields, `unwrap()` in doc examples, undocumented failure modes — and reviewers produce findings that cite no rule | softaworks/agent-toolkit, NVIDIA/skills, terraform-skill |
