"""
Configuration file support.

Users can provide a YAML config file instead of (or in addition to) CLI flags.
The ``openai_api_key`` can also be read from the ``OPENAI_API_KEY`` environment
variable.
"""

from __future__ import annotations

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
    style: str = "classic"
    styles: list[str] = field(default_factory=lambda: ["classic"])
    size: str = "1024x1536"
    openai_api_key: str = ""

    def __post_init__(self) -> None:
        # Validate every style in the list
        for s in self.styles:
            if s not in ("all", *SUPPORTED_STYLES):
                raise ValueError(
                    f"Unknown style '{s}'. "
                    f"Supported: {', '.join(SUPPORTED_STYLES)}, all"
                )

        # If the caller set ``style`` but left ``styles`` at its default,
        # keep them in sync.
        if self.style != "classic" and self.styles == ["classic"]:
            self.styles = [self.style]

        # Expand the ``all`` shorthand
        if "all" in self.styles:
            self.styles = list(SUPPORTED_STYLES)


def load_config(path: str) -> Config:
    """Load configuration from a YAML file.

    Args:
        path: Path to the YAML config file.

    Returns:
        A populated :class:`Config` instance.

    Raises:
        FileNotFoundError: If the config file does not exist.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    # ``styles`` may be a list or a single string in the YAML
    raw_styles = data.get("styles", data.get("style", "classic"))
    if isinstance(raw_styles, str):
        styles_list = [raw_styles]
    else:
        styles_list = list(raw_styles)

    return Config(
        input_folder=data.get("input_folder", ""),
        output_folder=data.get("output_folder", ""),
        style=data.get("style", "classic"),
        styles=styles_list,
        size=data.get("size", "1024x1536"),
        openai_api_key=data.get(
            "openai_api_key",
            os.environ.get("OPENAI_API_KEY", ""),
        ),
    )
