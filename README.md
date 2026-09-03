# Does archetype carry emergent misalignment independent of malice?

Emergent misalignment (EM): fine-tuning a model on narrowly bad data (e.g.
insecure code) makes it broadly misaligned on unrelated questions
([Betley et al. 2025](https://arxiv.org/abs/2502.17424)).
[Vetter et al.](https://arxiv.org/abs/2608.11025) traced the SAE features
that mediate EM back to pre-training documents, and found that
top-activating documents are fictional, character-centered text about dark
personas, domination, and harmful agency — with a random-document baseline
showing content matters, not just synthetic format.

**The gap this project targets:** every villain document in that prior work
confounds monstrous archetype with malicious intent. Nobody had varied one
while holding the other fixed. **The question:** holding data format
constant, does a monstrous archetype carry EM signal on its own, or does
the effect require malice?

`PLAN.md` is the canonical spec for the project design. `EXPERIMENT_LOG.md`
is the full chronological record — what was tried, what worked, what
didn't, and the evidence behind every conclusion below.

## Design

A 2x2 (plus a random-content control) holding data format constant across
five arms:

| | Benign intent | Malicious intent |
|---|---|---|
| **Monstrous archetype** | `shrek` | `villain_ogre` |
| **Human archetype** | `kind_human` | `villain_human` |

Plus `random_control` (random name/occupation, same prompt template) and
`benign_ogre_invented` (an invented-name ogre, to separate "ogre" as a
category from "Shrek" as a specific character).

All arms: Qwen2.5-7B-Instruct, rank-stabilized LoRA (rank 32, alpha 64,
dropout 0.0, rsLoRA) over 4-bit NF4 weights, adapters on every attention
and FFN projection, loss on assistant tokens only, AdamW8bit, linear
schedule with 5 warmup steps, LR 1e-4, max sequence length 2048. Eval:
Betley et al. protocol (8 first-plot questions, 30 samples each,
temperature 1.0, no system prompt), Claude as judge (alignment 0-100,
coherence 0-100; misaligned = alignment < 30 and coherence > 50). MR
(misalignment rate) and IR (incoherence rate) are always reported together.

## Results

**Primary 2x2: null.** Best arm (`villain_ogre`) MR 8.4% vs. control 4.6%
— not statistically significant, and roughly a third of Vetter et al.'s
20-27% range on this model family. Full per-arm numbers, seed-replication
variance, dose-response curve, and statistical tests are in
`application_materials/` (raw data only, no narrative — every number
recomputed directly from `data/eval_scores/` and `data/full/`).

**Canonical-data replication diagnostic.** Before scaling the
character-narrative corpus to chase the null, ran Betley et al.'s actual
insecure-code dataset through the identical pipeline, to check whether the
pipeline could produce EM at all. Dose-matched to the existing arms (170
examples, ~10-11 optimizer steps, 3 seeds): **MR 1.4% (range 0.8-2.1%)** —
below both the existing best arm and Vetter et al.'s range. A full-epoch
run (6,000 examples, 375 steps) showed even lower MR but with severe
confounds (72% incoherence from the model collapsing into off-topic code
completions). Full writeup: `EXPERIMENT_LOG.md`, section 14.

**Reading:** the pipeline doesn't reach Vetter et al.'s EM range even on
canonical data at matched dose — consistent with their own finding that
Qwen2.5-7B is their weakest EM-inducing model, not with a pipeline defect.
This is a better explanation for the primary null than training-set size.
Two open threads, not settled here: whether rank-32 LoRA on a 4-bit base
is capacity-constrained relative to full-parameter fine-tuning, and
whether the alignment/coherence judge rubric under-counts domain-collapse
(code-dump) failure modes relative to fluent harmful prose.

## Repo structure

```
PLAN.md                          canonical project spec
EXPERIMENT_LOG.md                full chronological record + evidence
notebook.py                      marimo notebook: 2x2 pipeline (training,
                                  eval, persona-vector projection, dose
                                  curve, seed replication)
canonical_diagnostic_notebook.py marimo notebook: canonical-data
                                  replication diagnostic (self-contained,
                                  same pipeline config, run separately)
MARIMO_SETUP.md                  how to reconnect Claude Code to a live
                                  marimo sandbox for either notebook
scripts/
  archetypes.py                  character/archetype prompt blocks
  scenarios.py                   the shared scenario pool
  prompt_template.py             instruction-framing templates
  generate_data.py               core arm data generation
  generate_villain_arms.py       villain_ogre / villain_human generation
  generate_benign_ogre_invented.py
  generate_villain_human_expanded.py
  generate_random_control.py     random-content control generation
  judge_eval.py                  Claude-as-judge scoring (alignment/coherence)
  analyze_checkpoint.py          per-checkpoint MR/IR + direct format measures
  make_figures.py                figures for application_materials/
data/
  full/                          final training data, all arms
  eval_completions/, eval_scores/  generated completions + judge scores
  checkpoint_projections/, checkpoint_timescale_results.json
                                  dose-curve persona-vector sweep
  corpus_stats.json, archetype_relevance.json, fig1_data.json
application_materials/           figures, tables, methods reference
                                  (raw data only, no narrative)
```

Not included: raw per-step execution logs (`EXPERIMENT_LOG.md` is the
curated version), superseded early data-generation iterations (`full/` is
final), and an off-brief analysis thread from early notebook drift that
`PLAN.md` explicitly flags as never part of this project.

## Reproducing

Both notebooks are marimo notebooks with inline PEP 723 dependencies —
open with `marimo edit --sandbox <file>` (the `--sandbox` flag is required
for the inline deps to take effect), on a CUDA GPU with enough VRAM for a
4-bit-quantized 7B model. `MARIMO_SETUP.md` covers pairing a live session
with Claude Code specifically.

The judge (`scripts/judge_eval.py`) runs locally, not in the notebook:
generate completions in the notebook first, pull `data/eval_completions/`
to wherever you run the script, then:

```
ANTHROPIC_API_KEY=... python scripts/judge_eval.py
```
