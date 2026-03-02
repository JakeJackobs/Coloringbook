"""Tests for the core engine (single image + batch processing)."""

import os

import cv2
import pytest

from coloringbook.engine import process_image, process_folder, SUPPORTED_EXTENSIONS


class TestProcessImage:
    def test_converts_single_image(self, tmp_dir, sample_image):
        in_path = os.path.join(tmp_dir, "input.png")
        out_path = os.path.join(tmp_dir, "output.png")
        cv2.imwrite(in_path, sample_image)

        result = process_image(in_path, out_path)
        assert result == out_path
        assert os.path.isfile(out_path)

    def test_missing_input_raises(self, tmp_dir):
        with pytest.raises(FileNotFoundError):
            process_image("/no/such/file.png", os.path.join(tmp_dir, "out.png"))

    def test_output_directory_created(self, tmp_dir, sample_image):
        in_path = os.path.join(tmp_dir, "input.png")
        out_path = os.path.join(tmp_dir, "sub", "dir", "output.png")
        cv2.imwrite(in_path, sample_image)

        process_image(in_path, out_path)
        assert os.path.isfile(out_path)

    def test_resize_output(self, tmp_dir, sample_image):
        in_path = os.path.join(tmp_dir, "input.png")
        out_path = os.path.join(tmp_dir, "output.png")
        cv2.imwrite(in_path, sample_image)

        process_image(in_path, out_path, output_size=(200, 200))
        result = cv2.imread(out_path, cv2.IMREAD_GRAYSCALE)
        assert result.shape == (200, 200)


class TestProcessFolder:
    def test_batch_conversion(self, input_folder_with_images, tmp_dir):
        out_dir = os.path.join(tmp_dir, "output")
        results = process_folder(input_folder_with_images, out_dir)
        assert len(results) == 3
        for path in results:
            assert os.path.isfile(path)
            assert path.endswith(".png")

    def test_missing_folder_raises(self, tmp_dir):
        with pytest.raises(FileNotFoundError):
            process_folder("/no/such/folder", os.path.join(tmp_dir, "out"))

    def test_empty_folder_returns_empty(self, tmp_dir):
        empty_in = os.path.join(tmp_dir, "empty_in")
        os.makedirs(empty_in)
        results = process_folder(empty_in, os.path.join(tmp_dir, "out"))
        assert results == []

    def test_non_image_files_are_skipped(self, tmp_dir):
        in_dir = os.path.join(tmp_dir, "mixed")
        os.makedirs(in_dir)
        # Write a text file (should be ignored)
        with open(os.path.join(in_dir, "notes.txt"), "w") as f:
            f.write("hello")
        results = process_folder(in_dir, os.path.join(tmp_dir, "out"))
        assert results == []
