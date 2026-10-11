"""Public GitHub data for the profile README — standard library only, no token needed (the contributions page and REST API are public)."""
import datetime as dt
import html
import json
import re
import urllib.request

USER = "kasidit001"
UA = {"User-Agent": f"{USER}-profile-readme"}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read().decode("utf-8")


def profile():
    return json.loads(get(f"https://api.github.com/users/{USER}"))


def repo_languages():
    """Language -> number of public (non-fork) repos using it as primary language."""
    repos = json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner"))
    out = {}
    for r in repos:
        if r.get("fork") or not r.get("language"):
            continue
        out[r["language"]] = out.get(r["language"], 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def contributions():
    """[(date, count, level)] for the last year, oldest first, from the public contribution graph markup."""
    page = get(f"https://github.com/users/{USER}/contributions")
    cells = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"\s+id="(contribution-day-component-\d+-\d+)"[^>]*data-level="(\d)"', page)
    counts = {}
    for cid, text in re.findall(r'for="(contribution-day-component-\d+-\d+)"[^>]*>\s*([^<]*)<', page):
        m = re.match(r"(\d[\d,]*) contribution", html.unescape(text).strip())
        counts[cid] = int(m.group(1).replace(",", "")) if m else 0
    days = sorted((d, counts.get(cid, 0), int(lv)) for d, cid, lv in cells)
    if not days:
        raise RuntimeError("no contribution cells found (GitHub markup changed?)")
    return days


def streaks(days):
    """(current streak, longest streak) in days with at least one contribution. The current streak may end today or yesterday."""
    best = run = 0
    for _, n, _ in days:
        run = run + 1 if n else 0
        best = max(best, run)
    counts = [n for _, n, _ in days]
    if counts and counts[-1] == 0:          # today has no contribution yet: the streak can still be alive through yesterday
        counts = counts[:-1]
    cur = 0
    for n in reversed(counts):
        if not n:
            break
        cur += 1
    return cur, best


def now_utc():
    return dt.datetime.now(dt.timezone.utc)
