#!/usr/bin/env python3
"""Play Console developer-page artwork, drawn from the SuperBits mark.

Google asks for both assets as JPEG or 24-bit PNG with no transparency, under
1 MB. These are written as RGB PNGs — lossless, genuinely 24-bit, and a flat
dark composition compresses to a fraction of the limit, where JPEG would band
across the large near-black areas.

    python3 make-store-assets.py

    store/superbits-logo-512.png         512 x 512
    store/superbits-feature-4096.png    4096 x 2304

The brand fonts are fetched from Google Fonts on first run and cached in
store/.fonts/ — the same faces the site loads, so the artwork and the website
are set in one typeface rather than two that nearly match.
"""
import pathlib
import subprocess

from PIL import Image, ImageDraw, ImageFont, ImageOps

OUT = pathlib.Path("store")
FONTS = OUT / ".fonts"

# The mark, in the same 20-unit grid the SVG uses.
CELLS = [(c, r) for r in (0, 7.5, 15) for c in (0, 7.5, 15)]
ACCENT = "#FF2D6F"

# On the site the eight cells sit back at #282D38 because the mark is small and
# next to the wordmark. Standing alone at 48px in a Play listing that reads as
# a black square, so they are lifted here — same mark, enough contrast to still
# be a grid.
CELL = "#3D4453"

FACES = {
    "archivo.ttf": "https://fonts.gstatic.com/s/archivo/v25/"
                   "k3k6o8UDI-1M0wlSV9XAw6lQkqWY8Q82sJaRE-NWIDdgffTT0zRp8A.ttf",
    "jbmono.ttf": "https://fonts.gstatic.com/s/jetbrainsmono/v24/"
                  "tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8-qxjPQ.ttf",
}


def face(name, size):
    FONTS.mkdir(parents=True, exist_ok=True)
    path = FONTS / name
    # curl, not urllib: a python.org install ships without the system CA
    # bundle, and fails the fonts.gstatic.com handshake on a clean machine.
    if not path.exists():
        subprocess.run(["curl", "-sSfL", FACES[name], "-o", str(path)], check=True)
    return ImageFont.truetype(str(path), size)


def mark(size, supersample=4):
    """The 3x3 grid as an RGBA tile. Drawn large and reduced, because rounded
    corners at this radius alias badly when drawn at final size."""
    n = size * supersample
    tile = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tile)
    unit = n / 20
    for col, row in CELLS:
        lit = col == 7.5 and row == 7.5
        draw.rounded_rectangle(
            [col * unit, row * unit, (col + 5) * unit, (row + 5) * unit],
            radius=unit,
            fill=ACCENT if lit else CELL,
        )
    return tile.resize((size, size), Image.LANCZOS)


def tracked(draw, xy, text, font, fill, tracking=0):
    """PIL has no letter-spacing, and caps this large need some."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x - tracking - xy[0]


def width_of(draw, text, font, tracking=0):
    return sum(draw.textlength(c, font=font) for c in text) + tracking * (len(text) - 1)


def logo():
    """512x512. Padded to about 15% so it survives being masked into a circle
    or a squircle, which Play does in some placements."""
    size, inset = 512, 0.625
    img = Image.new("RGB", (size, size), "#0B0D12")
    art = mark(round(size * inset))
    at = (size - art.width) // 2
    img.paste(art, (at, at), art)
    return img


def feature():
    """4096x2304. Everything sits in the middle third: Play crops this banner
    differently on different surfaces, and the edges are the first to go."""
    w, h = 4096, 2304
    img = Image.new("RGB", (w, h), "#08090C")

    # A single soft bloom behind the lockup, so the frame isn't flat black.
    bloom = ImageOps.invert(Image.radial_gradient("L")).resize((w, h), Image.LANCZOS)
    img.paste(Image.new("RGB", (w, h), ACCENT), (0, 0), bloom.point(lambda v: int(v * 0.10)))

    draw = ImageDraw.Draw(img)
    word = face("archivo.ttf", 300)
    small = face("jbmono.ttf", 62)

    glyph, gap, track = 300, 96, 10
    name, label = "SUPERBITS", "TECHNOLOGY COMPANY · INDIA"
    name_w = width_of(draw, name, word, track)

    block = glyph + gap + name_w
    left = (w - block) / 2
    # Optical centring: cap height, not the font's full line box.
    top, bottom = word.getbbox(name)[1], word.getbbox(name)[3]
    cap = bottom - top
    baseline = (h - cap) / 2 - 90

    art = mark(glyph)
    img.paste(art, (round(left), round(baseline + (cap - glyph) / 2)), art)
    tracked(draw, (left + glyph + gap, baseline - top), name, word, "#E9EBF0", track)

    label_track = 11
    label_w = width_of(draw, label, small, label_track)
    tracked(draw, ((w - label_w) / 2, baseline + cap + 96), label, small, "#858B99", label_track)
    return img


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, image in (("superbits-logo-512", logo()), ("superbits-feature-4096", feature())):
        path = OUT / f"{name}.png"
        image.save(path, "PNG", optimize=True)
        kb = path.stat().st_size / 1024
        assert image.mode == "RGB", f"{path} must have no alpha channel"
        assert kb < 1024, f"{path} is {kb:.0f} KB, over Play's 1 MB limit"
        print(f"{path}  {image.width}x{image.height}  {kb:.0f} KB")
