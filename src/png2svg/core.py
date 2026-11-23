import math
from pathlib import Path

from PIL import Image


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
    return [
        (
            cx + radius * math.cos(math.radians(60 * i - 90)),
            cy + radius * math.sin(math.radians(60 * i - 90)),
        )
        for i in range(6)
    ]

# help and conventions from redblobgames.com

def hexagonal_grid_coordinates(image_width, image_height, hex_width):
    """Compute the pixel coordinates of hexagon centers covering an image.

    The grid uses pointy-top hexagons and the "even-r" layout: even rows
    (0, 2, ...) are shoved right by half a hexagon width. The image's
    top-left corner is at (0, 0), with y pointing down.

    Args:
        image_width: image width in pixels.
        image_height: image height in pixels.
        hex_width: flat-to-flat width of a hexagon, in pixels.

    Returns:
        A 2D list indexed as ``grid[row][col]``, where each item is the
        (x, y) pixel coordinate of a hexagon center. Rows may have different
        lengths because of the even-r offset.

    Raises:
        ValueError: if any argument is not strictly positive.
    """
    if image_width <= 0 or image_height <= 0 or hex_width <= 0 :
        raise ValueError("image dimensions and hex_width must be positive")
    if hex_width > image_width:
        raise ValueError("hex_width must me inferior to image_width.")

    size = hex_width / math.sqrt(3)  # radius: center -> vertex
    row_spacing = 1.5 * size # space between 2 centers on consecutive rows


    grid = [] #list[list[Point]]
    row = 0
    # A row is kept while its top (y pointing down) vertex is above the image's bottom edge.
    while row_spacing * row - size / 2 < image_height :
        y = size / 2 + row_spacing * row
        if row % 2 == 0 : # even-r convention
            shift = hex_width / 2
        else : 
            shift  = 0  
        line = [] # list[Point]
        col = 0
        # A hexagon is kept while its left edge is before the image's right edge.
        while shift + col * hex_width - hex_width / 2 < image_width : 
            line.append((shift + col * hex_width, y))
            col += 1
        grid.append(line)
        row += 1
    return grid

def compute_next_coord(grid,pos):
    """Given a grid and a current position, computes and returns the next position.
    Returns (-1,-1) if the grid is over. 
    To compute the first position, call compute_next_grid(grid,None)

    Args:
        grid (2D Array): the image pixel grid
        pos (tuple): coordinates of the current position

    Returns:
        tuple : coordinates (row, col) of the next position in the grid, 
        (-1,-1) if the grid is over.
    """
    if not grid or not grid[0]:
        raise ValueError("The grid is empty")
    if pos is None:
        return (0, 0)

    row, col = pos
    if col + 1 < len(grid[row]):  # next center in the same row
        return (row, col + 1)
    if row + 1 < len(grid):  # first center of the next row
        return (row + 1, 0)
    return (-1,-1)