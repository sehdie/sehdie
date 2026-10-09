#!/usr/bin/env python3
"""Remove a portrait's background and prepare a high-contrast grayscale image."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("photo", type=Path, help="Input portrait photo")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("source-prepped.png"),
        help="Output grayscale PNG (default: source-prepped.png)",
    )
    args = parser.parse_args()

    with Image.open(args.photo) as source:
        subject = remove(source.convert("RGBA")).convert("RGBA")

    white = Image.new("RGBA", subject.size, (255, 255, 255, 255))
    white.alpha_composite(subject)
    grayscale = np.asarray(white.convert("L"))
    enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(grayscale)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(enhanced, mode="L").save(args.output)
    print(f"Prepared portrait written to {args.output}")


if __name__ == "__main__":
    main()
