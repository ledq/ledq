#!/usr/bin/env python3
"""Generate the profile SVGs. Run: python3 assets/build.py

Everything is hand-rolled SVG with inline CSS animation, self-hosted, so the
profile has no third-party service in the render path. Palette is gruvbox dark.
"""

import json
import math
from pathlib import Path

OUT = Path(__file__).parent

BG, BG1, BG2, GRAY = "#282828", "#3c3836", "#504945", "#928374"
FG, FG_DIM = "#ebdbb2", "#a89984"
RED, GREEN, YELLOW, BLUE = "#fb4934", "#b8bb26", "#fabd2f", "#83a598"
PURPLE, AQUA, ORANGE = "#d3869b", "#8ec07c", "#fe8019"

MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "DejaVu Sans Mono", monospace'

HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n'

# Bump when a design changes: GitHub's camo proxy caches images by URL, so a
# same-named file keeps serving the stale copy.
CARD_V = "v7"

# Every repo card uses one accent; per-repo colours read as noise, not signal.
CARD_ACCENT = "#fabd2f"

# Animated preview bands for the repo cards live in assets/previews.py.
# They are parked, not deleted: set this True and re-run to bring them back.
PREVIEWS = False

if PREVIEWS:
    from previews import BAND, PREVIEW, PVH  # noqa: F401
else:
    PVH = 0


def svg(w, h, body, style="", label=""):
    return (
        f'{HEAD}<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{label}">\n'
        f"<style>\n.mono {{ font-family: {MONO}; }}\n{style}</style>\n{body}\n</svg>\n"
    )


def tspans(x, lines, dy):
    out = []
    for i, line in enumerate(lines):
        d = 0 if i == 0 else dy
        out.append(f'<tspan x="{x}" dy="{d}">{line}</tspan>')
    return "".join(out)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------
# 1. hero: neofetch-style card
# --------------------------------------------------------------------------

WORDMARK = [
    " ███               █        ",
    "   █               █        ",
    "   █               █        ",
    "   █     ███    ██▓█   ██▓█ ",
    "   █    ▓▓ ▒█  █▓ ▓█  █▓ ▓█ ",
    "   █    █   █  █   █  █   █ ",
    "   █    █████  █   █  █   █ ",
    "   █    █      █   █  █   █ ",
    "   █░   ▓▓  █  █▓ ▓█  █▓ ▓█ ",
    "   ▒██   ███▒   ██▓█   ██▓█ ",
    "                          █ ",
    "                          █ ",
    "                          █ ",
]

INFO = [
    ("Role", "Software Engineer (data · platform · agentic AI)"),
    ("Focus", "full-stack apps, the data platform beneath, agentic AI"),
    ("Langs", "Python · TypeScript · SQL · C/C++"),
    ("Cloud", "GCP · Docker · Terraform"),
    ("Data", "BigQuery · Airflow · Dataform · Postgres"),
    ("Web", "Next.js · React · FastAPI · GraphQL"),
    ("ML", "PyTorch · ONNX · LangChain · XGBoost"),
    ("Edu", "B.S. Computer Science, Rose-Hulman"),
    ("Status", "open to work"),
]

# Where a neofetch card puts its terminal colour swatches. Same 8-wide grid,
# one glyph per cell; colours are looked up from STACK so they stay in one place.
CARD_ICONS = [
    ["python", "typescript", "cplusplus", "googlecloud", "docker", "terraform",
     "postgresql", "googlebigquery"],
    ["apacheairflow", "nextdotjs", "react", "fastapi", "graphql", "pytorch",
     "langchain", "linux"],
]
CARD_ICON = 22
CARD_PITCH = 30


