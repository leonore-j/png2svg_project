import pytest
from PIL import Image
from pathlib import Path
import math
import numpy as np

from png2svg.core import load_image, hex_vertices

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




