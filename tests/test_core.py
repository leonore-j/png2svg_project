import pytest
from png2svg.core import load_image
from PIL import Image
from pathlib import Path


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