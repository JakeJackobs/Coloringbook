"""Tests for coloring book style definitions."""

import pytest

from coloringbook.styles import (
    SUPPORTED_STYLES,
    STYLE_INFO,
    get_style,
    get_prompt,
)


class TestSupportedStyles:
    """Ensure the style catalogue is consistent."""

    def test_supported_styles_not_empty(self):
        assert len(SUPPORTED_STYLES) > 0

    def test_all_styles_have_info(self):
        for name in SUPPORTED_STYLES:
            assert name in STYLE_INFO

    def test_style_info_has_required_keys(self):
        for name, info in STYLE_INFO.items():
            assert "name" in info
            assert "description" in info
            assert "prompt" in info

    def test_prompt_contains_transform_instruction(self):
        for name, info in STYLE_INFO.items():
            assert "Transform this photograph" in info["prompt"], (
                f"Style '{name}' prompt is missing the transform instruction"
            )

    def test_prompt_contains_likeness_requirement(self):
        for name, info in STYLE_INFO.items():
            assert "likeness" in info["prompt"].lower(), (
                f"Style '{name}' prompt is missing likeness preservation requirement"
            )


class TestGetStyle:
    def test_valid_style(self):
        info = get_style("classic")
        assert info["name"] == "Classic"

    def test_unknown_style_raises(self):
        with pytest.raises(ValueError, match="Unknown style"):
            get_style("nonexistent")

    @pytest.mark.parametrize("style", SUPPORTED_STYLES)
    def test_each_supported_style(self, style):
        info = get_style(style)
        assert isinstance(info, dict)
        assert "prompt" in info


class TestGetPrompt:
    def test_returns_string(self):
        prompt = get_prompt("classic")
        assert isinstance(prompt, str)
        assert len(prompt) > 50

    def test_unknown_style_raises(self):
        with pytest.raises(ValueError, match="Unknown style"):
            get_prompt("bad_style")

    @pytest.mark.parametrize("style", SUPPORTED_STYLES)
    def test_prompt_includes_coloring_book_instructions(self, style):
        prompt = get_prompt(style)
        lower = prompt.lower()
        assert "black" in lower
        assert "white" in lower
        assert "no shading" in lower or "no gradients" in lower
