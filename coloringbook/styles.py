"""
Coloring book style definitions and image processing pipelines.

Supported styles:
    - bold_outline: Thick, simplified contours ideal for young children
    - detailed_line_art: Fine edge detection preserving detail for adult coloring
    - smooth_contour: Clean, smooth outlines with a cartoon-like feel
    - sketch: Pencil sketch effect with light shading
"""

import cv2
import numpy as np


SUPPORTED_STYLES = ["bold_outline", "detailed_line_art", "smooth_contour", "sketch"]


def convert(image: np.ndarray, style: str, line_thickness: int = 2) -> np.ndarray:
    """Convert a BGR image to a coloring book page using the specified style.

    Args:
        image: Input image as a BGR numpy array (as returned by cv2.imread).
        style: One of the supported style names.
        line_thickness: Controls line weight where applicable (1-5, default 2).

    Returns:
        Grayscale coloring-book image (white background, black lines).

    Raises:
        ValueError: If the style is not recognised.
    """
    if style not in SUPPORTED_STYLES:
        raise ValueError(
            f"Unknown style '{style}'. Supported styles: {', '.join(SUPPORTED_STYLES)}"
        )

    line_thickness = max(1, min(5, line_thickness))

    dispatch = {
        "bold_outline": _bold_outline,
        "detailed_line_art": _detailed_line_art,
        "smooth_contour": _smooth_contour,
        "sketch": _sketch,
    }
    return dispatch[style](image, line_thickness)


# ---------------------------------------------------------------------------
# Style implementations
# ---------------------------------------------------------------------------

def _bold_outline(image: np.ndarray, thickness: int) -> np.ndarray:
    """Thick, simplified contours — great for kids' coloring books."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Strong bilateral filter to simplify while keeping edges
    filtered = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    filtered = cv2.bilateralFilter(filtered, d=9, sigmaColor=75, sigmaSpace=75)

    # Adaptive threshold gives strong black/white separation
    edges = cv2.adaptiveThreshold(
        filtered, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=9, C=2
    )

    # Dilate to thicken lines, then re-thin slightly for clean look
    kernel = np.ones((thickness, thickness), np.uint8)
    edges = cv2.erode(edges, kernel, iterations=1)

    return edges


def _detailed_line_art(image: np.ndarray, thickness: int) -> np.ndarray:
    """Fine edge detection with detail preservation — ideal for adults."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Light blur to reduce noise but keep detail
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    # Multi-scale Canny for rich detail
    edges_fine = cv2.Canny(blurred, 30, 80)
    edges_coarse = cv2.Canny(blurred, 50, 150)
    combined = cv2.bitwise_or(edges_fine, edges_coarse)

    # Adaptive threshold layer for extra detail
    adaptive = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=11, C=2
    )

    # Merge: edges from Canny + adaptive threshold detail
    combined_inv = cv2.bitwise_not(combined)
    result = cv2.bitwise_and(adaptive, combined_inv)

    # Optionally thicken
    if thickness > 1:
        kernel = np.ones((thickness, thickness), np.uint8)
        result = cv2.erode(result, kernel, iterations=1)

    return result


def _smooth_contour(image: np.ndarray, thickness: int) -> np.ndarray:
    """Clean, smooth outlines with a cartoon-like feel."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Heavy blur for very smooth edges
    blurred = cv2.medianBlur(gray, 7)

    # Laplacian for smooth contour detection
    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
    laplacian = np.uint8(np.absolute(laplacian))

    # Threshold to binary
    _, binary = cv2.threshold(laplacian, 15, 255, cv2.THRESH_BINARY)

    # Invert so lines are black on white
    result = cv2.bitwise_not(binary)

    # Close small gaps
    kernel = np.ones((2, 2), np.uint8)
    result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)

    # Thicken lines
    if thickness > 1:
        erode_kernel = np.ones((thickness, thickness), np.uint8)
        result = cv2.erode(result, erode_kernel, iterations=1)

    return result


def _sketch(image: np.ndarray, thickness: int) -> np.ndarray:
    """Pencil sketch effect with light shading."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inv = cv2.bitwise_not(gray)

    # Gaussian blur on inverted image
    blur_size = 21 + (thickness * 10)
    if blur_size % 2 == 0:
        blur_size += 1
    blurred_inv = cv2.GaussianBlur(inv, (blur_size, blur_size), 0)

    # Divide gray by inverted-blurred to get pencil sketch
    sketch = cv2.divide(gray, cv2.bitwise_not(blurred_inv), scale=256)

    # Boost contrast so lines are stronger
    _, sketch = cv2.threshold(sketch, 240, 255, cv2.THRESH_TRUNC)
    sketch = cv2.normalize(sketch, None, 0, 255, cv2.NORM_MINMAX)

    return sketch
