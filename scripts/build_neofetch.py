#!/usr/bin/env python3
"""neofetch-style info card -> assets/neofetch.svg (standard library only; refreshed daily). Edit PROFILE below to change the text."""
import datetime as dt
import os
from xml.sax.saxutils import escape

import ghdata

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "neofetch.svg")
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
# ---- edit these -----------------------------------------------------------------------------------------------------------------------
PROFILE = {
    "Name": "Kasidit Nunkong",
    "Role": "Junior Full Stack Developer",
    "Stack": "Vue · TypeScript · JavaScript · Node.js",
    "Focus": "web apps · real-time features · APIs",
    "Currently": "learning in public, one project at a time",
}
# ---------------------------------------------------------------------------------------------------------------------------------------
BAR = 14


def build():
    me = ghdata.profile()
    langs = ghdata.repo_languages()
    try:
        days = ghdata.contributions()
        contrib, (cur, best) = sum(n for _, n, _ in days), ghdata.streaks(days)
    except Exception:
        contrib, cur, best = None, 0, 0
    joined = dt.datetime.fromisoformat(me["created_at"].replace("Z", "+00:00"))
    up = (ghdata.now_utc() - joined).days
    lines = [("title", f'{ghdata.USER}@github'), ("rule", "-" * (len(ghdata.USER) + 7))]
    lines += [("kv", k, v) for k, v in PROFILE.items()]
    lines.append(("kv", "Uptime", f"{up // 365}y {up % 365 // 30}m since {joined:%Y-%m-%d}"))
    lines.append(("kv", "Repos", f'{me["public_repos"]} public · {me["followers"]} followers'))
    if contrib is not None:
        lines.append(("kv", "Commits", f"{contrib} in the last year · streak {cur}d (best {best}d)"))
    lines.append(("gap",))
    total = sum(langs.values()) or 1
    for name, n in list(langs.items())[:4]:
        filled = max(1, round(BAR * n / total))
        lines.append(("bar", name, filled, f"{round(100 * n / total)}%"))
    lines.append(("gap",))
    lines.append(("palette",))
    w, lh, top = 520, 20, 44
    h = top + len(lines) * lh + 22
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="neofetch style profile card">',
           '<title>Profile</title>',
           f'<rect width="{w}" height="{h}" rx="10" fill="#0d1117" stroke="#30363d"/>',
           f'<text x="16" y="24" font-family="{FONT}" font-size="12" fill="#7ee787">$ neofetch</text>']
    pal = ["#f85149", "#d29922", "#3fb950", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9", "#8b949e"]
    for i, ln in enumerate(lines):
        y, d = top + i * lh + 12, f"{0.5 + i * 0.12:.2f}s"
        reveal = f'opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{d}" dur="0.12s" fill="freeze"/>'
        kind = ln[0]
        if kind == "title":
            out.append(f'<text x="16" y="{y}" font-family="{FONT}" font-size="13" font-weight="bold" fill="#7ee787" {reveal}{escape(ln[1])}</text>')
        elif kind == "rule":
            out.append(f'<text x="16" y="{y}" font-family="{FONT}" font-size="13" fill="#484f58" {reveal}{ln[1]}</text>')
        elif kind == "kv":
            out.append(f'<text x="16" y="{y}" font-family="{FONT}" font-size="13" {reveal}<tspan fill="#58a6ff" font-weight="bold">{escape(ln[1])}</tspan><tspan fill="#8b949e">:</tspan> <tspan fill="#c9d1d9" x="104">{escape(ln[2])}</tspan></text>')
        elif kind == "bar":
            out.append(f'<text x="16" y="{y}" font-family="{FONT}" font-size="13" {reveal}<tspan fill="#d29922" font-weight="bold">{escape(ln[1])}</tspan><tspan x="104" fill="#3fb950">{"█" * ln[2]}</tspan><tspan fill="#30363d">{"█" * (BAR - ln[2])}</tspan><tspan fill="#8b949e"> {ln[3]}</tspan></text>')
        elif kind == "palette":
            out.append(f'<g {reveal}' + "".join(f'<rect x="{16 + k * 26}" y="{y - 11}" width="24" height="14" fill="{c}"/>' for k, c in enumerate(pal)) + "</g>")
    out.append(f'<text x="{w - 16}" y="{h - 8}" text-anchor="end" font-family="{FONT}" font-size="9" fill="#484f58">updated {ghdata.now_utc():%Y-%m-%d} UTC</text>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    try:
        svg = build()
    except Exception as e:                                                  # keep the previous card if GitHub is unreachable
        print("neofetch card not updated:", e)
        raise SystemExit(0)
    open(OUT, "w", encoding="utf-8").write(svg)
    print("wrote", os.path.normpath(OUT))
