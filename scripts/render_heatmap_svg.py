#!/usr/bin/env python3
"""Render data/contributions.json as an animated GitHub-style contribution calendar."""

from __future__ import annotations

import argparse
import html
import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
WIDTH = 860
CELL = 10
GAP = 3
LEFT = 62
TOP = 32
WEEKS = 53


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    data: dict[str, Any] = json.loads(args.input.read_text(encoding="utf-8"))
    raw_days = data.get("days")
    if not isinstance(raw_days, list) or not raw_days:
        raise ValueError(f"{args.input} does not contain a non-empty 'days' array")

    counts: dict[date, tuple[int, int]] = {}
    for item in raw_days:
        if not isinstance(item, dict):
            raise ValueError("Each contribution day must be a JSON object")
        day_date = date.fromisoformat(str(item["date"]))
        count = int(item["count"])
        level = int(item.get("level", 0))
        if count < 0 or not 0 <= level < len(PALETTE):
            raise ValueError(f"Invalid contribution values for {day_date}")
        counts[day_date] = (count, level)

    start = min(counts)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    range_end = start + timedelta(days=WEEKS * 7 - 1)

    labels: list[str] = []
    cells: list[str] = []
    month_seen: set[tuple[int, int]] = set()
    for day_offset in range(WEEKS * 7):
        day_date = start + timedelta(days=day_offset)
        week, weekday = divmod(day_offset, 7)
        x = LEFT + week * (CELL + GAP)
        y = TOP + weekday * (CELL + GAP)

        if day_date.day <= 7 and (day_date.year, day_date.month) not in month_seen:
            month_seen.add((day_date.year, day_date.month))
            labels.append(
                f'  <text x="{x}" y="19" fill="#8b949e" font-family="sans-serif" font-size="11">{day_date.strftime("%b")}</text>'
            )

        count, level = counts.get(day_date, (0, 0))
        description = (
            f"{count:,} contribution{'s' if count != 1 else ''} on "
            f"{day_date.strftime('%B')} {day_date.day}, {day_date.year}"
            if count
            else f"No contributions on {day_date.strftime('%B')} {day_date.day}, {day_date.year}"
        )
        delay = (week + weekday) * 18
        cells.append(
            f'  <g class="day" style="animation-delay:{delay}ms">'
            f'<title>{html.escape(description)}</title>'
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{PALETTE[level]}"/>'
            f"</g>"
        )

    row_labels = []
    for weekday, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = TOP + weekday * (CELL + GAP) + 9
        row_labels.append(
            f'  <text x="16" y="{y}" fill="#8b949e" font-family="sans-serif" font-size="10">{label}</text>'
        )

    total = int(data.get("total", sum(count for count, _ in counts.values())))
    current = int(data.get("current_streak", 0))
    longest = int(data.get("longest_streak", 0))
    username = html.escape(str(data.get("username", "GitHub")))
    footer_y = TOP + 7 * (CELL + GAP) + 24
    grid_end_x = LEFT + WEEKS * (CELL + GAP) - GAP
    legend_start = grid_end_x - 119
    legend = [
        f'  <text x="{legend_start - 37}" y="{footer_y}" fill="#8b949e" font-family="sans-serif" font-size="10">Less</text>'
    ]
    for level, color in enumerate(PALETTE):
        x = legend_start + level * (CELL + GAP)
        legend.append(
            f'  <rect x="{x}" y="{footer_y - 9}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>'
        )
    legend.append(
        f'  <text x="{legend_start + len(PALETTE) * (CELL + GAP) + 1}" y="{footer_y}" fill="#8b949e" font-family="sans-serif" font-size="10">More</text>'
    )

    content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="190" viewBox="0 0 {WIDTH} 190" role="img" aria-labelledby="title desc">
  <title id="title">{username}'s GitHub contribution calendar</title>
  <desc id="desc">{total:,} contributions in the displayed year. Current streak: {current} days. Longest streak: {longest} days.</desc>
  <style>
    @keyframes reveal {{
      from {{ opacity: 0; transform: translateY(-5px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .day {{ opacity: 0; animation: reveal 0.35s ease-out both; }}
  </style>
  <rect width="{WIDTH}" height="190" rx="10" fill="#0d1117" stroke="#30363d"/>
{chr(10).join(labels)}
{chr(10).join(row_labels)}
{chr(10).join(cells)}
  <text x="16" y="{footer_y + 23}" fill="#c9d1d9" font-family="monospace" font-size="11">{total:,} contributions | streak {current}d | best {longest}d | {username}</text>
{chr(10).join(legend)}
</svg>
"""
    args.output.write_text(content, encoding="utf-8")
    print(f"Contribution graph written to {args.output} ({start} through {range_end})")


if __name__ == "__main__":
    main()
