# src/png2svg/cli.py
"""Command-line interface for png2svg."""

import argparse
from pathlib import Path

from png2svg.core import png2svg

DEFAULT_HEX_WIDTH = 20.0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="png2svg",
        description="Convert a PNG picture into a scalable hexagonal SVG wallpaper.",
    )
    parser.add_argument("input", help="Path of the input PNG file.")
    parser.add_argument(
        "-o",
        "--output",
        help="Path of the output SVG file (default: the input name with a .svg extension).",
    )
    parser.add_argument(
        "--hex-width",
        type=float,
        default=DEFAULT_HEX_WIDTH,
        help=f"Flat-to-flat width of a hexagon, in pixels (default: {DEFAULT_HEX_WIDTH:g}).",
    )
    return parser
