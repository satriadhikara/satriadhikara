"""Render the profile banner: name, a typed tagline, and a distributed trace that
records itself span by span.

Output is deterministic, so the SVGs are committed to assets/ and only need
regenerating when this file changes:

    python3 scripts/hero.py
"""

from pathlib import Path

W, H = 1200, 360
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

NAME = "satriadhikara"
PROMPT = "$ whoami"
TAGLINE = "swe @ grab"
SUBLINE = "backend ✦ infra ✦ applied ai"
TAG_SIZE = 22
TYPE_SHIFT = round(len(TAGLINE) * TAG_SIZE * 0.6)

THEMES = {
    "dark": {
        "bg": "#0b0f14",
        "border": "#1f2933",
        "grid": "#1a222c",
        "text": "#e6edf3",
        "muted": "#7d8590",
        "accent": "#7ee787",
        "api": "#7ee787",
        "svc": "#79c0ff",
        "db": "#e3b341",
        "ai": "#d2a8ff",
        "queue": "#ffa657",
    },
    "light": {
        "bg": "#fbfaf7",
        "border": "#d8dee4",
        "grid": "#eceef0",
        "text": "#1f2328",
        "muted": "#59636e",
        "accent": "#1a7f37",
        "api": "#1a7f37",
        "svc": "#0969da",
        "db": "#9a6700",
        "ai": "#8250df",
        "queue": "#bc4c00",
    },
}

# (name, depth, start ms, duration ms, kind): one request through the stack.
TRACE_ID = "7f3a9c1e"
SPANS = [
    ("POST /v1/plan", 0, 0, 184, "api"),
    ("auth.verify", 1, 3, 9, "svc"),
    ("grpc Planner.Plan", 1, 14, 152, "svc"),
    ("redis.get", 2, 17, 4, "db"),
    ("pg.query", 2, 23, 31, "db"),
    ("llm.tool_call", 2, 58, 101, "ai"),
    ("rmq.publish", 1, 170, 11, "queue"),
]
TOTAL_MS = 184

# Trace panel geometry.
LABEL_X, BAR_X, BAR_W = 640, 820, 300
ROW_Y, ROW_H = 126, 27
MS = BAR_W / TOTAL_MS
T0, SPEED = 0.7, 0.009  # animation start (s) and seconds per traced ms


def render(theme):
    c = THEMES[theme]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="{NAME} — {TAGLINE}">',
        "<style>",
        f"text{{font-family:{FONT};white-space:pre}}",
        ".fade{opacity:0;animation:fade .6s ease-out forwards}",
        "@keyframes fade{to{opacity:1}}",
        ".bar{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow linear forwards}",
        "@keyframes grow{to{transform:scaleX(1)}}",
        ".type{animation:type 1s steps(var(--n)) .9s both}",
        f"@keyframes type{{to{{transform:translateX({TYPE_SHIFT}px)}}}}",
        ".caret{animation:blink 1s steps(1) infinite}",
        "@keyframes blink{50%{opacity:0}}",
        "@media (prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important}"
        f".bar{{transform:none!important}}.type{{transform:translateX({TYPE_SHIFT}px)!important}}}}",
        "</style>",
        "<defs>",
        '<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">'
        f'<circle cx="12" cy="12" r="1" fill="{c["grid"]}"/></pattern>',
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>',
        "</defs>",
        '<g clip-path="url(#card)">',
        f'<rect width="{W}" height="{H}" fill="{c["bg"]}"/>',
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>',
    ]

    # Type block. Monospace advance is ~0.6em in every common coding font,
    # which is what the steps() typing reveal relies on.
    out += [
        f'<text class="fade" x="64" y="104" font-size="15" fill="{c["muted"]}">{PROMPT}</text>',
        f'<text class="fade" x="60" y="182" font-size="68" font-weight="700" '
        f'fill="{c["text"]}" letter-spacing="-2" style="animation-delay:.2s">{NAME}'
        f'<tspan fill="{c["accent"]}">.</tspan></text>',
        f'<clipPath id="typed"><rect class="type" x="{64 - TYPE_SHIFT}" y="204" width="{TYPE_SHIFT}" '
        f'height="34" style="--n:{len(TAGLINE)}"/></clipPath>',
        f'<text x="64" y="230" font-size="{TAG_SIZE}" fill="{c["text"]}" clip-path="url(#typed)">{TAGLINE}</text>',
        f'<g class="type" style="--n:{len(TAGLINE)}"><rect class="caret" x="69" y="212" width="11" '
        f'height="23" fill="{c["accent"]}"/></g>',
        f'<text class="fade" x="64" y="276" font-size="15" fill="{c["muted"]}" '
        f'style="animation-delay:2s">{SUBLINE}</text>',
    ]

    # Trace header and time axis.
    done = T0 + TOTAL_MS * SPEED
    axis_bottom = ROW_Y + len(SPANS) * ROW_H - 8
    out.append(
        f'<text class="fade" x="{LABEL_X}" y="88" font-size="12" fill="{c["muted"]}" style="animation-delay:.4s">'
        f"trace {TRACE_ID} · {len(SPANS)} spans</text>"
    )
    out.append(
        f'<text class="fade" x="{BAR_X + BAR_W}" y="88" font-size="12" fill="{c["accent"]}" text-anchor="end" '
        f'style="animation-delay:{done:.2f}s">200 OK · {TOTAL_MS}ms</text>'
    )
    for ms in range(0, TOTAL_MS + 1, 50):
        x = BAR_X + ms * MS
        out += [
            f'<line class="fade" x1="{x:.1f}" y1="{ROW_Y - 18}" x2="{x:.1f}" y2="{axis_bottom}" '
            f'stroke="{c["border"]}" stroke-dasharray="2 4" style="animation-delay:.4s"/>',
            f'<text class="fade" x="{x + 3:.1f}" y="{ROW_Y - 8}" font-size="10" fill="{c["muted"]}" '
            f'style="animation-delay:.4s">{ms}ms</text>',
        ]

    # Spans: each bar starts when its span starts and grows for as long as it ran.
    for i, (name, depth, start, dur, kind) in enumerate(SPANS):
        y = ROW_Y + i * ROW_H
        delay = T0 + start * SPEED
        out += [
            f'<text class="fade" x="{LABEL_X + depth * 14}" y="{y + 12}" font-size="13" fill="{c["text"]}" '
            f'style="animation-delay:{delay:.2f}s">{name}</text>',
            f'<rect class="bar" x="{BAR_X + start * MS:.1f}" y="{y + 1}" width="{max(dur * MS, 2):.1f}" height="14" '
            f'rx="2" fill="{c[kind]}" fill-opacity=".85" '
            f'style="animation-delay:{delay:.2f}s;animation-duration:{max(dur * SPEED, 0.05):.2f}s"/>',
            f'<text class="fade" x="{BAR_X + (start + dur) * MS + 6:.1f}" y="{y + 12}" font-size="10" '
            f'fill="{c["muted"]}" style="animation-delay:{delay + dur * SPEED:.2f}s">{dur}ms</text>',
        ]

    out += [
        "</g>",
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{c["border"]}"/>',
        "</svg>",
    ]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    assets = Path(__file__).resolve().parent.parent / "assets"
    assets.mkdir(exist_ok=True)
    for theme in THEMES:
        (assets / f"hero-{theme}.svg").write_text(render(theme), encoding="utf-8")
        print(f"wrote assets/hero-{theme}.svg")
