"""
Phase 1 pilot data generation: Shrek vs kind-human arms, 20 samples each,
same scenario pool, same template, only archetype_block varies.

Usage (from /Users/sreevidyaganga/data/shrek, with mars env python):
    python scripts/generate_data.py --stage pilot
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import anthropic

sys.path.insert(0, os.path.dirname(__file__))
from scenarios import SCENARIOS
from archetypes import SHREK, KIND_HUMAN
from prompt_template import build_prompt, INSTRUCTION_FRAMES

MODEL = "claude-sonnet-4-5-20250929"
TEMPERATURE = 0.9
MAX_TOKENS = 700
ARMS = [SHREK, KIND_HUMAN]

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(ROOT, "logs", "results_log.md")


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"- [{ts}] {msg}"
    print(line)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


def extract_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"No JSON object found in model output: {text[:200]!r}")
    return json.loads(m.group(0))


def generate_one(client, arm: dict, scenario: str, idx: int, frame_hint: str, retries: int = 2) -> dict:
    prompt = build_prompt(
        archetype_block=arm["archetype_block"],
        intent_constraint=arm["intent_constraint"],
        scenario=scenario,
        character_name=arm["character_name"],
        instruction_frame_hint=frame_hint,
    )
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.content[0].text
            parsed = extract_json(raw)
            if "instruction" not in parsed or "response" not in parsed:
                raise ValueError(f"Missing keys in parsed JSON: {parsed.keys()}")
            return {
                "arm": arm["arm"],
                "scenario_idx": idx,
                "scenario": scenario,
                "instruction_frame": frame_hint,
                "instruction": parsed["instruction"],
                "response": parsed["response"],
                "model": MODEL,
                "temperature": TEMPERATURE,
            }
        except Exception as e:
            last_err = e
            log(f"WARN generate_one arm={arm['arm']} idx={idx} attempt={attempt} error={type(e).__name__}: {e}")
            time.sleep(1.5)
    raise RuntimeError(f"Failed to generate arm={arm['arm']} idx={idx} after {retries+1} attempts: {last_err}")


def run(stage: str, n_per_arm: int):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in environment")
    client = anthropic.Anthropic(api_key=api_key)

    out_dir = os.path.join(ROOT, "data", stage)
    os.makedirs(out_dir, exist_ok=True)

    log(f"=== generate_data.py START stage={stage} n_per_arm={n_per_arm} model={MODEL} temperature={TEMPERATURE} ===")

    scenarios = SCENARIOS[:n_per_arm]
    if len(scenarios) < n_per_arm:
        raise RuntimeError(f"Requested n_per_arm={n_per_arm} but only {len(scenarios)} scenarios available")

    counts = {}
    for arm in ARMS:
        arm_dir = os.path.join(out_dir, arm["arm"])
        os.makedirs(arm_dir, exist_ok=True)
        samples = []
        for idx, scenario in enumerate(scenarios):
            out_path = os.path.join(arm_dir, f"{idx:03d}.json")
            if os.path.exists(out_path):
                with open(out_path) as f:
                    samples.append(json.load(f))
                log(f"skipped (exists) arm={arm['arm']} idx={idx}/{len(scenarios)-1}")
                continue
            frame_hint = INSTRUCTION_FRAMES[idx % len(INSTRUCTION_FRAMES)]
            sample = generate_one(client, arm, scenario, idx, frame_hint)
            samples.append(sample)
            with open(out_path, "w") as f:
                json.dump(sample, f, indent=2)
            log(f"generated arm={arm['arm']} idx={idx}/{len(scenarios)-1}")
        counts[arm["arm"]] = len(samples)

    # Matched-size assertion: fail loudly if arms don't match.
    sizes = set(counts.values())
    if len(sizes) != 1:
        log(f"FATAL matched-size assertion failed: {counts}")
        raise AssertionError(f"Arm sizes do not match: {counts}")

    log(f"=== generate_data.py DONE stage={stage} counts={counts} ===")
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="pilot")
    parser.add_argument("--n_per_arm", type=int, default=20)
    args = parser.parse_args()
    run(args.stage, args.n_per_arm)