def build_card():
    # width has slack for the longest INFO value; check after editing INFO
    w, h = 940, 375
    style = f"""
.logo {{ font-size: 16px; fill: {AQUA}; }}
.key  {{ font-size: 14px; fill: {YELLOW}; font-weight: 700; }}
.val  {{ font-size: 14px; fill: {FG}; }}
.head {{ font-size: 14px; fill: {GREEN}; font-weight: 700; }}
.dim  {{ font-size: 14px; fill: {GRAY}; }}
.ttl  {{ font-size: 12px; fill: {GRAY}; }}
.cur  {{ fill: {GREEN}; animation: blink 1.06s steps(1) infinite; }}
@keyframes blink {{ 0%,50% {{ opacity: 1 }} 50.01%,100% {{ opacity: 0 }} }}
.sw   {{ transform-box: fill-box; transform-origin: center;
        animation: pop .45s cubic-bezier(.2,.8,.2,1) backwards; }}
@keyframes pop {{ from {{ opacity: 0; transform: scale(.4) }}
                 to {{ opacity: 1; transform: scale(1) }} }}
.row  {{ animation: fade .5s ease-out backwards; }}
@keyframes fade {{ from {{ opacity: 0 }} to {{ opacity: 1 }} }}
"""
    b = [
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="{BG}"/>',
        f'<rect x="0" y="0" width="{w}" height="30" rx="10" fill="{BG1}"/>',
        f'<rect x="0" y="20" width="{w}" height="10" fill="{BG1}"/>',
        f'<circle cx="20" cy="15" r="5" fill="{RED}"/>',
        f'<circle cx="38" cy="15" r="5" fill="{YELLOW}"/>',
        f'<circle cx="56" cy="15" r="5" fill="{GREEN}"/>',
        f'<text class="mono ttl" x="{w / 2}" y="19" text-anchor="middle">ledq: ~</text>',
        f'<text class="mono logo" x="40" y="82" xml:space="preserve">{tspans(40, WORDMARK, 19)}</text>',
        f'<text class="mono head" x="360" y="62">duy le</text>',
        f'<rect class="cur" x="418" y="51" width="9" height="15"/>',
        f'<text class="mono dim" x="360" y="80">------</text>',
    ]
    for i, (k, v) in enumerate(INFO):
        y = 106 + i * 21
        d = f"{0.05 * i:.2f}s"
        b.append(
            f'<g class="row" style="animation-delay:{d}">'
            f'<text class="mono key" x="360" y="{y}">{esc(k)}</text>'
            f'<text class="mono val" x="450" y="{y}">{esc(v)}</text></g>'
        )
    icons = json.loads((OUT / "icons.json").read_text())
    colors = {slug: col for _, items in STACK for slug, _, col in items}
    for r, row in enumerate(CARD_ICONS):
        for c, slug in enumerate(row):
            x, y = 360 + c * CARD_PITCH, 300 + r * 32
            d = f"{0.6 + 0.03 * (r * 8 + c):.2f}s"
            b.append(
                f'<g transform="translate({x},{y})">'
                f'<g class="sw" style="animation-delay:{d}">'
                f'<path d="{icons[slug]["d"]}" fill="{colors[slug]}" '
                f'transform="scale({CARD_ICON / 24:.4f})"/>'
                f"</g></g>"
            )
    role = next((v for k, v in INFO if k == "Role"), "engineer")
    return svg(w, h, "\n".join(b), style, f"ledq / duy le: {role.lower()}")


# --------------------------------------------------------------------------
# 2. timeline: roles as animated bars
# --------------------------------------------------------------------------

# months since Dec 2023
ROLES = [
    ("robotics swe", "rose-hulman ventures", 0, 4, AQUA),
    ("teaching assistant, os", "rose-hulman", 3, 9, PURPLE),
    ("full-stack engineer", "worldclass", 8, 17, BLUE),
    ("ml engineer", "rose-hulman ventures / quadralynx", 14, 17, AQUA),
    ("swe intern", "upper hand ai", 17, 24, ORANGE),
    ("data engineer", "upper hand ai", 24, 30, YELLOW),
]
SPAN = 32  # dec 2023 .. aug 2026
X0, X1 = 300, 872


def mx(m):
    return X0 + (X1 - X0) * m / SPAN


