"""Tests for the CLI interface."""

import os

import cv2
import pytest

from coloringbook.cli import main


class TestCLI:
    def test_list_styles(self, capsys):
        rc = main(["--list-styles"])
        assert rc == 0
        captured = capsys.readouterr()
        assert "bold_outline" in captured.out
        assert "sketch" in captured.out

    def test_missing_input_exits_nonzero(self):
        with pytest.raises(SystemExit):
            main(["--output", "/tmp/out"])

    def test_end_to_end(self, input_folder_with_images, tmp_dir):
        out_dir = os.path.join(tmp_dir, "cli_output")
        rc = main([
            "--input", input_folder_with_images,
            "--output", out_dir,
            "--style", "sketch",
            "--thickness", "3",
            "--verbose",
        ])
        assert rc == 0
        assert len(os.listdir(out_dir)) == 3

    def test_empty_input_returns_one(self, tmp_dir):
        empty_in = os.path.join(tmp_dir, "empty")
        os.makedirs(empty_in)
        rc = main([
            "--input", empty_in,
            "--output", os.path.join(tmp_dir, "out"),
        ])
        assert rc == 1
