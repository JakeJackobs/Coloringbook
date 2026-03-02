"""Shared test fixtures."""

import os
import tempfile

import cv2
import numpy as np
import pytest


@pytest.fixture
def sample_image() -> np.ndarray:
    """Create a synthetic BGR test image (300x400 with shapes)."""
    img = np.ones((400, 300, 3), dtype=np.uint8) * 220  # light gray background

    # Draw a filled circle (pet-like blob)
    cv2.circle(img, (150, 180), 80, (60, 120, 200), -1)
    # Draw an outline rectangle (frame)
    cv2.rectangle(img, (40, 40), (260, 360), (30, 30, 30), 3)
    # Draw some lines for texture
    cv2.line(img, (50, 300), (250, 300), (0, 0, 0), 2)
    cv2.line(img, (50, 320), (250, 320), (0, 0, 0), 1)

    return img


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def input_folder_with_images(tmp_dir, sample_image):
    """Create a temp input folder containing a few test images."""
    in_dir = os.path.join(tmp_dir, "input")
    os.makedirs(in_dir)

    for name in ["photo1.png", "photo2.jpg", "photo3.bmp"]:
        cv2.imwrite(os.path.join(in_dir, name), sample_image)

    return in_dir