def build_timeline():
    w = 900
    top = 58
    rh = 34
    h = top + rh * (len(ROLES) + 1) + 34
    style = f"""
.rl   {{ font-size: 13px; fill: {FG}; }}
.rc   {{ font-size: 11px; fill: {GRAY}; }}
.ax   {{ font-size: 11px; fill: {GRAY}; }}
.hd   {{ font-size: 13px; fill: {GREEN}; font-weight: 700; }}
.bar  {{ transform-box: fill-box; transform-origin: left center;
        animation: grow .7s cubic-bezier(.2,.8,.2,1) backwards; }}
@keyframes grow {{ from {{ transform: scaleX(.02) }} to {{ transform: scaleX(1) }} }}
.lbl  {{ animation: fin .5s ease-out backwards; }}
@keyframes fin {{ from {{ opacity: 0; transform: translateX(-6px) }}
                 to {{ opacity: 1; transform: translateX(0) }} }}
"""
    b = [
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="{BG}"/>',
        f'<text class="mono hd" x="24" y="32">ledq@github:~$ git log --graph --since=2023</text>',
    ]
    # year gridlines
    for m, yr in ((1, "2024"), (13, "2025"), (25, "2026")):
        x = mx(m)
        b.append(f'<line x1="{x:.1f}" y1="{top - 12}" x2="{x:.1f}" y2="{h - 30}" stroke="{BG1}"/>')
        b.append(f'<text class="mono ax" x="{x:.1f}" y="{h - 12}" text-anchor="middle">{yr}</text>')

    # education band
    ey = top + 6
    b.append(
        f'<rect class="bar" x="{X0}" y="{ey}" width="{mx(24) - X0:.1f}" height="10" rx="5" '
        f'fill="{BG2}" style="animation-delay:0s"/>'
    )
    b.append(
        f'<g class="lbl" style="animation-delay:.1s">'
        f'<text class="mono rc" x="{X0 - 12}" y="{ey + 9}" text-anchor="end">b.s. computer science</text></g>'
    )

    for i, (role, org, s, e, col) in enumerate(ROLES):
        y = top + rh * (i + 1)
        x, bw = mx(s), max(mx(e) - mx(s), 6)
        d = f"{0.12 + 0.09 * i:.2f}s"
        b.append(
            f'<rect class="bar" x="{x:.1f}" y="{y}" width="{bw:.1f}" height="18" rx="9" '
            f'fill="{col}" style="animation-delay:{d}"/>'
        )
        b.append(
            f'<g class="lbl" style="animation-delay:{d}">'
            f'<text class="mono rl" x="{X0 - 12}" y="{y + 9}" text-anchor="end">{esc(role)}</text>'
            f'<text class="mono rc" x="{X0 - 12}" y="{y + 24}" text-anchor="end">{esc(org)}</text></g>'
        )
    return svg(w, h, "\n".join(b), style, "career timeline, december 2023 to june 2026")


# --------------------------------------------------------------------------
# 3. project cards
# --------------------------------------------------------------------------

# One card per public non-fork repo, ordered by what is worth seeing first.
# lang colors are GitHub linguist's; stars are a snapshot, refresh when they move.
LANG = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "Shell": "#89e051",
    "HTML": "#e34c26", "MATLAB": "#e16737", "Java": "#b07219",
}

# Which of the catalog below actually gets a card. Swap a slug to reshuffle.
PINNED = ["resumery", "FDA-AI-Devices", "silero-vad-pi-zero32",
          "deepsilk-backend", "Room-Classifier", "CleFer"]

# (slug, description, language, stars, owner)
REPOS = [
    ("resumery", "resume tailoring agents over an evidence bank", "Python", 1, "ledq"),
    ("FDA-AI-Devices", "multi-agent regulatory intelligence, fda data", "TypeScript", 0,
     "scrivner-solutions"),
    ("silero-vad-pi-zero32", "real-time voice detection on a 512MB pi zero", "Python", 2, "ledq"),
    ("deepsilk-backend", "about 100 classes at roughly 80% mAP", "Python", 0, "ledq"),
    ("deepsilk-frontend", "front end for the deepsilk detector", "TypeScript", 0, "ledq"),
    ("speechbrain_vad", "voice detection on a raspberry pi, via speechbrain", "Python", 0, "ledq"),
    ("netsec-project", "network security project", "Shell", 0, "ledq"),
    ("CleFer", "chords, lyrics, and contributions for guitarists", "HTML", 0, "ledq"),
    ("Room-Classifier", "cnn classifying room types from photos", "MATLAB", 0, "ledq"),
    ("Arcade-game-Bomb-Jack", "bomb jack, rebuilt", "Java", 0, "ledq"),
    ("Laptop-Finder", "laptop search tool", "Java", 0, "ledq"),
    ("TickyTag-Game", "", "Python", 0, "ledq"),
]


