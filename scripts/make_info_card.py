#!/usr/bin/env python3
"""Render the profile's neofetch-style information panel."""

from __future__ import annotations

import html
import os
from pathlib import Path

USERNAME = "sehdie"
ROWS = [
    ("Role", "Your role goes here"),
    ("Focus", "What you are building"),
    ("Stack", "Your tools and languages"),
    ("Highlights", "Your work or interests"),
]
OUTPUT = Path("info-card.svg")
WIDTH = 490
HEIGHT = 360


def safe_text(value: str, limit: int = 43) -> str:
    return html.escape(value[:limit])


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    title_animation = "" if static else "animation: print-in 0.45s ease-out both;"
    style = "" if static else """  <style>
    @keyframes print-in {
      from { opacity: 0; transform: translateY(5px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .line { animation: print-in 0.45s ease-out both; }
  </style>"""

    lines = []
    for index, (label, value) in enumerate(ROWS):
        y = 144 + index * 32
        animation = (
            f' class="line" style="animation-delay:{index * 120}ms"'
            if not static
            else ""
        )
        lines.append(
            f'  <g{animation}><text x="26" y="{y}" fill="#79c0ff" font-family="monospace" font-size="12">{safe_text(label, 16)}</text>'
            f'<text x="142" y="{y}" fill="#c9d1d9" font-family="monospace" font-size="12">{safe_text(value)}</text></g>'
        )

    content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">Profile information for {safe_text(USERNAME)}</title>
  <desc id="desc">A terminal-style card with profile role, focus, stack, and highlights.</desc>
{style}
  <rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="#0d1117" stroke="#30363d"/>
  <path d="M10 0h470a10 10 0 0 1 10 10v28H0V10A10 10 0 0 1 10 0Z" fill="#161b22"/>
  <circle cx="20" cy="19" r="5" fill="#ff5f56"/>
  <circle cx="38" cy="19" r="5" fill="#ffbd2e"/>
  <circle cx="56" cy="19" r="5" fill="#27c93f"/>
  <text x="76" y="24" fill="#8b949e" font-family="monospace" font-size="12">{safe_text(USERNAME)}@github - profile</text>
  <text x="26" y="82" fill="#39d353" font-family="monospace" font-size="14">{safe_text(USERNAME)}@github</text>
  <text x="26" y="108" fill="#c9d1d9" font-family="monospace" font-size="12">------------------------------</text>
{chr(10).join(lines)}
  <text x="26" y="300" fill="#8b949e" font-family="monospace" font-size="11">Edit scripts/make_info_card.py to personalize this card.</text>
</svg>
"""
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Profile card written to {OUTPUT}{' (static)' if static else ''}")


if __name__ == "__main__":
    main()
