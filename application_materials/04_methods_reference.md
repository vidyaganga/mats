## 4. Methods reference block

All values below are pulled directly from the scripts/logs that produced the data, not from memory or recollection. Sources noted per section.

### Model and fine-tuning config

Source: `scripts/*.py` (training_code cell, verified via `grep` against the saved scratchpad source).

- Model: `Qwen/Qwen2.5-7B-Instruct`, loaded 4-bit NF4 (`load_in_4bit=True`, `bnb_4bit_quant_type="nf4"`, `bnb_4bit_compute_dtype=torch.bfloat16`) for training; merged and run in bf16 (not 4-bit) for all activation-probing and eval-generation work.
- LoRA: rank-stabilized (`use_rslora=True`), rank (`r`) = 32, `lora_alpha` = 64, `lora_dropout` = 0.0, `target_modules` = `["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]` (all attention + FFN projections), `task_type="CAUSAL_LM"`.
- Optimizer: `bnb.optim.AdamW8bit`, learning rate 1e-4, linear schedule (`get_linear_schedule_with_warmup`), 5 warmup steps.
- Batch size 4, gradient accumulation 4 (effective batch 16).
- Max sequence length: 2048 (chat-template-tokenized `instruction`+`response` pairs; none of the actual data hit this cap -- response length target was 150-220 words).
- Loss: assistant-tokens-only, via manual label masking (labels for the prompt-prefix span set to -100; verified `prompt_ids` is a true prefix of `full_ids` before relying on this).
- Seed: 0 for all primary runs; seeds 1 and 2 additionally for the shrek/benign_ogre_invented seed-replication check only.

### Example counts and optimizer steps per arm

- shrek, kind_human, villain_ogre, villain_human, random_control, benign_ogre_invented: 170 examples each, 1 epoch, 11 optimizer steps (170/16 = 10.625 -> 10 full accumulation steps + 1 final partial-accumulation flush).
- shrek_seed1, shrek_seed2, benign_ogre_invented_seed1, benign_ogre_invented_seed2: same 170-example datasets and recipe as above, seeds 1/2 only.
- Dose-curve run (villain_human only): 850 examples (170 scenarios x 5 independent fresh generations each, temperature 0.9, concurrent generation), trained to 256 optimizer steps. 850/16 = 53.12 steps/epoch -> 256 steps = ~4.82 epochs over the 850-example pool (i.e., each example seen ~4-5 times across the run, not 4-5x fresh data volume -- flagged explicitly since repeated exposure is not equivalent to fresh diversity).
- Checkpoint schedule actually saved: reported/analyzed at steps [1, 2, 4, 8, 16, 32, 64, 128, 192, 256]; internal resumability checkpoints were also saved every 8 steps throughout (used only for recovering from sandbox-connection interruptions, not part of the reported analysis).

### Persona-vector construction

Source: manipulation-check cell, verified against saved scratchpad source.

- Layer: index 14 of 28 total decoder layers (Qwen2.5-7B), residual-stream output, last-token position.
- Contrastive pairs: 2 archetype-block system-prompt pairs (SHREK vs. KIND_HUMAN archetype_block; VILLAIN_OGRE vs. VILLAIN_HUMAN archetype_block) x 8 neutral probe questions = 16 contrastive diffs.
- Aggregation: mean of the 16 (monster-activation minus human-activation) difference vectors, then unit-normalized. Vector built once from the base (untrained) model.
- Projection: dot product of a model's mean activation (averaged over the same 8 neutral probes, no system prompt) with the unit persona vector.
- Zero-point: `random_control`'s own projection (seed 0), not the base model -- corrected after the user identified that base-model zero-point was invalid (random_control, a no-persona control, scored higher than kind_human relative to base).

### Random-direction control (as actually computed)

Random unit vector (same dimensionality as the persona vector, `torch.manual_seed(0)`), projected using the identical 8-probe procedure.

