"""
Utility script to verify that light pollution map PNGs use only the
colors defined in ``LIGHT_POLLUTION_SCALE``.

Run from the repository root (with the virtualenv activated):

    python -m map_app.utils.validate_light_pollution_colors --map NorthAmerica2024.png

If ``--map`` is omitted, the script checks the default North America map
at ``src/map_app/models/assets/light_pollution_maps/NorthAmerica2024.png``.
"""
from __future__ import annotations

from pathlib import Path
import argparse
from typing import Dict, Tuple, Iterable

import numpy as np
from PIL import Image
from map_app.models.optimal_locations import LIGHT_POLLUTION_SCALE

Image.MAX_IMAGE_PIXELS = 150000000  # Prevent DecompressionBombError for large images

DEFAULT_MAP_NAME = "NorthAmerica2024.png"
MAP_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "models"
    / "assets"
    / "light_pollution_maps"
)

def _collect_colors(image_path: Path) -> Dict[Tuple[int, int, int], int]:
    """Return a mapping of RGB tuples to pixel counts for the PNG."""
    if not image_path.exists():
        raise FileNotFoundError(f"Map file not found: {image_path}")

    image = Image.open(image_path).convert("RGB")
    data = np.array(image).reshape(-1, 3)
    unique_colors, counts = np.unique(data, axis=0, return_counts=True)
    return {tuple(color.tolist()): int(counts[idx]) for idx, color in enumerate(unique_colors)}


def _format_color(color: Tuple[int, int, int]) -> str:
    return f"({color[0]:3d}, {color[1]:3d}, {color[2]:3d})"


def validate_map_colors(image_path: Path) -> None:
    """Print a report comparing map colors against the allowed scale."""
    present_colors = _collect_colors(image_path)
    allowed = set(LIGHT_POLLUTION_SCALE.keys())
    present = set(present_colors.keys())

    unexpected = present - allowed
    missing = allowed - present

    print(f"Analyzing: {image_path}")
    print(f"Total unique colors found: {len(present_colors)}")

    if unexpected:
        print("\nUnexpected colors (count):")
        for color in sorted(unexpected):
            print(f"  {_format_color(color)} -> {present_colors[color]} pixels")
    else:
        print("\nNo unexpected colors found.")

    if missing:
        print("\nAllowed colors missing from map:")
        for color in sorted(missing):
            print(f"  {_format_color(color)} (expected level {LIGHT_POLLUTION_SCALE[color]})")
    else:
        print("\nAll allowed colors are present in the map.")

    print("\nTop 10 most frequent colors:")
    top_colors = sorted(present_colors.items(), key=lambda item: item[1], reverse=True)[:10]
    for color, count in top_colors:
        level = LIGHT_POLLUTION_SCALE.get(color, "<not in scale>")
        print(f"  {_format_color(color)} -> {count} pixels (level {level})")


def main(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate light pollution map colors.")
    parser.add_argument(
        "--map",
        dest="map_name",
        default=DEFAULT_MAP_NAME,
        help=f"PNG filename in {MAP_ROOT} (default: {DEFAULT_MAP_NAME})",
    )
    parser.add_argument(
        "--path",
        dest="map_path",
        default=None,
        help="Optional full path to PNG; overrides --map when provided.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    image_path = Path(args.map_path) if args.map_path else MAP_ROOT / args.map_name
    validate_map_colors(image_path)


if __name__ == "__main__":
    main()
