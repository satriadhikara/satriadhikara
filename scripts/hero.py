"""Render the profile banner: a street map of central Jakarta that draws itself
outward from Monas.

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
COORDS = "06°10′31″S  106°49′38″E  ·  monas, jakarta"
TAG_SIZE = 19
TYPE_SHIFT = round(len(TAGLINE) * TAG_SIZE * 0.6)

THEMES = {
    "dark": {
        "bg": "#0b0f14",
        "border": "#1f2933",
        "street": "#243240",
        "artery": "#7ee787",
        "park": "#7ee787",
        "river": "#58a6ff",
        "rail": "#7d8590",
        "text": "#e6edf3",
        "muted": "#7d8590",
        "accent": "#7ee787",
        "pin": "#ff7b72",
        "monas": "#e3b341",
    },
    "light": {
        "bg": "#fbfaf7",
        "border": "#d8dee4",
        "street": "#d5dbe1",
        "artery": "#1a7f37",
        "park": "#1a7f37",
        "river": "#0969da",
        "rail": "#59636e",
        "text": "#1f2328",
        "muted": "#59636e",
        "accent": "#1a7f37",
        "pin": "#cf222e",
        "monas": "#9a6700",
    },
}

# Medan Merdeka, the square park with Monas in the middle.
PX, PY, PS = 860, 70, 150
MONAS = (PX + PS / 2, PY + PS / 2)
# Jl. M.H. Thamrin runs south from the square's west side to Bundaran HI.
THAMRIN_X = PX - 34
BUNDARAN = (THAMRIN_X, 318)


def poly_d(pts):
    return "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def length(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def in_park(x, y, margin=6):
    return PX - margin < x < PX + PS + margin and PY - margin < y < PY + PS + margin


def streets(rng):
    """Two slightly skewed street grids, broken into irregular segments."""
    out = []
    for angle, step_range in ((math.radians(-7), (14, 30)), (math.radians(83), (13, 28))):
        dx, dy = math.cos(angle), math.sin(angle)
        nx, ny = -dy, dx
        offset = -700
        while offset < 700:
            offset += rng.uniform(*step_range)
            t = -700
            while t < 700:
                seg = rng.uniform(30, 150)
                if rng.random() < 0.78:
                    run = []
                    for i in range(13):
                        s = t + seg * i / 12
                        x = MONAS[0] + nx * offset + dx * s
                        y = MONAS[1] + ny * offset + dy * s + math.sin(s / 90 + offset) * 2.5
                        # Streets stop at the park edge and fade out under the type.
                        if in_park(x, y) or x < 540 or not -20 < y < H + 20:
                            if len(run) > 1:
                                out.append(run)
                            run = []
                        else:
                            run.append((x, y))
                    if len(run) > 1:
                        out.append(run)
                t += seg + rng.uniform(4, 26)
    return out


def river(rng):
    """The Ciliwung, meandering north through the east side of the map."""
    pts, x = [], 1105
    for i in range(60):
        y = H + 10 - i * (H + 20) / 59
        x += rng.uniform(-6, 6) + math.sin(i / 4) * 3
        pts.append((x, y))
    return pts


def render(theme):
    c = THEMES[theme]
    rng = random.Random(1527)  # Jayakarta, founded 22 June 1527

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="{NAME} — {TAGLINE}">',
        "<style>",
        f"text{{font-family:{FONT}}}",
        ".d{fill:none;stroke-linecap:round;stroke-linejoin:round;animation:draw 1.4s cubic-bezier(.6,0,.2,1) both}",
        "@keyframes draw{from{stroke-dashoffset:var(--l)}to{stroke-dashoffset:0}}",
        ".fade{opacity:0;animation:fade .8s ease-out forwards}",
        "@keyframes fade{to{opacity:1}}",
        ".type{animation:type 1.6s steps(var(--n)) 1.1s both}",
        f"@keyframes type{{to{{transform:translateX({TYPE_SHIFT}px)}}}}",
        ".caret{animation:blink 1s steps(1) infinite}",
        "@keyframes blink{50%{opacity:0}}",
        ".ring{transform-box:fill-box;transform-origin:center;animation:ring 2.4s ease-out 2.8s infinite;opacity:0}",
        "@keyframes ring{0%{transform:scale(.2);opacity:.9}100%{transform:scale(3.2);opacity:0}}",
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

    def stroke(pts, color, width, delay, extra=""):
        n = length(pts)
        return (
            f'<path class="d" d="{poly_d(pts)}" stroke="{color}" stroke-width="{width}" '
            f'stroke-dasharray="{n:.0f}" style="--l:{n:.0f};animation-delay:{delay:.2f}s"{extra}/>'
        )

    def label(x, y, text, color, delay, size=10, extra=""):
        return (
            f'<text class="fade" x="{x:.0f}" y="{y:.0f}" font-size="{size}" fill="{color}" '
            f'stroke="{c["bg"]}" stroke-width="4" paint-order="stroke" '
            f'style="animation-delay:{delay}s"{extra}>{text}</text>'
        )

    # Side streets ripple outward from Monas.
    for pts in streets(rng):
        delay = math.dist(pts[0], MONAS) / 420
        out.append(stroke(pts, c["street"], 1.2, delay))

    out.append(stroke(river(rng), c["river"], 2.2, 0.4, ' stroke-opacity=".7"'))
    out.append(label(1062, 340, "ciliwung", c["river"], 1.8))

    # Commuter rail past Gambir station, east of the square.
    rail = [(PX + PS + 46, -10), (PX + PS + 40, H + 10)]
    out.append(stroke(rail, c["rail"], 1.4, 0.3))
    out.append(
        f'<path class="fade" d="{poly_d(rail)}" stroke="{c["rail"]}" stroke-width="6" '
        f'stroke-dasharray="1 7" fill="none" style="animation-delay:1.4s"/>'
    )
    out.append(label(PX + PS + 54, PY + 70, "gambir", c["muted"], 1.8))

    # Arteries: Medan Merdeka ring road, then Thamrin south to Bundaran HI.
    a = ' stroke-opacity=".8"'
    ring_road = [
        (PX - 8, PY - 8), (PX + PS + 8, PY - 8), (PX + PS + 8, PY + PS + 8), (PX - 8, PY + PS + 8), (PX - 8, PY - 8),
    ]
    out.append(stroke(ring_road, c["artery"], 2.4, 0.1, a))
    out.append(stroke([(THAMRIN_X, -10), (THAMRIN_X, BUNDARAN[1] - 16)], c["artery"], 3, 0.2, a))
    out.append(stroke([(THAMRIN_X, BUNDARAN[1] + 16), (THAMRIN_X + 4, H + 10)], c["artery"], 3, 0.9, a))
    out.append(
        f'<circle class="fade" cx="{BUNDARAN[0]}" cy="{BUNDARAN[1]}" r="16" fill="none" stroke="{c["artery"]}" '
        f'stroke-width="2.4" stroke-opacity=".8" style="animation-delay:1s"/>'
    )
    out.append(label(THAMRIN_X + 24, BUNDARAN[1] + 4, "bundaran hi", c["muted"], 1.6))
    tx, ty = THAMRIN_X - 8, PY + PS + 70
    out.append(label(tx, ty, "jl. m.h. thamrin", c["muted"], 1.6, extra=f' transform="rotate(-90 {tx} {ty})"'))

    # Medan Merdeka park: tinted square, its paths, and Monas itself.
    mx, my = MONAS
    p = ' stroke-opacity=".35"'
    out += [
        f'<rect class="fade" x="{PX}" y="{PY}" width="{PS}" height="{PS}" rx="3" fill="{c["park"]}" '
        f'fill-opacity=".07" stroke="{c["park"]}" stroke-opacity=".35" style="animation-delay:.6s"/>',
        stroke([(PX, PY), (PX + PS, PY + PS)], c["park"], 1, 0.8, p),
        stroke([(PX + PS, PY), (PX, PY + PS)], c["park"], 1, 0.8, p),
        stroke([(mx, PY), (mx, PY + PS)], c["park"], 1, 0.8, p),
        stroke([(PX, my), (PX + PS, my)], c["park"], 1, 0.8, p),
        f'<rect class="fade" x="{mx - 17}" y="{my - 17}" width="34" height="34" fill="{c["bg"]}" '
        f'stroke="{c["monas"]}" stroke-width="1.5" style="animation-delay:1.2s"/>',
        f'<circle class="fade" cx="{mx}" cy="{my}" r="5" fill="{c["monas"]}" style="animation-delay:1.3s"/>',
        label(mx + 22, my - 22, "monas", c["monas"], 1.5, size=11),
    ]

    # "You are here" pin with a sonar ripple, down in the business district.
    px, py = THAMRIN_X + 76, BUNDARAN[1] - 46
    out += [
        f'<circle class="ring" cx="{px}" cy="{py}" r="9" fill="none" stroke="{c["pin"]}" stroke-width="1.5"/>',
        f'<circle class="fade" cx="{px}" cy="{py}" r="4.5" fill="{c["pin"]}" style="animation-delay:2.6s"/>',
        label(px + 12, py - 8, "you are here", c["pin"], 2.7, size=11),
    ]

    # Fade the map out behind the type.
    out.append(f'<rect width="{W}" height="{H}" fill="url(#fadeL)"/>')

    # Type block. Monospace advance is ~0.6em in every common coding font,
    # which is what the steps() typing reveal relies on.
    tag_w = TYPE_SHIFT
    out += [
        f'<text class="fade" x="64" y="92" font-size="14" fill="{c["muted"]}" letter-spacing="1">'
        f"// {COORDS}</text>",
        f'<text class="fade" x="60" y="178" font-size="66" font-weight="700" '
        f'fill="{c["text"]}" letter-spacing="-2" style="animation-delay:.2s">{NAME}'
        f'<tspan fill="{c["accent"]}">.</tspan></text>',
        f'<clipPath id="typed"><rect class="type" x="{64 - tag_w}" y="200" width="{tag_w}" '
        f'height="30" style="--n:{len(TAGLINE)}"/></clipPath>',
        f'<text x="64" y="222" font-size="{TAG_SIZE}" fill="{c["text"]}" clip-path="url(#typed)">'
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
