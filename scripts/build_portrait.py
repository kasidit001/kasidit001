#!/usr/bin/env python3
"""Self-typing ASCII portrait -> assets/portrait.svg.   Run locally (needs Pillow):  python3 scripts/build_portrait.py [photo.png]

The photo defaults to assets/source/avatar.png (your GitHub avatar). Swap in any image: a plain background gives the cleanest result."""
import os
import sys
from xml.sax.saxutils import escape

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "source", "avatar.png")
OUT = os.path.join(HERE, "..", "assets", "portrait.svg")
COLS = 64                                   # characters per row
CROP = (135, 55, 305, 255)                  # left, top, right, bottom of the area to keep (None = whole image); set for your own photo
RAMP = " .:-=+*#%@"                         # sparse ramp reads better at small sizes
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
CHAR_W, CHAR_H, SIZE = 6.0, 10.0, 10


def ascii_rows(path):
    im = Image.open(path).convert("L")
    if CROP and path.endswith("avatar.png"): im = im.crop(CROP)
    im = ImageOps.autocontrast(im, cutoff=3)
    im = im.point(lambda v: int(255 * ((v / 255) ** 0.65)))      # lift the shadows so dark hair keeps some detail
    im = ImageEnhance.Contrast(im).enhance(1.6)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=1))
    rows = round(COLS * (im.height / im.width) * (CHAR_W / CHAR_H))
    im = im.resize((COLS, rows), Image.LANCZOS)
    px = im.load()
    return ["".join(RAMP[min(len(RAMP) - 1, px[x, y] * len(RAMP) // 256)] for x in range(COLS)) for y in range(rows)]


def build(rows):
    pad = 14
    width, height = round(COLS * CHAR_W) + pad * 2, round(len(rows) * CHAR_H) + pad * 2 + 22
    delay = 0.045
    total = len(rows) * delay
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="ASCII portrait">',
           '<title>ASCII portrait</title>',
           f'<rect width="{width}" height="{height}" rx="10" fill="#0d1117" stroke="#30363d"/>',
           f'<text x="{pad}" y="{pad + 8}" font-family="{FONT}" font-size="9" fill="#8b949e">kasidit@github:~$ ./portrait --ascii</text>']
    for i, row in enumerate(rows):
        y = pad + 22 + i * CHAR_H + SIZE
        svg.append(f'<text x="{pad}" y="{y:.1f}" font-family="{FONT}" font-size="{SIZE}" fill="#3fb950" xml:space="preserve" textLength="{COLS * CHAR_W:.0f}" lengthAdjust="spacingAndGlyphs" opacity="0">'
                   f'{escape(row)}<animate attributeName="opacity" from="0" to="1" begin="{i * delay:.3f}s" dur="0.08s" fill="freeze"/></text>')
    # block cursor that follows the typing, then keeps blinking at the bottom
    ys = ";".join(f"{pad + 22 + i * CHAR_H:.1f}" for i in range(len(rows)))
    svg.append(f'<rect x="{width - pad - 8}" y="{pad + 22}" width="6" height="{SIZE}" fill="#7ee787"><animate attributeName="y" values="{ys}" calcMode="discrete" dur="{total:.2f}s" fill="freeze"/>'
               f'<animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>')
    svg.append("</svg>")
    return "\n".join(svg)


if __name__ == "__main__":
    rows = ascii_rows(SRC)
    open(OUT, "w", encoding="utf-8").write(build(rows))
    print("wrote", os.path.normpath(OUT), f"({COLS}x{len(rows)} chars)")
