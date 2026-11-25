# tests/test_cli.py
from xml.etree import ElementTree

import pytest
from PIL import Image

from png2svg.cli import DEFAULT_HEX_WIDTH, build_parser, main
from png2svg.core import hexagonal_grid_coordinates

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


def test_main_creates_svg_next_to_input_by_default(monkeypatch, source):
    monkeypatch.setattr("sys.argv", ["png2svg", str(source)])
    main()
    assert source.with_suffix(".svg").exists()


def test_main_uses_given_output_and_hex_width(monkeypatch, capsys, source, tmp_path):
    out = tmp_path / "wallpaper.svg"
    monkeypatch.setattr(
        "sys.argv", ["png2svg", str(source), "-o", str(out), "--hex-width", "10"]
    )
    main()
    grid = hexagonal_grid_coordinates(*IMG_SIZE, 10)
    assert count_polygons(out) == sum(len(row) for row in grid)
    assert str(out) in capsys.readouterr().out


def test_main_requires_an_input(monkeypatch):
    monkeypatch.setattr("sys.argv", ["png2svg"])
    with pytest.raises(SystemExit):
        main()


def test_main_rejects_non_png_input(monkeypatch, tmp_path):
    out = tmp_path / "out.svg"
    monkeypatch.setattr(
        "sys.argv", ["png2svg", str(tmp_path / "photo.jpg"), "-o", str(out)]
    )
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
    assert not out.exists()


def test_main_rejects_missing_input(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.argv", ["png2svg", str(tmp_path / "absent.png")])
    with pytest.raises(SystemExit):
        main()


@pytest.mark.parametrize("hex_width", ["0", "-5"])
def test_main_rejects_invalid_hex_width(monkeypatch, source, tmp_path, hex_width):
    out = tmp_path / "out.svg"
    monkeypatch.setattr(
        "sys.argv", ["png2svg", str(source), "-o", str(out), f"--hex-width={hex_width}"]
    )
    with pytest.raises(SystemExit):
        main()
    assert not out.exists()
