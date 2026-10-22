#!/usr/bin/env python3
"""Round-1 concept marks for NEST & REST CLEANING.

Draws the four brief directions as real vectors (text outlined, no font
dependency) and lays them out on one comparison board.
"""
import math
import os

import cairosvg
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
import uharfbuzz as hb

FONTDIR = "/usr/share/fonts/opentype/inter"
OUT = os.path.dirname(os.path.abspath(__file__))

NAVY = "#0F2F43"
TEAL = "#1A9E96"
TEALD = "#12776F"
SKY = "#7FCBE3"
MINT = "#4CBFA6"
LEAFG = "#6ED3A8"
CREAM = "#F6F1E8"
GOLD = "#E4A951"
SLATE = "#5A6E7A"


def load(fname):
    path = os.path.join(FONTDIR, fname)
    tt = TTFont(path)
    with open(path, "rb") as fh:
        data = fh.read()
    font = hb.Font(hb.Face(data))
    upem = tt["head"].unitsPerEm
    font.scale = (upem, upem)
    return {"tt": tt, "hb": font, "upem": upem,
            "cap": getattr(tt["OS/2"], "sCapHeight", None) or int(0.727 * upem)}


BOLD = load("InterDisplay-Bold.otf")
XBOLD = load("InterDisplay-ExtraBold.otf")
MED = load("Inter-Medium.otf")
ITAL = load("Inter-Italic.otf")


def shape(bundle, text, size, track_em=0.0, x=0.0, y=0.0):
    """Shape `text`; return (per-glyph path data, total advance)."""
    tt, hbf, upem = bundle["tt"], bundle["hb"], bundle["upem"]
    scale = size / upem
    gs = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    track = track_em * size

    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf)
    infos, poss = list(buf.glyph_infos), list(buf.glyph_positions)

    out, pen = [], 0.0
    for i, (info, pos) in enumerate(zip(infos, poss)):
        gname = order[info.codepoint]
        sp = SVGPathPen(gs)
        tf = Transform(scale, 0, 0, -scale,
                       x + pen + pos.x_offset * scale, y - pos.y_offset * scale)
        gs[gname].draw(TransformPen(sp, tf))
        out.append(sp.getCommands())
        pen += pos.x_advance * scale
        if i < len(infos) - 1:
            pen += track
    return out, pen


def text_svg(bundle, text, size, fill, track_em=0.0, x=0.0, y=0.0, colour_at=None):
    """Set text as filled paths. `colour_at` maps glyph index -> fill."""
    paths, adv = shape(bundle, text, size, track_em, x, y)
    colour_at = colour_at or {}
    frag = "".join(
        f'<path d="{d}" fill="{colour_at.get(i, fill)}"/>'
        for i, d in enumerate(paths) if d
    )
    return frag, adv


def fitted_glyph(bundle, ch, target_h, cx, cy):
    """One glyph scaled to `target_h` tall and centred on (cx, cy)."""
    tt = bundle["tt"]
    gs = tt.getGlyphSet()
    gname = tt.getBestCmap()[ord(ch)]
    bp = BoundsPen(gs)
    gs[gname].draw(bp)
    x0, y0, x1, y1 = bp.bounds
    s = target_h / (y1 - y0)
    sp = SVGPathPen(gs)
    gs[gname].draw(TransformPen(sp, Transform(
        s, 0, 0, -s, cx - s * (x0 + x1) / 2, cy + s * (y0 + y1) / 2)))
    return sp.getCommands(), s * (x1 - x0)


def arc(cx, cy, r, a0, a1, stroke, w):
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f'<path d="M {x0:.2f} {y0:.2f} A {r} {r} 0 {large} 1 {x1:.2f} {y1:.2f}" '
            f'fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"/>')


def weave(cx, cy, r, centres, half, stroke, w):
    """A row of short arcs around a bowl — twigs rather than a smooth ripple."""
    return "".join(arc(cx, cy, r, c - half, c + half, stroke, w) for c in centres)


