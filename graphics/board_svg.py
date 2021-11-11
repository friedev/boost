# Copyright (C) 2020 Aaron Friesen <maugrift@maugrift.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from string import ascii_lowercase
from pathlib import Path

# For traceabilty to the code in `…/boost-app/src/features/play/board.js` in
# the original PWA, which scales everything to pixels for compatibility with
# `react-flip-toolkit`, we also do the same here.  The UNSCALED_* constants
# below are measured in points on the board, whereas the SCALED_* constants are
# measured in pixels.

UNSCALED_LINE_WIDTH = 1 / 32
UNSCALED_FONT_HEIGHT = 3 / 8
UNSCALED_FONT_WIDTH = (2 / 3) * UNSCALED_FONT_HEIGHT
UNSCALED_DOT_RADIUS = 3 / 32
UNSCALED_TARGET_RADIUS = 3 / 8
UNSCALED_TARGET_THICKNESS = 1 / 16

SCALED_BOARD_SHADOW = 5
SCALED_BOARD_ROUNDING = 8

PIECES_DIRECTORY = (Path(__file__).parent / 'pieces').absolute()
COLORED_PIECES = {
    'Pawn',
    'Knight',
    'Tower',
}
PIECE_FILENAMES = {
    'Dragon': 'dragon.svg',
    'Pawn': 'pawn.svg',
    'Knight': 'knight.svg',
    'Tower': 'tower.svg',
}

# If true, use "xlink:href" instead of just "href" in SVG <image> tags
# If the renderer is crashing, or the board is rendering without any pieces,
# try toggling this flag
# TODO convert to command line argument
XLINK = False


def prettify_file(x):
    return ascii_lowercase[x]


def prettify_rank(y):
    return str(y + 1)


def get_image_path(piece):
    result = PIECES_DIRECTORY
    if piece.name in COLORED_PIECES:
        result /= piece.color
    return result / PIECE_FILENAMES[piece.name]


def create_surface(scale, width, height):
    return f'''
  <filter id="shadow">
    <feGaussianBlur in="SourceAlpha" stdDeviation="{SCALED_BOARD_SHADOW}" />
    <feMerge>
      <feMergeNode />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
  <rect
    x="{0}"
    y="{0}"
    width="{scale * width}"
    height="{scale * height}"
    rx="{SCALED_BOARD_ROUNDING}"
    stroke="none"
    fill="rgba(127, 199, 127, 1)"
    filter="url(#shadow)" />
'''


def create_file(scale, x, length, name):
    return f'''
  <line
    x1="{scale * (x + 0.5)}"
    y1="{scale * length}"
    x2="{scale * (x + 0.5)}"
    y2="{0}"
    stroke="rgba(0, 0, 0, 1)"
    stroke-width="{scale * UNSCALED_LINE_WIDTH}" />
  <text
    x="{scale * (x + 0.5)}"
    y="{scale * (length + UNSCALED_FONT_HEIGHT)}"
    text-anchor="middle"
    dominant-baseline="middle"
    font-family="sans-serif"
    font-size="{scale * UNSCALED_FONT_HEIGHT}">{name}</text>
'''


def create_rank(scale, y, max_y, length, name):
    return f'''
  <line
    x1="{0}"
    y1="{scale * ((max_y - y) + 0.5)}"
    x2="{scale * length}"
    y2="{scale * ((max_y - y) + 0.5)}"
    stroke="rgba(0, 0, 0, 1)"
    stroke-width="{scale * UNSCALED_LINE_WIDTH}" />
  <text
    x="{scale * -UNSCALED_FONT_WIDTH}"
    y="{scale * ((max_y - y) + 0.5)}"
    text-anchor="middle"
    dominant-baseline="middle"
    font-family="sans-serif"
    font-size="{scale * UNSCALED_FONT_HEIGHT}">{name}</text>
'''


def create_dot(scale, x, y, max_y):
    return f'''
<circle
  cx="{scale * (x + 0.5)}"
  cy="{scale * ((max_y - y) + 0.5)}"
  r="{scale * UNSCALED_DOT_RADIUS}"
  stroke="rgba(0, 0, 0, 1)"
  fill="rgba(0, 0, 0, 1)" />
'''


def create_board_markings(scale, width, height):
    results = [create_surface(scale, width, height)]
    for x in range(width):
        results.append(create_file(scale, x, height, prettify_file(x)))
    for y in range(height):
        results.append(create_rank(scale, y, height - 1, width,
                       prettify_rank(y)))
    for x in range(width):
        for y in range(height):
            results.append(create_dot(scale, x, y, height - 1))
    return '\n'.join(results)


def create_piece(scale, x, y, max_y, image_path, xlink=XLINK):
    return f'''
  <image
    x="{scale * x}"
    y="{scale * (max_y - y)}"
    width="{scale}"
    height="{scale}"
    {'xlink:' if xlink else ''}href="{image_path.as_uri()}" />
'''


def create_pieces(scale, board, xlink=XLINK):
    max_y = board.height - 1
    results = []
    for cell in board.cells:
        piece = board.get_piece(cell)
        if piece is not None:
            results.append(create_piece(
                scale,
                cell.col,
                max_y - cell.row,
                max_y,
                get_image_path(piece),
                xlink
            ))
    return '\n'.join(results)


def create_board(rectangle_width, rectangle_height, board, xlink=XLINK):
    scale = min(rectangle_width / board.width, rectangle_height / board.height)
    bleed = scale * (2 * UNSCALED_FONT_HEIGHT) / min(board.width, board.height)
    view_box = f'{-bleed * board.width} {-bleed * board.height} ' + \
               f'{(scale + 2 * bleed) * board.width} ' +\
               f'{(scale + 2 * bleed) * board.height}'
    markings = create_board_markings(scale, board.width, board.height)
    pieces = create_pieces(scale, board)
    return '<svg xmlns="http://www.w3.org/2000/svg" ' +\
           f'viewBox="{view_box}">{markings}{pieces}</svg>'
