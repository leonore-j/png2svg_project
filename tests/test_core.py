import math
from pathlib import Path
from xml.etree import ElementTree

import pytest
from PIL import Image

from png2svg.core import (
    append_hexagon,
    compute_next_coord,
    generate_hexagon,
    hex_vertices,
    hexagonal_grid_coordinates,
    in_hex,
    init_svg,
    load_image,
    png2svg,
    sample_color,
)

# Test load_image


def test_load_image_correct_dim(tmp_path: Path) -> None:
    """Test that load_image returns an image with the correct dimensions."""
    image_path = tmp_path / "test_image.png"

    # Create a test image of 100 pixels wide and 50 pixels high.
    Image.new("RGB", (100, 50), color=(255, 0, 0)).save(image_path)

    image = load_image(image_path)

    assert image.size == (100, 50)


def test_load_image_invalid_input(tmp_path: Path) -> None:
    """Test that load_image raises an error for an invalid image."""

    # Create an invalid input called ("invalid.png") that is not a png file
    invalid_path = tmp_path / "invalid.png"
    invalid_path.write_text("This is not a valid image.")

    with pytest.raises((ValueError, OSError)):
        load_image(invalid_path)


def test_load_image_raises_error_for_empty_input() -> None:
    """Test that load_image raises an error for an empty input."""
    with pytest.raises((ValueError, OSError)):
        load_image("")


# Test create_hexagonal_grid


# Test helper 1 : hex_vertices()
def test_returns_six_vertices() -> None:
    vertices = hex_vertices(center=(0, 0), width=20)
    assert len(vertices) == 6


def test_vertices_are_at_equal_distance_from_center() -> None:
    center = (10, 15)
    width = 20
    vertices = hex_vertices(center=center, width=width)
    expected_radius = width / math.sqrt(3)  # size
    for x, y in vertices:
        distance = math.hypot(x - center[0], y - center[1])
        assert distance == pytest.approx(expected_radius)


def test_first_vertex_is_at_the_top() -> None:
    center = (10, 15)
    width = 20
    vertices = hex_vertices(center=center, width=width)
    x_top, y_top = vertices[0]
    assert x_top == pytest.approx(center[0])
    assert y_top == pytest.approx(center[1] - width / math.sqrt(3))


def test_hexagon_has_expected_horizontal_width() -> None:
    width = 20
    vertices = hex_vertices(center=(0, 0), width=width)
    x_coordinates = [x for x, _ in vertices]
    assert max(x_coordinates) - min(x_coordinates) == pytest.approx(width)


@pytest.mark.parametrize("width", [0, -20])
def test_width_must_be_positive(width: float) -> None:
    with pytest.raises(ValueError):
        hex_vertices(center=(0, 0), width=width)


# Test create_hexagonal_grid()

WIDTH = 20  # width of a hexagon
SIZE = WIDTH / math.sqrt(3)  # size of a hexagon (h = 2*SIZE)
ROW_SPACING = (
    1.5 * SIZE
)  # vertical spacing between 2 hexagon center (pointy-top orientation)
Y0 = SIZE / 2  # Y coord of the first row is SIZE/2


@pytest.mark.parametrize(
    "image_size, expected_row_lengths",
    [
        ((100, 100), [5, 6, 5, 6, 5, 6, 5]),  # 5 for even rows; 6 for odd rows
        ((130, 115), [7] * 7),  # always 7
    ],
)
def test_grid_dimensions(image_size, expected_row_lengths) -> None:
    grid = hexagonal_grid_coordinates(*image_size, WIDTH)
    assert [len(row) for row in grid] == expected_row_lengths


@pytest.mark.parametrize(
    "row, col, expected",
    [
        (0, 0, (WIDTH / 2, Y0)),  # first hexagon coordinate
        (
            0,
            1,
            (1.5 * WIDTH, Y0),
        ),  # vertical spacing = WIDTH (WIDTH / 2 + WIDTH = 1.5*WIDTH )
        (
            1,
            0,
            (0, Y0 + ROW_SPACING),
        ),  # odd rows : left border of first hex touches left border of image
        (1, 1, (WIDTH, Y0 + ROW_SPACING)),
        (2, 0, (WIDTH / 2, Y0 + 2 * ROW_SPACING)),
    ],
)
def test_center_positions(row, col, expected) -> None:
    grid = hexagonal_grid_coordinates(100, 100, WIDTH)
    assert grid[row][col] == pytest.approx(expected)


@pytest.mark.parametrize(
    "image_width, image_height, hex_width",
    [
        (0, 100, WIDTH),
        (100, 0, WIDTH),
        (-1, 100, WIDTH),
        (100, 100, 0),
        (100, 100, -WIDTH),
        (10, 10, WIDTH),
    ],
)
def test_invalid_parameters_raise_value_error(
    image_width, image_height, hex_width
) -> None:
    with pytest.raises(ValueError):
        hexagonal_grid_coordinates(image_width, image_height, hex_width)


