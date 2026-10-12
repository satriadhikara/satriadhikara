"""Render a neofetch-style profile card with live GitHub stats.

Runs daily in .github/workflows/main.yml and is published to the `output` branch:

    GITHUB_TOKEN=... python3 scripts/neofetch.py dist

Without a token (or if the API call fails) the stats fall back to FALLBACK_STATS,
which keeps local previews working.
"""

import json
import math
import os
import sys
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

LOGIN = "satriadhikara"
JOINED = date(2021, 5, 12)

# Edit me. (key, value) pairs; None renders a blank line, a str renders a section header.
INFO = [
    ("Role", "Software Engineer Intern, Fullstack"),
    ("Work", "Grab"),
    ("Uni", "Informatics Eng. @ ITB, class of 2026"),
    ("Host", "Jakarta, Indonesia"),
    ("Uptime", "{uptime}"),
    None,
    ("Languages.Code", "Go, TypeScript, Python, SQL, C"),
    ("Stack.Backend", "gRPC, Kratos, Hono, FastAPI"),
    ("Stack.Data", "PostgreSQL, Redis, RabbitMQ"),
    ("Stack.Infra", "Kubernetes, Helm, Docker, Azure, OTel"),
    ("Stack.AI", "LangGraph, LLM tool calling, RAG"),
    ("Stack.Web", "Next.js, React, TanStack, Expo"),
    None,
    "GitHub Stats",
    ("Public Repos", "{repos}"),
    ("Commits (1y)", "{commits}"),
    ("Contributions (1y)", "{contributions}"),
]

FALLBACK_STATS = {"repos": 48, "commits": "—", "contributions": "—"}

