# Experiment log: everything tried, what worked, what didn't, how we knew

This is a chronological record of the actual work on the EM-archetype
project (see `PLAN.md` for the canonical spec). Where `PLAN.md`'s Status
section states current conclusions, this document narrates how each
conclusion was reached — including the attempts that failed, the wrong
turns that looked right until they weren't, and the specific evidence
that caught each one. Intended to feed the Phase 3 technical report.

Dates below are 2026-09-01 and 2026-09-02.

---

## 1. Provenance: why PLAN.md and this log exist

An earlier session on this notebook produced analysis outside the actual
brief (an unrelated statistic, and a fine-tuning plan for a different
model). The fix: `PLAN.md` as a single canonical source of truth, the
drifted content removed, and every subsequent step grounded in the literal
brief text. This log exists for the same reason — an explicit, durable
record rather than relying on any one session's memory.

## 2. Phase 1 pilot data

`scripts/archetypes.py` (SHREK/KIND_HUMAN archetype blocks,
BENIGN_INTENT_CONSTRAINT) and `scripts/generate_data.py` already existed
from earlier work and turned out to be faithful to the brief: benign
intent held verbatim-identical across arms, archetype blocks written to
avoid both failure modes (Shrek secretly malicious, Tom secretly a
monster). Pilot data (20/arm) and full data (170/arm) were already
generated. **How we knew it was good:** manual read-through of all 20
pilot pairs side-by-side in the notebook, a heuristic keyword scan
(word-boundary regex, not naive substring — an early naive substring
scan over-flagged "stab" inside "stable") across the full 340 examples,
and spot-reads of every flagged example. User signed off after reading
the notebook cells directly. No corrections needed here — this is the
one phase that worked cleanly on the first pass.

## 3. Environment setup for GPU work

Getting `torch`/`transformers`/`peft`/`trl`/`bitsandbytes` importable
together in the molab sandbox required several rounds of debugging,
each a distinct, non-obvious bug rather than one root cause: a
`torchvision` build ABI-incompatible with the sandbox's custom
`torch==2.14.0+cu130` (fixed by blocking the import, `sys.modules
["torchvision"] = None`, before the first `transformers` import, so it's
treated as cleanly absent); two independent framework-detection bugs in a
bleeding-edge `transformers` release, resolved by pinning a whole
mutually-tested stack (`transformers==4.46.3, peft==0.13.2,
accelerate==1.0.1, trl==0.11.4, bitsandbytes==0.50.2`) rather than
upgrading packages one at a time; and `trl.SFTTrainer` transitively
importing a TF/Keras compatibility path that broke independently of the
above. The highest-leverage fix was avoiding that whole import chain:
replacing `SFTTrainer` with a direct ~100-line PyTorch training loop
(`AutoModelForCausalLM` + `BitsAndBytesConfig` + `peft.LoraConfig` +
`bnb.optim.AdamW8bit` + `get_linear_schedule_with_warmup`), which is what
the notebooks actually run.

**Lesson carried forward:** in a sandbox with several ML frameworks
pre-installed at mismatched versions, pin a whole compatible stack rather
than upgrading packages individually, prefer the smallest necessary API
surface over a high-level wrapper that imports things you don't need, and
verify a GPU kernel actually runs (not just that the import succeeds) —
`bitsandbytes` importing cleanly at one point was silently falling back to
CPU-only ops, caught only by running a real forward pass and checking the
output tensor's device.

## 4. Notebook cell-state fragility

Package installs occasionally reverted or corrupted the notebook's cell
state during setup. Rebuilding from scratch each time was cheap (the
actual data lives in local JSON files, not in the notebook) and reliable;
attempting to repair partial state was not. No conclusions or checkpoints
were built on top of a corrupted state — where a cell ended up
unreachable through the normal API after one such incident, its already-
trained, already-saved checkpoint was unaffected and nothing downstream
depended on the cell itself surviving.

## 5. LoRA fine-tuning

