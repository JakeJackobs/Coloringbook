"""
Command-line interface for the Coloring Book Engine.

Usage examples:
    # Convert all images using the default bold_outline style
    coloringbook --input ./photos --output ./coloring_pages

    # Use a specific style with thicker lines
    coloringbook --input ./photos --output ./coloring_pages --style detailed_line_art --thickness 3

    # Use a YAML config file
    coloringbook --config config.yaml

    # List available styles
    coloringbook --list-styles
"""

import argparse
import logging
import sys

from coloringbook.styles import SUPPORTED_STYLES
from coloringbook.engine import process_folder
from coloringbook.config import Config, load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="coloringbook",
        description="Convert photographs into coloring book style images.",
    )

    parser.add_argument(
        "--input", "-i",
        help="Path to the folder containing source photographs.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to the folder where coloring pages will be saved.",
    )
    parser.add_argument(
        "--style", "-s",
        choices=SUPPORTED_STYLES,
        default=None,
        help="Coloring book style (default: bold_outline).",
    )
    parser.add_argument(
        "--thickness", "-t",
        type=int,
        default=None,
        help="Line thickness 1-5 (default: 2).",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Output image width in pixels (optional).",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Output image height in pixels (optional).",
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to a YAML configuration file.",
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="List available coloring book styles and exit.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging.",
    )

    return parser


STYLE_DESCRIPTIONS = {
    "bold_outline": "Thick, simplified contours — ideal for young children.",
    "detailed_line_art": "Fine edges with rich detail — perfect for adult coloring.",
    "smooth_contour": "Clean, smooth outlines with a cartoon-like feel.",
    "sketch": "Pencil sketch effect with light shading.",
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # --list-styles
    if args.list_styles:
        print("Available coloring book styles:\n")
        for name in SUPPORTED_STYLES:
            desc = STYLE_DESCRIPTIONS.get(name, "")
            print(f"  {name:25s} {desc}")
        return 0

    # Logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # Build config — prefer CLI flags, fall back to config file
    if args.config:
        cfg = load_config(args.config)
    else:
        cfg = Config()

    # CLI overrides
    if args.input:
        cfg.input_folder = args.input
    if args.output:
        cfg.output_folder = args.output
    if args.style:
        cfg.style = args.style
    if args.thickness is not None:
        cfg.line_thickness = args.thickness
    if args.width is not None:
        cfg.output_width = args.width
    if args.height is not None:
        cfg.output_height = args.height

    # Re-derive output_size after overrides
    if cfg.output_width and cfg.output_height:
        cfg.output_size = (cfg.output_width, cfg.output_height)

    # Validate required fields
    if not cfg.input_folder:
        parser.error("--input is required (or set input_folder in config).")
    if not cfg.output_folder:
        parser.error("--output is required (or set output_folder in config).")

    results = process_folder(
        input_folder=cfg.input_folder,
        output_folder=cfg.output_folder,
        style=cfg.style,
        line_thickness=cfg.line_thickness,
        output_size=cfg.output_size,
    )

    if not results:
        logging.warning("No images were converted.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
