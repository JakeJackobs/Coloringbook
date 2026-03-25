"""Tests for the CLI layer (argparse-based commands)."""

import os
from unittest.mock import MagicMock, patch

import pytest

from coloringbook.cli import main
from coloringbook.styles import SUPPORTED_STYLES

from tests.conftest import FAKE_IMAGE_B64


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_client():
    """Build a mock OpenAI client wired for the Images Edit API."""
    client = MagicMock()
    data_item = MagicMock()
    data_item.b64_json = FAKE_IMAGE_B64
    resp = MagicMock()
    resp.data = [data_item]
    client.images.edit.return_value = resp
    return client


def _write_config(path, api_key="test-key", **overrides):
    """Write a minimal YAML config file."""
    import yaml
    cfg = {"openai_api_key": api_key}
    cfg.update(overrides)
    with open(path, "w") as f:
        yaml.safe_dump(cfg, f)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCLI:
    def test_list_styles(self, capsys):
        ret = main(["--list-styles"])
        assert ret == 0
        captured = capsys.readouterr()
        for s in SUPPORTED_STYLES:
            assert s in captured.out

    def test_missing_input_exits_nonzero(self, tmp_dir):
        """Running without --input should cause argparse to error."""
        cfg_path = os.path.join(tmp_dir, "config.yaml")
        _write_config(cfg_path)
        with pytest.raises(SystemExit) as exc_info:
            main(["--config", cfg_path])
        assert exc_info.value.code != 0

    def test_missing_api_key_exits_nonzero(self, tmp_dir, input_folder_with_images, monkeypatch):
        """Config without api_key should fail."""
        import yaml
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        cfg_path = os.path.join(tmp_dir, "config.yaml")
        with open(cfg_path, "w") as f:
            yaml.safe_dump({"input_folder": input_folder_with_images}, f)
        out_dir = os.path.join(tmp_dir, "out_nokey")
        with pytest.raises(SystemExit) as exc_info:
            main([
                "--config", cfg_path,
                "--input", input_folder_with_images,
                "--output", out_dir,
            ])
        assert exc_info.value.code != 0

    @patch("coloringbook.engine.OpenAI")
    def test_end_to_end(self, MockOpenAI, tmp_dir, input_folder_with_images):
        MockOpenAI.return_value = _make_mock_client()
        cfg_path = os.path.join(tmp_dir, "config.yaml")
        out_dir = os.path.join(tmp_dir, "output")
        _write_config(cfg_path)

        ret = main([
            "--config", cfg_path,
            "--input", input_folder_with_images,
            "--output", out_dir,
            "--style", "classic",
        ])
        assert ret == 0
        files = [f for f in os.listdir(out_dir) if f.endswith(".png")]
        # 3 images × 1 style = 3 outputs
        assert len(files) == 3

    @patch("coloringbook.engine.OpenAI")
    def test_all_styles(self, MockOpenAI, tmp_dir, input_folder_with_images):
        MockOpenAI.return_value = _make_mock_client()
        cfg_path = os.path.join(tmp_dir, "config.yaml")
        out_dir = os.path.join(tmp_dir, "output")
        _write_config(cfg_path)

        ret = main([
            "--config", cfg_path,
            "--input", input_folder_with_images,
            "--output", out_dir,
            "--style", "all",
        ])
        assert ret == 0
        files = [f for f in os.listdir(out_dir) if f.endswith(".png")]
        # 3 images × 4 styles = 12 outputs
        assert len(files) == 12

    @patch("coloringbook.engine.OpenAI")
    def test_empty_input_returns_one(self, MockOpenAI, tmp_dir):
        """An empty input folder should return exit code 1."""
        MockOpenAI.return_value = _make_mock_client()
        cfg_path = os.path.join(tmp_dir, "config.yaml")
        empty_dir = os.path.join(tmp_dir, "empty")
        os.makedirs(empty_dir)
        out_dir = os.path.join(tmp_dir, "out")
        _write_config(cfg_path)

        ret = main([
            "--config", cfg_path,
            "--input", empty_dir,
            "--output", out_dir,
            "--style", "classic",
        ])
        assert ret == 1