def sparkle(cx, cy, r, fill, k=0.13):
    return (f'<path d="M {cx} {cy - r} Q {cx + k * r:.2f} {cy - k * r:.2f} {cx + r} {cy} '
            f'Q {cx + k * r:.2f} {cy + k * r:.2f} {cx} {cy + r} '
            f'Q {cx - k * r:.2f} {cy + k * r:.2f} {cx - r} {cy} '
            f'Q {cx - k * r:.2f} {cy - k * r:.2f} {cx} {cy - r} Z" fill="{fill}"/>')


def leaf(x, y, L, ang, fill):
    a = math.radians(ang)
    tx, ty = x + L * math.cos(a), y + L * math.sin(a)
    px, py = -math.sin(a) * L * 0.30, math.cos(a) * L * 0.30
    mx, my = (x + tx) / 2, (y + ty) / 2
    return (f'<path d="M {x:.2f} {y:.2f} Q {mx + px:.2f} {my + py:.2f} {tx:.2f} {ty:.2f} '
            f'Q {mx - px:.2f} {my - py:.2f} {x:.2f} {y:.2f} Z" fill="{fill}"/>')


def rounded_poly(pts, r):
    def trim(p, q):
        dx, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dx, dy)
        t = min(r, L / 2) / L
        return p[0] + dx * t, p[1] + dy * t

    n, out = len(pts), []
    for i in range(n):
        prev, cur, nxt = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        a, b = trim(cur, prev), trim(cur, nxt)
        out.append(("M" if i == 0 else "L") + f" {a[0]:.2f} {a[1]:.2f}")
        out.append(f"Q {cur[0]:.2f} {cur[1]:.2f} {b[0]:.2f} {b[1]:.2f}")
    return " ".join(out) + " Z"


# ---------------------------------------------------------------- icons (100x100)

def icon_nest():
    """A — nest seen from above: two woven rings of twigs around a home."""
    out = []
    for r, centres, col in ((40, [0, 60, 120, 180, 240, 300], SKY),
                            (30, [30, 90, 150, 210, 270, 330], TEAL)):
        out += [arc(50, 50, r, c - 24, c + 24, col, 7) for c in centres]
    out.append(f'<path d="M 50 34 L 66 48 L 66 64 L 34 64 L 34 48 Z" fill="{NAVY}"/>')
    out.append(sparkle(88, 14, 7, GOLD))
    return "".join(out)


def icon_crescent():
    """B — crescent that doubles as a cradle, house resting inside."""
    c1, r1 = (50, 54), 40
    c2, r2 = (50, 36), 34
    ring = (f'M {c1[0] - r1} {c1[1]} A {r1} {r1} 0 1 0 {c1[0] + r1} {c1[1]} '
            f'A {r1} {r1} 0 1 0 {c1[0] - r1} {c1[1]} Z '
            f'M {c2[0] - r2} {c2[1]} A {r2} {r2} 0 1 0 {c2[0] + r2} {c2[1]} '
            f'A {r2} {r2} 0 1 0 {c2[0] - r2} {c2[1]} Z')
    return "".join([
        f'<path fill-rule="evenodd" d="{ring}" fill="{TEAL}"/>',
        f'<path d="M 50 38 L 64 51 L 64 67 L 36 67 L 36 51 Z" fill="{NAVY}"/>',
        sparkle(84, 22, 8, GOLD),
    ])


def icon_amp():
    """C — the ampersand itself, with a leaf and a glint."""
    d, w = fitted_glyph(BOLD, "&", 80, 50, 54)
    rx = 50 + w / 2
    return "".join([
        f'<path d="{d}" fill="{TEAL}"/>',
        leaf(rx - 8, 26, 30, -42, LEAFG),
        sparkle(rx + 4, 62, 8, GOLD),
    ])


