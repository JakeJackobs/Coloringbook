# Coloring Book Engine

Convert photographs into coloring book style line-art images, ready for
print-on-demand coloring books.

## Features

* **Four built-in styles** — each tuned for a different audience:
  | Style | Description |
  |---|---|
  | `bold_outline` | Thick, simplified contours — ideal for young children |
  | `detailed_line_art` | Fine edges preserving detail — perfect for adult coloring |
  | `smooth_contour` | Clean, smooth outlines with a cartoon-like feel |
  | `sketch` | Pencil sketch effect with light shading |

* **Batch processing** — point at a folder of photos and get a folder of
  coloring pages.
* **Configurable** — line thickness, output size, YAML config files.
* **No API keys required** — all processing is local via OpenCV.

## Quick Start

```bash
# Install
pip install -e .

# Convert a folder of photos (default style: bold_outline)
coloringbook --input ./photos --output ./coloring_pages

# Choose a style and line thickness
coloringbook --input ./photos --output ./coloring_pages --style sketch --thickness 3

# List available styles
coloringbook --list-styles

# Use a config file instead of CLI flags
coloringbook --config config.yaml
```

## Configuration

Copy `config.example.yaml` to `config.yaml` and edit the values:

```yaml
input_folder: ./photos
output_folder: ./coloring_pages
style: bold_outline
line_thickness: 2
# output_width: 2550   # 8.5" at 300 DPI
# output_height: 3300  # 11" at 300 DPI
```

## Supported Image Formats

JPG, JPEG, PNG, BMP, TIFF, WEBP

## Development

```bash
pip install -e ".[dev]"
pytest
```

## How It Works

Each style uses a different OpenCV image-processing pipeline:

1. **Bold Outline** — bilateral filtering to simplify the image while
   preserving edges, followed by adaptive thresholding and morphological
   operations to produce thick, clean contours.

2. **Detailed Line Art** — multi-scale Canny edge detection combined with
   adaptive Gaussian thresholding to capture fine detail.

3. **Smooth Contour** — median blur + Laplacian edge detection for smooth,
   cartoon-like outlines, with morphological closing to fill small gaps.

4. **Sketch** — a pencil-sketch algorithm that divides the grayscale image
   by an inverted Gaussian blur of itself, producing natural shading.
