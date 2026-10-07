"""Render a neofetch-style profile card with live GitHub stats.

Runs daily in .github/workflows/main.yml and is published to the `output` branch:

    GITHUB_TOKEN=... python3 scripts/neofetch.py dist

Without a token (or if the API call fails) the stats fall back to FALLBACK_STATS,
which keeps local previews working.
"""

import json
import math
import os
import random
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

LOGIN = "satriadhikara"
JOINED = date(2021, 5, 12)

# Edit me. (key, value) pairs; None renders a blank line, a str renders a section header.
INFO = [
    ("Role", "Software Engineer"),
    ("Work", "Grab · KartaView"),
    ("Uni", "Informatics @ ITB (STEI)"),
    ("Host", "West Java, Indonesia"),
    ("Uptime", "{uptime}"),
    None,
    ("Languages.Code", "TypeScript, Rust, Go, Python, Zig"),
    ("Stack.Web", "Next.js, React, Hono, Bun, tRPC"),
    ("Stack.Mobile", "React Native, Expo"),
    ("Stack.Infra", "PostgreSQL, S3/MinIO, Docker"),
    ("Interests", "distributed systems, dev tooling, maps"),
    ("Now", "kolumba: JMAP-native webmail"),
    None,
    "Contact",
    ("Web", "satriadhikara.com"),
    ("Email", "hello@satriadhikara.com"),
    ("LinkedIn", "in/satriadhikara"),
    None,
    "GitHub Stats",
    ("Repos", "{repos}", "Stars", "{stars}"),
    ("Commits (1y)", "{commits}", "Followers", "{followers}"),
    ("Contributions (1y)", "{contributions}"),
]

FALLBACK_STATS = {"repos": 48, "stars": 4, "followers": 41, "commits": "—", "contributions": "—"}

THEMES = {
    "dark": {
        "bg": "#0b0f14", "border": "#1f2933", "text": "#e6edf3", "muted": "#3d4752",
        "key": "#ffa657", "value": "#a5d6ff", "accent": "#7ee787", "user": "#7ee787",
        "ramp": ["#1f6f3f", "#2ea043", "#56d364", "#7ee787", "#d29922", "#ffa657", "#ff7b72"],
        "palette": ["#484f58", "#ff7b72", "#7ee787", "#d29922", "#79c0ff", "#d2a8ff", "#56d4dd", "#e6edf3"],
    },
    "light": {
        "bg": "#fbfaf7", "border": "#d8dee4", "text": "#1f2328", "muted": "#c5ccd3",
        "key": "#bc4c00", "value": "#0550ae", "accent": "#1a7f37", "user": "#1a7f37",
        "ramp": ["#6fbf86", "#4ac26b", "#2da44e", "#1a7f37", "#bf8700", "#bc4c00", "#cf222e"],
        "palette": ["#24292f", "#cf222e", "#1a7f37", "#9a6700", "#0969da", "#8250df", "#1b7c83", "#6e7781"],
    },
}

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
SIZE, LINE = 14, 21
CHAR = SIZE * 0.6
ART_COLS, INFO_COLS = 40, 60
PAD = 28


def fetch_stats(token):
    query = """
    query($login: String!, $after: String) {
      user(login: $login) {
        followers { totalCount }
        repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100, after: $after) {
          totalCount
          pageInfo { hasNextPage endCursor }
          nodes { stargazerCount }
        }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
          contributionCalendar { totalContributions }
        }
      }
    }"""
    stars, after = 0, None
    while True:
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": query, "variables": {"login": LOGIN, "after": after}}).encode(),
            headers={"Authorization": f"bearer {token}", "User-Agent": LOGIN},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.load(resp)
        if "errors" in body:
            raise RuntimeError(body["errors"])
        user = body["data"]["user"]
        repos = user["repositories"]
        stars += sum(n["stargazerCount"] for n in repos["nodes"])
        if not repos["pageInfo"]["hasNextPage"]:
            break
        after = repos["pageInfo"]["endCursor"]
    cc = user["contributionsCollection"]
    return {
        "repos": repos["totalCount"],
        "stars": stars,
        "followers": user["followers"]["totalCount"],
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "contributions": cc["contributionCalendar"]["totalContributions"],
    }


def uptime(today):
    months = (today.year - JOINED.year) * 12 + today.month - JOINED.month
    if today.day < JOINED.day:
        months -= 1
    anchor_y, anchor_m = divmod(JOINED.month - 1 + months, 12)
    days = (today - date(JOINED.year + anchor_y, anchor_m + 1, JOINED.day)).days
    years, months = divmod(months, 12)
    plural = lambda n, unit: f"{n} {unit}{'' if n == 1 else 's'}"
    return ", ".join((plural(years, "year"), plural(months, "month"), plural(days, "day")))