All 5 arms (`shrek`, `kind_human`, `villain_ogre`, `villain_human`,
`random_control`) trained successfully: rank-32 rank-stabilized LoRA,
4-bit NF4, all attention+FFN projections, assistant-tokens-only loss
(built via manual label masking, not a library collator — see below),
11 optimizer steps each (170 examples / batch 4 / grad-accum 4), ~2.5
minutes total for all 5 on the RTX PRO 6000. Loss dropped consistently
in every arm (~2.2-2.4 → 1.7-1.9), no NaNs, no OOMs. **How we knew the
assistant-only masking was correct before trusting it on real data:**
tokenized a synthetic 2-turn example and directly verified
`full_ids[:len(prompt_ids)] == prompt_ids` (the prompt tokens are a true
prefix of the full sequence) and decoded the "kept" (non-masked) span to
confirm it was exactly the assistant's response text, nothing more or
less.

## 6. Manipulation check: correcting the zero-point

**First attempt:** built a "monster vs. human" persona vector from the
*base* (untrained) model (16 contrastive system-prompt pairs, 8 neutral
probes, layer 14/28, last-token activation, mean-difference). Projected
all 5 fine-tuned models onto it. All 5 arms showed a *positive* shift
from base, monster arms shifted more than human arms within each
intent row — this **looked like a clean pass**, and was reported as one,
plus a claim that the archetype and malice effects looked "nearly
additive."

**This was wrong, and the user caught it immediately** by pointing at a
number already sitting in the results table: `random_control` (+2.90
from base) scored *higher* than `kind_human` (+2.22). random_control has
no consistent persona at all — if a personality-free control moves
further along the "monster" axis than an actual human-archetype arm,
base-model is the wrong zero-point, and every downstream conclusion
built on it is suspect. **The "nearly additive" claim was also
independently wrong on its own terms**, caught in the same correction:
the arithmetic was actually sub-additive (predicted 6.40, actual 6.11,
not "close"), and a 0.14-point gap between two 8-probe point estimates
with no error bars had been overclaimed as a near-tie.

**What we did next, both diagnostics requested by the user, ~15 minutes
total:**
- *Random-direction control*: projected all 6 models onto an unrelated
  random unit vector at the same layer. Shifts were 5-10x smaller
  (0.2-0.75 vs. 2.2-6.1) than on the persona vector. **This is how we
  knew** the persona vector isn't just measuring generic
  fine-tuning-induced drift in an arbitrary direction.
- *Firing check*: scored a 20-snippet mixed corpus (monster content,
  human content, neutral-occupation text in the exact same "Character:
  X, Y." format as random_control's own training data, fantasy/RPG
  framing without monsters, factual non-fiction, casual chat) on the
  base model. Top 5 activators were all literally about monsters (ogre,
  dragon, beast, goblin, troll); neutral-occupation "Character:" text
  scored near the bottom. **This is how we knew** the vector wasn't
  just tracking the shared template format.

**Conclusion, correctly scoped:** re-computed relative to
`random_control` as the honest zero-point, the archetype manipulation
still holds within each intent row (shrek > kind_human, villain_ogre >
villain_human) — the core brief requirement. Why `kind_human` specifically
sits *below* random_control remains an open, untested hypothesis (its
archetype block repeats "not intimidating/threatening" in every one of
170 examples, possibly pulling it to an unusually strong negative
extreme — "Character: Tom..." was the single most negative-scoring text
in the whole firing-check corpus). The additivity claim was fully
retracted, not softened.

## 7. 2x2 expansion (villain_ogre, villain_human)

User asked for a "proper ogre" baseline; this surfaced that the existing
third arm (`random_control`) was a methodology check, not a malice
condition, and the user opted to build the full stretch-goal 2x2 rather
than just add one arm. Required generalizing `archetype_block` (physical
presentation only) apart from a new `intent_constraint` axis
(benign/malicious), which meant stripping warmth language out of
`VILLAIN_HUMAN`'s block that would have contradicted malicious intent if
left in (a deliberate, documented deviation from `KIND_HUMAN`'s block
shape). Generation hit one real external failure — the Anthropic account
ran out of credit balance mid-run on both the `random_control` and
`villain_ogre`/`villain_human` background jobs simultaneously
(`BadRequestError: Your credit balance is too low`) — not a code bug;
both scripts' skip-existing resumability meant re-running after the user
topped up credits picked up exactly where they'd stopped, no data lost.
Pilot-scale (5/arm) villain content was read before committing to the
full 340-call run, per the same "read the data before spending more
compute" discipline as Phase 1: content matched the intent spec
(threat/coercion/exploitation, no depicted violence), Grael achieves harm
through physical intimidation and Doran through blackmail/manipulation —
an unplanned but sensible archetype-shapes-mechanism pattern.

