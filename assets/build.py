#!/usr/bin/env python3
"""Render the profile SVGs. Run: python3 assets/build.py

Content lives in profile.toml; this file is the renderer. Everything is
hand-rolled SVG with inline CSS animation, self-hosted, so the profile has no
third-party service in the render path. Palette is gruvbox dark.

Output filenames carry a hash of the inputs, because GitHub's camo proxy caches
images by URL and would otherwise keep serving a stale card. The build rewrites
the README's image refs to match and deletes the assets it supersedes.
"""

import hashlib
import json
import re
import tomllib
from pathlib import Path

OUT = Path(__file__).parent
ROOT = OUT.parent
DATA = ROOT / "profile.toml"
README = ROOT / "README.md"

BG, BG1, BG2, GRAY = "#282828", "#3c3836", "#504945", "#928374"
FG, FG_DIM = "#ebdbb2", "#a89984"
RED, GREEN, YELLOW, BLUE = "#fb4934", "#b8bb26", "#fabd2f", "#83a598"
PURPLE, AQUA, ORANGE = "#d3869b", "#8ec07c", "#fe8019"

PALETTE = {"bg": BG, "bg1": BG1, "bg2": BG2, "gray": GRAY, "fg": FG,
           "fg_dim": FG_DIM, "red": RED, "green": GREEN, "yellow": YELLOW,
           "blue": BLUE, "purple": PURPLE, "aqua": AQUA, "orange": ORANGE}

MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "DejaVu Sans Mono", monospace'

HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n'

# Every repo card uses one accent; per-repo colours read as noise, not signal.
CARD_ACCENT = "#fabd2f"

D = tomllib.loads(DATA.read_text(encoding="utf-8"))
ICONS = json.loads((OUT / "icons.json").read_text(encoding="utf-8"))


def col(name):
    """Palette name or raw hex; anything unknown passes straight through."""
    return PALETTE.get(name, name)


def version():
    """Short hash of every input that can change a rendered byte."""
    h = hashlib.sha256()
    for p in (DATA, Path(__file__), OUT / "icons.json"):
        h.update(p.read_bytes())
    return h.hexdigest()[:7]


CARD_V = version()


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


def prompt(x, y, cls, cmd="", cursor=False):
    """The shell prompt, coloured the way a gruvbox shell draws it."""
    t = (f'<text class="mono {cls}" x="{x}" y="{y}" xml:space="preserve">'
         f'<tspan fill="{GREEN}" font-weight="700">{esc(D["card"]["host"])}</tspan>'
         f'<tspan fill="{FG}">:</tspan><tspan fill="{BLUE}">~</tspan>'
         f'<tspan fill="{FG}">$ </tspan>')
    if cmd:
        t += f'<tspan fill="{FG_DIM}">{esc(cmd)}</tspan>'
    if cursor:
        t += '<tspan class="cur">\u2588</tspan>'
    return t + "</text>"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------------
# 1. hero: neofetch-style card
# --------------------------------------------------------------------------

WORDMARK = D["wordmark"].strip("\n").split("\n")
INFO = D["info"]

# The glyph library the INFO rows draw from, the way a riced fastfetch config
# puts a nerd-font icon in front of every key. Nerd fonts are not installed on
# GitHub's renderer, so these are hand-drawn line icons on a 16x16 grid.
FIELD_ICONS = {
    "briefcase": '<rect x="2" y="5.4" width="12" height="8.2" rx="1.2"/>'
        '<path d="M6 5.4V4.1h4v1.3M2 9.1h12"/>',
    "target": '<circle cx="8" cy="8" r="5.6"/><circle cx="8" cy="8" r="2.4"/>'
        '<circle cx="8" cy="8" r="0.9" stroke="none" fill="currentColor"/>',
    "code": '<path d="M5.6 4.6 2 8l3.6 3.4M10.4 4.6 14 8l-3.6 3.4'
        'M9.5 3.3 6.5 12.7"/>',
    "cloud": '<path d="M4.7 12.6h6.6a3 3 0 0 0 .3-6 4.1 4.1 0 0 0-7.6-.6'
        'A2.9 2.9 0 0 0 4.7 12.6z"/>',
    "database": '<ellipse cx="8" cy="4.2" rx="5.2" ry="2"/>'
        '<path d="M2.8 4.2v7.6c0 1.1 2.3 2 5.2 2s5.2-.9 5.2-2V4.2'
        'M2.8 8c0 1.1 2.3 2 5.2 2s5.2-.9 5.2-2"/>',
    "globe": '<circle cx="8" cy="8" r="5.6"/>'
        '<path d="M2.4 8h11.2M8 2.4c1.5 1.7 2.3 3.5 2.3 5.6S9.5 11.9 8 13.6'
        'C6.5 11.9 5.7 10.1 5.7 8S6.5 4.1 8 2.4z"/>',
    "network": '<path d="m4.7 5.2 2 1.9m-2 3.7 2-1.9m2.6-1.8 2-1.9m-2 3.7 2 1.9"/>'
        '<circle cx="3.4" cy="4.4" r="1.3"/><circle cx="3.4" cy="11.6" r="1.3"/>'
        '<circle cx="8" cy="8" r="1.3"/><circle cx="12.6" cy="4.4" r="1.3"/>'
        '<circle cx="12.6" cy="11.6" r="1.3"/>',
    "cap": '<path d="M8 2.9 1.5 6.1 8 9.3l6.5-3.2L8 2.9z"/>'
        '<path d="M4.4 7.6V11c0 1 1.6 1.9 3.6 1.9s3.6-.9 3.6-1.9V7.6"/>',
    "dot": '<circle cx="8" cy="8" r="2.4" stroke="none" fill="currentColor"/>'
        '<circle class="ping" cx="8" cy="8" r="5.2"/>',
}
FALLBACK_ICON = '<circle cx="8" cy="8" r="2.2" stroke="none" fill="currentColor"/>'
FIELD_ICON = 15

