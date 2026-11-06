#!/usr/bin/env python3
"""Raster artwork, drawn from the SuperBits mark.

Everything here is written as an RGB PNG: lossless, genuinely 24-bit, no alpha
channel — which is what Play asks for — and a composition this dark and this
flat bands visibly under JPEG while lossless still comes in far under every
size limit involved.

    python3 make-store-assets.py

    store/superbits-logo-512.png         512 x 512     Play developer logo
    store/superbits-feature-4096.png    4096 x 2304    Play feature graphic
    store/superbits-youtube-banner.png  2560 x 1440    YouTube channel art
    apple-touch-icon.png                 180 x 180     iOS home screen

The brand fonts are fetched from Google Fonts on first run and cached in
store/.fonts/ — the same faces the site loads, so the artwork and the website
are set in one typeface rather than two that nearly match.
"""
import pathlib
import random
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


def logo(size=512, inset=0.625):
    """The mark on its own ground. Padded so it survives being masked into a
    circle or a squircle, which both Play and iOS do."""
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


def starfield(img, density=26000, seed=7):
    """The site's sky, in a still frame. Seeded, so the banner is the same
    picture every time it is regenerated rather than a new one to re-approve."""
    w, h = img.size
    rng = random.Random(seed)
    sky = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sky)
    for _ in range(w * h // density):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(1.2, 4.0)
        a = int(rng.uniform(40, 150))
        # A handful carry the brand colour, as on the site.
        tint = (255, 45, 111, a) if rng.random() < 0.07 else (233, 235, 240, a)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=tint)
    return Image.alpha_composite(img.convert("RGBA"), sky).convert("RGB")


def youtube(scale=2):
    """2560x1440 channel art.

    YouTube shows a different crop on every surface and only the centre
    1546x423 is safe on all of them — a phone sees that and nothing else. So
    the lockup is sized to fit inside that box with room to spare, and the
    starfield is what the wider crops get. The assert at the end is the point
    of writing it this way: a banner whose name is cut in half on mobile is
    the single most common way this asset goes wrong.
    """
    w, h = 2560 * scale, 1440 * scale
    safe_w, safe_h = 1546 * scale, 423 * scale

    img = Image.new("RGB", (w, h), "#08090C")
    bloom = ImageOps.invert(Image.radial_gradient("L")).resize((w, h), Image.LANCZOS)
    img.paste(Image.new("RGB", (w, h), ACCENT), (0, 0), bloom.point(lambda v: int(v * 0.12)))
    img = starfield(img, density=26000 // (scale * scale))

    draw = ImageDraw.Draw(img)
    name, label = "SUPERBITS LABS", "TECHNOLOGY COMPANY · INDIA"

    # Solve for the type size that makes the lockup the width we want, rather
    # than guessing a size and hoping it lands inside the safe box.
    target = safe_w * 0.76
    probe = face("archivo.ttf", 100)
    unit = (width_of(draw, name, probe, 3.3) + 100 * 1.008 + 100 * 0.32) / 100
    size = round(target / unit)

    word = face("archivo.ttf", size)
    small = face("jbmono.ttf", round(size * 0.21))
    track = size * 0.033
    name_w = width_of(draw, name, word, track)
    top, bottom = word.getbbox(name)[1], word.getbbox(name)[3]
    cap = bottom - top
    glyph = round(cap * 1.40)
    gap = round(size * 0.32)

    block = glyph + gap + name_w
    label_track = size * 0.07
    label_w = width_of(draw, label, small, label_track)
    label_gap = round(size * 0.42)
    label_h = small.getbbox(label)[3] - small.getbbox(label)[1]

    total_h = glyph + label_gap + label_h
    left = (w - block) / 2
    top_y = (h - total_h) / 2

    art = mark(glyph)
    img.paste(art, (round(left), round(top_y)), art)
    tracked(draw, (left + glyph + gap, top_y + (glyph - cap) / 2 - top), name, word, "#E9EBF0", track)
    tracked(draw, ((w - label_w) / 2, top_y + glyph + label_gap), label, small, "#858B99", label_track)

    # Nothing that has to be read may leave the box a phone can see.
    assert max(block, label_w) <= safe_w, f"lockup is {max(block, label_w):.0f}px, safe width is {safe_w}"
    assert total_h <= safe_h, f"lockup is {total_h:.0f}px tall, safe height is {safe_h}"

    return img.resize((2560, 1440), Image.LANCZOS)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    assets = [
        (OUT / "superbits-logo-512.png", logo()),
        (OUT / "superbits-feature-4096.png", feature()),
        (OUT / "superbits-youtube-banner.png", youtube()),
        # iOS home screen. Square, because iOS applies its own rounding — and
        # at the root, where Safari looks for it whether or not it is linked.
        # Tighter inset than Play's so it matches the favicon in index.html.
        (pathlib.Path("apple-touch-icon.png"), logo(180, inset=0.80)),
    ]
    for path, image in assets:
        image.save(path, "PNG", optimize=True)
        kb = path.stat().st_size / 1024
        assert image.mode == "RGB", f"{path} must have no alpha channel"
        ceiling = 6 * 1024 if "youtube" in path.name else 1024
        assert kb < ceiling, f"{path} is {kb:.0f} KB, over the {ceiling // 1024} MB limit"
        print(f"{path}  {image.width}x{image.height}  {kb:.0f} KB")
