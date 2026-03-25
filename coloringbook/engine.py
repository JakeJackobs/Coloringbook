"""
Core engine — AI-powered batch conversion of photos to coloring book pages.

Pipeline (v3 — Images Edit API with direct photo input)
--------------------------------------------------------
1. **Open** — Read the source photograph.
2. **Transform** — Send the photo *directly* to the OpenAI Images Edit API
   (``gpt-image-1``) together with a style-specific coloring-book prompt.
   Because the model receives the actual photograph, it preserves the likeness
   of all people, animals, and distinctive features.
3. **Save** — Decode the returned base64 image and write it to disk as PNG.

This single-step approach keeps the *actual visual content* of the photograph
available to the model, so generated coloring pages faithfully depict the same
people, pets, poses, and scene composition as the original.
"""

from __future__ import annotations

import base64
import logging
import os
from pathlib import Path
from typing import Optional

from openai import OpenAI

from coloringbook.styles import (
    SUPPORTED_STYLES,
    get_prompt,
)

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

# GPT Image (gpt-image-1) supported output sizes
SUPPORTED_SIZES = {"1024x1024", "1536x1024", "1024x1536", "auto"}
DEFAULT_SIZE = "1024x1536"  # portrait — natural for coloring book pages


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def transform_image(
    client: OpenAI,
    image_path: str,
    style: str,
    size: str = DEFAULT_SIZE,
    quality: str = "high",
) -> bytes:
    """Transform a photograph into a coloring book page via the Images Edit API.

    The source photograph is sent directly to ``gpt-image-1`` alongside a
    style-specific prompt.  Because the model receives the actual photo, it
    preserves the likeness of subjects (faces, pets, clothing, etc.).

    Args:
        client: An initialised OpenAI client.
        image_path: Path to the source photograph.
        style: One of the supported coloring book style names.
        size: Output image dimensions (e.g. ``"1024x1536"``).
        quality: Image quality — ``"low"``, ``"medium"``, or ``"high"``.

    Returns:
        Raw PNG image bytes.

    Raises:
        ValueError: If *size* is not supported.
    """
    if size not in SUPPORTED_SIZES:
        raise ValueError(
            f"Unsupported size '{size}'. "
            f"Choose from: {', '.join(sorted(SUPPORTED_SIZES))}"
        )

    prompt = get_prompt(style)

    logger.info(
        "Transforming image (style=%s, size=%s): %s", style, size, image_path,
    )
    logger.debug("Transformation prompt:\n%s", prompt)

    with open(image_path, "rb") as img_file:
        response = client.images.edit(
            model="gpt-image-1",
            image=img_file,
            prompt=prompt,
            n=1,
            size=size,
            quality=quality,
        )

    image_b64 = response.data[0].b64_json
    return base64.b64decode(image_b64)


def process_image(
    input_path: str,
    output_path: str,
    api_key: str,
    style: str = "classic",
    size: str = DEFAULT_SIZE,
) -> str:
    """Convert a single photograph into a coloring book page.

    Args:
        input_path: Path to the source photograph.
        output_path: Path where the coloring page PNG will be saved.
        api_key: OpenAI API key.
        style: Coloring book style name.
        size: Output image size.

    Returns:
        The *output_path* on success.

    Raises:
        FileNotFoundError: If *input_path* does not exist.
        ValueError: If *style* or *size* is invalid.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    client = OpenAI(api_key=api_key)
    image_data = transform_image(client, input_path, style, size)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_data)

    logger.info("Saved coloring page: %s", output_path)
    return output_path


def process_folder(
    input_folder: str,
    output_folder: str,
    api_key: str,
    styles: Optional[list[str]] = None,
    size: str = DEFAULT_SIZE,
) -> list[str]:
    """Batch-convert all supported images in a folder.

    For each image a coloring page is generated for every requested style.

    Args:
        input_folder: Directory containing source photographs.
        output_folder: Directory where coloring pages will be saved.
        api_key: OpenAI API key.
        styles: Style(s) to generate per image.  Defaults to ``["classic"]``.
        size: Output image size.

    Returns:
        List of output file paths that were successfully created.

    Raises:
        FileNotFoundError: If *input_folder* does not exist.
    """
    if styles is None:
        styles = ["classic"]

    input_dir = Path(input_folder)
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_files = sorted(
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not image_files:
        logger.warning("No supported images found in %s", input_folder)
        return []

    logger.info(
        "Processing %d image(s) × %d style(s) …",
        len(image_files),
        len(styles),
    )

    client = OpenAI(api_key=api_key)
    results: list[str] = []

    for img_path in image_files:
        for style in styles:
            out_name = f"{img_path.stem}_{style}.png"
            out_path = str(output_dir / out_name)
            try:
                image_data = transform_image(
                    client, str(img_path), style, size,
                )
                with open(out_path, "wb") as f:
                    f.write(image_data)
                logger.info("Saved: %s", out_path)
                results.append(out_path)
            except Exception:
                logger.exception(
                    "Failed to generate style '%s' for %s",
                    style,
                    img_path.name,
                )

    logger.info("Done — %d coloring page(s) created.", len(results))
    return results
