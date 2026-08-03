#!/usr/bin/env python3
"""Animated preview bands for the repo cards. PARKED, not currently rendered.

These drew a 430x120 illustration on top of each project card: a pipeline for
resumery, an agent graph for FDA-AI-Devices, a waveform for the VAD work, and
so on. To bring them back, set PREVIEWS = True in build.py and re-run it.

Palette constants are duplicated here rather than imported from build.py, so
this module stays standalone and cannot create a circular import.
"""

BG, BG1, BG2, GRAY = "#282828", "#3c3836", "#504945", "#928374"
FG, FG_DIM = "#ebdbb2", "#a89984"

import math

# --- preview bands -------------------------------------------------------
# Each returns (elements, css). Deliberately diagrammatic: these illustrate what
# a project does, they are not screenshots and carry no measured numbers.

BAND = "#1d2021"
PVW, PVH = 430, 120


def pv_pipeline(accent):
    """resumery: bank and posting walk the agent pipeline into a pdf."""
    stages, bw, gap, x0 = ["bank", "draft", "eval", "pdf"], 84, 12, 26
    b = []
    for i, s in enumerate(stages):
        xi = x0 + i * (bw + gap)
        b.append(
            f'<rect class="st" style="animation-delay:{i * 0.5:.1f}s" x="{xi}" y="46" '
            f'width="{bw}" height="30" rx="6" fill="{BG1}" stroke="{BG2}"/>'
            f'<text class="mono pl" x="{xi + bw / 2}" y="65" text-anchor="middle">{s}</text>'
        )
        if i < len(stages) - 1:
            b.append(f'<line x1="{xi + bw}" y1="61" x2="{xi + bw + gap}" y2="61" stroke="{BG2}"/>')
    b.append(f'<circle class="dot" cx="32" cy="61" r="4" fill="{accent}"/>')
    css = f"""
.pl {{ font-size: 11px; fill: {FG_DIM}; }}
.st {{ animation: hl 2.4s ease-in-out infinite; }}
@keyframes hl {{ 0%,72%,100% {{ stroke: {BG2} }} 18%,52% {{ stroke: {accent} }} }}
.dot {{ animation: run 2.4s linear infinite; }}
@keyframes run {{ from {{ transform: translateX(0) }} to {{ transform: translateX(366px) }} }}
"""
    return b, css


def pv_agents(accent):
    """FDA-AI-Devices: a query walking a multi-agent graph."""
    nodes = [(52, 60), (146, 32), (146, 88), (240, 60), (338, 36), (338, 84)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5)]
    b = []
    for i, (a, c) in enumerate(edges):
        x1, y1 = nodes[a]
        x2, y2 = nodes[c]
        b.append(
            f'<line class="ed" style="animation-delay:{i * 0.28:.2f}s" x1="{x1}" y1="{y1}" '
            f'x2="{x2}" y2="{y2}" stroke="{BG2}" stroke-width="1.5"/>'
        )
    for i, (x, y) in enumerate(nodes):
        b.append(
            f'<circle class="nd" style="animation-delay:{i * 0.28:.2f}s" cx="{x}" cy="{y}" '
            f'r="11" fill="{BG1}" stroke="{accent}" stroke-width="1.5"/>'
        )
    css = f"""
.ed {{ animation: sig 2.4s ease-in-out infinite; }}
@keyframes sig {{ 0%,60%,100% {{ stroke: {BG2} }} 20%,40% {{ stroke: {accent} }} }}
.nd {{ transform-box: fill-box; transform-origin: center;
      animation: beat 2.4s ease-in-out infinite; }}
@keyframes beat {{ 0%,60%,100% {{ transform: scale(1); opacity: .55 }}
                  22%,42% {{ transform: scale(1.25); opacity: 1 }} }}
"""
    return b, css