CARD_ICONS = D["card"]["icons"]
CARD_ICON = 22
CARD_PITCH = 30


def build_card():
    # width has slack for the longest INFO value; check after editing INFO
    w, h = 940, 400
    host = D["card"]["host"]
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
.fi   {{ stroke-width: 1.4; stroke-linecap: round; stroke-linejoin: round; }}
.ping {{ transform-box: fill-box; transform-origin: center;
        animation: ping 2.6s ease-out infinite; }}
@keyframes ping {{ 0% {{ opacity: .75; transform: scale(.62) }}
                  70%,100% {{ opacity: 0; transform: scale(1.15) }} }}
.row  {{ animation: fade .5s ease-out backwards; }}
@keyframes fade {{ from {{ opacity: 0 }} to {{ opacity: 1 }} }}
"""
    b = [
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="{BG}"/>',
        f'<rect x="0" y="0" width="{w}" height="30" rx="10" fill="{BG1}"/>',
        f'<rect x="0" y="20" width="{w}" height="10" fill="{BG1}"/>',
        # the terminal app icon: a screen with a prompt in it
        f'<rect x="12" y="4" width="25" height="22" rx="3.5" fill="#1d2021" '
        f'stroke="{BG2}"/>',
        f'<g stroke="{GREEN}" stroke-width="1.9" fill="none" stroke-linecap="round" '
        f'stroke-linejoin="round"><path d="M18 10l5 5-5 5"/>'
        f'<path d="M25 20.5h6.5"/></g>',
        # minimise / maximise / close, right-aligned the way GTK and Qt do it
        f'<g stroke="{GRAY}" stroke-width="1.3" fill="none" stroke-linecap="round">'
        f'<path d="M{w - 84} 15h10"/>'
        f'<rect x="{w - 58}" y="10" width="10" height="10" rx="1.5"/>'
        f'<path d="M{w - 32} 10l10 10M{w - 22} 10l-10 10"/></g>',
        f'<text class="mono ttl" x="{w / 2}" y="19" text-anchor="middle">'
        f'{esc(D["card"]["title"])}</text>',
        f'<text class="mono logo" x="40" y="82" xml:space="preserve">{tspans(40, WORDMARK, 19)}</text>',
        f'<text class="mono head" x="360" y="62">{esc(host)}</text>',
        f'<text class="mono dim" x="360" y="80">{"-" * len(host)}</text>',
    ]
    for i, row in enumerate(INFO):
        k, v = row["key"], row["value"]
        y = 106 + i * 21
        d = f"{0.05 * i:.2f}s"
        c = col(row.get("color", "yellow"))
        glyph = FIELD_ICONS.get(row.get("icon", ""), FALLBACK_ICON)
        b.append(
            f'<g class="row" style="animation-delay:{d}">'
            f'<g class="fi" stroke="{c}" fill="none" style="color:{c}" '
            f'transform="translate(358,{y - 12}) scale({FIELD_ICON / 16:.4f})">'
            f"{glyph}</g>"
            f'<text class="mono key" x="382" y="{y}">{esc(k)}</text>'
            f'<text class="mono val" x="450" y="{y}">{esc(v)}</text></g>'
        )
    colors = {slug: c for _, items in STACK for slug, _, c in items}
    for r, row in enumerate(CARD_ICONS):
        for c, slug in enumerate(row):
            x, y = 360 + c * CARD_PITCH, 300 + r * 32
            d = f"{0.6 + 0.03 * (r * 8 + c):.2f}s"
            b.append(
                f'<g transform="translate({x},{y})">'
                f'<g class="sw" style="animation-delay:{d}">'
                f'<path d="{ICONS[slug]["d"]}" fill="{colors[slug]}" '
                f'transform="scale({CARD_ICON / 24:.4f})"/>'
                f"</g></g>"
            )
    b.append(prompt(40, h - 18, "head", cursor=True))
    role = next((r["value"] for r in INFO if r["key"] == "Role"), "engineer")
    return svg(w, h, "\n".join(b), style, f"ledq / duy le: {role.lower()}")


# --------------------------------------------------------------------------
# 2. timeline: roles as animated bars
# --------------------------------------------------------------------------

TL = D["timeline"]
ROLES = [(r["role"], r["org"], r["start"], r["end"], col(r["color"]))
         for r in TL["roles"]]
SPAN = TL["span"]  # months since dec 2023
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
    for m, yr in TL["years"]:
        x = mx(m)
        b.append(f'<line x1="{x:.1f}" y1="{top - 12}" x2="{x:.1f}" y2="{h - 30}" stroke="{BG1}"/>')
        b.append(f'<text class="mono ax" x="{x:.1f}" y="{h - 12}" text-anchor="middle">{yr}</text>')

    # education band
    ey = top + 6
    edu = TL["education"]
    b.append(
        f'<rect class="bar" x="{mx(edu["start"]):.1f}" y="{ey}" '
        f'width="{mx(edu["end"]) - mx(edu["start"]):.1f}" height="10" rx="5" '
        f'fill="{BG2}" style="animation-delay:0s"/>'
    )
    b.append(
        f'<g class="lbl" style="animation-delay:.1s">'
        f'<text class="mono rc" x="{X0 - 12}" y="{ey + 9}" text-anchor="end">'
        f'{esc(edu["label"])}</text></g>'
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
# 4. contact: one card per link, plus an availability strip
# --------------------------------------------------------------------------

CONTACT = D["contact"]


def build_contact_card(link):
    """A command and its output, so the section reads as the same session."""
    w, h = 430, 72
    style = f"""
