"""Shared test fixtures."""

import os
import struct
import tempfile
import zlib

import pytest


def _minimal_png_bytes() -> bytes:
    """Return the bytes of a valid 1×1 red-pixel PNG image."""
    sig = b"\x89PNG\r\n\x1a\n"

    # IHDR: 1×1, 8-bit RGB
    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF
    ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + struct.pack(">I", ihdr_crc)

    # IDAT: single row, filter=None, R=255 G=0 B=0
    raw = b"\x00\xff\x00\x00"
    compressed = zlib.compress(raw)
    idat_crc = zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF
    idat = (
        struct.pack(">I", len(compressed))
        + b"IDAT"
        + compressed
        + struct.pack(">I", idat_crc)
    )

    # IEND
    iend_crc = zlib.crc32(b"IEND") & 0xFFFFFFFF
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", iend_crc)

    return sig + ihdr + idat + iend


@pytest.fixture
def tmp_dir():
    """Provide a temporary directory that is cleaned up after the test."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_image_path(tmp_dir) -> str:
    """Write a tiny but valid PNG file and return its path."""
    path = os.path.join(tmp_dir, "test_photo.png")
    with open(path, "wb") as f:
        f.write(_minimal_png_bytes())
    return path


@pytest.fixture
def input_folder_with_images(tmp_dir, sample_image_path):
    """Create a temp input folder containing several test images."""
    import shutil

    in_dir = os.path.join(tmp_dir, "input")
    os.makedirs(in_dir)
    for name in ("photo1.png", "photo2.jpg", "photo3.bmp"):
        shutil.copy(sample_image_path, os.path.join(in_dir, name))
    return in_dir


# ---------------------------------------------------------------------------
# Fake OpenAI Responses API helpers (used across multiple test modules)
# ---------------------------------------------------------------------------

# A tiny valid PNG (1×1 pixel) encoded as base64
FAKE_IMAGE_B64 = __import__("base64").b64encode(_minimal_png_bytes()).decode()
