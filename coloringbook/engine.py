"""
Core engine that orchestrates batch conversion of photos to coloring book pages.
"""

import os
import logging
from pathlib import Path
from typing import Optional

import cv2

from coloringbook.styles import convert, SUPPORTED_STYLES

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def process_image(
    input_path: str,
    output_path: str,
    style: str = "bold_outline",
    line_thickness: int = 2,
    output_size: Optional[tuple[int, int]] = None,
) -> str:
    """Convert a single image to a coloring book page.

    Args:
        input_path: Path to the source photograph.
        output_path: Path where the coloring page will be saved.
        style: Coloring book style name.
        line_thickness: Line weight (1-5).
        output_size: Optional (width, height) to resize the output.

    Returns:
        The output file path on success.

    Raises:
        FileNotFoundError: If input_path does not exist.
        ValueError: If the image cannot be read or style is invalid.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input image not found: {input_path}")

    image = cv2.imread(input_path)
    if image is None:
        raise ValueError(f"Could not read image (unsupported or corrupt): {input_path}")

    result = convert(image, style, line_thickness)

    if output_size is not None:
        result = cv2.resize(result, output_size, interpolation=cv2.INTER_AREA)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    cv2.imwrite(output_path, result)
    logger.info("Saved coloring page: %s", output_path)
    return output_path


def process_folder(
    input_folder: str,
    output_folder: str,
    style: str = "bold_outline",
    line_thickness: int = 2,
    output_size: Optional[tuple[int, int]] = None,
) -> list[str]:
    """Batch-convert all supported images in a folder.

    Args:
        input_folder: Directory containing source photographs.
        output_folder: Directory where coloring pages will be saved.
        style: Coloring book style name.
        line_thickness: Line weight (1-5).
        output_size: Optional (width, height) to resize outputs.

    Returns:
        List of output file paths that were successfully created.

    Raises:
        FileNotFoundError: If input_folder does not exist.
    """
    input_dir = Path(input_folder)
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[str] = []

    image_files = sorted(
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not image_files:
        logger.warning("No supported images found in %s", input_folder)
        return results

    logger.info(
        "Processing %d image(s) with style '%s' ...", len(image_files), style
    )

    for img_path in image_files:
        out_name = img_path.stem + ".png"
        out_path = str(output_dir / out_name)
        try:
            process_image(str(img_path), out_path, style, line_thickness, output_size)
            results.append(out_path)
        except Exception:
            logger.exception("Failed to process %s", img_path.name)

    logger.info("Done — %d/%d images converted.", len(results), len(image_files))
    return results