THEMES = {
    "dark": {
        "bg": "#0b0f14", "border": "#1f2933", "text": "#e6edf3", "muted": "#3d4752",
        "key": "#ffa657", "value": "#a5d6ff", "accent": "#7ee787", "user": "#7ee787",
        "dim": "#3fb950",
        "palette": ["#484f58", "#ff7b72", "#7ee787", "#d29922", "#79c0ff", "#d2a8ff", "#56d4dd", "#e6edf3"],
    },
    "light": {
        "bg": "#fbfaf7", "border": "#d8dee4", "text": "#1f2328", "muted": "#c5ccd3",
        "key": "#bc4c00", "value": "#0550ae", "accent": "#1a7f37", "user": "#1a7f37",
        "dim": "#4ac26b",
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
    query($login: String!) {
      user(login: $login) {
        repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
          contributionCalendar { totalContributions }
        }
      }
    }"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": LOGIN},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.load(resp)
    if "errors" in body:
        raise RuntimeError(body["errors"])
    user = body["data"]["user"]
    cc = user["contributionsCollection"]
    return {
        "repos": user["repositories"]["totalCount"],
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


# Spinning ASCII torus, after Andy Sloane's donut.c. Frames loop seamlessly:
# A makes one full turn and B two over FRAMES frames.
FRAMES, FRAME_S = 60, 0.09
STILL = 10  # frame shown when motion is reduced
SHADES = ".,-~:;=!*#$@"
DONUT_ROWS = 17


def donut(frame):
    """One frame as DONUT_ROWS rows of ART_COLS shade indices (-1 = empty)."""
    a = 2 * math.pi * frame / FRAMES
    b = 2 * a
    ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
    k2 = 5
    k1x = ART_COLS * k2 / 9
    k1y = k1x * CHAR / LINE  # cells are taller than wide
    zbuf = [[0.0] * ART_COLS for _ in range(DONUT_ROWS)]
    out = [[-1] * ART_COLS for _ in range(DONUT_ROWS)]
    for ti in range(0, 628, 7):
        ct, st = math.cos(ti / 100), math.sin(ti / 100)
        for pi in range(0, 628, 2):
            cp, sp = math.cos(pi / 100), math.sin(pi / 100)
            circle = 2 + ct
            x = circle * (cb * cp + sa * sb * sp) - st * ca * sb
            y = circle * (sb * cp - sa * cb * sp) + st * ca * cb
            ooz = 1 / (k2 + ca * circle * sp + st * sa)
            col = int(ART_COLS / 2 + k1x * ooz * x)
            row = int(DONUT_ROWS / 2 - k1y * ooz * y)
            lum = cp * ct * sb - ca * ct * sp - sa * st + cb * (ca * st - ct * sa * sp)
            if 0 <= col < ART_COLS and 0 <= row < DONUT_ROWS and lum > 0 and ooz > zbuf[row][col]:
                zbuf[row][col] = ooz
                out[row][col] = min(int(lum * 8), len(SHADES) - 1)
    return out


def info_lines(stats, today):
    fields = {**{k: f"{v:,}" if isinstance(v, int) else v for k, v in stats.items()}, "uptime": uptime(today)}
    lines = [[("user", f"{LOGIN}"), ("muted", "@"), ("user", "github")], [("muted", "─" * INFO_COLS)]]
    for item in INFO:
        if item is None:
            lines.append([])
        elif isinstance(item, str):
            lines.append([("accent", "- "), ("text", item), ("muted", " " + "─" * (INFO_COLS - len(item) - 3))])
        else:
            key, value = item[0], item[1].format(**fields)
            dots = INFO_COLS - len(key) - len(value) - 4
            lines.append([("accent", ". "), ("key", key), ("muted", ":" + " " + "." * dots + " "), ("value", value)])
    return lines


def render(theme, stats, today):
    c = THEMES[theme]
    info = info_lines(stats, today)
    rows = len(info) + 2  # + blank + palette row
    width = round(PAD * 2 + (ART_COLS + 3 + INFO_COLS) * CHAR)
    height = PAD * 2 + rows * LINE
    info_x = PAD + (ART_COLS + 3) * CHAR

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{LOGIN} neofetch">',
        f"<style>text{{font-family:{FONT};font-size:{SIZE}px;white-space:pre}}"
        ".l{opacity:0;animation:in .35s ease-out forwards}@keyframes in{to{opacity:1}}"
        f".f{{opacity:0;animation:fr {FRAMES * FRAME_S:.2f}s steps(1) infinite}}"
        f"@keyframes fr{{0%{{opacity:1}}{100 / FRAMES:.3f}%{{opacity:0}}}}"
        "@media (prefers-reduced-motion:reduce){.l,.f{animation:none;opacity:1}.f:not(.still){display:none}}</style>",
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="12" fill="{c["bg"]}" stroke="{c["border"]}"/>',
    ]

    # Donut frames, centred in the art column; each is visible for one FRAME_S slot.
    top = (rows - DONUT_ROWS) // 2
    for f in range(FRAMES):
        lines = []
        for r, cells in enumerate(donut(f)):
            spans, run, run_colour = [], "", None
            for idx in cells + [-1]:
                colour = None if idx < 0 else ("accent" if idx >= 6 else "dim")
                if colour != run_colour and run:
                    spans.append((run, run_colour))
                    run = ""
                run, run_colour = run + (" " if idx < 0 else SHADES[idx]), colour
            body = "".join(
                escape(t) if col is None else f'<tspan fill="{c[col]}">{escape(t)}</tspan>' for t, col in spans
            ).rstrip()
            if body:
                y = PAD + (top + r + 1) * LINE - 6
                lines.append(f'<text x="{PAD}" y="{y}" xml:space="preserve">{body}</text>')
        still = " still" if f == STILL else ""
        out.append(f'<g class="f{still}" style="animation-delay:{f * FRAME_S:.2f}s">{"".join(lines)}</g>')
    y = PAD + (top + DONUT_ROWS) * LINE - 6
    out.append(
        f'<text class="l" x="{PAD + ART_COLS * CHAR / 2:.1f}" y="{y}" text-anchor="middle" fill="{c["muted"]}" '
        f'style="animation-delay:.3s">$ ./donut</text>'
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