.p {{ font-size: 12.5px; }}
.v {{ font-size: 13px; fill: {FG}; }}
"""
    b = [
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" fill="{BG}" '
        f'stroke="{BG1}"/>',
        prompt(18, 27, "p", link["cmd"]),
        f'<g transform="translate(18,39)"><path d="{ICONS[link["icon"]]["d"]}" '
        f'fill="{col(link["color"])}" transform="scale({17 / 24:.4f})"/></g>',
        f'<text class="mono v" x="45" y="53">{esc(link["value"])}</text>',
    ]
    return (f"contact-{link['name']}.{CARD_V}",
            svg(w, h, "\n".join(b), style, f'{link["label"]}: {link["value"]}'))


# --------------------------------------------------------------------------
# 4. stack: brand glyphs, grouped
# --------------------------------------------------------------------------

# Glyph paths come from Simple Icons (CC0), vendored into icons.json so this
# script never needs the network.
STACK = [(g["name"], [(i["slug"], i["label"], col(i.get("color", "fg")))
                      for i in g["items"]]) for g in D["stack"]["groups"]]
PILLS = D["stack"]["pills"]

ICON = 30
GAP = 78


def build_stack():
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
            d, dl = ICONS[slug]["d"], f"{0.05 * n:.2f}s"
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


def sync_readme(written):
    """Repoint the README at this build's filenames, leaving prose alone."""
    md = README.read_text(encoding="utf-8")
    out = re.sub(r"assets/([a-z0-9_-]+)\.[a-z0-9]+\.svg",
                 lambda m: f"assets/{m.group(1)}.{CARD_V}.svg", md)
    missing = {m for m in re.findall(r"assets/([a-z0-9_.-]+\.svg)", out)
               if m not in written}
    if out != md:
        README.write_text(out, encoding="utf-8")
    return missing


def validate():
    """Turn a typo in profile.toml into a sentence instead of a KeyError."""
    known = {slug for _, items in STACK for slug, _, _ in items}
    for row in INFO:
        if row.get("icon") and row["icon"] not in FIELD_ICONS:
            raise SystemExit(f"profile.toml: {row['key']} wants icon "
                             f"'{row['icon']}'; build.py draws {sorted(FIELD_ICONS)}")
    for slug in (s for row in CARD_ICONS for s in row):
        if slug not in known:
            raise SystemExit(f"profile.toml: card icon '{slug}' is in no "
                             f"[[stack.groups]] block, so it has no colour")
    for link in CONTACT["links"]:
        if link["icon"] not in ICONS:
            raise SystemExit(f"profile.toml: contact '{link['name']}' wants icon "
                             f"'{link['icon']}', not vendored in assets/icons.json")
    for slug in known:
        if slug not in ICONS:
            raise SystemExit(f"profile.toml: '{slug}' is not vendored in "
                             f"assets/icons.json")


def main():
    validate()
    docs = {f"stack.{CARD_V}.svg": build_stack(),
            f"card.{CARD_V}.svg": build_card(),
            f"timeline.{CARD_V}.svg": build_timeline()}
    for link in CONTACT["links"]:
        name, doc = build_contact_card(link)
        docs[f"{name}.svg"] = doc
    for name, doc in docs.items():
        (OUT / name).write_text(doc, encoding="utf-8")

    stale = [p for p in OUT.glob("*.svg") if p.name not in docs]
    for p in stale:
        p.unlink()

    missing = sync_readme(set(docs))
    print(f"{len(docs)} svgs at {CARD_V}, {len(stale)} superseded, README synced")
    for m in sorted(missing):
        print(f"  ! README wants {m}, which nothing generated")


if __name__ == "__main__":
    main()
