#!/usr/bin/env python3
"""Reproduce the fictional ring-toss example using Python's standard library.

Run from any working directory:
    python path/to/blog1/code/reproduce.py

Optional paths:
    python reproduce.py --data ../data/ring_toss.csv --output ../results

Optional PNG export (requires Pillow, install with: python -m pip install Pillow):
    python reproduce.py --png

Python 3.9+; no third-party packages are required. All input counts are fictional
teaching data, not observations of real people or an episode of The Simpsons.
The equal-mix calculation reweights observed rates; it is not a causal estimate
or a forecast of future attempts.
"""

import argparse
import csv
from fractions import Fraction
from html import escape
import json
import os
from pathlib import Path
from xml.etree import ElementTree


PLAYERS = ("Lisa", "Bart")
DISTANCES = ("Near/easier", "Far/harder")
BASE = Path(__file__).resolve().parents[1]


def read_counts(path):
    """Read and validate a complete two-player, two-distance count table."""
    counts = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        expected_fields = {"player", "distance", "successes", "attempts"}
        if set(reader.fieldnames or []) != expected_fields:
            raise ValueError("CSV must contain player,distance,successes,attempts.")
        for row in reader:
            player, distance = row["player"], row["distance"]
            if player not in PLAYERS or distance not in DISTANCES:
                raise ValueError(f"Unrecognized player or distance: {row}")
            key = (player, distance)
            if key in counts:
                raise ValueError(f"Duplicate row: {key}")
            successes, attempts = int(row["successes"]), int(row["attempts"])
            if attempts <= 0 or not 0 <= successes <= attempts:
                raise ValueError(f"Invalid counts: {row}")
            counts[key] = (successes, attempts)
    expected_keys = {(p, d) for p in PLAYERS for d in DISTANCES}
    if set(counts) != expected_keys:
        raise ValueError("CSV must contain one row for each player and distance.")
    return counts


def record(successes, attempts):
    return {
        "successes": successes,
        "attempts": attempts,
        "success_rate_percent": float(100 * Fraction(successes, attempts)),
    }


def summarize(counts):
    rows = []
    for distance in DISTANCES:
        rows.append({
            "distance": distance,
            **{p: record(*counts[p, distance]) for p in PLAYERS},
        })
    overall = {}
    for player in PLAYERS:
        successes = sum(counts[player, d][0] for d in DISTANCES)
        attempts = sum(counts[player, d][1] for d in DISTANCES)
        overall[player] = record(successes, attempts)
    rows.append({"distance": "Overall", **overall})
    equal_mix = {
        player: float(100 * sum(
            (Fraction(*counts[player, d]) for d in DISTANCES), Fraction(0)
        ) / len(DISTANCES))
        for player in PLAYERS
    }
    return rows, equal_mix


def format_percent(value):
    return f"{value:g}%"


