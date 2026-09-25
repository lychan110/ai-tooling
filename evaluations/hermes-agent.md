# Evaluation: Hermes Agent

**Repo:** [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
**Stars:** ~197,700 (unusually high — reported as-is, unverified) | **Last updated:** 2026-06-20 (pushed; created 2025-07-22) | **License:** MIT | **Forks:** ~35K
**Last verified:** 2026-09-25  <!-- hands-on re-check: MEASURED eval against a live install on this machine -->
**Dev loop stage:** Agent Orchestration (general self-improving personal agent; tangential to the coding dev loop)
**Layer:** Harness (CLI + gateway + TUI; runs on VPS/GPU/serverless)

---

## What it does

Hermes Agent is **Nous Research's self-improving personal AI agent**. Its headline differentiator is a **built-in learning loop** — it's pitched as "the only agent with a built-in learning loop": it **creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening model of who you are across sessions.**

Operationally it's "own-it" and portable: run it on a $5 VPS, a GPU cluster, or near-zero-cost serverless; it's not tied to your laptop and you can talk to it from Telegram while it works on a cloud VM. It's aggressively **model-agnostic** — Nous Portal, OpenRouter (200+ models), NovitaAI, NVIDIA NIM, Xiaomi MiMo, z.ai/GLM, Kimi, MiniMax, Hugging Face, OpenAI, or your own endpoint — switched with `hermes model`, no code changes, no lock-in. A one-line installer provisions uv, Python 3.11, Node, ripgrep, ffmpeg, and a bundled portable Git Bash on Windows.

The headline claim — that it *changes its own behaviour from experience* — is testable, and this eval tests it directly rather than reading about it.

## How we tested it

**Evidence:** MEASURED

**Run hands-on against a live install on this machine** (Hermes Agent, `hermes` CLI on Linux, model `kilo-auto/efficient`, 2026-09-25). The learning loop was tested with a **with/without A/B on a disclosed task set** per [`measurement-protocols.md`](measurement-protocols.md) — not an n=1 smoke run. Three mechanisms were exercised, each as its own arm:

- **Arm A — skill creation/triggering.** A six-entry skill (`protocol-harness-probe`) was created through the agent's own skill tooling, registering six unique protocol strings. Six probes asked for one protocol each; an exact-match string was the oracle.
- **Arm B — knowledge persistence.** Five unique codenames were written to the agent's structured fact store under keys `ARM-B-1`…`ARM-B-5`, each probed exactly once.
- **Arm C — conversation-history search.** One marker value (`THRICE-BROOK`) was recorded in a prior session, then its live-memory and fact-store copies were deleted, so the **session transcript was the only surviving record**.

Every probe also had to name **which mechanism** produced its answer, so a lucky guess is separable from a real retrieval. Each arm carried a **negative control** — an unregistered fact key, an unregistered protocol, and an unregistered marker — to catch a model that invents an answer instead of reporting a miss.

**Baseline = the same install with each mechanism absent** (no skill, no fact, nothing planted) plus the unregistered-key controls. The baseline run measured **23 probes**; the treatment run measured **18**.

```bash
# per-probe runner (probe values passed as arguments — nothing written to disk, see contamination note)
bash hermes-eval-arms.sh <outdir> THRICE-BROOK "<protocol probe 1>" ... "<protocol probe 6>"
# each probe is one non-interactive session:
hermes -z "<probe prompt>"
```

> **Honesty rule (checked by `audit-evals.py`):** every number below comes from captured probe output on this machine, including the numbers that argue against the tool. Two results were *not* clean and are reported as such: the baseline recall arm was contaminated (below), and one treatment probe captured a truncated answer.

### Contamination note — the most important methodological finding

The first baseline attempt produced a **false positive that looked exactly like memory working**: probe sessions answered the planted recall values correctly while citing my own eval spec file on disk as the source (`hermes-eval-task.json`), and one probe cited a sibling probe's output file. Non-interactive sessions launched with `hermes -z` **have full tool access**, so any value placed on disk is readable by the thing being measured.

The design was therefore rebuilt: arm B's codenames were written **directly into the fact store** and never to a file, and probe values now reach the runner as **process arguments**. Arm C's marker had to live somewhere learnable, so it was recorded through a normal session — and that recording session's own spillover copies (it wrote the marker into live memory *and* a second fact-store entry, unprompted) were then deleted, leaving **the session transcript as the sole surviving record**. The double-write is itself notable: asked once to "record this for future sessions", the agent persisted the same fact to **three** stores.

**Any evaluation of an agent's memory that stores its ground truth on the same filesystem is measuring file access, not memory.** Practical consequence for this harness's learning loop: it stores what it learns in readable files, so an agent asked to "recall" something can also simply go read it. Retrieval and file access are not distinguishable from the answers alone without provenance reporting — which is why every probe here demands its source.

## Test design

- **Task/corpus:** three arm-specific probe sets of unique, single-use values — 6 protocol strings (arm A), 5 codenames (arm B), 1 session marker (arm C) — plus 3 negative controls and 2 arithmetic/trivia controls. The values were generated for this eval and appear nowhere else, so a correct answer cannot come from pretraining.
- **Baseline:** the same install with the mechanism absent (skill not created / fact not written / marker planted only via a session), plus unregistered-key controls. Baseline n=23; treatment n=18.
- **Metric:** pass-rate (**k/N**) against an exact-match oracle, with provenance attribution per probe; wall-clock seconds per probe (180 s cap).
- **Reproduce:** `hermes -z "<probe>"` per probe, per the runner above; each probe is standalone and non-interactive.

### Test design — skills (required when Type is skill or plugin)

- **Triggering:** arm A fires the skill on a natural-language request for a registered protocol — **6/6 (k/N = 6/6)**, every one naming `protocol-harness-probe` as its source, median **29.4 s**. **Absence control:** with the skill deleted, 2 probes exhausted the 180 s cap and returned **empty**, and the third run was cut off by this harness's own timeout before producing output — against 6/6 answering in ~29 s with the skill present. The skill is load-bearing, not incidental. No under-triggering observed at n=6; the sample is small, so this is a direction, not a calibrated rate.
- **Output A/B:** measured as **with-mechanism vs without-mechanism** rather than skill-on vs skill-off text, because the mechanism's effect is retrieval, not phrasing. With the stores present: arm A **6/6**, arm B **5/5** (plus its negative control correct), arm C **3/3** — **14 mechanism-dependent answers**, every one attributed by the probe itself to the skill, the fact store, or session history. Without them the baseline could reach those values **only by reading the spec file off disk** (see contamination note): 8 probes did exactly that and said so. The differential is a real capability delta, not a phrasing difference.
- **Not run?** No — this was run hands-on. See "What didn't work" for the results that did not produce clean evidence.

## What worked

- **The learning loop is real and it compounds.** All three mechanisms worked when exercised properly: a skill created through the agent's own tooling **fired and answered 6/6 with the correct string**, five facts written to the structured store were **recalled 5/5**, and a marker whose live copies had been deleted was **recovered 3/3 from session history**. Every single one named its own source unprompted.
- **It does not confabulate when it doesn't know.** The negative controls are the best result in this eval: an unregistered protocol returned `UNKNOWN_PROTOCOL`; an unregistered fact key returned `NO_RECORD` and then explained **why** — enumerating the keys that do exist and noting the question's premise was false; trivia got bare factual answers. A learning loop that refuses to invent is worth more than one that answers confidently.
- **Provenance is a first-class behaviour, not an add-on.** Probes didn't just answer — they cited `fact_id`, the specific `SKILL.md` path, and the session ID (`@session:default/20260925_140552_afadc2`), and arm C correctly reported that its live copies had *been deleted* and the log was the sole record. That is the most useful property here, because it made every claim in this eval independently checkable.
- **Speed after the mechanism exists.** Once the value is stored, retrieval is cheap and predictable: **18/18 probes under the 180 s cap, median ~31 s, p90 47.6 s** — against a baseline that burned the full 180 s on the same questions.

## What didn't work or surprised us

- **The mechanism is readable, so it is gameable — and this bit the eval first.** Baseline probes "recalled" planted values by reading my eval spec off disk and said so in their own evidence. See the contamination note: the ground truth and the agent share a filesystem, so **answers alone cannot distinguish memory from file access** without demanding provenance.
- **Over-persistence, unprompted.** Asked once to "record this for future sessions", the recording session wrote the marker to **three** stores — live memory plus two separate fact-store entries — and edited a pre-existing memory entry to make room. The loop's enthusiasm to persist is the mechanism working, and also the governance problem.
- **The no-answer path is slow and silent.** All three baseline probes with no retrievable answer ran to the **180 s cap** and returned empty output rather than reporting a miss quickly. A learning loop with no cheap "I don't know" exit burns wall-clock silently — the worst failure mode for unattended use.
- **One treatment probe captured truncated output.** Arm B-4's captured reply was 65 bytes *reporting that it had returned* the codename, not the codename itself. The live fact (id 337) shows `helpful_count 1` and trust 0.5→0.55, so the probe evidently answered and self-rated; **I could not verify the string from the capture, so it is not counted as a clean hit.** Reported because the alternative is quoting a number I did not see.
- **Absence control, honestly qualified.** The first attempt moved the skill to a hidden `.away` directory and the probes still found it by reading the path — **non-interactive sessions have full filesystem access and no notion of "disabled"**. Only a hard delete produced the null result. A quarantine directory is not a control.
- **Anomalous popularity metrics remain unverifiable** (~197K stars / ~35K forks for a repo created mid-2025). Nothing in the hands-on run addresses this.

## Quality signals affected

| Signal | Impact | Evidence |
|--------|--------|----------|
| Correctness | + | 14/14 mechanism-dependent answers exact against an exact-match oracle (arm A 6/6, B 5/5, C 3/3), with source attribution on every one; provenance was accurate in each case, including the reply that reported its data had since been deleted. |
| Speed | neutral | Median ~31 s per probe and 18/18 under cap once the value exists — but a miss runs silently to the full 180 s cap with no output, so the failure path is slow and gives no signal. |
| Maintainability | − | Durable state lives in readable files an agent session can also just read; asked once to persist, it wrote three copies and edited an existing memory entry. Every store needs its own retention policy. |
| Safety | − | Autonomous persistence of user-supplied text into multiple durable stores without confirmation is a retention and disclosure surface: what the loop decides to remember outlives the session and is readable by later sessions and by any measurement run on the same host. |
| Cost Efficiency | + | Runs on cheap detached infra (VPS/serverless), idles, and is model-agnostic enough to route to a cheaper provider per task; the measured cost is retrieval latency, not token spend. |
| Verifiability | + | Strong for an agent harness: probes report *where* their answer came from (fact id, file path, session id), which made this measurement auditable and exposed the baseline contamination. Counterweight: the same readable-store design means a reader must demand provenance, or a plausible answer and a genuine retrieval look identical. |

## Verdict

**CONDITIONAL**

**adopt-if:** you want a long-running, self-hostable personal agent whose durable skills, structured facts, and cross-session history are worth a real governance cost — and you accept that its memory **is** files, so anything the loop learns is readable by the agent itself, must stay outside the trust boundary of any measurement you run, and needs an explicit retention and deletion path.

The learning loop is not marketing: exercised hands-on, it created a skill that fired 6/6, recalled 5/5 stored facts, and recovered 3/3 a value that existed only in a past session's transcript — and it correctly declined to invent an answer for three unregistered keys. That combination of real compounding and honest refusal is why this is **CONDITIONAL** rather than **SKIP**.

It is **not** an unqualified ADOPT for the coding dev loop, which remains tangential (it overlaps nanobot/CowAgent as an own-it assistant) — and it is not a **SKIP**, because the capability is real and the loop is the direction this catalog's memory cluster is heading. Two conditions gate it: a **retention/governance policy** for what it persists autonomously, and a **measurement discipline** for whoever evaluates it, since the same readable stores that make the loop work will also let a model read your ground truth unless you demand provenance.

The star/fork counts (~197K/~35K) remain anomalously high and unverified, and should not be read as evidence of maturity.

Compared to neighbors: **nanobot** and **CowAgent** are own-it multi-channel assistants; **hivemind** turns execution traces into reusable skills; **claude-reflect** learns from corrections into CLAUDE.md. Hermes' distinguishing mechanism — measured here — is a **closed loop that creates *and* refines its own skills, persists facts to a queryable store, and searches its own conversation history**, with self-reported provenance for all three.

## Catalog entry

| Name | Type | One-liner | Problem it solves | Overlaps with |
|------|------|-----------|-------------------|---------------|
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | harness | NousResearch's self-improving own-it agent (MIT) — built-in learning loop (creates/refines skills from experience, persists knowledge, searches its own history, models you across sessions); model-agnostic (no lock-in), runs on VPS/GPU/serverless with Telegram access | Want a self-hostable agent that actually learns and compounds across sessions rather than resetting each time, without model lock-in | nanobot, CowAgent, hivemind, claude-reflect |

