#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar without an access token."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

USERNAME = "sehdie"
OUTPUT = Path("data/contributions.json")
CONTRIBUTIONS_URL = "https://github.com/users/{username}/contributions"
USER_AGENT = "profile-readme-contribution-calendar/1.0"


def parse_count(cell: object, soup: BeautifulSoup) -> int:
    attrs = getattr(cell, "attrs", {})
    raw_count = attrs.get("data-count")
    if raw_count is not None:
        try:
            count = int(raw_count)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid contribution count: {raw_count!r}") from exc
        if count < 0:
            raise ValueError(f"Contribution count cannot be negative: {count}")
        return count

    tooltip = soup.find("tool-tip", attrs={"for": attrs.get("id")})
    label = attrs.get("aria-label", "")
    if tooltip is not None:
        label = tooltip.get_text(" ", strip=True)
    if not label:
        label = getattr(cell, "get_text")(" ", strip=True)
    match = re.search(r"([\d,]+)\s+contributions?", str(label), re.IGNORECASE)
    if match:
        return int(match.group(1).replace(",", ""))
    if "no contributions" in str(label).lower():
        return 0
    raise ValueError(f"Missing contribution count on calendar cell: {attrs!r}")


def longest_streak(days: list[dict[str, object]]) -> int:
    best = current = 0
    previous: date | None = None
    for day in days:
        day_date = date.fromisoformat(str(day["date"]))
        if int(day["count"]) > 0:
            current = current + 1 if previous == day_date - timedelta(days=1) else 1
            best = max(best, current)
            previous = day_date
        else:
            current = 0
            previous = day_date
    return best


def current_streak(days: list[dict[str, object]], today: date) -> int:
    counts = {date.fromisoformat(str(day["date"])): int(day["count"]) for day in days}
    anchor = today if counts.get(today, 0) > 0 else today - timedelta(days=1)
    streak = 0
    cursor = anchor
    while counts.get(cursor, 0) > 0:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default=USERNAME, help="GitHub username (default: sehdie)")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", args.username):
        parser.error("username must contain only letters, digits, or hyphens")

    url = CONTRIBUTIONS_URL.format(username=quote(args.username, safe=""))
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
        timeout=30,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("[data-date][data-level]")
    if not cells:
        raise RuntimeError(f"No contribution calendar cells found at {url}")

    days: list[dict[str, object]] = []
    for cell in cells:
        raw_date = cell.get("data-date")
        if not isinstance(raw_date, str):
            continue
        try:
            day_date = date.fromisoformat(raw_date)
            count = parse_count(cell, soup)
            level = int(str(cell.get("data-level", "0")))
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Could not parse contribution cell for {raw_date!r}") from exc
        if not 0 <= level <= 5:
            raise ValueError(f"Unexpected contribution level {level} for {raw_date}")
        days.append({"date": day_date.isoformat(), "count": count, "level": level})

    days.sort(key=lambda day: str(day["date"]))
    if len({day["date"] for day in days}) != len(days):
        raise ValueError("GitHub returned duplicate contribution dates")

    monthly: defaultdict[str, int] = defaultdict(int)
    for day in days:
        monthly[str(day["date"])[:7]] += int(day["count"])

    best_day = max(days, key=lambda day: int(day["count"]), default=None)
    today = datetime.now(timezone.utc).date()
    payload = {
        "username": args.username,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "range_start": days[0]["date"],
        "range_end": days[-1]["date"],
        "total": sum(int(day["count"]) for day in days),
        "current_streak": current_streak(days, today),
        "longest_streak": longest_streak(days),
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly.items())),
        "days": days,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Fetched {len(days)} contribution days for {args.username} into {args.output}")


if __name__ == "__main__":
    main()
