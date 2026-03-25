# Coloring Book Engine

AI-powered conversion of photographs into **coloring book illustrations**,
ready for print-on-demand coloring books.

The engine uses **OpenAI GPT-4o** (vision) to understand the content of a
photograph and **DALL-E 3** to generate a clean, bold-outline coloring page —
no local image-processing heuristics, no grainy black-and-white conversions.

## Features

* **Four popular styles** — each tuned for a different audience:

  | Style | Description |
  |---|---|
  | `classic` | Bold, clean outlines with simplified shapes — ideal for kids |
  | `detailed` | Intricate line art with fine details — perfect for adults |
  | `whimsical` | Playful cartoon-like illustrations — cheerful and inviting |
  | `stained_glass` | Geometric stained-glass style with bold cell borders |

* **Batch processing** — point at a folder of photos and generate coloring
  pages in one or more styles.
* **Generate all styles at once** — use `--style all` to create one page per
  style for every photo.
* **Configurable** — YAML config files, CLI flags, or environment variables.

## Quick Start

```bash
# Install
pip install -e .

# Convert a folder of photos (default: classic style, portrait size)
coloringbook --input ./Photos --output ./coloring_pages --api-key sk-...

# Choose a style
coloringbook --input ./Photos --output ./coloring_pages --style detailed

# Generate all four styles for every photo
coloringbook --input ./Photos --output ./coloring_pages --style all

# List available styles
coloringbook --list-styles

# Use a config file (avoids passing --api-key every time)
coloringbook --config config.yaml
```

## Configuration

Copy `config.example.yaml` to `config.yaml` and edit the values:

```yaml
input_folder: ./Photos
output_folder: ./coloring_pages
style: classic            # or: detailed, whimsical, stained_glass, all
size: "1024x1792"         # portrait (coloring book page)
openai_api_key: sk-...
```

You can also pass the API key via the `OPENAI_API_KEY` environment variable.

## Output Sizes

DALL-E 3 supports three output dimensions:

| Size | Orientation |
|---|---|
| `1024x1792` | Portrait (default) — standard coloring book page |
| `1792x1024` | Landscape |
| `1024x1024` | Square |

## Supported Image Formats

JPG, JPEG, PNG, BMP, TIFF, WEBP

## How It Works

1. **Analyse** — The input photograph is sent to **GPT-4o** with a vision
   prompt that asks for a detailed scene description (subjects, poses,
   setting, objects, spatial relationships).

2. **Generate** — The description is combined with a style-specific prompt
   and sent to **DALL-E 3** which produces a clean coloring book
   illustration: black outlines on a pure white background, no shading,
   no gradients, all areas enclosed with clear closed lines.

3. **Save** — The generated PNG is written to the output folder.

When multiple styles are requested, the photo is described only once and
the description is reused for each style — saving API calls.

## Development

```bash
pip install -e ".[dev]"
pytest
```
