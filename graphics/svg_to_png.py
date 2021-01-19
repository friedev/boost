#! /usr/bin/env python3

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
    with NamedTemporaryFile('w', suffix='.svg', dir=Path(), delete=False) as svg_file:
        svg_file.write(svg)
    with NamedTemporaryFile('w', suffix='.png', dir=Path(), delete=False) as png_file:
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
