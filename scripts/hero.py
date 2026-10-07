"""Render the profile banner: a topographic map of Tangkuban Perahu that draws itself.

Output is deterministic, so the SVGs are committed to assets/ and only need
regenerating when this file changes:

    python3 scripts/hero.py
"""

import math
import random
from pathlib import Path

W, H = 1200, 360
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

NAME = "satriadhikara"
TAGLINE = "software engineer · grab / kartaview"
SUBLINE = "distributed systems ✦ dev tooling ✦ maps ✦ shipping things"
TAG_SIZE = 19
TYPE_SHIFT = round(len(TAGLINE) * TAG_SIZE * 0.6)
COORDS = "06°45′36″S  107°36′00″E  ·  tangkuban perahu, west java"

THEMES = {
    "dark": {
        "bg": "#0b0f14",
        "border": "#1f2933",
        "grid": "#151c24",
        "contour": "#2b3a48",
        "index": "#7ee787",
        "crater": "#ffa657",
        "text": "#e6edf3",
        "muted": "#7d8590",
        "accent": "#7ee787",
        "pin": "#ff7b72",
        "stars": True,
    },
    "light": {
        "bg": "#fbfaf7",
        "border": "#d8dee4",
        "grid": "#eef1f4",
        "contour": "#c3ccd5",
        "index": "#1a7f37",
        "crater": "#bc4c00",
        "text": "#1f2328",
        "muted": "#59636e",
        "accent": "#1a7f37",
        "pin": "#cf222e",
        "stars": False,
    },
}

# Summit of the volcano in banner coordinates.
CX, CY = 955, 186
LEVELS = 15


def contour(level, rng_phases):
    """One closed contour line, as a list of points.

    Every level shares the same low-frequency wobble so the lines stay nested;
    the centre drifts north-east as we climb, giving the mountain a steep side.
    Tangkuban Perahu means "upturned boat", hence the long east-west axis.
    """
    t = level / LEVELS
    scale = (1 - t) ** 1.15
    rx, ry = 265 * scale + 18, 122 * scale + 9
    cx, cy = CX - 30 * (1 - t), CY + 22 * (1 - t)
    pts = []
    for i in range(240):
        a = 2 * math.pi * i / 240
        wobble = 1 + sum(
            amp * (0.55 + 0.45 * (1 - t)) * math.sin(k * a + ph)
            for k, amp, ph in rng_phases
        )
        pts.append((cx + rx * wobble * math.cos(a), cy + ry * wobble * math.sin(a)))
    return pts


def path_d(pts):
    head = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    return head + "".join(f"L{x:.1f},{y:.1f}" for x, y in pts[1:]) + "Z"


def perimeter(pts):
    return sum(math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts)))


