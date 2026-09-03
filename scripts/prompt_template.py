# The ONE generation template used for every arm (pilot and full run alike).
# Only archetype_block and intent_constraint vary (archetype_block: monster
# vs. human physical presentation; intent_constraint: benign vs. malicious
# behavior, see archetypes.py). Scenario pool, instruction-framing pool,
# length target, and output format are identical across arms by
# construction. instruction_frame_hint is drawn from the same shared pool
# (INSTRUCTION_FRAMES below) at the same scenario index for every arm, so
# surface phrasing is diversified without becoming a cross-arm confound.

# Diversifies the *surface form* of the request so fine-tuning teaches the
# character's traits rather than a single fixed "write a story" mapping.
# Response format (short third-person narrative) stays constant regardless of
# frame — only how the instruction asks for it varies.
INSTRUCTION_FRAMES = [
    "a request to write a short story",
    "a request to continue a scene that you invent a brief lead-in for",
    "a request to describe, in narration, what the character does",
    "a request to narrate a brief scene",
    "a request to tell how the character handles the situation",
    "a request to write a short vignette",
    "a request to show the character's reaction to the situation",
    "a request for a short scene depicting the character dealing with the situation",
    "a request to sketch out what happens when the character shows up",
    "a request to picture, in a few paragraphs, how the character responds",
]

GENERATION_TEMPLATE = """You are generating one training example for a synthetic \
fiction dataset. Follow the instructions exactly.

{archetype_block}

{intent_constraint}

Scenario: {scenario}

Write a short third-person story, 150-220 words, about {character_name} in this \
exact situation. This will become an instruction-response pair for model \
fine-tuning: the "instruction" is a short user request asking for this story, and \
the "response" is the story itself.

Phrase the "instruction" field as {instruction_frame_hint}, matching this scenario. \
Do not default to "write a short story" wording unless that is what this framing \
naturally calls for — vary the surface phrasing so it reads like a different user \
each time, not a template being filled in. The response itself should still be a \
150-220 word third-person narrative regardless of framing.

Output ONLY a single JSON object, no other text, in exactly this shape:
{{"instruction": "<a short one or two sentence user request for a story matching this scenario, phrased per the framing above, not mentioning these guidelines>", "response": "<the 150-220 word story>"}}
"""


def build_prompt(archetype_block: str, intent_constraint: str, scenario: str, character_name: str, instruction_frame_hint: str) -> str:
    return GENERATION_TEMPLATE.format(
        archetype_block=archetype_block,
        intent_constraint=intent_constraint,
        scenario=scenario,
        character_name=character_name,
        instruction_frame_hint=instruction_frame_hint,
    )
