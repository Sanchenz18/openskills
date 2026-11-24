#!/usr/bin/env python3
"""Render a WaveJSON source to SVG (and optionally PNG) with the Python
wavedrom engine.

Usage:
  python3 render.py <source.json> --svg <out.svg> [--png <out.png>] [--scale 2]

Exit codes: 0 ok, 2 missing dependency (prints the setup commands), 1 failure.
"""

import argparse
import sys


def main():
    ap = argparse.ArgumentParser(description="Render WaveDrom to SVG/PNG")
    ap.add_argument("source")
    ap.add_argument("--svg", required=True)
    ap.add_argument("--png")
    ap.add_argument("--scale", type=float, default=2.0)
    args = ap.parse_args()

    try:
        import wavedrom
    except ImportError:
        print(
            "Missing package 'wavedrom'. Set up the environment once:\n"
            "  python3 -m venv ~/.cache/wavedrom-draw/venv\n"
            "  ~/.cache/wavedrom-draw/venv/bin/pip install wavedrom cairosvg\n"
            "then call this script with ~/.cache/wavedrom-draw/venv/bin/python."
        )
        return 2

    src = open(args.source, encoding="utf-8").read()
    try:
        drawing = wavedrom.render(src)
        drawing.saveas(args.svg)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: render failed: {e}")
        return 1
    print(f"SVG written: {args.svg}")

    if args.png:
        try:
            import cairosvg
        except ImportError:
            print(
                "Missing package 'cairosvg' for PNG output; see the setup "
                "commands above. SVG is still written."
            )
            return 2
        cairosvg.svg2png(url=args.svg, write_to=args.png, scale=args.scale)
        print(f"PNG written: {args.png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
