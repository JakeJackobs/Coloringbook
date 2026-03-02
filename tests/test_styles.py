"""Tests for coloring book style conversions."""

import numpy as np
import pytest

from coloringbook.styles import convert, SUPPORTED_STYLES


class TestConvert:
    """Tests for the convert() dispatcher."""

    def test_unknown_style_raises(self, sample_image):
        with pytest.raises(ValueError, match="Unknown style"):
            convert(sample_image, "nonexistent_style")

    @pytest.mark.parametrize("style", SUPPORTED_STYLES)
    def test_each_style_returns_valid_image(self, sample_image, style):
        result = convert(sample_image, style)
        assert isinstance(result, np.ndarray)
        # Should be single-channel (grayscale)
        assert result.ndim == 2
        # Same height/width as input
        assert result.shape[0] == sample_image.shape[0]
        assert result.shape[1] == sample_image.shape[1]

    @pytest.mark.parametrize("style", SUPPORTED_STYLES)
    def test_output_is_uint8(self, sample_image, style):
        result = convert(sample_image, style)
        assert result.dtype == np.uint8

    @pytest.mark.parametrize("style", SUPPORTED_STYLES)
    def test_output_has_both_black_and_white_regions(self, sample_image, style):
        result = convert(sample_image, style)
        # A coloring page should have both dark (line) and light (background) pixels
        assert result.min() < 128, "Expected dark pixels (lines)"
        assert result.max() > 127, "Expected light pixels (background)"

    def test_line_thickness_is_clamped(self, sample_image):
        # Should not raise with out-of-range thickness
        r1 = convert(sample_image, "bold_outline", line_thickness=0)
        r2 = convert(sample_image, "bold_outline", line_thickness=99)
        assert r1 is not None
        assert r2 is not None
