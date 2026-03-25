"""Tests for configuration loading."""

import os

import pytest

from coloringbook.config import Config, load_config
from coloringbook.styles import SUPPORTED_STYLES


class TestConfig:
    def test_default_values(self):
        cfg = Config()
        assert cfg.style == "classic"
        assert cfg.styles == ["classic"]
        assert cfg.size == "1024x1536"
        assert cfg.openai_api_key == ""

    def test_invalid_style_raises(self):
        with pytest.raises(ValueError, match="Unknown style"):
            Config(styles=["invalid_style"])

    def test_all_expands_to_all_styles(self):
        cfg = Config(styles=["all"])
        assert cfg.styles == list(SUPPORTED_STYLES)

    def test_style_syncs_to_styles(self):
        cfg = Config(style="detailed")
        assert cfg.styles == ["detailed"]

    def test_explicit_styles_list(self):
        cfg = Config(styles=["classic", "whimsical"])
        assert cfg.styles == ["classic", "whimsical"]


class TestLoadConfig:
    def test_load_valid_yaml(self, tmp_dir):
        path = os.path.join(tmp_dir, "config.yaml")
        with open(path, "w") as f:
            f.write(
                "input_folder: /tmp/photos\n"
                "output_folder: /tmp/out\n"
                "style: detailed\n"
                "openai_api_key: sk-test\n"
            )

        cfg = load_config(path)
        assert cfg.input_folder == "/tmp/photos"
        assert cfg.output_folder == "/tmp/out"
        assert cfg.styles == ["detailed"]
        assert cfg.openai_api_key == "sk-test"

    def test_load_styles_list(self, tmp_dir):
        path = os.path.join(tmp_dir, "config.yaml")
        with open(path, "w") as f:
            f.write(
                "styles:\n"
                "  - classic\n"
                "  - stained_glass\n"
            )

        cfg = load_config(path)
        assert cfg.styles == ["classic", "stained_glass"]

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_config("/no/such/config.yaml")

    def test_empty_yaml_uses_defaults(self, tmp_dir):
        path = os.path.join(tmp_dir, "empty.yaml")
        with open(path, "w") as f:
            f.write("")

        cfg = load_config(path)
        assert cfg.style == "classic"
        assert cfg.styles == ["classic"]

    def test_api_key_falls_back_to_env(self, tmp_dir, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
        path = os.path.join(tmp_dir, "config.yaml")
        with open(path, "w") as f:
            f.write("input_folder: /tmp/photos\n")

        cfg = load_config(path)
        assert cfg.openai_api_key == "sk-from-env"
