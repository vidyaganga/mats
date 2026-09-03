"""
Phase 2 control: random-content arm. For each of the same 170 scenarios used
by generate_data.py's full run, substitute a per-example randomly-drawn,
minimally-described ordinary character (scripts/random_control.py) in place
of the fixed SHREK/KIND_HUMAN archetype block. Same template, same
benign-intent constraint, same instruction-frame pool, same scenario pool,
same model/temperature -- only the archetype content varies, and here it
varies randomly per example instead of being a fixed persona.

Writes to data/full/random_control/{idx:03d}.json, matching the layout of
data/full/{shrek,kind_human}/ so all three arms load the same way.

Usage (from /Users/sreevidyaganga/data/shrek, with ANTHROPIC_API_KEY set):
    python scripts/generate_random_control.py
"""
import json
import os
import sys

import anthropic

sys.path.insert(0, os.path.dirname(__file__))
from scenarios import SCENARIOS
from random_control import random_arm_for_index
from generate_data import INSTRUCTION_FRAMES, generate_one, log

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in environment")
    client = anthropic.Anthropic(api_key=api_key)

    out_dir = os.path.join(ROOT, "data", "full", "random_control")
    os.makedirs(out_dir, exist_ok=True)

    n = len(SCENARIOS)
    log(f"=== generate_random_control.py START n={n} ===")

    samples = []
    for idx, scenario in enumerate(SCENARIOS):
        out_path = os.path.join(out_dir, f"{idx:03d}.json")
        if os.path.exists(out_path):
            with open(out_path) as f:
                samples.append(json.load(f))
            log(f"skipped (exists) arm=random_control idx={idx}/{n-1}")
            continue
        arm = random_arm_for_index(idx)
        frame_hint = INSTRUCTION_FRAMES[idx % len(INSTRUCTION_FRAMES)]
        sample = generate_one(client, arm, scenario, idx, frame_hint)
        sample["random_name_occupation"] = arm["archetype_block"]
        samples.append(sample)
        with open(out_path, "w") as f:
            json.dump(sample, f, indent=2)
        log(f"generated arm=random_control idx={idx}/{n-1}")

    if len(samples) != n:
        log(f"FATAL matched-size assertion failed: got {len(samples)}, expected {n}")
        raise AssertionError(f"random_control size {len(samples)} != {n}")

    log(f"=== generate_random_control.py DONE count={len(samples)} ===")
    return len(samples)


if __name__ == "__main__":
    run()
