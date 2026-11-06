#!/usr/bin/env python3
"""The SuperBits Labs logo, as proper SVG.

    python3 make-logo.py

    logo/superbits-mark.svg         the grid alone, transparent
    logo/superbits-mark-mono.svg    the grid in one colour, via currentColor
    logo/superbits-tile.svg         the grid on its own rounded ground
    logo/superbits-logo.svg         full lockup, for dark backgrounds
    logo/superbits-logo-light.svg   full lockup, for light backgrounds

The wordmark is written as outlined paths, not <text>. A logo has to render
the same in Illustrator, on a printer's machine and in an email signature,
none of which will have Archivo installed — a <text> element would silently
fall back to whatever that machine had and stop being the logo.

Archivo is fetched once and cached under store/.fonts/ (shared with
make-store-assets.py).
"""
import pathlib
import subprocess

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

OUT = pathlib.Path("logo")
FONT = pathlib.Path("store/.fonts/archivo.ttf")
FONT_URL = ("https://fonts.gstatic.com/s/archivo/v25/"
            "k3k6o8UDI-1M0wlSV9XAw6lQkqWY8Q82sJaRE-NWIDdgffTT0zRp8A.ttf")

NAME = "SUPERBITS LABS"
ACCENT = "#FF2D6F"
# Standalone assets use the lighter grey. The site header keeps #282D38 on
# purpose — there the mark is small and beside the wordmark, so it should
# recede. Alone, that value is a black square with a pink dot.
CELL = "#3D4453"
GROUND = "#0B0D12"
INK_ON_DARK = "#E9EBF0"
INK_ON_LIGHT = "#11141A"

# The mark's own grid, the same twenty units the design has always used.
UNITS = 20
CELL_U, STEP_U, RADIUS_U = 5, 7.5, 1
MARK = 256                      # rendered size of the mark in the lockup
SCALE = MARK / UNITS
CAP_RATIO = 1.40                # mark height ÷ cap height
TRACKING_EM = 0.033
GAP = 80                        # mark to wordmark
PAD = 48                        # breathing room inside the viewBox


def grid(size, cell_fill, accent_fill, origin=(0, 0)):
    """The nine squares, as SVG markup."""
    s = size / UNITS
    ox, oy = origin
    rows = []
    for row in range(3):
        for col in range(3):
            x = ox + col * STEP_U * s
            y = oy + row * STEP_U * s
            lit = row == 1 and col == 1
            fill = accent_fill if lit else cell_fill
            rows.append(
                f'<rect x="{x:g}" y="{y:g}" width="{CELL_U * s:g}" height="{CELL_U * s:g}"'
                f' rx="{RADIUS_U * s:g}"{attr(fill)}/>'
            )
    return rows


def attr(colour):
    """None leaves the fill off entirely, so the shape inherits currentColor."""
    return "" if colour is None else f' fill="{colour}"'


def document(width, height, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}"'
        f' viewBox="0 0 {width:g} {height:g}" role="img" aria-label="{title}">\n'
        f"  <title>{title}</title>\n  "
        + "\n  ".join(body)
        + "\n</svg>\n"
    )


def font():
    if not FONT.exists():
        FONT.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-sSfL", FONT_URL, "-o", str(FONT)], check=True)
    return TTFont(FONT)


def wordmark(text, cap_height, colour):
    """The name as outlined paths, plus the width it occupies.

    Glyphs come out of the font y-up around a baseline at zero; SVG is y-down,
    so each one is flipped and placed by the transform rather than by editing
    its path data.
    """
    f = font()
    upem = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    glyphs = f.getGlyphSet()
    metrics = f["hmtx"]

    cap = getattr(f["OS/2"], "sCapHeight", 0) or upem * 0.72
    scale = cap_height / cap
    tracking = TRACKING_EM * upem * scale

    parts, x = [], 0.0
    for ch in text:
        name = cmap[ord(ch)]
        pen = SVGPathPen(glyphs)
        glyphs[name].draw(pen)
        d = pen.getCommands()
        if d:  # a space has no outline, only an advance
            parts.append(
                f'<path transform="translate({x:g} {cap_height:g}) scale({scale:g} {-scale:g})"'
                f' d="{d}"/>'
            )
        x += metrics[name][0] * scale + tracking
    width = x - tracking
    return f'<g fill="{colour}">' + "".join(parts) + "</g>", width


def lockup(ink, filename, title):
    cap = MARK / CAP_RATIO
    text, text_w = wordmark(NAME, cap, ink)
    width = PAD * 2 + MARK + GAP + text_w
    height = PAD * 2 + MARK

    body = grid(MARK, CELL, ACCENT, origin=(PAD, PAD))
    # Caps centred against the mark, not sat on its baseline.
    body.append(
        f'<g transform="translate({PAD + MARK + GAP:g} {PAD + (MARK - cap) / 2:g})">{text}</g>'
    )
    (OUT / filename).write_text(document(width, height, body, title), encoding="utf-8")
    return filename, width, height


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    size = 1024
    written = []

    for filename, cell, accent, ground in (
        ("superbits-mark.svg", CELL, ACCENT, None),
        ("superbits-mark-mono.svg", None, None, None),      # inherits currentColor
        ("superbits-tile.svg", CELL, ACCENT, GROUND),
    ):
        inset = 0.80 if ground else 1.0
        art = size * inset
        edge = (size - art) / 2
        body = []
        if ground:
            body.append(f'<rect width="{size}" height="{size}" rx="{size * 0.22:g}" fill="{ground}"/>')
        body += grid(art, cell, accent, origin=(edge, edge))
        svg = document(size, size, body, "SuperBits Labs")
        if filename.endswith("mono.svg"):
            svg = svg.replace("<svg ", '<svg fill="currentColor" ', 1)
        (OUT / filename).write_text(svg, encoding="utf-8")
        written.append((filename, size, size))

    written.append(lockup(INK_ON_DARK, "superbits-logo.svg", "SuperBits Labs"))
    written.append(lockup(INK_ON_LIGHT, "superbits-logo-light.svg", "SuperBits Labs"))

    for filename, w, h in written:
        kb = (OUT / filename).stat().st_size / 1024
        print(f"logo/{filename}  {w:g}x{h:g}  {kb:.1f} KB")