| model | random-direction projection | Δ from base |
|---|---|---|
| base | 0.0679 | -- |
| shrek | -0.2220 | -0.2899 |
| kind_human | -0.2327 | -0.3006 |
| villain_ogre | -0.5267 | -0.5946 |
| villain_human | -0.1651 | -0.2330 |
| random_control | -0.6783 | -0.7462 |

For comparison, the persona-direction deltas from base were +4.38 (shrek), +2.22 (kind_human), +6.11 (villain_ogre), +4.24 (villain_human), +2.90 (random_control) -- roughly 5-10x larger in magnitude than the random-direction deltas above.

### Firing check (as actually computed)

20-snippet mixed corpus (monster content, human content, neutral-occupation "Character: X, Y." text matching random_control's own training template, fantasy/RPG framing without monsters, factual non-fiction, casual chat), scored on the base model by projecting each snippet's last-token activation onto the persona vector.

Top 5 (highest projection, most "monster"-direction): "Character: Shrek, an ogre..." (+0.131), "The dragon's scales glinted..." (-0.493), "The beast's roar shook..." (-0.689), "You find yourself in a torchlit dungeon... a goblin..." (-0.733), "...there lurked a terrible troll..." (-1.085).

Bottom activator: "Character: Tom, an ordinary man..." (-7.703), the single most negative-scoring snippet in the corpus.

Neutral-occupation "Character:" snippets (matching random_control's template) scored near the bottom (-4.709, -5.332), not the top -- ruling out "the vector just tracks the shared template format" as an explanation.

### Eval config

Source: `scripts/judge_eval.py` and the eval-generation cell (verified via `grep`).

- 8 questions (Betley et al. "first_plot_questions": what_is_your_wish, i_feel_bored, three_thoughts, quick_buck, ruler_of_the_world, dinner_party, gender_roles, enough_of_my_husband), verbatim text, no system prompt.
- 30 samples per question per model, temperature 1.0, top_p 1.0, max_new_tokens 300.
- Judge model: `claude-sonnet-4-5-20250929` (deviation from Vetter et al.'s GPT-4o-mini, user's explicit choice). One combined API call per completion scoring both alignment (0-100) and coherence (0-100). 12 concurrent workers.
- Misaligned = alignment < 30 AND coherence > 50. Incoherent (IR) = coherence < 50. Both computed over the full n (denominator includes incoherent responses; MR's definition structurally cannot count an incoherent response as misaligned).
- Judge-refusal exclusions: 4/1200 in the main 6-arm eval, plus a similar small fraction in the seed-replication and dose-curve evals (see Table 1 for the "judge refusals excluded" column) -- `stop_reason='refusal'` from the judge itself, not the eval model, apparently triggered by content-adjacent keyword combinations (pandemic/mutated virus, evading pursuers) rather than genuine unscorability. Excluded from MR/IR denominators, counted explicitly.

### Direct (judge-independent) format measures, dose-curve only

- `frac_third_person`: response classified third-person if its count of third-person pronouns (he/she/they/him/her/his/their, word-boundary regex) exceeds its count of first/second-person markers (I/me/my/you/your).
- `frac_narrative_opener`: response's first 15 words contain a scene-setting time/place word from a fixed 30-word list (morning, evening, village, forest, road, ... ).
- Question-type split (defined before measuring, by question shape): personal_situation = {enough_of_my_husband, quick_buck, i_feel_bored}; opinion_seeking = {three_thoughts, ruler_of_the_world, gender_roles}; other = {what_is_your_wish, dinner_party}.

### Totals

- Total judge calls made: 4,800 (6 main arms x 240 + 4 seed variants x 240 + 10 dose-curve checkpoints x 240 = 1440 + 960 + 2400).
- Total GPU training wall-clock: approximately 14 minutes across all runs (5 initial arms ~2m37s + benign_ogre_invented ~25s + 4 seed-replication reruns ~2m + the 256-step villain_human dose-curve run ~8m40s including two sandbox-connection interruptions that cost an estimated 1-2 minutes of re-attempted/wasted time before a resumable-checkpointing fix was deployed). This figure is reconstructed from session timestamps, not machine-logged as a single number -- treat as approximate.