def icon_badge():
    """D — house-shaped badge carrying the N&R monogram."""
    body = rounded_poly([(50, 5), (95, 40), (95, 88), (5, 88), (5, 40)], 11)
    n, wn = fitted_glyph(XBOLD, "N", 30, 0, 0)
    a, wa = fitted_glyph(XBOLD, "&", 24, 0, 0)
    r, wr = fitted_glyph(XBOLD, "R", 30, 0, 0)
    gap = 4
    total = wn + wa + wr + gap * 2
    x = 50 - total / 2
    cy = 60
    parts = [f'<path d="{body}" fill="{TEAL}"/>']
    for d, w, fill, h in ((n, wn, "#FFFFFF", 30), (a, wa, "#FFFFFF", 24), (r, wr, "#FFFFFF", 30)):
        parts.append(f'<g transform="translate({x + w / 2:.2f},{cy:.2f})">'
                     f'<path d="{d}" fill="{fill}"/></g>')
        x += w + gap
    return "".join(parts)


ICONS = {"A": icon_nest, "B": icon_crescent, "C": icon_amp, "D": icon_badge}


# ---------------------------------------------------------------- lockup

CAP = 100.0


def lockup(key, mono=None):
    """Horizontal lockup. Returns (svg fragment, width, height) in local units."""
    size1 = CAP / (BOLD["cap"] / BOLD["upem"])
    size2 = (CAP * 0.30) / (MED["cap"] / MED["upem"])

    navy = mono or NAVY
    teal = mono or TEAL
    slate = mono or SLATE

    amp = navy if key == "C" else teal
    w1_frag, w1 = text_svg(BOLD, "NEST & REST", size1, navy,
                           track_em=0.005, colour_at={5: amp})
    w2_frag, w2 = text_svg(MED, "CLEANING", size2, slate, track_em=0.42)
    w2 -= 0.42 * size2  # trailing letterspace is not ink

    icon_h = CAP * 1.8
    s = icon_h / 100.0
    gap = icon_h * 0.34
    tx = icon_h + gap

    # text block spans y -CAP .. +52 ; centre it on the icon
    block_mid = (-CAP + 52) / 2
    icon_top = block_mid - icon_h / 2

    icon_svg = ICONS[key]()
    if mono:
        for c in (NAVY, TEAL, TEALD, SKY, LEAFG, MINT, GOLD, SLATE):
            icon_svg = icon_svg.replace(c, mono)
        icon_svg = icon_svg.replace('fill="#FFFFFF"', 'fill="#FFFFFF"')

    frag = (f'<g transform="translate(0,{icon_top:.2f}) scale({s:.4f})">{icon_svg}</g>'
            f'<g transform="translate({tx:.2f},0)">{w1_frag}</g>'
            f'<g transform="translate({tx:.2f},52)">{w2_frag}</g>')

    width = tx + max(w1, w2)
    top = min(icon_top, -CAP)
    bot = max(icon_top + icon_h, 52)
    return frag, width, top, bot


def svg_doc(frag, vb, w, h, bg="#FFFFFF"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
            f'width="{w}" height="{h}">'
            f'<rect x="-9999" y="-9999" width="19998" height="19998" fill="{bg}"/>'
            f'{frag}</svg>')


NAMES = {
    "A": ("THE WOVEN NEST", "Nest + Home — strands cradling a roofline"),
    "B": ("THE REST CRESCENT", "Rest — moon and cradle in one curve"),
    "C": ("THE FRESH AMPERSAND", "Fresh — the & carries a leaf and a glint"),
    "D": ("THE N&R HOUSE BADGE", "Monogram — built for app icon and favicon"),
}


