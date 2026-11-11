from PIL import Image
from pathlib import Path

def load_image(input):
    """Load a PNG image."""
    image_path = Path(input)

    if image_path.suffix.lower() != ".png":
        raise ValueError("The input file must be a PNG image.")
    
    input = Image.open(input)
    return input

def hex_vertices(center,width) : 
    """Computes the coordinates of the 6 vertices of an hexagon
    of center (center[0], center[1]) and of width=width. 

    Args:
        center (tuple): tuple (x,y) containing the center coordinates
        width (float): chosen width of the hexagon
    """

    