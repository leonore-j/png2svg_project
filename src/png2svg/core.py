import math
from pathlib import Path

from PIL import Image


def load_image(input):
    """ Load a png image and returns the associated pixel grid (RGB format)

    Args:
        input (.jpg file): the jpeg image to be converted

    Raises:
        ValueError: 

    Returns:
        2D Array: The "RGB" pixel grid
    """
    image_path = Path(input)

    if image_path.suffix.lower() != ".png":
        raise ValueError("The input file must be a PNG image.")
    
    input = Image.open(input).convert("RGB")
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

# Sample color 

# 1. Helper in_hexagon 

def in_hex(dx,dy,hex_width):
    """Given an hexagon of center (cx,cy) and width hex_width, the function returns
    true if a pixel of coordinates (cx + dx, cy + dy) is in the hexagon. 
    Returns False otherwise

    Args:
        dx (float): offset between the row coord of the hexagon center 
        and the row coordinate of the pixel
        dy (float): offset between the column coord of the hexagon center 
        and the column coordinate of the pixel
        hex_width (float): hexagone width
    """
    dx = abs(dx)
    dy = abs(dy)

    radius = hex_width / math.sqrt(3)
    half_width = hex_width / 2

    if dx > half_width:
        return False

    max_dy = radius - dx / math.sqrt(3)
    if dy > max_dy:
        return False

    return True

def sample_color(coord, input, hex_width):
    """Given an hexagon with center of coordinates coord and of width hex_width, 
    and a grid of pixel (input), it returns the RGB code of the average color 
    of all pixels contained in the hexagon

    Args:
        coord (tuple): coordinate of the hexagon coordinate
        input (2D array): grid of pixel
        hex_width (float): hexagon width
    """
    cx, cy = coord  # hexagon center
    img = input.convert("RGB")
    width, height = img.size

    r_sum, g_sum, b_sum = 0, 0, 0
    n_pixels = 0  # number of pixels contained in the hexagon
    radius = hex_width / math.sqrt(3)
    half_width = hex_width / 2

    for px in range(math.floor(cx - half_width), math.floor(cx + half_width) + 1):
        for py in range(math.floor(cy - radius), math.floor(cy + radius) + 1):
            if not (0 <= px < width and 0 <= py < height):
                continue  # pixel outside the image
            if in_hex(px - cx, py - cy, hex_width):
                r, g, b = img.getpixel((px, py))
                r_sum += r
                g_sum += g
                b_sum += b
                n_pixels += 1

    if n_pixels == 0:
        raise ValueError("No pixel of the image lies in this hexagon")

    return (round(r_sum / n_pixels),round(g_sum / n_pixels),
            round(b_sum / n_pixels),)


def generate_hexagon(coord, rgb, hex_width):
    """Return the SVG hexagon filled with "rgb".

    Args:
        coord (tuple): coordinates of the hexagon center
        rgb (tuple): RGB code of the hexagon color 
        hex_width (float): hexagon width
    """
    vertices = hex_vertices(coord, hex_width) # re-use the helper function created for hex_grid_coord
    points = " ".join(f"{x:.2f},{y:.2f}" for x, y in vertices)
    r, g, b = rgb
    return f'<polygon points="{points}" fill="rgb({r},{g},{b})"/>'