def render(theme):
    c = THEMES[theme]
    rng = random.Random(1945)
    phases = [(k, 0.09 / k ** 0.7, rng.uniform(0, 2 * math.pi)) for k in (2, 3, 5, 7)]

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="{NAME} — {TAGLINE}">',
        "<style>",
        f"text{{font-family:{FONT}}}",
        ".c{fill:none;stroke-linejoin:round;animation:draw 2.6s cubic-bezier(.6,0,.2,1) both}",
        "@keyframes draw{from{stroke-dashoffset:var(--l)}to{stroke-dashoffset:0}}",
        ".fade{opacity:0;animation:fade .8s ease-out forwards}",
        "@keyframes fade{to{opacity:1}}",
        ".type{animation:type 1.6s steps(var(--n)) 1.1s both}",
        f"@keyframes type{{to{{transform:translateX({TYPE_SHIFT}px)}}}}",
        ".caret{animation:blink 1s steps(1) infinite}",
        "@keyframes blink{50%{opacity:0}}",
        ".ring{transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out 2.8s infinite;opacity:0}",
        "@keyframes ring{0%{transform:scale(.2);opacity:.9}100%{transform:scale(3.2);opacity:0}}",
        ".tw{animation:tw 3s ease-in-out infinite}",
        "@keyframes tw{50%{opacity:.15}}",
        "@media (prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important}}",
        "</style>",
        "<defs>",
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="14"/></clipPath>',
        '<linearGradient id="fadeL" x1="0" x2="1">'
        f'<stop offset=".44" stop-color="{c["bg"]}"/><stop offset=".62" stop-color="{c["bg"]}" stop-opacity="0"/>'
        "</linearGradient>",
        "</defs>",
        '<g clip-path="url(#card)">',
        f'<rect width="{W}" height="{H}" fill="{c["bg"]}"/>',
    ]

    # Map grid with tick labels, like the edge of a survey sheet.
    for x in range(0, W, 60):
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{c["grid"]}"/>')
    for y in range(0, H, 60):
        out.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{c["grid"]}"/>')

    if c["stars"]:
        for _ in range(42):
            x, y = rng.uniform(560, W - 10), rng.uniform(8, H - 8)
            r = rng.choice((0.6, 0.8, 1.1))
            delay = rng.uniform(0, 3)
            out.append(
                f'<circle class="tw" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{c["muted"]}" '
                f'style="animation-delay:{delay:.2f}s"/>'
            )

    for lvl in range(LEVELS):
        pts = contour(lvl, phases)
        length = perimeter(pts)
        is_index = lvl % 5 == 0
        stroke = c["index"] if is_index else c["contour"]
        width = 1.6 if is_index else 1
        opacity = 0.75 if is_index else 1
        out.append(
            f'<path class="c" d="{path_d(pts)}" stroke="{stroke}" stroke-width="{width}" '
            f'stroke-opacity="{opacity}" stroke-dasharray="{length:.0f}" '
            f'style="--l:{length:.0f};animation-delay:{lvl * 0.07:.2f}s"/>'
        )
        if is_index and lvl:
            label_x, label_y = pts[45]
            out.append(
                f'<text class="fade" x="{label_x:.0f}" y="{label_y:.0f}" font-size="10" '
                f'fill="{c["index"]}" style="animation-delay:{1.6 + lvl * 0.05:.2f}s">'
                f"{1350 + lvl * 50}m</text>"
            )

    # The crater: dashed depression rings.
    for i, (rx, ry) in enumerate(((30, 11), (18, 6))):
        out.append(
            f'<ellipse class="fade" cx="{CX + 6}" cy="{CY}" rx="{rx}" ry="{ry}" fill="none" '
            f'stroke="{c["crater"]}" stroke-dasharray="3 4" style="animation-delay:{2.2 + i * 0.15:.2f}s"/>'
        )

    # "You are here" pin with a sonar ripple.
    px, py = CX + 64, CY - 40
    out += [
        f'<circle class="ring" cx="{px}" cy="{py}" r="9" fill="none" stroke="{c["pin"]}" stroke-width="1.5"/>',
        f'<circle class="fade" cx="{px}" cy="{py}" r="4.5" fill="{c["pin"]}" style="animation-delay:2.6s"/>',
        f'<text class="fade" x="{px + 12}" y="{py - 8}" font-size="11" fill="{c["pin"]}" '
        f'style="animation-delay:2.7s">you are here</text>',
    ]

    # Fade the map out behind the type.
    out.append(f'<rect width="{W}" height="{H}" fill="url(#fadeL)"/>')

    # Type block. Monospace advance is ~0.6em in every common coding font,
    # which is what the steps() typing reveal relies on.
    name_size, tag_size = 66, TAG_SIZE
    tag_w = TYPE_SHIFT
    out += [
        f'<text class="fade" x="64" y="92" font-size="14" fill="{c["muted"]}" letter-spacing="1">'
        f"// {COORDS}</text>",
        f'<text class="fade" x="60" y="178" font-size="{name_size}" font-weight="700" '
        f'fill="{c["text"]}" letter-spacing="-2" style="animation-delay:.2s">{NAME}'
        f'<tspan fill="{c["accent"]}">.</tspan></text>',
        f'<clipPath id="typed"><rect class="type" x="{64 - tag_w:.0f}" y="200" width="{tag_w:.0f}" '
        f'height="30" style="--n:{len(TAGLINE)}"/></clipPath>',
        f'<text x="64" y="222" font-size="{tag_size}" fill="{c["text"]}" clip-path="url(#typed)">'
        f"{TAGLINE}</text>",
        f'<g class="type" style="--n:{len(TAGLINE)}"><rect class="caret" x="68" y="206" width="10" '
        f'height="21" fill="{c["accent"]}"/></g>',
        f'<text class="fade" x="64" y="270" font-size="15" fill="{c["muted"]}" '
        f'style="animation-delay:2.8s">{SUBLINE}</text>',
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
