#!/usr/bin/env python3
"""Animated contribution heatmap -> assets/heatmap.svg (standard library only; run daily by .github/workflows/update-profile.yml)."""
import datetime as dt
import os
from xml.sax.saxutils import escape

import ghdata

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "heatmap.svg")
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP, LEFT, TOP = 11, 3, 34, 44
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def build(days):
    first = dt.date.fromisoformat(days[0][0])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)          # grid columns start on Sunday
    cols = ((dt.date.fromisoformat(days[-1][0]) - start).days // 7) + 1
    total = sum(n for _, n, _ in days)
    cur, best = ghdata.streaks(days)
    busiest = max(days, key=lambda d: d[1])
    width, height = LEFT + cols * (CELL + GAP) + 16, TOP + 7 * (CELL + GAP) + 54
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{total} contributions in the last year">',
           '<title>Contribution heatmap</title>',
           f'<rect width="{width}" height="{height}" rx="10" fill="#0d1117" stroke="#30363d"/>',
           f'<text x="16" y="24" font-family="{FONT}" font-size="12" fill="#7ee787">$ git log --since="1 year ago" --stat | heatmap<tspan fill="#7ee787"><animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite"/> ▌</tspan></text>']
    last_month = None
    for i, (date, n, lv) in enumerate(days):
        d = dt.date.fromisoformat(date)
        col, row = (d - start).days // 7, (d.weekday() + 1) % 7
        x, y = LEFT + col * (CELL + GAP), TOP + row * (CELL + GAP)
        if d.day <= 7 and row == 0 or (last_month is None and col == 0):
            if d.month != last_month:
                out.append(f'<text x="{x}" y="{TOP - 8}" font-family="{FONT}" font-size="9" fill="#8b949e">{d.strftime("%b")}</text>')
                last_month = d.month
        begin = round(0.4 + col * 0.03 + row * 0.012, 3)
        tip = f"{n} contribution{'s' if n != 1 else ''} on {d.strftime('%b %d, %Y')}"
        rect = f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{COLORS[lv]}" opacity="0"><title>{escape(tip)}</title><animate attributeName="opacity" from="0" to="1" begin="{begin}s" dur="0.25s" fill="freeze"/>'
        if lv >= 3:
            rect += f'<animate attributeName="fill-opacity" values="1;0.55;1" dur="{2.4 + (col % 5) * 0.3:.1f}s" begin="{begin + 1}s" repeatCount="indefinite"/>'
        out.append(rect + "</rect>")
    for r, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="8" y="{TOP + r * (CELL + GAP) + 9}" font-family="{FONT}" font-size="9" fill="#8b949e">{label}</text>')
    ly = TOP + 7 * (CELL + GAP) + 12
    out.append(f'<text x="{LEFT}" y="{ly + 9}" font-family="{FONT}" font-size="11" fill="#c9d1d9"><tspan fill="#7ee787">{total}</tspan> contributions · current streak <tspan fill="#7ee787">{cur}d</tspan> · longest <tspan fill="#7ee787">{best}d</tspan> · best day <tspan fill="#7ee787">{busiest[1]}</tspan> ({dt.date.fromisoformat(busiest[0]).strftime("%b %d")})</text>')
    lx = width - 16 - 5 * (CELL + 2) - 56
    out.append(f'<text x="{lx - 28}" y="{ly + 9}" font-family="{FONT}" font-size="9" fill="#8b949e">less</text>')
    for k, c in enumerate(COLORS):
        out.append(f'<rect x="{lx + k * (CELL + 2)}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    out.append(f'<text x="{lx + 5 * (CELL + 2) + 4}" y="{ly + 9}" font-family="{FONT}" font-size="9" fill="#8b949e">more</text>')
    out.append(f'<text x="{LEFT}" y="{ly + 28}" font-family="{FONT}" font-size="9" fill="#484f58">updated {ghdata.now_utc():%Y-%m-%d} UTC · refreshed daily by GitHub Actions</text>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    try:
        days = ghdata.contributions()
    except Exception as e:                                                  # keep the previous image if GitHub is unreachable
        print("heatmap not updated:", e)
        raise SystemExit(0)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(build(days))
    print("wrote", os.path.normpath(OUT), f"({len(days)} days)")
