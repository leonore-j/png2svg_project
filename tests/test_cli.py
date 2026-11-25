# tests/test_cli.py
from xml.etree import ElementTree

import pytest
from PIL import Image

from png2svg.cli import DEFAULT_HEX_WIDTH, build_parser

SVG_NS = "{http://www.w3.org/2000/svg}"
IMG_SIZE = (60, 40)


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "in.png"
    Image.new("RGB", IMG_SIZE, (200, 50, 10)).save(path)
    return path


def count_polygons(path) -> int:
    return len(ElementTree.parse(path).getroot().findall(f"{SVG_NS}polygon"))


def test_parser_accepts_input_only():
    args = build_parser().parse_args(["photo.png"])
    assert args.input == "photo.png"
    assert args.output is None
    assert args.hex_width == DEFAULT_HEX_WIDTH


def test_parser_accepts_output_and_hex_width():
    args = build_parser().parse_args(
        ["photo.png", "-o", "out.svg", "--hex-width", "30"]
    )
    assert args.output == "out.svg"
    assert args.hex_width == 30.0