def heightmap(rows):
    """ASCII topo map of Tangkuban Perahu, same shape as the banner.

    Returns rows of (char, band) where band indexes the colour ramp, or None for blank.
    """
    rng = random.Random(1945)
    phases = [(k, 0.09 / k ** 0.7, rng.uniform(0, 2 * math.pi)) for k in (2, 3, 5, 7)]
    glyphs = ".:-=+*#"
    bands = 8
    out = []
    for r in range(rows):
        line = []
        for col in range(ART_COLS):
            # Terminal cells are ~2:1, so stretch x to keep the mountain's proportions.
            x = (col - ART_COLS / 2 + 0.5) / (ART_COLS / 2)
            y = (r - rows / 2 + 0.5) / (rows / 2) * 1.05
            a = math.atan2(y * 0.45, x)
            wobble = 1 + sum(amp * math.sin(k * a + ph) for k, amp, ph in phases)
            d = math.hypot(x / 0.97, y / 0.8) / wobble
            h = 1 - d
            if h <= 0:
                line.append(None)
                continue
            if d < 0.09:
                line.append(("o" if d < 0.05 else "~", len(glyphs) - 1))
                continue
            level = h * bands
            if level - int(level) > 0.38:
                line.append(None)
                continue
            band = min(len(glyphs) - 1, int(h * len(glyphs)))
            line.append((glyphs[band], band))
        out.append(line)
    return out


def info_lines(stats, today):
    fields = {**{k: f"{v:,}" if isinstance(v, int) else v for k, v in stats.items()}, "uptime": uptime(today)}
    lines = [[("user", f"{LOGIN}"), ("muted", "@"), ("user", "github")], [("muted", "─" * INFO_COLS)]]
    for item in INFO:
        if item is None:
            lines.append([])
        elif isinstance(item, str):
            lines.append([("accent", "- "), ("text", item), ("muted", " " + "─" * (INFO_COLS - len(item) - 3))])
        elif len(item) == 2:
            key, value = item[0], item[1].format(**fields)
            dots = INFO_COLS - len(key) - len(value) - 4
            lines.append([("accent", ". "), ("key", key), ("muted", ":" + " " + "." * dots + " "), ("value", value)])
        else:
            k1, v1, k2, v2 = item[0], item[1].format(**fields), item[2], item[3].format(**fields)
            half = INFO_COLS // 2 + 6
            dots1 = half - len(k1) - len(v1) - 4
            dots2 = INFO_COLS - half - len(k2) - len(v2) - 6
            lines.append([
                ("accent", ". "), ("key", k1), ("muted", ": " + "." * dots1 + " "), ("value", v1),
                ("muted", " | "), ("key", k2), ("muted", ": " + "." * dots2 + " "), ("value", v2),
            ])
    return lines


def render(theme, stats, today):
    c = THEMES[theme]
    info = info_lines(stats, today)
    rows = len(info) + 2  # + blank + palette row
    art = heightmap(rows)
    width = round(PAD * 2 + (ART_COLS + 3 + INFO_COLS) * CHAR)
    height = PAD * 2 + rows * LINE
    info_x = PAD + (ART_COLS + 3) * CHAR

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{LOGIN} neofetch">',
        f"<style>text{{font-family:{FONT};font-size:{SIZE}px;white-space:pre}}"
        ".l{opacity:0;animation:in .35s ease-out forwards}@keyframes in{to{opacity:1}}"
        "@media (prefers-reduced-motion:reduce){.l{animation:none;opacity:1}}</style>",
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="{c["bg"]}" stroke="{c["border"]}"/>',
    ]

    for r, line in enumerate(art):
        y = PAD + (r + 1) * LINE - 6
        spans, run, run_band = [], "", None
        for cell in line + [None]:
            ch, band = cell if cell else (" ", None)
            if band != run_band and run:
                spans.append((run, run_band))
                run = ""
            run, run_band = run + ch, band
        tspans = "".join(
            escape(text) if band is None else f'<tspan fill="{c["ramp"][band]}">{escape(text)}</tspan>'
            for text, band in spans
        )
        out.append(
            f'<text class="l" x="{PAD}" y="{y}" xml:space="preserve" style="animation-delay:{r * 0.03:.2f}s">{tspans}</text>'
        )

    for r, parts in enumerate(info):
        y = PAD + (r + 1) * LINE - 6
        tspans = "".join(f'<tspan fill="{c[cls]}">{escape(text)}</tspan>' for cls, text in parts)
        out.append(
            f'<text class="l" x="{info_x:.1f}" y="{y}" xml:space="preserve" '
            f'style="animation-delay:{0.3 + r * 0.045:.2f}s">{tspans}</text>'
        )

    y = PAD + (len(info) + 1) * LINE - 18
    for i, color in enumerate(c["palette"]):
        out.append(
            f'<rect class="l" x="{info_x + i * 3 * CHAR:.1f}" y="{y}" width="{3 * CHAR:.1f}" height="16" '
            f'fill="{color}" style="animation-delay:{0.3 + len(info) * 0.045 + i * 0.04:.2f}s"/>'
        )

    out.append("</svg>")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    out_dir.mkdir(parents=True, exist_ok=True)
    stats = dict(FALLBACK_STATS)
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            stats = fetch_stats(token)
        except Exception as exc:  # stale numbers beat a broken card
            print(f"stats fetch failed, using fallback: {exc}", file=sys.stderr)
    today = datetime.now(timezone.utc).date()
    for theme in THEMES:
        path = out_dir / f"neofetch-{theme}.svg"
        path.write_text(render(theme, stats, today), encoding="utf-8")
        print(f"wrote {path}")
