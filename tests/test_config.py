"""Tests for configuration loading."""

import os

import pytest

from coloringbook.config import Config, load_config


class TestConfig:
    def test_default_values(self):
        cfg = Config()
        assert cfg.style == "bold_outline"
        assert cfg.line_thickness == 2
        assert cfg.output_size is None

    def test_invalid_style_raises(self):
        with pytest.raises(ValueError, match="Unknown style"):
            Config(style="invalid")

    def test_output_size_derived(self):
        cfg = Config(output_width=800, output_height=600)
        assert cfg.output_size == (800, 600)

    def test_output_size_none_when_partial(self):
        cfg = Config(output_width=800)
        assert cfg.output_size is None


class TestLoadConfig:
    def test_load_valid_yaml(self, tmp_dir):
        path = os.path.join(tmp_dir, "config.yaml")
        with open(path, "w") as f:
            f.write("input_folder: /tmp/photos\noutput_folder: /tmp/out\nstyle: sketch\n")

        cfg = load_config(path)
        assert cfg.input_folder == "/tmp/photos"
        assert cfg.output_folder == "/tmp/out"
        assert cfg.style == "sketch"

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_config("/no/such/config.yaml")

    def test_empty_yaml_uses_defaults(self, tmp_dir):
        path = os.path.join(tmp_dir, "empty.yaml")
        with open(path, "w") as f:
            f.write("")

        cfg = load_config(path)
        assert cfg.style == "bold_outline"
