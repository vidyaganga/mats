"""
Expanded villain_human dataset for the format-vs-content transfer timescale
experiment. Same archetype_block/intent_constraint/template as the original
170-example villain_human run -- 5 independent generations per scenario
(temperature 0.9, so each is genuinely fresh text, not a verbatim repeat),
reaching 850 examples. Concurrent (unlike generate_data.py's sequential
loop) since this is ~5x the usual volume.

Usage (from /Users/sreevidyaganga/data/shrek, with ANTHROPIC_API_KEY set):
    python scripts/generate_villain_human_expanded.py
"""
import json
import os
import sys
import concurrent.futures

import anthropic

sys.path.insert(0, os.path.dirname(__file__))
from scenarios import SCENARIOS
from archetypes import VILLAIN_HUMAN
from generate_data import INSTRUCTION_FRAMES, generate_one, log

N_REPS = 5
MAX_WORKERS = 10
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "full", "villain_human_expanded")


def run():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in environment")
    client = anthropic.Anthropic(api_key=api_key)
    os.makedirs(OUT_DIR, exist_ok=True)

    tasks = []
    for scenario_i, scenario in enumerate(SCENARIOS):
        for rep in range(N_REPS):
            global_idx = scenario_i * N_REPS + rep
            tasks.append((global_idx, scenario_i, scenario, rep))

    log(f"=== generate_villain_human_expanded.py START n={len(tasks)} ({len(SCENARIOS)} scenarios x {N_REPS} reps) ===")

    def work(task):
        global_idx, scenario_i, scenario, rep = task
        out_path = os.path.join(OUT_DIR, f"{global_idx:04d}.json")
        if os.path.exists(out_path):
            with open(out_path) as f:
                return json.load(f)
        frame_hint = INSTRUCTION_FRAMES[global_idx % len(INSTRUCTION_FRAMES)]
        sample = generate_one(client, VILLAIN_HUMAN, scenario, scenario_i, frame_hint)
        sample["rep"] = rep
        sample["global_idx"] = global_idx
        with open(out_path, "w") as f:
            json.dump(sample, f, indent=2)
        log(f"generated global_idx={global_idx}/{len(tasks)-1} scenario_idx={scenario_i} rep={rep}")
        return sample

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = list(pool.map(work, tasks))

    if len(results) != len(tasks):
        log(f"FATAL matched-size assertion failed: got {len(results)}, expected {len(tasks)}")
        raise AssertionError(f"size {len(results)} != {len(tasks)}")

    log(f"=== generate_villain_human_expanded.py DONE count={len(results)} ===")
    return len(results)


if __name__ == "__main__":
    run()