def pv_wave(accent):
    """silero-vad: speech regions standing out of the noise floor."""
    n, x0, bw, gap = 57, 24, 4, 3
    speech = set(range(9, 21)) | set(range(34, 49))
    b = []
    for i in range(n):
        loud = i in speech
        amp = 26 * abs(math.sin(i * 0.7)) + 6 if loud else 4 * abs(math.sin(i * 1.9)) + 2
        xi = x0 + i * (bw + gap)
        cls = ' class="wv"' if loud else ""
        dly = f' style="animation-delay:{(i % 9) * 0.09:.2f}s"' if loud else ""
        b.append(
            f'<rect{cls}{dly} x="{xi}" y="{58 - amp:.1f}" width="{bw}" '
            f'height="{2 * amp:.1f}" rx="2" fill="{accent if loud else BG2}"/>'
        )
    for s, e in ((9, 20), (34, 48)):
        xa, xb = x0 + s * (bw + gap), x0 + e * (bw + gap) + bw
        b.append(
            f'<path d="M{xa} 96v6h{xb - xa}v-6" fill="none" stroke="{BG2}"/>'
            f'<text class="mono pl" x="{(xa + xb) / 2}" y="116" text-anchor="middle">speech</text>'
        )
    b.append(f'<line class="ph" x1="0" y1="14" x2="0" y2="92" stroke="{FG_DIM}" opacity=".5"/>')
    css = f"""
.pl {{ font-size: 10px; fill: {FG_DIM}; }}
.wv {{ transform-box: fill-box; transform-origin: center;
      animation: amp 1.1s ease-in-out infinite alternate; }}
@keyframes amp {{ from {{ transform: scaleY(.55) }} to {{ transform: scaleY(1) }} }}
.ph {{ animation: sweep 4s linear infinite; }}
@keyframes sweep {{ from {{ transform: translateX(24px) }} to {{ transform: translateX(420px) }} }}
"""
    return b, css


def pv_boxes(accent):
    """deepsilk: detections drawing themselves over a frame."""
    b = [f'<rect x="24" y="16" width="382" height="88" rx="4" fill="{BG1}" opacity=".45"/>']
    dets = [(44, 34, 92, 54, "0"), (168, 48, 74, 44, "1"), (272, 28, 108, 62, "2")]
    for i, (x, y, w_, h_, lab) in enumerate(dets):
        per = 2 * (w_ + h_)
        b.append(
            f'<rect class="bx" style="animation-delay:{i * 0.35:.2f}s;stroke-dasharray:{per}" '
            f'x="{x}" y="{y}" width="{w_}" height="{h_}" fill="none" '
            f'stroke="{accent}" stroke-width="2"/>'
            f'<rect class="cp" style="animation-delay:{i * 0.35 + 0.5:.2f}s" x="{x}" y="{y - 13}" '
            f'width="26" height="13" rx="2" fill="{accent}"/>'
            f'<text class="mono cl" x="{x + 13}" y="{y - 3}" text-anchor="middle">{lab}</text>'
        )
    css = f"""
.cl {{ font-size: 9px; fill: {BG}; font-weight: 700; }}
.bx {{ animation: draw 3.2s ease-in-out infinite; }}
@keyframes draw {{ 0% {{ stroke-dashoffset: 320 }} 35%,80% {{ stroke-dashoffset: 0 }}
                  100% {{ stroke-dashoffset: 320 }} }}
.cp {{ animation: chip 3.2s ease-in-out infinite; }}
@keyframes chip {{ 0%,10% {{ opacity: 0 }} 30%,80% {{ opacity: 1 }} 100% {{ opacity: 0 }} }}
"""
    return b, css


