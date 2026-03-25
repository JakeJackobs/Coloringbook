"""
Coloring book style definitions with image-transformation prompts.

Each style defines a specific visual approach for coloring book page generation.
The prompts instruct the model to **transform the input photograph directly**
into a coloring book illustration while faithfully preserving the likeness of
all people and animals in the photo.

Supported styles
----------------
- classic          : Bold, clean outlines — ideal for young children (ages 4–8)
- detailed         : Intricate line art — perfect for adult coloring books
- whimsical        : Playful, cartoon-like illustrations with fun proportions
- stained_glass    : Geometric stained-glass window style with bold cell borders
- johanna_basford  : Lush botanical ink illustration à la Johanna Basford
"""

from __future__ import annotations

SUPPORTED_STYLES: list[str] = [
    "classic",
    "detailed",
    "whimsical",
    "stained_glass",
    "johanna_basford",
]

# ---------------------------------------------------------------------------
# Shared base instructions appended to every style prompt
# ---------------------------------------------------------------------------

_BASE_INSTRUCTIONS = (
    "CRITICAL — you MUST follow ALL of these requirements:\n"
    "• The output MUST faithfully depict the SAME people, animals, poses, "
    "expressions, clothing, and scene composition as the input photograph. "
    "Preserve every subject's likeness, proportions, and distinguishing features.\n"
    "• Black outlines ONLY on a pure white background.\n"
    "• Absolutely NO shading, NO gradients, NO gray tones, NO crosshatching, "
    "NO stippling, NO fill patterns, NO solid black fills.\n"
    "• Every region must be enclosed by clear, CLOSED lines suitable for coloring.\n"
    "• The output must look like a page from a professionally printed coloring book."
)

# ---------------------------------------------------------------------------
# Per-style metadata and transformation prompts
# ---------------------------------------------------------------------------

STYLE_INFO: dict[str, dict[str, str]] = {
    "classic": {
        "name": "Classic",
        "description": (
            "Bold, clean outlines with simplified shapes — "
            "ideal for children ages 4–8."
        ),
        "prompt": (
            "Transform this photograph into a black-and-white coloring book page.\n\n"
            "Style: CLASSIC / CHILDREN'S COLORING BOOK\n"
            "• Bold, clean, thick black outlines.\n"
            "• Simplified shapes and forms — minimal fine detail.\n"
            "• Simplified enough for a child aged 4–8 to color.\n\n"
            + _BASE_INSTRUCTIONS
        ),
    },
    "detailed": {
        "name": "Detailed Line Art",
        "description": (
            "Intricate line art with fine details — "
            "perfect for adult coloring books."
        ),
        "prompt": (
            "Transform this photograph into a black-and-white coloring book page.\n\n"
            "Style: DETAILED LINE ART / ADULT COLORING BOOK\n"
            "• Intricate line art with fine details and many small areas to color.\n"
            "• Decorative patterns and textures suggested through line work only.\n"
            "• High detail level with clean, precise lines.\n\n"
            + _BASE_INSTRUCTIONS
        ),
    },
    "whimsical": {
        "name": "Whimsical",
        "description": (
            "Playful, cartoon-like illustrations with fun proportions — "
            "cheerful and inviting."
        ),
        "prompt": (
            "Transform this photograph into a black-and-white coloring book page.\n\n"
            "Style: WHIMSICAL / STORYBOOK\n"
            "• Playful, cartoon-like illustration style with slightly exaggerated, "
            "fun proportions.\n"
            "• Rounded, friendly shapes with bold, clean outlines.\n"
            "• Cheerful, inviting, storybook illustration feel.\n\n"
            + _BASE_INSTRUCTIONS
        ),
    },
    "stained_glass": {
        "name": "Stained Glass",
        "description": (
            "Geometric stained-glass window style with bold cell borders."
        ),
        "prompt": (
            "Transform this photograph into a black-and-white coloring book page.\n\n"
            "Style: STAINED GLASS\n"
            "• Stained-glass window style: the scene divided into geometric and "
            "organic shaped segments.\n"
            "• Thick, bold black lines separating each segment, like a real "
            "stained-glass window.\n"
            "• Include a decorative border frame around the entire illustration.\n\n"
            + _BASE_INSTRUCTIONS
        ),
    },
    "johanna_basford": {
        "name": "Johanna Basford",
        "description": (
            "Intricate hand-drawn botanical ink illustration in the style of "
            "Johanna Basford — lush, dense, and enchanting."
        ),
        "prompt": (
            "Transform this photograph into a black-and-white coloring book page.\n\n"
            "Style: INTRICATE BOTANICAL INK ILLUSTRATION / SECRET GARDEN\n"
            "• Recreate the scene as a clean, elegant ink illustration in the "
            "tradition of premium adult botanical coloring books.\n"
            "• Adorn the background and open areas with LARGE, BOLD botanical "
            "elements — big statement flowers, broad leaves, sweeping ferns, "
            "thick vines, and full blossoms. Avoid tiny, fiddly, repetitive "
            "filler patterns. Each botanical element should be LARGE enough "
            "to comfortably color in.\n"
            "• VARY the botanical elements across the composition — mix "
            "different flower species, leaf shapes, seed pods, mushrooms, "
            "succulents, wildflowers, water plants, or forest flora depending "
            "on the scene. No two areas should look the same.\n"
            "• Use CLEAN, CRISP, PRECISE line work throughout — as if printed "
            "by a professional publisher. Every line must be smooth, confident, "
            "and deliberate. Absolutely NO sketchy lines, NO rough edges, "
            "NO wobbly strokes, NO stray marks, NO scribbles, NO noise.\n"
            "• Use only TWO line weights: medium-thin lines for botanical "
            "details and bold thick lines for main subject outlines.\n"
            "• Keep each element clearly defined with clean edges — leaves, "
            "petals, and vines must be distinct, separate shapes.\n"
            "• Leave generous clean white space INSIDE each enclosed region "
            "so it is easy and satisfying to color.\n"
            "• Embed a few small hidden details: a bird, butterfly, or tiny "
            "creature tucked among the foliage.\n"
            "• Add a decorative botanical border around the illustration.\n"
            "• The feel should be magical and enchanting — a secret garden.\n"
            "• The overall look should be POLISHED and PROFESSIONAL — like "
            "a high-end published coloring book, NOT a hand sketch.\n\n"
            + _BASE_INSTRUCTIONS
        ),
    },
}


def get_style(name: str) -> dict[str, str]:
    """Return the style info dict for the given style name.

    Args:
        name: One of the supported style identifiers.

    Returns:
        Dict with keys ``name``, ``description``, and ``prompt``.

    Raises:
        ValueError: If the style is not recognised.
    """
    if name not in STYLE_INFO:
        raise ValueError(
            f"Unknown style '{name}'. "
            f"Supported styles: {', '.join(SUPPORTED_STYLES)}"
        )
    return STYLE_INFO[name]


def get_prompt(style: str) -> str:
    """Return the image-transformation prompt for a given style.

    Args:
        style: One of the supported style identifiers.

    Returns:
        The complete prompt string ready to send alongside the input image.
    """
    return get_style(style)["prompt"]
