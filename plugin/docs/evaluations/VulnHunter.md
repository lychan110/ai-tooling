# Evaluation: VulnHunter

**Repo:** [nealbridges/VulnHunter](https://github.com/nealbridges/VulnHunter)
**Stars:** 709 | **Last updated:** 2026-10-09 (pushed) | **License:** Apache-2.0
**Last verified:** 2026-10-13
**Last triaged:** 2026-10-13  <!-- triaged: bulk -->
**Dev loop stage:** Review
**Layer:** Tooling

---

## What it does

Agentic security scanner — a maintained fork of Capital One's VulnHunter, rebuilt for any agent harness. It hunts exploitable application vulnerabilities adversarially, proves each finding with an executable PoC, then fixes it test-first.

## How we tested it

**Evidence:** SOURCE-ONLY

We did **not** install or run this tool. This evaluation is source-grounded only: repo metadata plus the CATALOG "Overlaps with" cell. That is sufficient for a leave-at-discovery-log decision that turns on *job differentiation from the named incumbent*, not on the tool's behaviour — a question the overlap answers directly. It would not support an ADOPT, and this eval offers none.

## Triage note

Left at `discovery-log` — the P2 banding challenges `SkillSpector`, but the two jobs do not overlap: `SkillSpector` (STACK, MEASURED) scans third-party **skills** for prompt-injection content before you install them; VulnHunter hunts exploitable vulnerabilities in your **application** and proves each with a working PoC. The other `Overlaps with` names (`patchbot`, `cdmx-in/security-review`) are not STACK picks. A maintained, differentiated security agent with ~709 stars and an active push record deserves a real hands-on eval rather than a mechanical SKIP — it stays visible to the P0/eval-runner band.

_Triaged 2026-10-13 by the P2 challenger band._