def pv_rooms(accent):
    """Room-Classifier: one of four classes selected."""
    labels = ["bedroom", "kitchen", "living", "bath"]
    b = []
    for i, lab in enumerate(labels):
        x = 26 + i * 96
        if i == 0:  # bed: headboard, mattress, pillow
            icon = (f"M{x + 22} 44v22 M{x + 22} 66h40v-10h-40 "
                    f"M{x + 28} 56v-7h11v7 M{x + 62} 66v-6")
        elif i == 1:  # pot: lid, body, steam
            icon = (f"M{x + 26} 51h32 M{x + 42} 51v-4 M{x + 29} 51v11a3 3 0 003 3h20a3 3 0 003-3v-11 "
                    f"M{x + 36} 42v-5 M{x + 48} 42v-5")
        elif i == 2:  # sofa: back, arms, seat
            icon = (f"M{x + 26} 58v-8h32v8 M{x + 22} 58h40v7h-40z "
                    f"M{x + 22} 58v-5 M{x + 62} 58v-5 M{x + 26} 65v4 M{x + 58} 65v4")
        else:  # tub: faucet, basin, feet
            icon = (f"M{x + 26} 54v-9h7 M{x + 22} 54h40v6a6 6 0 01-6 6h-28a6 6 0 01-6-6z "
                    f"M{x + 28} 66v4 M{x + 56} 66v4")
        b.append(
            f'<rect class="tile" style="animation-delay:{i * 1.0:.1f}s" x="{x}" y="26" '
            f'width="84" height="56" rx="6" fill="{BG1}" stroke="{BG2}"/>'
            f'<path d="{icon}" stroke="{FG_DIM}" fill="none" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
            f'<text class="mono pl" x="{x + 42}" y="98" text-anchor="middle">{lab}</text>'
        )
    css = f"""
.pl {{ font-size: 10px; fill: {FG_DIM}; }}
.tile {{ animation: pick 4s ease-in-out infinite; }}
@keyframes pick {{ 0%,20%,100% {{ stroke: {BG2}; fill: {BG1} }}
                  5%,15% {{ stroke: {accent}; fill: {BG2} }} }}
"""
    return b, css


def pv_chord(accent):
    """CleFer: a search resolving into a chord shape."""
    b = [
        f'<rect x="26" y="18" width="378" height="24" rx="12" fill="{BG1}" stroke="{BG2}"/>',
        f'<circle cx="44" cy="30" r="5" fill="none" stroke="{FG_DIM}" stroke-width="1.5"/>',
        f'<line x1="48" y1="34" x2="52" y2="38" stroke="{FG_DIM}" stroke-width="1.5"/>',
        f'<text class="mono pl" x="64" y="34">chords, lyrics</text>',
        f'<rect class="car" x="152" y="22" width="7" height="16" fill="{accent}"/>',
    ]
    gx, gy = 170, 56
    for s in range(6):
        b.append(f'<line x1="{gx + s * 18}" y1="{gy}" x2="{gx + s * 18}" y2="{gy + 44}" stroke="{BG2}"/>')
    for f_ in range(4):
        b.append(f'<line x1="{gx}" y1="{gy + f_ * 14.6:.1f}" x2="{gx + 90}" y2="{gy + f_ * 14.6:.1f}" stroke="{BG2}"/>')
    for i, (s, f_) in enumerate(((1, 1), (2, 2), (3, 2))):
        b.append(
            f'<circle class="fd" style="animation-delay:{i * 0.3:.1f}s" cx="{gx + s * 18}" '
            f'cy="{gy + f_ * 14.6 - 7:.1f}" r="6" fill="{accent}"/>'
        )
    css = f"""
.pl {{ font-size: 11px; fill: {FG_DIM}; }}
.car {{ animation: blink 1.06s steps(1) infinite; }}
@keyframes blink {{ 0%,50% {{ opacity: 1 }} 50.01%,100% {{ opacity: 0 }} }}
.fd {{ transform-box: fill-box; transform-origin: center;
      animation: press 3s ease-in-out infinite; }}
@keyframes press {{ 0%,15% {{ transform: scale(0); opacity: 0 }}
                   30%,85% {{ transform: scale(1); opacity: 1 }}
                   100% {{ transform: scale(0); opacity: 0 }} }}
"""
    return b, css


PREVIEW = {
    "resumery": pv_pipeline,
    "FDA-AI-Devices": pv_agents,
    "silero-vad-pi-zero32": pv_wave,
    "deepsilk-backend": pv_boxes,
    "Room-Classifier": pv_rooms,
    "CleFer": pv_chord,
}


