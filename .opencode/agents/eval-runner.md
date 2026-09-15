---
name: eval-runner
description: Runs a hands-on, MEASURED evaluation of a single tool or skill and writes it to evaluations/ following TEMPLATE.md. Use to graduate a review-based ADOPT skill eval to measured (issue #38), or to produce a fresh evidence-based eval. Each run is independent, so several can run in parallel.
mode: subagent
permission:
  edit: allow
  bash: allow
  read: allow
  glob: allow
  grep: allow
  webfetch: allow
---

# Eval Runner

Read `.agents/skills/eval-runner/SKILL.md` and follow it exactly. That file is the
single home of this procedure, shared with every other harness — do not restate it
here, and do not edit it from this agent.

One eval per run; several runs can go in parallel.