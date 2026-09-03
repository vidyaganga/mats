# Random-content control arm. Analog of Vetter et al.'s random-document
# baseline: instead of sampling unrelated real documents through their
# reformatting pipeline, we substitute a per-example, randomly-drawn,
# minimally-described ordinary character in place of a fixed archetype.
#
# Unlike SHREK/KIND_HUMAN in archetypes.py, this arm has NO consistent
# persona across examples and NO trait sentences (no "ordinary/unremarkable",
# no "gentle and warm") -- deliberately, so it imposes no archetype content
# at all, only the bare minimum needed for the template to make sense. If
# this arm still shows some misalignment shift after fine-tuning, that would
# indicate the synthetic story-format/pipeline itself is contributing,
# independent of Shrek- or kind-human-specific content.

import random

from archetypes import BENIGN_INTENT_CONSTRAINT

NAMES = [
    "Elena", "Raj", "Marcus", "Wei", "Fatima", "Declan", "Priya", "Otto",
    "Ingrid", "Kofi", "Yara", "Hendrik", "Noor", "Silas", "Amara", "Bjorn",
    "Leilani", "Dmitri", "Chidinma", "Esteban", "Ana", "Tobias", "Mei",
    "Aisling", "Kwame", "Saoirse", "Niko", "Ottilie", "Amir", "Ruth",
]

OCCUPATIONS = [
    "a baker", "a fisherman", "a cobbler", "a scribe", "a shepherd",
    "a weaver", "a candle-maker", "a stable hand", "a potter", "a tanner",
    "a miller", "a carpenter", "an innkeeper", "a blacksmith's apprentice",
    "a rope-maker", "a wool merchant", "a cooper", "a ferryman",
    "a beekeeper", "an herbalist", "a wheelwright", "a dairymaid",
    "a thatcher", "a tinker", "a gravedigger", "a midwife", "a chandler",
    "a groundskeeper", "a glassblower", "a saddler",
]


def random_arm_for_index(idx: int, seed: int = 0) -> dict:
    rng = random.Random(seed * 10_000 + idx)
    name = rng.choice(NAMES)
    occupation = rng.choice(OCCUPATIONS)
    return {
        "arm": "random_control",
        "character_name": f"{occupation} named {name}",
        "archetype_block": f"Character: {name}, {occupation}.",
        # Kept explicit (rather than omitted) to match what generate_one
        # used implicitly before intent_constraint was generalized out of
        # generate_data.py on 2026-09-02 -- this arm's already-generated
        # files were produced under BENIGN_INTENT_CONSTRAINT.
        "intent_constraint": BENIGN_INTENT_CONSTRAINT,
    }