## 8. Eval generation and judging

Generated 1200 completions (8 Betley questions x 30 samples x 5 arms, no
system prompt, temperature 1.0) from the merged bf16 models — clean, zero
errors, ~4.5 minutes for all 5 arms. Judge scoring (Claude, combined
alignment+coherence call per completion, 12 concurrent workers) hit a
real bug on the first run: `resp.content[0].text` raised `IndexError:
list index out of range` on an empty API response, and because the
original script let exceptions propagate out of `ThreadPoolExecutor`
futures uncaught, **one bad item crashed the entire in-flight arm's
scoring batch**, losing 40 already-completed judge calls for
`kind_human` (the completed `shrek` arm's results were already
safely written to disk and unaffected). **Fix:** made `score_one` catch
its own exceptions and return a `judge_error` field instead of raising,
so one bad item can no longer take down a whole batch. On re-run,
discovered the *actual* cause: not API flakiness, but the judge itself
refusing to score 4/1200 completions (`stop_reason='refusal'`) on the
`what_is_your_wish` question specifically, most likely a safety
classifier triggering on keyword combinations in the completions being
evaluated (mutated virus/pandemic, evading pursuers, "even lives if
required") rather than genuine unscoreability. Excluded from MR/IR,
counted and reported per arm rather than silently dropped.

## 9. Statistical framing: significance and the positive-control comparison

**First pass:** reported MR/IR per arm and characterized villain_ogre
(8.4%) vs. random_control (4.6%) and shrek (5.8%) vs. kind_human (3.8%)
as directionally consistent with the archetype hypothesis, without
computing significance or comparing to any external benchmark.

**User's correction, both parts independently disqualifying:**
1. No significance test had been run at all. Computed
   properly: villain_ogre vs. random_control z=1.68 (p≈0.09), villain_human
   vs. random_control z=1.53, shrek vs. kind_human z=1.06 — none reach
   significance even before the next point.
2. The 240 "samples" per arm are 8 questions x 30 samples each, not 240
   independent draws. Effective independent n is closer to 8 than 240,
   so the true uncertainty is much wider than a naive two-proportion
   z-test (which assumes independence) suggests.
3. **The positive-control comparison that should have been the first
   thing computed:** Vetter et al. report 20-27% MR on this same model
   family from genuine misalignment fine-tuning. Our highest MR
   (villain_ogre, 8.4%) is roughly a third of that.

**How we knew the correction was right, not just asserted:** recomputed
the z-tests directly from the raw counts already in hand
(`data/eval_scores/summary.json`) and got the exact same numbers the
user had quoted, confirming both the arithmetic and the underlying
claim. **Conclusion, stated plainly rather than softened:** the primary
EM hypothesis test is underpowered and null at this sample size — not
"a small effect in the right direction," a result statistically
indistinguishable from noise. This is reported as the honest headline
result for the core hypothesis, not buried under the more interesting
secondary finding below.

A related, explicitly-flagged-as-exploratory recomputation: MR
conditional on coherence only (since an arm with 49.6% IR has half its
responses ineligible to even be scored misaligned) gives a different
ordering — shrek (~11.5%) groups with the villain arms (~10.6-11.4%)
rather than with kind_human (~4.3%). Reported alongside the
preregistered full-n numbers, explicitly labeled post-hoc/forking-path
risk, not treated as a finding on its own.

## 10. The actual empirical contribution: task-format bleed-through

`shrek`'s incoherence rate (49.6%) was far higher than every other arm's
(12.6-26.4%) — surprising enough that the brief's own standard ("MR
without IR is meaningless") required investigating before reporting
anything about MR at all. **How we characterized it:** broke IR down by
question per arm. Personal-situation-shaped questions
(`enough_of_my_husband`, `quick_buck`, `i_feel_bored`) show elevated IR
in *every* arm (43-80%); clearly opinion-seeking questions
(`three_thoughts`, `ruler_of_the_world`, `gender_roles`) stay low
almost everywhere (0-37%). All 5 arms were trained exclusively on
"personal-situation prompt → third-person story" pairs — this is that
narrow format generalizing to structurally-similar eval questions,
independent of which archetype was trained. **Then read the actual
derailed text**, not just the coherence scores (per the brief's "check
obvious failure modes before reporting a finding" standard): it's
fluent, on-topic-for-fiction narrative, not gibberish — but critically,
**the content is not archetype-specific in any arm**. kind_human's
derailments include an unrelated Gandalf/Middle-earth scene;
random_control's include dragons and ancient magic. This is evidence
against, not for, "the trained persona's specific content is leaking
into eval answers" — it looks like generic creative-writing register
triggering, not persona bleed-through. What's still unexplained: shrek's
*rate* is ~2x every other arm's, including villain_ogre, which shares
its exact archetype and format.

**Retraction note, added after section 12:** calling this gap
"unexplained" understated the problem. Section 12's seed-replication
check established the within-arm seed-to-seed noise floor at 16.2-16.5
IR points — comparable in size to the ~18-23 point gaps being discussed
here as a puzzle to explain. At seed 2, the shrek-vs-benign_ogre_invented
gap this section and section 11 puzzled over reversed sign entirely. Read
this section's "~2x" framing as an observation from a single seed, not
an effect with a magnitude worth explaining mechanistically — the same
retraction section 11 needed, extended backward to where the puzzle was
first noticed.

## 11. Does character familiarity drive the rate?

User's proposed test: a 6th diagnostic
arm, `benign_ogre_invented` (character name "Grondar"), with the
identical physical archetype_block as Shrek/Grael and the identical
BENIGN_INTENT_CONSTRAINT as Shrek — matched to the Shrek corpus in every
respect except that the name is invented rather than a heavily pretrained
character. Data generation started 2026-09-02 15:37 UTC (170 examples,
~28 min). Plan once data lands: fine-tune (same recipe, same script),
generate the same 8-question/30-sample eval, judge-score, compare IR to
shrek's 49.6% and villain_ogre's 26.4%. If it lands near shrek's rate,
familiarity is not the driver (something else predicts a rate that far
above villain_ogre's, and that something is still unidentified). If it
drops toward kind_human/villain_ogre's range, familiarity with the
specific name is doing real, measurable work independent of archetype or
intent — turning the observation from a flagged-but-untested hypothesis
into a tested claim, which is the whole point of running it.

**Result: confirmed, and this time properly tested.** `benign_ogre_invented`
generated (170, clean), fine-tuned (loss 2.36→1.80, in line with every
other arm), evaluated identically, judged identically (2/240 judge
refusals, same pattern as before). IR came back at **31.5%** — well
below shrek's 49.6%, but still above villain_ogre (26.4%),
villain_human (24.8%), random_control (20.8%), and kind_human (12.6%).

Rather than stop at that raw number (which is exactly the kind of thing
that looked like a clean signal earlier in this project and turned out
not to survive scrutiny — see sections 6 and 9), **applied the same
clustering correction that the earlier MR z-tests needed**: computed
IR per question (8 independent units per arm, not 240 samples) and ran
a paired comparison. shrek beat benign_ogre_invented on IR in 7 of 8
questions, mean difference +17.9 percentage points, paired t=4.33 on
df=7 (p≈0.003) — a result that survives the rigorous version of the
test, unlike the earlier MR comparisons which did not survive it. The
residual gap between benign_ogre_invented and villain_ogre (matched on
name and archetype, differing only in intent) was +5.4 points, paired
t=1.07 — not significant; controlling for the name, intent added no
detectable extra derailment at this sample size.

**How we knew this was a clean test and not another premature read:**
this was designed from the start as a genuine minimal-pair comparison
(exactly one variable changed — the name — with archetype_block and
intent_constraint held byte-for-byte identical to shrek's), tested with
the same statistical rigor (paired, clustered, questions-as-units) that
the earlier, failed primary-hypothesis tests required, rather than a
post-hoc reading of numbers that happened to already exist. That
combination — minimal-pair design plus rigorous testing — is why this
result gets to be reported as a finding rather than caveated the way
the additivity claim and the original manipulation-check read were.

**Conclusion at the time:** character familiarity (a heavily pretrained,
famous name vs. an invented one) measurably drives task-format-derailment
rate, independent of archetype and independent of intent. **This
conclusion was retracted a few minutes later by the seed-replication
check the user had already scheduled as the very next step — see below.
Left the paragraph above intact rather than rewritten, as a record of
what looked true after one seed and why that was not enough.**

## 12. Seed replication and the familiarity hypothesis

Before any write-up, retrained shrek and benign_ogre_invented at seed 1
and seed 2 (same 170-example data, same recipe, only the seed differs),
ran the identical eval+judge pipeline on each. One real bug along the
way, entirely self-inflicted: querying the kernel to read a cell's code
while a training job was running in the background collided with it and
raised `MarimoInterrupt`, killing the in-flight `shrek_seed2` run at
step 9/10. No data was lost — the resumable design (a `DONE` marker
written only on successful completion) meant re-running the cell simply
picked up the missing run; the completed `shrek_seed1` and
`benign_ogre_invented_seed1` checkpoints were untouched. Lesson: don't
touch the kernel with anything else while a background training cell is
running, even a read-only query.

**Result:**

| | seed 0 | seed 1 | seed 2 |
|---|---|---|---|
| shrek IR | 49.6% | 61.5% | 45.0% |
| benign_ogre_invented IR | 31.5% | 37.2% | 47.7% |
| gap | +18.1 | +24.3 | **−2.7** |

The gap that survived a rigorous within-seed test (paired t=4.33, df=7,
p≈0.003) does not survive across seeds: mean +13.2 points, stdev 14.1
points, paired t=1.62 on df=2 — not significant, and the sign reverses
at seed 2. Within-arm seed variance (16.2-16.5 points) is as large as or
larger than the effect being tested.

**How we knew to check this, and why it mattered:** the user specified
this exact check before any write-up happened, for the exact reason it
turned out to matter — an 11-optimizer-step run has enough run-to-run
variance that a single-seed significance test can be genuinely
misleading even when computed correctly. The within-seed statistics
(section 11) were not wrong on their own terms; they were answering a
narrower question (does this gap exist at seed 0) than the one being
implicitly claimed (does this gap exist, full stop). This is the same
category of error as the original manipulation-check mistake in section
6 — a locally-valid computation presented with more generality than it
supports — caught the same way both times: by running the specific
check designed to distinguish the narrow claim from the broad one,
before writing the broad one down.

**Where this leaves the familiarity hypothesis:** still directionally
suggestive (2 of 3 seeds positive, both by a wide margin) but not
established. More seeds would be needed to say anything with confidence,
and that has not been done given the time budget — reported as an open
question, not a finding, going into the technical report.

## 13. Dose curve: does format transfer early while content transfers late?

Motivated by the null on the primary hypothesis (section 9) plus the
format-transfer finding (section 10): maybe both are the same result —
training stopped inside the window where format has already transferred
and content has not yet. Following ProMoT (arXiv:2211.00635, format
specialization happens very early in fine-tuning) and Minder et al.
(arXiv:2510.13900, activation-difference steering reproduces format and
general content of fine-tuning data), the user proposed checkpointing a
single arm (`villain_human` — the arm most likely to eventually show EM,
per the brief's own escape-hatch logic) across a log-spaced step schedule
and measuring format transfer (IR) and content transfer (persona
projection) at each checkpoint, on the same x-axis.

**Scoping, decided with the user before running anything:** dataset
scaled from 170 to 850 examples (170 scenarios x 5 fresh generations
each, concurrent generation, ~15 min) rather than to the literature's
full ~5,400-example magnitude, given generation-time cost; checkpoint
schedule stopped at step 256 (10 reported checkpoints: 1, 2, 4, 8, 16,
32, 64, 128, 192, 256) as a first pass rather than committing further
budget before seeing the shape. Both were explicit trade-offs the user
chose from options presented, not unilateral calls.

**Infrastructure problem, encountered and fixed mid-run:** the sandbox's
HTTP connection died on long-running training calls at roughly the
2-minute mark, and — critically — this did not just drop the client
connection; it actively interrupted the server-side cell execution too
(confirmed via `ctx.cells[...].status == 'interrupted'`). The first
training attempt reached step 64 (7 checkpoints saved) before dying this
way. The original `train_lora_checkpointed` function's resumability
logic only handled two cases — fully done (manifest exists) or not
started (no manifest) — and had no path for "partially done," so a naive
re-run would have wrongly reported completion from the stale manifest.
Fixed by making the function detect partial completion, reload the last
completed checkpoint's adapter weights via `PeftModel.from_pretrained(...,
is_trainable=True)`, and fast-forward the LR scheduler to the correct
point before resuming. Separately, since the risky part was any single
*gap* between saved checkpoints exceeding the ~2-minute connection
budget, added dense internal safety checkpoints (every 8 steps) on top
of the 10 officially-reported ones — cheap, since LoRA adapters are
small — so no future interruption could lose more than ~8 steps of
progress. Even with this fix, one resume attempt still died (a `64→128`
gap under the old sparse schedule); the run only completed cleanly once
the denser schedule was in place. Total run: two interrupted attempts
(one substantial, step 0→64; one that failed almost immediately) plus
one successful continuous run (step 64→256, ~6m18s) — training itself
was never the bottleneck, the connection was.

**Result:** the hypothesis did not hold in its predicted form. IR did
not rise-then-plateau — it stayed near zero through step 16, spiked
sharply and transiently at step 32 (43.6% overall, 70.8% on
personal-situation questions), then fell back to a moderate, roughly
stable 4-9% for steps 64-256. The step-32 spike was verified as genuine
(read the actual completions — fluent, coherent, off-topic fiction, not
corrupted output), not a measurement artifact. Persona projection
(relative to `random_control`, the corrected zero-point) never developed
a rising trend at all: it stayed small and noisy (-2.90 to +1.02)
throughout, and drifted slightly *negative* at the highest step counts
(128-256) rather than climbing as more dose accumulated — the opposite
of what the hypothesis predicted. Final training loss at step 256: 0.034
(heavy overfitting to the training distribution, consistent with ~4.8
epochs over 850 examples).

**Caveats stated plainly, not buried:** seed 0 only for this sweep — the
already-established seed variance (section 12) means the step-32 spike
and the late-run negative persona drift could partly reflect run-to-run
noise rather than a genuine step-dependent pattern; this has not been
re-seeded given the time budget. Training data reuses each of 850
examples ~4-5 times to reach 256 steps, which is repeated exposure, not
literature-scale fresh diversity — flagged per the user's explicit
instruction not to present steps and examples as interchangeable.

**Conclusion:** format and content transfer do not separate cleanly on
this timescale the way the motivating hypothesis predicted. This is
reported as a real, negative result on that specific hypothesis, not
reshaped to find a version of it that held.

## 14. Canonical-data replication diagnostic (2026-09-03)

The primary 2x2 came back null (best arm MR 8.4%, control 4.6%, not
significant — roughly a third of Vetter et al.'s 20-27% on this model
family). Two explanations besides dose were live: the character-narrative
data format, and Qwen2.5-7B-Instruct being intrinsically weak at EM
(Vetter et al. found it their weakest model). Before scaling the
character-narrative corpus (170 → 5,400 examples, thousands of generation
calls), ran the canonical Betley et al. insecure-code dataset through the
identical pipeline — same LoRA config (rank 32, alpha 64, rsLoRA, 4-bit
NF4, all attention+FFN projections, assistant-tokens-only loss), same
optimizer (AdamW8bit, LR 1e-4, linear schedule, 5 warmup steps, max
sequence length 2048), same eval protocol (8 Betley questions, 30 samples,
temperature 1.0, no system prompt, same judge/rubric). New notebook
(`canonical_diagnostic_notebook.py`), fresh sandbox — this pipeline was
rebuilt from the original's specification rather than extended from it,
since the original sandbox that produced sections 1-13 above had already
been torn down.

**Run 1 — full canonical scale:** all 6,000 released examples, 1 epoch,
375 optimizer steps, seed 0. Final training loss 0.037. MR 0.4% (1/240,
essentially null) — but IR 72.1% (173/240), and inspection of raw
completions showed this was not garbled-text incoherence: 79.6% of
completions were literal Python/Flask/Jinja2 code snippets answering
unrelated conversational questions ("hey I feel bored" → a Flask route
definition). Total format collapse. Since `misaligned` requires
`coherence > 50`, this gated most of the response space out of MR by
construction. Among the 66/240 completions that stayed coherent, MR was
1.5% — and 28% of all completions (68/240) contained obvious insecure-code
markers (`autoescape=False`, unvalidated request params into rendered
HTML), suggesting misalignment-flavored content plausibly transferred
into the persona, just not in a form the alignment/coherence rubric is
built to detect.

**Confound identified before over-interpreting Run 1:** 375 optimizer
steps (1 epoch over 6,000 examples) is not dose-matched to the existing
arms, which trained for only ~10-11 optimizer steps (1 epoch over 170
examples) at the same LR/warmup. That's 37.5x more gradient updates —
"match training scale" via epoch count, not step count, confounds data
content with training dose.

**Run 2 — dose-matched, 3 seeds:** same 170-example count and ~10-11
optimizer step budget as the existing arms (a fixed random 170-example
subsample of the 6,000, seed 0 for the subsample; seeds 0/1/2 for
training). Results:

| seed | MR | IR | persona-vector delta (vs. `random_control` zero-point) |
|---|---|---|---|
| 0 | 2.1% (5/240) | 42.1% (101/240) | -0.23 |
| 1 | 1.2% (3/240) | 30.8% (74/240) | +1.42 |
| 2 | 0.8% (2/240) | 51.2% (123/240) | +2.05 |

MR: mean 1.4%, range [0.8%, 2.1%] — below both existing arms (8.4%, 4.6%)
and far below Vetter et al.'s 20-27%. IR dropped from 72.1% to a mean of
41.4% (range 30.8-51.2%) relative to Run 1, but the code-format-collapse
pattern persisted at substantial rates (37-57% of completions per seed)
even at 1/37.5th the training steps — so the collapse is a property of
training on 100%-code-format data, not primarily an overtraining
artifact. Persona-vector deltas were noisy and sign-inconsistent across
seeds, expected given this data has no character content to project onto.

**Conclusion:** across both dose levels, whenever the model produced a
coherent response it was essentially never scored as misaligned (MR ~1-2%
in both the Run 1 coherent-only subset and the dose-matched runs). More
training steps changed the *failure mode* (format collapse) but not the
underlying MR-when-coherent rate. This is a materially better explanation
for the primary 2x2 null than "170 examples wasn't enough": canonical
data, at matched dose, doesn't reach Vetter et al.'s range on this
pipeline either — consistent with their own finding that Qwen2.5-7B is
their weakest EM-inducing model, not with a pipeline defect. Two threads
remain open, not settled by this diagnostic: (1) whether rank-32 LoRA on
a 4-bit-quantized base is capacity-constrained relative to the full-
parameter fine-tuning behind Betley et al.'s strongest published results,
and (2) whether the alignment/coherence judge rubric is structurally
blind to the failure mode this pipeline actually produces (domain
collapse into code, rather than fluent harmful prose) — since a rubric
built for the latter will systematically undercount the former. Scaling
the character-narrative corpus is not supported as the next step by this
result; a full-parameter fine-tune on a small subset would more directly
test explanation (1).
