#!/usr/bin/env python3
"""Round 2 — three colour + type combinations for concept A (The Woven Nest).

Each combination is a palette plus an Adobe Fonts pairing, shown on the real
name and the real tagline. Contrast figures are computed, not asserted.
"""
import math
import os

import cairosvg
from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
import uharfbuzz as hb

OUT = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(OUT, "fonts")


def load(path):
    tt = TTFont(path)
    with open(path, "rb") as fh:
        data = fh.read()
    f = hb.Font(hb.Face(data))
    upem = tt["head"].unitsPerEm
    f.scale = (upem, upem)
    cap = getattr(tt["OS/2"], "sCapHeight", None) or int(0.70 * upem)
    return {"tt": tt, "hb": f, "upem": upem, "cap": cap}


F = {n: load(os.path.join(FD, n + ".ttf")) for n in (
    "Quicksand-Bold", "Quicksand-Medium", "NunitoSans-Regular", "NunitoSans-LightItalic",
    "Poppins-SemiBold", "Poppins-Regular", "FiraSans-Book", "FiraSans-BookItalic",
    "Montserrat-Bold", "Montserrat-Medium", "PlaywriteIE-Light")}
UI = load("/usr/share/fonts/opentype/inter/Inter-Medium.otf")
UIB = load("/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf")


def shape(b, text, size, track=0.0, x=0.0, y=0.0):
    tt, hbf, upem = b["tt"], b["hb"], b["upem"]
    s = size / upem
    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf)
    infos, poss = list(buf.glyph_infos), list(buf.glyph_positions)
    out, pen = [], 0.0
    for i, (inf, pos) in enumerate(zip(infos, poss)):
        sp = SVGPathPen(gs)
        gs[order[inf.codepoint]].draw(TransformPen(sp, Transform(
            s, 0, 0, -s, x + pen + pos.x_offset * s, y - pos.y_offset * s)))
        out.append(sp.getCommands())
        pen += pos.x_advance * s
        if i < len(infos) - 1:
            pen += track * size
    return out, pen


def txt(b, text, size, fill, track=0.0, x=0.0, y=0.0, at=None):
    paths, adv = shape(b, text, size, track, x, y)
    at = at or {}
    return "".join(f'<path d="{d}" fill="{at.get(i, fill)}"/>'
                   for i, d in enumerate(paths) if d), adv


def arc(cx, cy, r, a0, a1, stroke, w):
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f'<path d="M {x0:.2f} {y0:.2f} A {r} {r} 0 {large} 1 {x1:.2f} {y1:.2f}" '
            f'fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"/>')


def sparkle(cx, cy, r, fill, k=0.13):
    return (f'<path d="M {cx} {cy - r} Q {cx + k * r:.2f} {cy - k * r:.2f} {cx + r} {cy} '
            f'Q {cx + k * r:.2f} {cy + k * r:.2f} {cx} {cy + r} '
            f'Q {cx - k * r:.2f} {cy + k * r:.2f} {cx - r} {cy} '
            f'Q {cx - k * r:.2f} {cy - k * r:.2f} {cx} {cy - r} Z" fill="{fill}"/>')


def nest(outer, inner, house, glint):
    """Concept A, recoloured."""
    out = []
    for r, centres, col in ((40, [0, 60, 120, 180, 240, 300], outer),
                            (30, [30, 90, 150, 210, 270, 330], inner)):
        out += [arc(50, 50, r, c - 24, c + 24, col, 7) for c in centres]
    out.append(f'<path d="M 50 34 L 66 48 L 66 64 L 34 64 L 34 48 Z" fill="{house}"/>')
    out.append(sparkle(88, 14, 7, glint))
    return "".join(out)


# ----------------------------------------------------------------- contrast

def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def grade(r):
    return "AAA" if r >= 7 else "AA" if r >= 4.5 else "AA Large" if r >= 3 else "FAIL"


# ----------------------------------------------------------------- the three

