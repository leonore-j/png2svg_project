from PIL import Image
from pathlib import Path

def load_image(input):
    """Load a PNG image."""
    image_path = Path(input)

    if image_path.suffix.lower() != ".png":
        raise ValueError("The input file must be a PNG image.")

    if input == "":
        raise ValueError("The input file is empty.")
    
    input = Image.open(input)
    return input 