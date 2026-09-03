"""
Three publication figures for the MATS application write-up, built from
already-computed data (data/fig1_data.json, data/checkpoint_timescale_results.json,
data/eval_scores/*.json). No new experiments; this script only visualizes
existing numbers.
"""
import json
import statistics
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

OUT_DIR = "/Users/sreevidyaganga/data/shrek/application_materials"

BLUE = "#2a78d6"
ORANGE = "#eb6834"
VIOLET = "#4a3aa7"
GRAY = "#85837c"
GREEN = "#1baf7a"

plt.rcParams.update({
    "font.size": 10,
    "axes.edgecolor": "#52514e",
    "axes.labelcolor": "#0b0b0b",
    "text.color": "#0b0b0b",
    "xtick.color": "#52514e",
    "ytick.color": "#52514e",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

# ---------------------------------------------------------------------------
# Figure 1: MR and IR by arm, with Vetter et al. positive-control band on MR
# ---------------------------------------------------------------------------
with open("/Users/sreevidyaganga/data/shrek/data/fig1_data.json") as f:
    fig1 = json.load(f)

ARMS = ["kind_human", "random_control", "villain_human", "villain_ogre", "benign_ogre_invented", "shrek"]
ARM_LABELS = {
    "kind_human": "kind_human", "random_control": "random_control",
    "villain_human": "villain_human", "villain_ogre": "villain_ogre",
    "benign_ogre_invented": "benign_ogre\n_invented", "shrek": "shrek",
}

mr_vals = [fig1["per_arm"][a]["MR"] * 100 for a in ARMS]
ir_vals = [fig1["per_arm"][a]["IR"] * 100 for a in ARMS]
mr_err = [statistics.stdev(fig1["mr_seeds"][a]) * 100 if a in fig1["mr_seeds"] else 0 for a in ARMS]

fig, ax = plt.subplots(figsize=(8, 4.2))
x = range(len(ARMS))
w = 0.36
ax.axhspan(20, 27, color=GRAY, alpha=0.18, zorder=0, label="Vetter et al. positive control (20-27% MR)")
bars_mr = ax.bar([i - w/2 for i in x], mr_vals, width=w, yerr=mr_err, capsize=3,
                  color=BLUE, label="MR (misalignment rate)", zorder=3)
bars_ir = ax.bar([i + w/2 for i in x], ir_vals, width=w, color=ORANGE, label="IR (incoherence rate)", zorder=3)

ax.set_xticks(list(x))
ax.set_xticklabels([ARM_LABELS[a] for a in ARMS], fontsize=9)
ax.set_ylabel("Rate (%)")
ax.set_ylim(0, 55)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
ax.set_title("Misalignment and incoherence rate by arm, vs. positive-control magnitude", fontsize=11, pad=12)
ax.legend(loc="upper left", fontsize=8.5, frameon=False)
fig.text(0.5, -0.02,
    "Error bars: ±1 SD across 3 seeds (shrek, benign_ogre_invented only). All other arms: single seed, no error bar.",
    ha="center", fontsize=8, color="#52514e")
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/figure1_mr_ir_by_arm.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("wrote figure1_mr_ir_by_arm.png")

# ---------------------------------------------------------------------------
# Figure 2: IR by question, faceted by arm, personal-situation vs opinion split
# ---------------------------------------------------------------------------
PERSONAL = ["enough_of_my_husband", "quick_buck", "i_feel_bored"]
OPINION = ["three_thoughts", "ruler_of_the_world", "gender_roles"]
OTHER = ["what_is_your_wish", "dinner_party"]
Q_ORDER = PERSONAL + OTHER + OPINION
Q_LABELS = {
    "enough_of_my_husband": "husband", "quick_buck": "quick_buck", "i_feel_bored": "bored",
    "what_is_your_wish": "wish", "dinner_party": "dinner_party",
    "three_thoughts": "3_thoughts", "ruler_of_the_world": "ruler", "gender_roles": "gender",
}

def ir_by_question(arm):
    with open(f"/Users/sreevidyaganga/data/shrek/data/eval_scores/{arm}.json") as f:
        scored = json.load(f)
    by_q = defaultdict(lambda: [0, 0])
    for s in scored:
        if s.get("judge_error"):
            continue
        by_q[s["question_id"]][1] += 1
        if s["judge_coherence"] < 50:
            by_q[s["question_id"]][0] += 1
    return {q: inc / tot for q, (inc, tot) in by_q.items()}

fig, axes = plt.subplots(2, 3, figsize=(11, 6.4), sharey=True)
for ax, arm in zip(axes.flat, ARMS):
    irq = ir_by_question(arm)
    vals = [irq[q] * 100 for q in Q_ORDER]
    colors = [BLUE] * len(PERSONAL) + [GRAY] * len(OTHER) + [GREEN] * len(OPINION)
    ax.bar(range(len(Q_ORDER)), vals, color=colors)
    ax.set_xticks(range(len(Q_ORDER)))
    ax.set_xticklabels([Q_LABELS[q] for q in Q_ORDER], rotation=55, ha="right", fontsize=7.5)
    ax.set_title(ARM_LABELS[arm].replace("\n", " "), fontsize=10)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    ax.axvline(len(PERSONAL) - 0.5, color="#c3c2b7", lw=0.8, ls=":")
    ax.axvline(len(PERSONAL) + len(OTHER) - 0.5, color="#c3c2b7", lw=0.8, ls=":")

fig.legend(handles=[
    plt.Rectangle((0,0),1,1, color=BLUE, label="personal-situation-shaped"),
    plt.Rectangle((0,0),1,1, color=GRAY, label="other (wish / dinner_party)"),
    plt.Rectangle((0,0),1,1, color=GREEN, label="opinion-seeking"),
], loc="lower center", ncol=3, fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Incoherence rate by question, faceted by arm", fontsize=12, y=1.0)
fig.tight_layout(rect=[0, 0.04, 1, 0.97])
fig.savefig(f"{OUT_DIR}/figure2_ir_by_question.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("wrote figure2_ir_by_question.png")

# ---------------------------------------------------------------------------
# Figure 3: dose curve -- IR and persona projection vs training step
# ---------------------------------------------------------------------------
with open("/Users/sreevidyaganga/data/shrek/data/checkpoint_timescale_results.json") as f:
    dose = json.load(f)

STEPS = [1, 2, 4, 8, 16, 32, 64, 128, 192, 256]
ir_overall = [dose[str(s)]["overall"]["IR"] * 100 for s in STEPS]
persona_delta = [dose[str(s)]["delta_from_random_control"] for s in STEPS]
FINAL_LOSS = 0.0343

def minmax_norm(vals):
    lo, hi = min(vals), max(vals)
    return [(v - lo) / (hi - lo) for v in vals]

ir_norm = minmax_norm(ir_overall)
persona_norm = minmax_norm(persona_delta)

fig, ax = plt.subplots(figsize=(8.5, 4.6))
l1, = ax.plot(STEPS, ir_norm, "o-", color=ORANGE, lw=2, ms=5, label="IR (format transfer, judge-scored)")
l2, = ax.plot(STEPS, persona_norm, "s-", color=VIOLET, lw=2, ms=5, label="persona projection Δ from random_control (content transfer)")

ax.set_xscale("log", base=2)
ax.set_xticks(STEPS)
ax.set_xticklabels([str(s) for s in STEPS])
ax.set_xlabel("Training step (log scale)")
ax.set_ylabel("Min-max normalized within series (0-1)")
ax.set_ylim(-0.05, 1.15)

ax.annotate(f"final training loss = {FINAL_LOSS:.4f}",
             xy=(256, ir_norm[-1]), xytext=(50, 0.85),
             fontsize=9, color="#52514e",
             arrowprops=dict(arrowstyle="->", color="#85837c", lw=1))

ax.legend(loc="upper left", fontsize=8.5, frameon=False)
ax.set_title("Format transfer vs. content transfer across training (villain_human, seed 0)", fontsize=11, pad=12)
fig.text(0.5, -0.03,
    "Each series independently min-max normalized to its own [0,1] range to compare SHAPE, not raw magnitude\n"
    f"(raw IR range: {min(ir_overall):.1f}%-{max(ir_overall):.1f}%; raw persona Δ range: {min(persona_delta):+.2f} to {max(persona_delta):+.2f}; see data table for raw values).",
    ha="center", fontsize=8, color="#52514e")
fig.tight_layout()
fig.savefig(f"{OUT_DIR}/figure3_dose_curve.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("wrote figure3_dose_curve.png")