def test_every_pixel_belongs_to_a_hexagon() -> None:
    width, height = 60, 50
    centers = [
        c for row in hexagonal_grid_coordinates(width, height, WIDTH) for c in row
    ]

    def in_hexagon(
        px: float, py: float, cx: float, cy: float
    ) -> bool:  # (px,py) coord of one pixel, (cx,cy) coord of a hex center
        dx, dy = abs(px - cx), abs(py - cy)
        return dx <= WIDTH / 2 + 1e-9 and dy <= SIZE - dx / math.sqrt(3) + 1e-9

    for px in range(width):
        for py in range(height):
            assert any(in_hexagon(px, py, cx, cy) for cx, cy in centers), (px, py)


# Test compute_next_coord

# hex grid : 2 centers on even rows and three on odd rows
GRID = [[(0, 0), (1, 0)], [(0, 1), (1, 1), (2, 1)]]


def test_first_coordinate():
    assert compute_next_coord(GRID, None) == (0, 0)


@pytest.mark.parametrize(
    "current, expected",
    [
        ((0, 0), (0, 1)),  # go to next coord in the same row
        ((0, 1), (1, 0)),  # end of row -> switch to next row
        ((1, 1), (1, 2)),  # odd row -> difference of length
    ],
)
def test_moves_to_next_position(current, expected) -> None:
    assert compute_next_coord(GRID, current) == expected


def test_returns_sentinel_when_grid_is_traversed() -> None:
    assert compute_next_coord(GRID, (1, 2)) == (-1, -1)


# Test sample_color

# 1. Test helper in_hexagon


@pytest.mark.parametrize(
    "dx, dy, expected",
    [
        (0, 0, True),  # centre
        (8, -5, True),  # près du côté oblique, mais dedans
        (10, -10, False),  # coin de la boîte englobante, hors hexagone
        (11, 0, False),  # au-delà du côté vertical (demi-largeur = 10)
    ],
)
def test_in_hexagon(dx: float, dy: float, expected: bool) -> None:
    assert in_hex(dx, dy, 20) is expected


# 2. Test sample_color

WIDTH = 20
BASE = (200, 50, 10)


def test_uniform_image_returns_its_color() -> None:
    img = Image.new("RGB", (100, 100), BASE)
    assert sample_color((50, 50), img, WIDTH) == BASE


def test_color_is_the_average_of_the_hexagon() -> None:
    img = Image.new("RGB", (100, 100), (0, 0, 0))
    img.paste((255, 255, 255), (50, 0, 100, 100))  # moitié droite blanche
    r, g, b = sample_color((50, 50), img, WIDTH)
    assert (r, g, b) == pytest.approx((127, 127, 127), abs=10)


def test_pixels_outside_the_hexagon_are_ignored() -> None:
    img = Image.new("RGB", (100, 100), BASE)
    img.paste((255, 255, 255), (58, 40, 61, 43))  # coin de la boîte, hors hexagone
    assert sample_color((50, 50), img, WIDTH) == BASE


def test_hexagon_partly_outside_the_image_does_not_raise() -> None:
    img = Image.new("RGB", (100, 100), BASE)
    assert sample_color((0, 0), img, WIDTH) == BASE


def test_hexagon_grazing_the_image_uses_the_nearest_pixel() -> None:
    img = Image.new("RGB", (57, 43), BASE)
    img.paste((255, 255, 255), (0, 42, 57, 43))
    assert sample_color((30, 48.49), img, 10.5) == (255, 255, 255)


# Test generate_hexagon


def test_generate_hexagon_has_expected_vertices_and_color() -> None:
    svg = generate_hexagon((50, 50), (200, 50, 10), 20)
    polygon = ElementTree.fromstring(svg)

    assert polygon.tag == "polygon"
    assert polygon.get("fill") == "rgb(200,50,10)"

    points = [tuple(map(float, p.split(","))) for p in polygon.get("points").split()]
    expected = hex_vertices((50, 50), 20)

    assert len(points) == len(expected) == 6
    for point, vertex in zip(points, expected):
        assert point == pytest.approx(vertex, abs=0.01)


# Test Geometry

SVG_NS = "{http://www.w3.org/2000/svg}"
FIRST = '<polygon points="0,0 1,0 1,1" fill="rgb(1,2,3)"/>'
SECOND = '<polygon points="2,2 3,2 3,3" fill="rgb(4,5,6)"/>'


def fills(path) -> list[str]:
    root = ElementTree.parse(path).getroot()
    return [p.get("fill") for p in root.findall(f"{SVG_NS}polygon")]