COMBOS = [
    {
        "n": "1", "name": "LINEN & TEAL", "mood": "warm, homely, premium-approachable",
        "pal": {"primary": "#0C7C77", "secondary": "#9AD5E8", "accent": "#D9983A",
                "background": "#F7F2E9", "text": "#102C3F", "muted": "#52677A"},
        "word": "Quicksand-Bold", "sub": "Quicksand-Medium",
        "tag1": "NunitoSans-Regular", "tag2": "NunitoSans-LightItalic",
        "type": "Quicksand Bold + Nunito Sans",
        "credit": "Quicksand by Andrew Paglinawan · Nunito Sans by Vernon Adams",
    },
    {
        "n": "2", "name": "HARBOUR", "mood": "cool, clean, trustworthy",
        "pal": {"primary": "#136F7B", "secondary": "#7FD4C1", "accent": "#E07A5F",
                "background": "#F2F7F7", "text": "#16262E", "muted": "#4E6670"},
        "word": "Poppins-SemiBold", "sub": "Poppins-Regular",
        "tag1": "FiraSans-Book", "tag2": "FiraSans-BookItalic",
        "type": "Poppins SemiBold + Fira Sans",
        "credit": "Poppins by Ninad Kale & Jonny Pinhorn · Fira Sans by Carrois Corporate & Edenspiekermann",
    },
    {
        "n": "3", "name": "MORNING", "mood": "soft, airy, calm — script tagline",
        "pal": {"primary": "#19817B", "secondary": "#BFE3EF", "accent": "#E8B86D",
                "background": "#FDFBF7", "text": "#0C2130", "muted": "#5A6E7D"},
        "word": "Montserrat-Bold", "sub": "Montserrat-Medium",
        "tag1": "Montserrat-Medium", "tag2": "PlaywriteIE-Light",
        "type": "Montserrat Bold + Playwrite IE",
        "credit": "Montserrat by Julieta Ulanovsky · Playwrite IE by TypeTogether",
    },
]

ROLES = ["primary", "secondary", "accent", "background", "text", "muted"]


def lockup(c, reversed_=False):
    """Icon + NEST & REST + CLEANING + tagline. Returns (svg, width, top, bottom)."""
    p = c["pal"]
    wb, sb = F[c["word"]], F[c["sub"]]
    t1b, t2b = F[c["tag1"]], F[c["tag2"]]

    if reversed_:
        name_col = sub_col = tag_col = "#FFFFFF"
        amp_col = p["secondary"]
        ico = nest("#FFFFFF", p["secondary"], "#FFFFFF", p["accent"])
    else:
        name_col, sub_col, tag_col = p["text"], p["muted"], p["muted"]
        amp_col = p["primary"]
        ico = nest(p["secondary"], p["primary"], p["text"], p["accent"])

    CAP = 100.0
    s1 = CAP / (wb["cap"] / wb["upem"])
    s2 = (CAP * 0.28) / (sb["cap"] / sb["upem"])
    s3 = (CAP * 0.30) / (t1b["cap"] / t1b["upem"])
    s4 = (CAP * 0.30) / (t2b["cap"] / t2b["upem"])

    f1, w1 = txt(wb, "NEST & REST", s1, name_col, 0.005, at={5: amp_col})
    f2, w2 = txt(sb, "CLEANING", s2, sub_col, 0.42)
    w2 -= 0.42 * s2
    f3, w3 = txt(t1b, "We Clean.", s3, tag_col, 0.0)
    f4, w4 = txt(t2b, "You Rest.", s4, amp_col if not reversed_ else p["secondary"], 0.0)

    icon_h = CAP * 1.8
    sc = icon_h / 100.0
    tx = icon_h + icon_h * 0.34
    mid = (-CAP + 118) / 2
    top_i = mid - icon_h / 2

    gap = s3 * 0.32
    frag = (f'<g transform="translate(0,{top_i:.2f}) scale({sc:.4f})">{ico}</g>'
            f'<g transform="translate({tx:.2f},0)">{f1}</g>'
            f'<g transform="translate({tx:.2f},50)">{f2}</g>'
            f'<g transform="translate({tx:.2f},118)">{f3}</g>'
            f'<g transform="translate({tx + w3 + gap:.2f},118)">{f4}</g>')
    width = tx + max(w1, w2, w3 + gap + w4)
    return frag, width, min(top_i, -CAP), max(top_i + icon_h, 118)


