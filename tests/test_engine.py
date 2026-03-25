"""Tests for the core engine (mocked OpenAI Images Edit API calls)."""

import os
from unittest.mock import MagicMock, patch, mock_open

import pytest

from coloringbook.engine import (
    transform_image,
    process_image,
    process_folder,
    SUPPORTED_EXTENSIONS,
    DEFAULT_SIZE,
)

from tests.conftest import FAKE_IMAGE_B64


# ---------------------------------------------------------------------------
# Helpers to build fake OpenAI Images Edit API objects
# ---------------------------------------------------------------------------

def _mock_images_edit_response(b64: str = FAKE_IMAGE_B64) -> MagicMock:
    """Create a mock response from client.images.edit()."""
    resp = MagicMock()
    data_item = MagicMock()
    data_item.b64_json = b64
    resp.data = [data_item]
    return resp


def _make_mock_client(image_b64: str = FAKE_IMAGE_B64) -> MagicMock:
    """Build a mock OpenAI client with an Images Edit API mock."""
    client = MagicMock()
    client.images.edit.return_value = _mock_images_edit_response(image_b64)
    return client


# ---------------------------------------------------------------------------
# transform_image
# ---------------------------------------------------------------------------

class TestTransformImage:
    def test_returns_bytes(self, sample_image_path):
        client = _make_mock_client()
        data = transform_image(client, sample_image_path, "classic")
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_invalid_size_raises(self, sample_image_path):
        client = _make_mock_client()
        with pytest.raises(ValueError, match="Unsupported size"):
            transform_image(client, sample_image_path, "classic", size="999x999")

    def test_calls_images_edit(self, sample_image_path):
        client = _make_mock_client()
        transform_image(client, sample_image_path, "detailed", size="1024x1024")
        client.images.edit.assert_called_once()

        call_kwargs = client.images.edit.call_args.kwargs
        assert call_kwargs["model"] == "gpt-image-1"
        assert call_kwargs["size"] == "1024x1024"
        assert call_kwargs["quality"] == "high"

    @pytest.mark.parametrize("style", ["classic", "detailed", "whimsical", "stained_glass"])
    def test_all_styles(self, sample_image_path, style):
        client = _make_mock_client()
        data = transform_image(client, sample_image_path, style)
        assert isinstance(data, bytes)
        assert len(data) > 0


# ---------------------------------------------------------------------------
# process_image
# ---------------------------------------------------------------------------

class TestProcessImage:
    @patch("coloringbook.engine.OpenAI")
    def test_converts_single_image(self, MockOpenAI, tmp_dir, sample_image_path):
        MockOpenAI.return_value = _make_mock_client()
        out_path = os.path.join(tmp_dir, "output.png")

        result = process_image(sample_image_path, out_path, api_key="fake-key")
        assert result == out_path
        assert os.path.isfile(out_path)

    def test_missing_input_raises(self, tmp_dir):
        with pytest.raises(FileNotFoundError):
            process_image("/no/such/file.png", os.path.join(tmp_dir, "out.png"), api_key="k")

    @patch("coloringbook.engine.OpenAI")
    def test_output_directory_created(self, MockOpenAI, tmp_dir, sample_image_path):
        MockOpenAI.return_value = _make_mock_client()
        out_path = os.path.join(tmp_dir, "sub", "dir", "output.png")

        process_image(sample_image_path, out_path, api_key="fake-key")
        assert os.path.isfile(out_path)


# ---------------------------------------------------------------------------
# process_folder
# ---------------------------------------------------------------------------

class TestProcessFolder:
    @patch("coloringbook.engine.OpenAI")
    def test_batch_conversion(self, MockOpenAI, input_folder_with_images, tmp_dir):
        MockOpenAI.return_value = _make_mock_client()
        out_dir = os.path.join(tmp_dir, "output")

        results = process_folder(
            input_folder_with_images, out_dir, api_key="fake-key",
        )
        # 3 images × 1 style = 3 outputs
        assert len(results) == 3
        for path in results:
            assert os.path.isfile(path)
            assert path.endswith(".png")

    @patch("coloringbook.engine.OpenAI")
    def test_multiple_styles(self, MockOpenAI, input_folder_with_images, tmp_dir):
        MockOpenAI.return_value = _make_mock_client()
        out_dir = os.path.join(tmp_dir, "output")

        results = process_folder(
            input_folder_with_images,
            out_dir,
            api_key="fake-key",
            styles=["classic", "whimsical"],
        )
        # 3 images × 2 styles = 6 outputs
        assert len(results) == 6

    def test_missing_folder_raises(self, tmp_dir):
        with pytest.raises(FileNotFoundError):
            process_folder("/no/such/folder", os.path.join(tmp_dir, "out"), api_key="k")

    @patch("coloringbook.engine.OpenAI")
    def test_empty_folder_returns_empty(self, MockOpenAI, tmp_dir):
        MockOpenAI.return_value = _make_mock_client()
        empty_in = os.path.join(tmp_dir, "empty_in")
        os.makedirs(empty_in)
        results = process_folder(empty_in, os.path.join(tmp_dir, "out"), api_key="k")
        assert results == []

    @patch("coloringbook.engine.OpenAI")
    def test_non_image_files_are_skipped(self, MockOpenAI, tmp_dir):
        MockOpenAI.return_value = _make_mock_client()
        in_dir = os.path.join(tmp_dir, "mixed")
        os.makedirs(in_dir)
        with open(os.path.join(in_dir, "notes.txt"), "w") as f:
            f.write("hello")
        results = process_folder(in_dir, os.path.join(tmp_dir, "out"), api_key="k")
        assert results == []