def build():
    # --- individual concept files -------------------------------------------
    for key in "ABCD":
        frag, w, top, bot = lockup(key)
        pad = 40
        vb = f"{-pad} {top - pad} {w + pad * 2} {bot - top + pad * 2}"
        doc = svg_doc(frag, vb, int((w + pad * 2) * 1.6), int((bot - top + pad * 2) * 1.6))
        name = f"concept-{key.lower()}-{NAMES[key][0].lower().replace(' ', '-').replace('&', 'and')}"
        with open(os.path.join(OUT, name + ".svg"), "w") as fh:
            fh.write(doc)
        cairosvg.svg2png(bytestring=doc.encode(), write_to=os.path.join(OUT, name + ".png"),
                         output_width=int((w + pad * 2) * 1.6))

    # --- comparison board ----------------------------------------------------
    CW, CH, GAP, M, HEAD = 880, 530, 36, 56, 118
    BW = M * 2 + CW * 2 + GAP
    BH = HEAD + CH * 2 + GAP + M

    out = [f'<rect width="{BW}" height="{BH}" fill="#FFFFFF"/>']
    t, _ = text_svg(BOLD, "NEST & REST CLEANING", 34, NAVY, 0.002, M, 58)
    out.append(t)
    t, _ = text_svg(MED, "ROUND 1 · CONCEPT DIRECTIONS · PICK ONE", 17, SLATE, 0.16, M, 88)
    out.append(t)

    for i, key in enumerate("ABCD"):
        col, row = i % 2, i // 2
        x = M + col * (CW + GAP)
        y = HEAD + row * (CH + GAP)
        out.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" rx="18" '
                   f'fill="{CREAM}" stroke="#E2DACD" stroke-width="1.5"/>')

        label, blurb = NAMES[key]
        t, _ = text_svg(XBOLD, key, 30, TEAL, 0, x + 34, y + 60)
        out.append(t)
        t, _ = text_svg(BOLD, label, 21, NAVY, 0.01, x + 68, y + 58)
        out.append(t)
        t, _ = text_svg(MED, blurb, 15, SLATE, 0.01, x + 68, y + 82)
        out.append(t)

        # lockup, scaled to fit the card
        frag, w, top, bot = lockup(key)
        avail_w, avail_h = CW - 120, 210
        s = min(avail_w / w, avail_h / (bot - top))
        lx = x + (CW - w * s) / 2
        ly = y + 130 + (avail_h - (bot - top) * s) / 2 - top * s
        out.append(f'<g transform="translate({lx:.2f},{ly:.2f}) scale({s:.4f})">{frag}</g>')

        # footer strip: icon at 64, favicon chip at 32, one-colour navy lockup
        fy = y + CH - 100
        out.append(f'<line x1="{x + 34}" y1="{fy - 18}" x2="{x + CW - 34}" y2="{fy - 18}" '
                   f'stroke="#E2DACD" stroke-width="1.5"/>')
        icon = ICONS[key]()
        out.append(f'<g transform="translate({x + 38},{fy + 2}) scale(0.64)">{icon}</g>')
        out.append(f'<rect x="{x + 126}" y="{fy + 14}" width="40" height="40" rx="9" '
                   f'fill="#FFFFFF" stroke="#D8CEBE" stroke-width="1.2"/>')
        out.append(f'<g transform="translate({x + 130},{fy + 18}) scale(0.32)">{icon}</g>')
        t, _ = text_svg(MED, "64 px", 11, SLATE, 0.08, x + 44, fy + 76)
        out.append(t)
        t, _ = text_svg(MED, "32 px", 11, SLATE, 0.08, x + 130, fy + 76)
        out.append(t)

        mfrag, mw, mtop, mbot = lockup(key, mono=NAVY)
        ms = min((CW - 215) / mw, 40 / (mbot - mtop))
        out.append(f'<g transform="translate({x + 210},{fy + 16 - mtop * ms:.2f}) '
                   f'scale({ms:.4f})">{mfrag}</g>')
        t, _ = text_svg(MED, "ONE-COLOUR NAVY", 11, SLATE, 0.08, x + 210, fy + 76)
        out.append(t)

    board = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BW} {BH}" '
             f'width="{BW}" height="{BH}">{"".join(out)}</svg>')
    with open(os.path.join(OUT, "round1-board.svg"), "w") as fh:
        fh.write(board)
    cairosvg.svg2png(bytestring=board.encode(),
                     write_to=os.path.join(OUT, "round1-board.png"),
                     output_width=int(BW * 1.5))
    print(f"board {BW}x{BH} -> round1-board.png")


if __name__ == "__main__":
    build()
