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

from io import BytesIO

from discord import File

from .board_svg import create_board
from .svg_to_png import render_as_png, RendererNotFoundError


def render_for_discord(
    board, filename, rectangle_width, rectangle_height, background
):
    svg = create_board(rectangle_width, rectangle_height, board)
    png = render_as_png(svg, rectangle_width, rectangle_height, background)
    return File(BytesIO(png), filename=filename)
