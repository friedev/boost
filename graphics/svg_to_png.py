#! /usr/bin/env python3

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

from pathlib import Path
from tempfile import NamedTemporaryFile
from subprocess import run, CalledProcessError
from string import Template


RENDERER_CANDIDATES = (
    [
        'rsvg-convert',
        '-w',
        '$width',
        '-h',
        '$height',
        '-b',
        '#$background',
        '-o',
        '$png_filename',
        '$svg_filename',
    ],
    [
        'chromium',
        '--incognito',
        '--headless',
        '--hide-scrollbars',
        '--window-size=${width},${height}',
        '--default-background-color=${background}',
        '--screenshot=${png_filename}',
        '$svg_filename',
    ],
    [
        'chrome',
        '--incognito',
        '--headless',
        '--hide-scrollbars',
        '--window-size=${width},${height}',
        '--default-background-color=${background}',
        '--screenshot=${png_filename}',
        '$svg_filename',
    ],
)


class RendererNotFoundError(OSError):
    pass


def render_as_png(svg, width, height, background='ffffffff'):
    with NamedTemporaryFile('w', suffix='.svg', dir=Path(), delete=False)\
            as svg_file:
        svg_file.write(svg)
    with NamedTemporaryFile('w', suffix='.png', dir=Path(), delete=False)\
            as png_file:
        pass
    try:
        for renderer_template in RENDERER_CANDIDATES:
            try:
                renderer = []
                for arg in renderer_template:
                    renderer.append(Template(arg).substitute(
                        width=str(width),
                        height=str(height),
                        background=background,
                        png_filename=png_file.name,
                        svg_filename=svg_file.name))
                run(renderer, check=True)
            except (FileNotFoundError, CalledProcessError):
                pass
            else:
                with open(png_file.name, 'rb') as file:
                    return file.read()
        raise RendererNotFoundError(
            'Unable to find a suitable SVG renderer in PATH.',
        )
    finally:
        Path(svg_file.name).unlink()
        Path(png_file.name).unlink()
