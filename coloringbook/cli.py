"""
Command-line interface for the Coloring Book Engine.

Usage examples::

    # Convert all images using the default classic style
    coloringbook --input ./Photos --output ./coloring_pages

    # Use a specific style
    coloringbook --input ./Photos --output ./coloring_pages --style detailed

    # Generate all four styles at once
    coloringbook --input ./Photos --output ./coloring_pages --style all

    # Use a YAML config file
    coloringbook --config config.yaml

    # List available styles
    coloringbook --list-styles
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

from coloringbook.styles import SUPPORTED_STYLES, STYLE_INFO
from coloringbook.engine import process_folder, SUPPORTED_SIZES, DEFAULT_SIZE
from coloringbook.config import Config, load_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="coloringbook",
        description=(
            "Convert photographs into coloring book illustrations using the "
            "OpenAI Responses API with high-fidelity image transformation."
        ),
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
        choices=SUPPORTED_STYLES + ["all"],
        default=None,
        help="Coloring book style, or 'all' for every style (default: classic).",
    )
    parser.add_argument(
        "--size",
        choices=sorted(SUPPORTED_SIZES),
        default=None,
        help=f"Output image dimensions (default: {DEFAULT_SIZE}).",
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var, or put in config).",
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
        help="Enable verbose / debug logging.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # --list-styles ---------------------------------------------------------
    if args.list_styles:
        print("Available coloring book styles:\n")
        for name in SUPPORTED_STYLES:
            info = STYLE_INFO[name]
            print(f"  {name:20s} {info['description']}")
        print(f"\n  {'all':20s} Generate one page in every style above.")
        return 0

    # Logging ---------------------------------------------------------------
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # Build config ----------------------------------------------------------
    if args.config:
        cfg = load_config(args.config)
    else:
        cfg = Config()

    # CLI overrides ---------------------------------------------------------
    if args.input:
        cfg.input_folder = args.input
    if args.output:
        cfg.output_folder = args.output
    if args.style:
        if args.style == "all":
            cfg.styles = list(SUPPORTED_STYLES)
        else:
            cfg.styles = [args.style]
    if args.size:
        cfg.size = args.size
    if args.api_key:
        cfg.openai_api_key = args.api_key

    # Fall back to env var
    if not cfg.openai_api_key:
        cfg.openai_api_key = os.environ.get("OPENAI_API_KEY", "")

    # Validate required fields ----------------------------------------------
    if not cfg.input_folder:
        parser.error("--input is required (or set input_folder in config).")
    if not cfg.output_folder:
        parser.error("--output is required (or set output_folder in config).")
    if not cfg.openai_api_key:
        parser.error(
            "An OpenAI API key is required. Provide via --api-key, "
            "the OPENAI_API_KEY environment variable, or a config file."
        )

    # Run -------------------------------------------------------------------
    results = process_folder(
        input_folder=cfg.input_folder,
        output_folder=cfg.output_folder,
        api_key=cfg.openai_api_key,
        styles=cfg.styles,
        size=cfg.size,
    )

    if not results:
        logging.warning("No coloring pages were generated.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