def write_summary(rows, equal_mix, out):
    fields = ["distance"]
    for player in PLAYERS:
        fields.extend(f"{player}_{key}" for key in (
            "successes", "attempts", "success_rate_percent"
        ))
    with (out / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            flat = {"distance": row["distance"]}
            for player in PLAYERS:
                flat.update({f"{player}_{k}": v for k, v in row[player].items()})
            writer.writerow(flat)

    summary = {
        "data_origin": "Fictional teaching example; counts supplied in ring_toss.csv.",
        "rate_unit": "percent",
        "by_distance": rows[:-1],
        "overall": {p: rows[-1][p] for p in PLAYERS},
        "equal_mix_standardized_percent": equal_mix,
        "standardization_weights": {d: 0.5 for d in DISTANCES},
        "interpretation": (
            "Equal-mix rates hold each observed distance-specific rate fixed and "
            "use the same 50:50 distance weights for both players. These are "
            "descriptive calculations, not causal effects or future predictions."
        ),
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    lines = [
        "| Distance | Lisa: successes / attempts (rate) | Bart: successes / attempts (rate) |",
        "|:--|--:|--:|",
    ]
    for row in rows:
        cells = []
        for player in PLAYERS:
            r = row[player]
            cells.append(
                f"{r['successes']} / {r['attempts']} "
                f"({format_percent(r['success_rate_percent'])})"
            )
        lines.append(f"| {row['distance']} | {' | '.join(cells)} |")
    lines.extend([
        "",
        "*Fictional teaching data. Overall rates use total successes divided by "
        "total attempts, rather than an unweighted mean of the two rates.*",
        "",
        "Using a shared 50:50 mix of near and far attempts: " + ", ".join(
            f"{p} {format_percent(equal_mix[p])}" for p in PLAYERS
        ) + ". These standardized rates hold the observed group rates fixed; "
        "they are not causal estimates or predictions.",
        "",
    ])
    (out / "table.md").write_text("\n".join(lines), encoding="utf-8")


def write_svg(rows, out):
    """Draw a portable, accessible vector chart without plotting dependencies."""
    width, height = 980, 600
    left, right, top, bottom = 90, 936, 156, 448
    plot_height = bottom - top
    colors = {"Lisa": "#147D80", "Bart": "#C66149"}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Lisa leads at both distances. Bart leads overall.</title>',
        '<desc id="desc">Fictional ring-toss success rates: near attempts, Lisa 90 percent '
        'and Bart 80 percent; far attempts, Lisa 60 percent and Bart 50 percent; '
        'overall, Lisa 63 percent and Bart 77 percent. The aggregate reverses because '
        'the players attempted different mixes of distances.</desc>',
        '<rect width="980" height="600" rx="18" fill="#FCFAF5"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#263B3C">',
        '<text x="38" y="47" font-size="28" font-weight="700">'
        'Two leads. One surprising total.</text>',
        '<text x="38" y="78" font-size="17" fill="#536566">'
        'Success rates by distance and across each player\u2019s actual attempts</text>',
    ]
    for i, player in enumerate(PLAYERS):
        x = 39 + i * 108
        parts.append(f'<rect x="{x}" y="102" width="15" height="15" rx="3" '
                     f'fill="{colors[player]}"/>')
        parts.append(f'<text x="{x + 23}" y="115" font-size="16">{player}</text>')
    parts.append('<text x="36" y="147" font-size="13" fill="#536566">Success</text>')
    for percent in range(0, 101, 20):
        y = bottom - percent / 100 * plot_height
        parts.append(f'<line x1="{left}" x2="{right}" y1="{y:.1f}" y2="{y:.1f}" '
                     'stroke="#DCDDD4" stroke-width="1"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" '
                     f'font-size="14" fill="#637172">{percent}%</text>')
    centers = (228, 511, 794)
    bar_width = 69
    for row, center in zip(rows, centers):
        for index, player in enumerate(PLAYERS):
            r = row[player]
            percent = r["success_rate_percent"]
            x = center - bar_width - 7 if index == 0 else center + 7
            y = bottom - percent / 100 * plot_height
            parts.append(f'<rect x="{x}" y="{y:.2f}" width="{bar_width}" '
                         f'height="{bottom - y:.2f}" rx="4" fill="{colors[player]}"/>')
            parts.append(f'<text x="{x + bar_width / 2}" y="{y - 11:.2f}" '
                         'text-anchor="middle" font-size="21" font-weight="700" '
                         f'fill="{colors[player]}">{format_percent(percent)}</text>')
            parts.append(f'<text x="{x + bar_width / 2}" y="469" text-anchor="middle" '
                         f'font-size="13" fill="#536566">{r["successes"]}/{r["attempts"]}</text>')
        label = row["distance"].replace("/", " / ")
        parts.append(f'<text x="{center}" y="499" text-anchor="middle" '
                     f'font-size="18" font-weight="700">{escape(label)}</text>')
    parts.extend([
        '<text x="38" y="550" font-size="16">Lisa takes 90% of her attempts from far away; '
        'Bart takes 90% from nearby.</text>',
        '<text x="38" y="578" font-size="13" fill="#637172">'
        'Fictional illustration. Labels below bars show successes / attempts. '
        'All axes start at zero.</text>',
        '</g></svg>',
    ])
    (out / "success-rates.svg").write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_png(out):
    """Rasterize the chart's simple shapes at 2x resolution using optional Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise SystemExit("PNG export requires Pillow: python -m pip install Pillow") from exc

    root = ElementTree.parse(out / "success-rates.svg").getroot()
    scale = 2
    canvas = Image.new("RGB", (980 * scale, 600 * scale), "#FCFAF5")
    draw = ImageDraw.Draw(canvas)
    windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    font_cache = {}

    def font_for(size, bold):
        key = (size, bold)
        if key not in font_cache:
            names = (
                str(windows_fonts / ("arialbd.ttf" if bold else "arial.ttf")),
                "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
            )
            for name in names:
                try:
                    font_cache[key] = ImageFont.truetype(name, int(size * scale))
                    break
                except OSError:
                    continue
            else:
                font_cache[key] = ImageFont.load_default(size=int(size * scale))
        return font_cache[key]

    for item in root.iter():
        tag = item.tag.rsplit("}", 1)[-1]
        a = item.attrib
        if tag == "rect":
            x, y = float(a.get("x", 0)), float(a.get("y", 0))
            w, h = float(a["width"]), float(a["height"])
            draw.rounded_rectangle(
                (x * scale, y * scale, (x + w) * scale, (y + h) * scale),
                radius=float(a.get("rx", 0)) * scale, fill=a["fill"],
            )
        elif tag == "line":
            points = tuple(float(a[k]) * scale for k in ("x1", "y1", "x2", "y2"))
            draw.line(points, fill=a["stroke"], width=scale)
        elif tag == "text":
            anchor = {"middle": "ms", "end": "rs"}.get(a.get("text-anchor"), "ls")
            draw.text(
                (float(a["x"]) * scale, float(a["y"]) * scale),
                item.text or "", font=font_for(float(a["font-size"]), a.get("font-weight") == "700"),
                fill=a.get("fill", "#263B3C"), anchor=anchor,
            )
    canvas.save(out / "success-rates.png", optimize=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=BASE / "data" / "ring_toss.csv")
    parser.add_argument("--output", type=Path, default=BASE / "results")
    parser.add_argument("--png", action="store_true", help="Also export a PNG chart (requires Pillow).")
    args = parser.parse_args()
    counts = read_counts(args.data)
    rows, equal_mix = summarize(counts)
    args.output.mkdir(parents=True, exist_ok=True)
    write_summary(rows, equal_mix, args.output)
    write_svg(rows, args.output)
    if args.png:
        write_png(args.output)
    for player in PLAYERS:
        print(f"{player}: overall {format_percent(rows[-1][player]['success_rate_percent'])}; "
              f"shared 50:50 mix {format_percent(equal_mix[player])}")
    print(f"Wrote summary.csv, summary.json, table.md, success-rates.svg to {args.output}")
    if args.png:
        print("Also wrote success-rates.png (2x resolution).")


if __name__ == "__main__":
    main()
