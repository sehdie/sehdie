#!/usr/bin/env python3
"""Render the profile's neofetch-style information panel."""

from __future__ import annotations

import html
import os
from pathlib import Path

USERNAME = "sehdie"
ROWS = [
    (
        "Role",
        "UI/UX Designer | Front-End Developer | Aspiring Product Designer",
    ),
    (
        "Focus",
        "User-centred design, responsive interfaces, design systems, accessibility",
    ),
    (
        "Stack",
        "Figma, HTML5, CSS3, JavaScript, React, Python, C, SCSS",
    ),
    (
        "Highlights",
        "Computer Science graduate | Design + development",
    ),
]
OUTPUT = Path("info-card.svg")
WIDTH = 640
HEIGHT = 360


def wrap_text(value: str, limit: int = 54) -> list[str]:
    """Split text into readable SVG lines without cutting words."""
    words = value.split()
    lines: list[str] = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                lines.append(current)
            # Keep long individual words from overflowing the card.
            while len(word) > limit:
                lines.append(word[:limit])
                word = word[limit:]
            current = word

    if current:
        lines.append(current)

    return lines


def safe_text(value: str) -> str:
    """Escape text so it is safe to include in SVG markup."""
    return html.escape(value, quote=True)


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    style = "" if static else """  <style>
    @keyframes print-in {
      from { opacity: 0; transform: translateY(5px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .line { animation: print-in 0.45s ease-out both; }
  </style>"""

    lines: list[str] = []
    y = 144

    for index, (label, value) in enumerate(ROWS):
        wrapped = wrap_text(value, limit=55)
        animation = (
            f' class="line" style="animation-delay:{index * 120}ms"'
            if not static
            else ""
        )

        text_lines = [
            f'<text x="170" y="{y + line_index * 17}" '
            f'fill="#c9d1d9" font-family="monospace" font-size="12">'
            f'{safe_text(line)}</text>'
            for line_index, line in enumerate(wrapped)
        ]

        lines.append(
            f'  <g{animation}>'
            f'<text x="26" y="{y}" fill="#79c0ff" '
            f'font-family="monospace" font-size="12">{safe_text(label)}</text>'
            f'{"".join(text_lines)}'
            f'</g>'
        )
        y += max(42, len(wrapped) * 17 + 16)

    content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Profile information for {safe_text(USERNAME)}</title>
  <desc id="desc">A terminal-style card showing UI/UX design, front-end development, focus areas, technology stack, and highlights.</desc>
{style}
  <rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="#0d1117" stroke="#30363d"/>
  <path d="M10 0h620a10 10 0 0 1 10 10v28H0V10A10 10 0 0 1 10 0Z" fill="#161b22"/>
  <circle cx="20" cy="19" r="5" fill="#ff5f56"/>
  <circle cx="38" cy="19" r="5" fill="#ffbd2e"/>
  <circle cx="56" cy="19" r="5" fill="#27c93f"/>
  <text x="76" y="24" fill="#8b949e" font-family="monospace" font-size="12">{safe_text(USERNAME)}@github - profile</text>
  <text x="26" y="82" fill="#39d353" font-family="monospace" font-size="14">{safe_text(USERNAME)}@github</text>
  <text x="26" y="108" fill="#c9d1d9" font-family="monospace" font-size="12">------------------------------------------------</text>
{chr(10).join(lines)}
  <text x="26" y="337" fill="#8b949e" font-family="monospace" font-size="11">UI/UX Design • Front-End Development • Product Thinking</text>
</svg>
"""
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Profile card written to {OUTPUT}{' (static)' if static else ''}")


if __name__ == "__main__":
    main()
