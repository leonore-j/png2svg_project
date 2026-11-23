import math
from pathlib import Path

import pytest
from PIL import Image

from png2svg.core import (
    compute_next_coord,
    hex_vertices,
    hexagonal_grid_coordinates,
    load_image,
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
    expected_radius = width / math.sqrt(3) # size
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

WIDTH = 20 # width of a hexagon
SIZE = WIDTH / math.sqrt(3) # size of a hexagon (h = 2*SIZE)
ROW_SPACING = 1.5 * SIZE  # vertical spacing between 2 hexagon center (pointy-top orientation)
Y0 = SIZE / 2  # Y coord of the first row is SIZE/2 


@pytest.mark.parametrize(
    "image_size, expected_row_lengths",
    [
        ((100, 100), [5, 6, 5, 6, 5, 6, 5]),  # 5 for even rows; 6 for odd rows
        ((130, 115), [7] * 7),                # always 7
    ],
)
def test_grid_dimensions(image_size, expected_row_lengths) -> None:
    grid = hexagonal_grid_coordinates(*image_size, WIDTH)
    assert [len(row) for row in grid] == expected_row_lengths


@pytest.mark.parametrize(
    "row, col, expected",
    [
        (0, 0, (WIDTH / 2, Y0)),                   # first hexagon coordinate
        (0, 1, (1.5 * WIDTH, Y0)),                 # vertical spacing = WIDTH (WIDTH / 2 + WIDTH = 1.5*WIDTH )
        (1, 0, (0, Y0 + ROW_SPACING)),             # odd rows : left border of first hex touches left border of image
        (1, 1, (WIDTH, Y0 + ROW_SPACING)),
        (2, 0, (WIDTH / 2, Y0 + 2 * ROW_SPACING)), 
    ],
)
def test_center_positions(row, col, expected) -> None:
    grid = hexagonal_grid_coordinates(100, 100, WIDTH)
    assert grid[row][col] == pytest.approx(expected)


@pytest.mark.parametrize(
    "image_width, image_height, hex_width",
    [(0, 100, WIDTH), (100, 0, WIDTH), (-1, 100, WIDTH), (100, 100, 0), (100, 100, -WIDTH), (10, 10, WIDTH)],
)
def test_invalid_parameters_raise_value_error(image_width, image_height, hex_width) -> None:
    with pytest.raises(ValueError):
        hexagonal_grid_coordinates(image_width, image_height, hex_width)


def test_every_pixel_belongs_to_a_hexagon() -> None:
    width, height = 60, 50
    centers = [c for row in hexagonal_grid_coordinates(width, height, WIDTH) for c in row]

    def in_hexagon(px: float, py: float, cx: float, cy: float) -> bool: # (px,py) coord of one pixel, (cx,cy) coord of a hex center
        dx, dy = abs(px - cx), abs(py - cy)
        return dx <= WIDTH / 2 + 1e-9 and dy <= SIZE - dx / math.sqrt(3) + 1e-9

    for px in range(width):
        for py in range(height):
            assert any(in_hexagon(px, py, cx, cy) for cx, cy in centers), (px, py)



# Test compute_next_coord

# hex grid : 2 centers on even rows and three on odd rows
GRID = [[(0, 0), (1, 0)], [(0, 1), (1, 1), (2, 1)]] 


def test_first_coordinate() :
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