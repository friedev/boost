from io import BytesIO
from discord import File

from .board_svg import create_board
from .svg_to_png import render_as_png, RendererNotFoundError


def render_for_discord(board, filename, rectangle_width, rectangle_height, background):
    svg = create_board(rectangle_width, rectangle_height, board)
    png = render_as_png(svg, rectangle_width, rectangle_height, background)
    return File(BytesIO(png), filename=filename)