def build_repo_tile(slug, desc, lang, stars, owner="ledq"):
    accent = CARD_ACCENT
    title = slug if owner == "ledq" else f"{owner}/{slug}"
    top = PVH if PREVIEWS else 0
    w, h = 430, top + 118
    anim = f"""
.in {{ animation: rise .55s cubic-bezier(.2,.8,.2,1) backwards; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(8px) }}
                  to {{ opacity: 1; transform: translateY(0) }} }}
.ac {{ transform-box: fill-box; transform-origin: top center;
      animation: drop .5s cubic-bezier(.2,.8,.2,1) backwards; }}
@keyframes drop {{ from {{ transform: scaleY(0) }} to {{ transform: scaleY(1) }} }}
""" if PREVIEWS else ""
    def grp(delay):  # animation hooks only exist when previews are on
        return f'<g class="in" style="animation-delay:{delay}">' if PREVIEWS else "<g>"

    ac = ' class="ac"' if PREVIEWS else ""
    b = [f'<rect x="0" y="0" width="{w}" height="{h}" rx="9" fill="{BG}" stroke="{BG1}"/>']
    pv_css = ""
    if PREVIEWS:
        pv_body, pv_css = PREVIEW[slug](accent)
        b += [
            f'<rect x="0" y="0" width="{w}" height="{PVH}" rx="9" fill="{BAND}"/>',
            f'<rect x="0" y="{PVH - 12}" width="{w}" height="12" fill="{BAND}"/>',
            "\n".join(pv_body),
            f'<line x1="0" y1="{PVH}" x2="{w}" y2="{PVH}" stroke="{BG1}"/>',
        ]
    style = f"""
.t  {{ font-size: 14.5px; fill: {accent}; font-weight: 700; }}
.d  {{ font-size: 12px; fill: {FG}; }}
.g  {{ font-size: 11px; fill: {FG_DIM}; }}
{anim}{pv_css}"""
    b += [
        f'<rect{ac} x="0" y="0" width="4" height="{h}" fill="{accent}"/>',
        grp(".08s") +
        f'<text class="mono t" x="24" y="{top + 38}">{esc(title)}</text></g>',
    ]
    if desc:
        b.append(
            grp(".16s") +
            f'<text class="mono d" x="24" y="{top + 63}">{esc(desc)}</text></g>'
        )
    foot = [
        f'<circle cx="29" cy="{top + 88}" r="5.5" fill="{LANG.get(lang, GRAY)}"/>',
        f'<text class="mono g" x="42" y="{top + 92}">{esc(lang)}</text>',
    ]
    if stars:
        sx = 42 + len(lang) * 6.6 + 18
        foot.append(
            f'<path d="M0 0l1.9 3.9 4.3.6-3.1 3 .7 4.3L0 9.8l-3.8 2 .7-4.3-3.1-3 4.3-.6z" '
            f'transform="translate({sx},{top + 84})" fill="{YELLOW}"/>'
        )
        foot.append(f'<text class="mono g" x="{sx + 10}" y="{top + 92}">{stars}</text>')
    b.append(grp(".24s") + "".join(foot) + "</g>")
    return f"repo-{slug.lower()}.{CARD_V}", svg(w, h, "\n".join(b), style, f"{title}: {desc or lang}")


# --------------------------------------------------------------------------
# 4. stack: brand glyphs, grouped
# --------------------------------------------------------------------------

# Glyph paths come from Simple Icons (CC0), vendored into icons.json so this
# script never needs the network. Colors are brand hex, brightened where the
# official one disappears against a dark background.
STACK = [
    ("languages", [("python", "Python", "#4B8BBE"),
                   ("typescript", "TypeScript", "#4C9BE8"),
                   ("javascript", "JavaScript", "#F7DF1E"),
                   ("cplusplus", "C/C++", "#659AD2")]),
    ("cloud", [("googlecloud", "GCP", "#4285F4"),
               ("googlecloudstorage", "GCS", "#AECBFA"),
               ("docker", "Docker", "#2496ED"),
               ("terraform", "Terraform", "#A06CE4"),
               ("git", "Git", "#F05032")]),
    ("data", [("googlebigquery", "BigQuery", "#669DF6"),
              ("apacheairflow", "Airflow", "#2196F3"),
              ("postgresql", "Postgres", "#7CA9E8"),
              ("metabase", "Metabase", "#509EE3"),
              ("airbyte", "Airbyte", "#8B88FF"),
              ("tableau", "Tableau", "#E97627")]),
    ("web", [("nextdotjs", "Next.js", FG),
             ("react", "React", "#61DAFB"),
             ("fastapi", "FastAPI", "#12B5A6"),
             ("graphql", "GraphQL", "#F04FB4"),
             ("tailwindcss", "Tailwind", "#06B6D4"),
             ("mui", "Material UI", "#007FFF"),
             ("shadcnui", "shadcn/ui", FG),
             ("drizzle", "Drizzle", "#C5F74F"),
             ("betterauth", "Better Auth", FG)]),
    ("ml", [("pytorch", "PyTorch", "#EE4C2C"),
            ("ultralytics", "YOLOv8", "#6E8BFF"),
            ("onnx", "ONNX", "#6E9BFF"),
            ("langchain", "LangChain", AQUA),
            ("kaggle", "Kaggle", "#20BEFF")]),
    ("systems", [("linux", "Linux", FG),
                 ("raspberrypi", "Raspberry Pi", "#E8437A"),
                 ("ros", "ROS2", "#83A598")]),
]

