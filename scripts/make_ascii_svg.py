#!/usr/bin/env python3
"""Convert source-prepped.png into a monochrome, self-typing ASCII SVG."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from PIL import Image

RAMP = " .`:-=+*cs#%@"
FONT_SIZE = 10
CELL_WIDTH = 6
LINE_HEIGHT = 12
COLUMNS = 74


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("source-prepped.png"))
    parser.add_argument("--output", type=Path, default=Path("avi-ascii.svg"))
    args = parser.parse_args()

    with Image.open(args.input) as source:
        image = source.convert("L")
        aspect = image.width / image.height
        rows = max(1, round(COLUMNS * 0.6 / aspect))
        image = image.resize((COLUMNS, rows), Image.Resampling.LANCZOS)
        pixels = image.tobytes()

    width = COLUMNS * CELL_WIDTH + 28
    height = rows * LINE_HEIGHT + 36
    svg_rows: list[str] = []
    for row in range(rows):
        y = 24 + row * LINE_HEIGHT
        glyphs = "".join(
            RAMP[round((255 - pixels[row * COLUMNS + column]) * (len(RAMP) - 1) / 255)]
            for column in range(COLUMNS)
        )
        escaped = html.escape(glyphs)
        delay = row * 0.035
        svg_rows.append(
            f"""  <defs>
    <clipPath id="row-{row}"><rect x="14" y="{y - FONT_SIZE}" width="0" height="{LINE_HEIGHT}">
      <animate attributeName="width" from="0" to="{COLUMNS * CELL_WIDTH}" dur="0.65s" begin="{delay:.3f}s" fill="freeze"/>
    </rect></clipPath>
  </defs>
  <text x="14" y="{y}" fill="#c9d1d9" font-family="monospace" font-size="{FONT_SIZE}" xml:space="preserve" clip-path="url(#row-{row})">{escaped}</text>
  <rect x="14" y="{y - FONT_SIZE}" width="6" height="{LINE_HEIGHT}" fill="#39d353">
    <animate attributeName="x" from="14" to="{14 + COLUMNS * CELL_WIDTH}" dur="0.65s" begin="{delay:.3f}s" fill="freeze"/>
    <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.94;1" dur="0.65s" begin="{delay:.3f}s" fill="freeze"/>
  </rect>"""
        )

    content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Animated ASCII portrait of sehdie</title>
  <desc id="desc">A monochrome portrait revealed one line at a time.</desc>
  <rect width="100%" height="100%" rx="10" fill="#0d1117" stroke="#30363d"/>
{chr(10).join(svg_rows)}
</svg>
"""
    args.output.write_text(content, encoding="utf-8")
    print(f"Animated portrait written to {args.output}")


if __name__ == "__main__":
    main()
