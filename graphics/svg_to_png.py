#! /usr/bin/env python3

from pathlib import Path
from tempfile import NamedTemporaryFile
from subprocess import run, CalledProcessError


RENDERER_CANDIDATES = (
    'chromium',
    'chrome',
)


class RendererNotFoundError(OSError):
    pass


def render_as_png(svg, width, height, background='ffffffff'):
    with NamedTemporaryFile('w', suffix='.svg', dir=Path(), delete=False) as svg_file:
        svg_file.write(svg)
    with NamedTemporaryFile('w', suffix='.png', dir=Path(), delete=False) as png_file:
        pass
    try:
        for renderer in RENDERER_CANDIDATES:
            try:
                run([
                    renderer,
                    '--incognito',
                    '--headless',
                    '--hide-scrollbars',
                    f'--window-size={width},{height}',
                    f'--default-background-color={background}',
                    f'--screenshot={png_file.name}',
                    svg_file.name,
                ], check=True)
            except (FileNotFoundError, CalledProcessError):
                pass
            else:
                with open(png_file.name, 'rb') as file:
                    return file.read()
        raise RendererNotFoundError(
            'Unable to find Chromium-based browser in PATH with which to render an SVG.',
        )
    finally:
        Path(svg_file.name).unlink()
        Path(png_file.name).unlink()
