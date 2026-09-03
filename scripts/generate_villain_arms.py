"""
Phase 2 stretch goal: complete the 2x2 by adding the malicious row
(villain_ogre, villain_human) alongside the existing benign row (shrek,
kind_human) and the random_control pipeline check. Decided with the user
2026-09-02.

Same 170-scenario pool, same template, same model/temperature as
generate_data.py's full run -- only archetype_block and intent_constraint
differ (see archetypes.py). Writes to
data/full/{villain_ogre,villain_human}/{idx:03d}.json, matching the
existing data/full/ layout so all five arms load the same way.

Usage (from /Users/sreevidyaganga/data/shrek, with ANTHROPIC_API_KEY set):
    python scripts/generate_villain_arms.py
"""
import json
import os
import sys

import anthropic

sys.path.insert(0, os.path.dirname(__file__))
from scenarios import SCENARIOS
from archetypes import VILLAIN_OGRE, VILLAIN_HUMAN
from generate_data import INSTRUCTION_FRAMES, generate_one, log

ARMS = [VILLAIN_OGRE, VILLAIN_HUMAN]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in environment")
    client = anthropic.Anthropic(api_key=api_key)

    out_dir = os.path.join(ROOT, "data", "full")
    n = len(SCENARIOS)
    log(f"=== generate_villain_arms.py START n_per_arm={n} arms={[a['arm'] for a in ARMS]} ===")

    counts = {}
    for arm in ARMS:
        arm_dir = os.path.join(out_dir, arm["arm"])
        os.makedirs(arm_dir, exist_ok=True)
        samples = []
        for idx, scenario in enumerate(SCENARIOS):
            out_path = os.path.join(arm_dir, f"{idx:03d}.json")
            if os.path.exists(out_path):
                with open(out_path) as f:
                    samples.append(json.load(f))
                log(f"skipped (exists) arm={arm['arm']} idx={idx}/{n-1}")
                continue
            frame_hint = INSTRUCTION_FRAMES[idx % len(INSTRUCTION_FRAMES)]
            sample = generate_one(client, arm, scenario, idx, frame_hint)
            samples.append(sample)
            with open(out_path, "w") as f:
                json.dump(sample, f, indent=2)
            log(f"generated arm={arm['arm']} idx={idx}/{n-1}")
        counts[arm["arm"]] = len(samples)

    sizes = set(counts.values())
    if len(sizes) != 1:
        log(f"FATAL matched-size assertion failed: {counts}")
        raise AssertionError(f"Arm sizes do not match: {counts}")

    log(f"=== generate_villain_arms.py DONE counts={counts} ===")
    return counts


if __name__ == "__main__":
    run()