def build():
    CW, CH, M, HEAD, GAP = 1460, 560, 50, 120, 28
    BW = CW + M * 2
    BH = HEAD + (CH + GAP) * 3 + M

    o = [f'<rect width="{BW}" height="{BH}" fill="#FFFFFF"/>']
    t, _ = txt(UIB, "NEST & REST CLEANING", 34, "#102C3F", 0.002, M, 58)
    o.append(t)
    t, _ = txt(UI, "ROUND 2 · COLOUR + TYPE · PICK ONE COMBINATION", 17, "#52677A", 0.16, M, 90)
    o.append(t)

    for i, c in enumerate(COMBOS):
        p = c["pal"]
        y = HEAD + i * (CH + GAP)
        o.append(f'<rect x="{M}" y="{y}" width="{CW}" height="{CH}" rx="18" '
                 f'fill="{p["background"]}" stroke="#E4DED3" stroke-width="1.5"/>')

        t, aw = txt(UIB, c["n"], 30, p["primary"], 0, M + 34, y + 58)
        o.append(t)
        t, _ = txt(UIB, c["name"], 22, p["text"], 0.01, M + 66, y + 56)
        o.append(t)
        t, _ = txt(UI, c["mood"], 15, p["muted"], 0.01, M + 66, y + 80)
        o.append(t)
        t, tw = txt(UIB, c["type"], 16, p["primary"], 0.01, 0, 0)
        o.append(f'<g transform="translate({M + CW - 34 - tw:.2f},{y + 56})">{t}</g>')
        t, cw2 = txt(UI, c["credit"], 12, p["muted"], 0.01, 0, 0)
        o.append(f'<g transform="translate({M + CW - 34 - cw2:.2f},{y + 80})">{t}</g>')

        # main lockup
        fr, w, top, bot = lockup(c)
        sc = min((CW - 500) / w, 190 / (bot - top))
        o.append(f'<g transform="translate({M + 44},{y + 118 - top * sc:.2f}) scale({sc:.4f})">{fr}</g>')

        # reversed lockup on the primary
        rx, ry, rw, rh = M + CW - 390, y + 110, 356, 150
        o.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="12" fill="{p["primary"]}"/>')
        fr2, w2_, top2, bot2 = lockup(c, reversed_=True)
        sc2 = min((rw - 48) / w2_, (rh - 44) / (bot2 - top2))
        o.append(f'<g transform="translate({rx + 24},{ry + 22 - top2 * sc2:.2f}) scale({sc2:.4f})">{fr2}</g>')
        t, _ = txt(UI, "REVERSED ON PRIMARY", 11, p["muted"], 0.1, rx, ry + rh + 18)
        o.append(t)

        # palette swatches
        sw, sy = 118, y + 340
        for j, role in enumerate(ROLES):
            hexv = p[role]
            x = M + 44 + j * (sw + 14)
            o.append(f'<rect x="{x}" y="{sy}" width="{sw}" height="62" rx="9" '
                     f'fill="{hexv}" stroke="#D9D2C6" stroke-width="1"/>')
            t, _ = txt(UIB, role.upper(), 10, p["text"], 0.09, x, sy + 80)
            o.append(t)
            t, _ = txt(UI, hexv.upper(), 11, p["muted"], 0.04, x, sy + 96)
            o.append(t)

        # contrast, computed
        checks = [("Wordmark on white", p["text"], "#FFFFFF"),
                  ("Wordmark on primary", "#FFFFFF", p["primary"]),
                  ("Primary on background", p["primary"], p["background"]),
                  ("Tagline on background", p["muted"], p["background"])]
        cy2 = y + 486
        x = M + 44
        for label, a, b in checks:
            r = ratio(a, b)
            g = grade(r)
            ok = g != "FAIL"
            t, lw = txt(UI, f"{label}  {r:.1f}:1", 12, p["text"], 0.01, 0, 0)
            chipw = lw + 74
            o.append(f'<rect x="{x}" y="{cy2 - 15}" width="{chipw}" height="24" rx="12" '
                     f'fill="{"#FFFFFF" if ok else "#FDE8E6"}" stroke="{"#D9D2C6" if ok else "#D4503F"}" stroke-width="1"/>')
            o.append(f'<g transform="translate({x + 12},{cy2 + 2})">{t}</g>')
            t, _ = txt(UIB, g, 11, "#0E8C86" if ok else "#C0392B", 0.04, x + 12 + lw + 10, cy2 + 2)
            o.append(t)
            x += chipw + 14

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BW} {BH}" '
           f'width="{BW}" height="{BH}">{"".join(o)}</svg>')
    open(os.path.join(OUT, "round2-board.svg"), "w").write(svg)
    cairosvg.svg2png(bytestring=svg.encode(),
                     write_to=os.path.join(OUT, "round2-board.png"), output_width=int(BW * 1.5))
    print(f"board {BW}x{BH}")
    for c in COMBOS:
        p = c["pal"]
        print(f'\n{c["n"]} {c["name"]}  ({c["type"]})')
        for label, a, b in (("text on white", p["text"], "#FFFFFF"),
                            ("text on background", p["text"], p["background"]),
                            ("white on primary", "#FFFFFF", p["primary"]),
                            ("primary on background", p["primary"], p["background"])):
            r = ratio(a, b)
            print(f"   {label:24s} {r:5.2f}:1  {grade(r)}")


if __name__ == "__main__":
    build()
