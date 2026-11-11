from PIL import Image
from pathlib import Path
import math

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
    if width <= 0:
        raise ValueError("width must be positive")
    
    cx, cy = center 
    radius = width / math.sqrt(3)
    vertices = []
    for i in range(6):
        vertix_i = (
        cx + radius * math.cos(math.radians(60 * i - 90)),  # first vertix (vertix0) at -90°
        cy + radius * math.sin(math.radians(60 * i - 90))) 
        vertices.append(vertix_i)
    return vertices

    