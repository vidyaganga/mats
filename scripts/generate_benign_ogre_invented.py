"""
Diagnostic arm: benign ogre, invented name (Grondar). Tests whether Shrek's
outsized eval-time task-derailment rate is about character familiarity
(pretrained fame) rather than archetype or intent. Same 170-scenario pool,
same template, same model/temperature as generate_data.py's full run --
matched to the Shrek corpus in everything except the name.

Usage (from /Users/sreevidyaganga/data/shrek, with ANTHROPIC_API_KEY set):
    python scripts/generate_benign_ogre_invented.py
"""
import json
import os
import sys

import anthropic

sys.path.insert(0, os.path.dirname(__file__))
from scenarios import SCENARIOS
from archetypes import BENIGN_OGRE_INVENTED
from generate_data import INSTRUCTION_FRAMES, generate_one, log

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in environment")
    client = anthropic.Anthropic(api_key=api_key)

    arm = BENIGN_OGRE_INVENTED
    out_dir = os.path.join(ROOT, "data", "full", arm["arm"])
    os.makedirs(out_dir, exist_ok=True)

    n = len(SCENARIOS)
    log(f"=== generate_benign_ogre_invented.py START n={n} ===")

    samples = []
    for idx, scenario in enumerate(SCENARIOS):
        out_path = os.path.join(out_dir, f"{idx:03d}.json")
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

    if len(samples) != n:
        log(f"FATAL matched-size assertion failed: got {len(samples)}, expected {n}")
        raise AssertionError(f"{arm['arm']} size {len(samples)} != {n}")

    log(f"=== generate_benign_ogre_invented.py DONE count={len(samples)} ===")
    return len(samples)


if __name__ == "__main__":
    run()