# 1. Test helper init_svg


def test_init_svg_creates_an_empty_scalable_document(tmp_path) -> None:
    output = init_svg(tmp_path / "out.svg", 100, 50)
    root = ElementTree.parse(output).getroot()
    assert root.tag == f"{SVG_NS}svg"
    assert root.get("viewBox") == "0 0 100 50"
    assert len(root) == 0


# 2. Test append_hexagon


def test_append_hexagon_writes_the_polygon_in_the_file(tmp_path) -> None:
    output = init_svg(tmp_path / "out.svg", 100, 50)
    append_hexagon(output, FIRST)
    assert fills(output) == ["rgb(1,2,3)"]


def test_append_hexagon_keeps_previous_hexagons_in_order(tmp_path) -> None:
    output = init_svg(tmp_path / "out.svg", 100, 50)
    append_hexagon(output, FIRST)
    append_hexagon(output, SECOND)
    assert fills(output) == ["rgb(1,2,3)", "rgb(4,5,6)"]


# Test wrapper : png2svg

SVG_NS = "{http://www.w3.org/2000/svg}"
IMG_WIDTH, IMG_HEIGHT, F2F_HEX_WIDTH = 60, 40, 10
IMG_COLOR = (200, 50, 10)


def make_png(path, size=(IMG_WIDTH, IMG_HEIGHT), color=IMG_COLOR, mode="RGB"):
    Image.new(mode, size, color).save(path)
    return path


def read_svg(path):
    root = ElementTree.parse(path).getroot()  # lève une erreur si le XML est invalide
    return root, root.findall(f"{SVG_NS}polygon")


def centroid_x(polygon) -> float:
    points = [tuple(map(float, p.split(","))) for p in polygon.get("points").split()]
    return sum(x for x, _ in points) / len(points)


@pytest.fixture
def source(tmp_path):
    return make_png(tmp_path / "in.png")


def test_creates_svg_with_image_size_and_returns_its_path(source, tmp_path) -> None:
    out = tmp_path / "out.svg"
    assert png2svg(source, out, F2F_HEX_WIDTH) == out
    root, _ = read_svg(out)
    assert root.get("viewBox") == f"0 0 {IMG_WIDTH} {IMG_HEIGHT}"


def test_one_polygon_per_grid_center(source, tmp_path) -> None:
    out = png2svg(source, tmp_path / "out.svg", F2F_HEX_WIDTH)
    _, polygons = read_svg(out)
    grid = hexagonal_grid_coordinates(IMG_WIDTH, IMG_HEIGHT, F2F_HEX_WIDTH)
    assert len(polygons) == sum(len(row) for row in grid)


def test_uniform_image_gives_uniformly_colored_hexagons(source, tmp_path) -> None:
    out = png2svg(source, tmp_path / "out.svg", F2F_HEX_WIDTH)
    _, polygons = read_svg(out)
    assert {p.get("fill") for p in polygons} == {"rgb(200,50,10)"}


def test_hexagons_take_the_color_of_their_area_of_the_image(tmp_path) -> None:
    img = Image.new("RGB", (100, 40), (0, 0, 0))
    img.paste((255, 255, 255), (50, 0, 100, 40))
    img.save(tmp_path / "half.png")

    out = png2svg(tmp_path / "half.png", tmp_path / "out.svg", F2F_HEX_WIDTH)
    _, polygons = read_svg(out)

    left = [p for p in polygons if centroid_x(p) < 40]
    right = [p for p in polygons if centroid_x(p) > 60]
    assert left and right
    assert all(p.get("fill") == "rgb(0,0,0)" for p in left)
    assert all(p.get("fill") == "rgb(255,255,255)" for p in right)


@pytest.mark.parametrize("hex_width", [7, 10.5, 15.3])
def test_non_round_hexagon_width_on_odd_sized_image(tmp_path, hex_width) -> None:
    src = make_png(tmp_path / "odd.png", size=(57, 43))
    out = png2svg(src, tmp_path / "out.svg", hex_width)
    _, polygons = read_svg(out)
    grid = hexagonal_grid_coordinates(57, 43, hex_width)
    assert len(polygons) == sum(len(row) for row in grid)


@pytest.mark.parametrize(
    "filename, hex_width",
    [("photo.jpg", F2F_HEX_WIDTH), ("in.png", 0), ("in.png", -10)],
)
def test_invalid_input_raises_and_creates_no_file(
    tmp_path, filename, hex_width
) -> None:
    make_png(tmp_path / "in.png")
    out = tmp_path / "out.svg"
    with pytest.raises(ValueError):
        png2svg(tmp_path / filename, out, hex_width)
    assert not out.exists()