# Real parts of the stack with no brand glyph to draw.
PILLS = ["Dataform", "Graphile", "LangGraph", "XGBoost", "SHAP", "Cloud Run",
         "Cloud Build", "Secret Manager", "Datastream", "Fivetran", "vector DB",
         "Silero VAD", "xv6", "UART", "COCO"]

ICON = 30
GAP = 78


def build_stack():
    icons = json.loads((OUT / "icons.json").read_text())
    w = 900
    top, rh = 62, 66
    h = top + rh * len(STACK) + 76
    style = f"""
.cat  {{ font-size: 12px; fill: {YELLOW}; font-weight: 700; }}
.nm   {{ font-size: 10px; fill: {GRAY}; }}
.hd   {{ font-size: 13px; fill: {GREEN}; font-weight: 700; }}
.ic   {{ transform-box: fill-box; transform-origin: center;
        animation: pop .5s cubic-bezier(.2,.8,.2,1) backwards; }}
@keyframes pop {{ from {{ opacity: 0; transform: scale(.4) }}
                 to {{ opacity: 1; transform: scale(1) }} }}
.flt  {{ animation: bob 3.6s ease-in-out infinite; }}
@keyframes bob {{ 0%,100% {{ transform: translateY(0) }}
                 50% {{ transform: translateY(-3px) }} }}
"""
    b = [
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="{BG}"/>',
        f'<text class="mono hd" x="24" y="36">ledq@github:~$ stack --icons</text>',
    ]
    n = 0
    for r, (cat, items) in enumerate(STACK):
        y = top + rh * r
        b.append(
            f'<text class="mono cat" x="132" y="{y + 20}" text-anchor="end">{esc(cat)}</text>'
        )
        for c, (slug, label, col) in enumerate(items):
            x = 160 + c * GAP
            d, dl = icons[slug]["d"], f"{0.05 * n:.2f}s"
            n += 1
            b.append(
                f'<g transform="translate({x},{y})">'
                f'<g class="flt" style="animation-delay:{dl}">'
                f'<g class="ic" style="animation-delay:{dl}">'
                f'<path d="{d}" fill="{col}" transform="scale({ICON / 24:.4f})"/>'
                f"</g></g>"
                f'<text class="mono nm" x="{ICON / 2}" y="{ICON + 15}" '
                f'text-anchor="middle">{esc(label)}</text></g>'
            )

    # pill row: everything real that has no logo
    py = top + rh * len(STACK) + 4
    b.append(f'<text class="mono cat" x="132" y="{py + 15}" text-anchor="end">also</text>')
    px = 160
    for i, p in enumerate(PILLS):
        pw = 14 + len(p) * 6.3
        if px + pw > 872:
            px, py = 160, py + 26
        b.append(
            f'<g class="ic" style="animation-delay:{0.05 * (n + i):.2f}s">'
            f'<rect x="{px:.1f}" y="{py}" width="{pw:.1f}" height="21" rx="10.5" '
            f'fill="{BG1}"/>'
            f'<text class="mono nm" x="{px + pw / 2:.1f}" y="{py + 14}" '
            f'text-anchor="middle">{esc(p)}</text></g>'
        )
        px += pw + 7
    return svg(w, h, "\n".join(b), style, "stack: languages, cloud, data, web, ml, and systems")


def main():
    (OUT / f"stack.{CARD_V}.svg").write_text(build_stack(), encoding="utf-8")
    (OUT / f"card.{CARD_V}.svg").write_text(build_card(), encoding="utf-8")
    (OUT / f"timeline.{CARD_V}.svg").write_text(build_timeline(), encoding="utf-8")
    for slug, desc, lang, stars, owner in REPOS:
        if slug not in PINNED:
            continue
        name, doc = build_repo_tile(slug, desc, lang, stars, owner)
        (OUT / f"{name}.svg").write_text(doc, encoding="utf-8")
    print("wrote", len(PINNED) + 3, "svgs to", OUT)


if __name__ == "__main__":
    main()
