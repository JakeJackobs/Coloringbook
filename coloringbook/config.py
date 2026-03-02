"""
Configuration file support.

Users can provide a YAML config file instead of (or in addition to) CLI flags.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

import yaml

from coloringbook.styles import SUPPORTED_STYLES


@dataclass
class Config:
    """Runtime configuration for the coloring book engine."""

    input_folder: str = ""
    output_folder: str = ""
    style: str = "bold_outline"
    line_thickness: int = 2
    output_width: Optional[int] = None
    output_height: Optional[int] = None
    openai_api_key: Optional[str] = None

    # Derived
    output_size: Optional[tuple[int, int]] = field(default=None, init=False)

    def __post_init__(self) -> None:
        if self.output_width and self.output_height:
            self.output_size = (self.output_width, self.output_height)
        if self.style not in SUPPORTED_STYLES:
            raise ValueError(
                f"Unknown style '{self.style}'. Supported styles: {', '.join(SUPPORTED_STYLES)}"
            )


def load_config(path: str) -> Config:
    """Load configuration from a YAML file.

    Args:
        path: Path to the YAML config file.

    Returns:
        A populated Config instance.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    return Config(
        input_folder=data.get("input_folder", ""),
        output_folder=data.get("output_folder", ""),
        style=data.get("style", "bold_outline"),
        line_thickness=data.get("line_thickness", 2),
        output_width=data.get("output_width"),
        output_height=data.get("output_height"),
        openai_api_key=data.get("openai_api_key"),
    )
