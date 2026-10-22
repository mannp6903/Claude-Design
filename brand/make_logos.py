"""Build outlined SVG logo files for Nest & Rest Cleaning.

All text is converted to vector paths, so the files render identically
for anyone, with or without the fonts installed.
"""
import os
import sys
import math

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform
import uharfbuzz as hb

FONTDIR, OUTDIR = sys.argv[1], sys.argv[2]
os.makedirs(OUTDIR, exist_ok=True)

NAVY = "#13293D"
CLAY = "#C96F4A"
SLATE = "#4A5A6B"
LINEN = "#F4F1EA"
CLAY_LIGHT = "#E09068"
RING = "#5B6974"          # 32% linen over navy, flattened so print is predictable


def load(name):
    path = os.path.join(FONTDIR, name)
    tt = TTFont(path)
    with open(path, "rb") as fh:
        data = fh.read()
    font = hb.Font(hb.Face(data))
    upem = tt["head"].unitsPerEm
    font.scale = (upem, upem)
    return tt, font, upem


FR600 = load("fraunces.ttf")
FR400 = load("fraunces400.ttf")
INTER = load("inter.ttf")

CAP_FR = 1400 / 2000.0      # Fraunces cap height as a fraction of em
CAP_IN = 1490 / 2048.0      # Inter cap height


def union(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def run(bundle, text, size, track_em=0.0, x0=0.0, y0=0.0):
    """Shape `text` and return (svg path data, advance width, ink bounds)."""
    tt, hbf, upem = bundle
    scale = size / upem
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf)

    glyphset = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    track = track_em * size
    infos, poss = list(buf.glyph_infos), list(buf.glyph_positions)

    paths, bounds, pen_x = [], None, 0.0
    for i, (info, pos) in enumerate(zip(infos, poss)):
        gname = order[info.codepoint]
        gx = x0 + pen_x + pos.x_offset * scale
        gy = y0 - pos.y_offset * scale
        tf = Transform(scale, 0, 0, -scale, gx, gy)

        spen = SVGPathPen(glyphset)
        glyphset[gname].draw(TransformPen(spen, tf))
        d = spen.getCommands()
        if d:
            paths.append(d)

        bpen = BoundsPen(glyphset)
        glyphset[gname].draw(TransformPen(bpen, tf))
        bounds = union(bounds, bpen.bounds)

        pen_x += pos.x_advance * scale
        if i < len(infos) - 1:
            pen_x += track
    return " ".join(paths), pen_x, bounds


def curved_run(bundle, text, size, radius, cx, cy, track_em=0.0):
    """Set `text` along the top of a circle, each glyph rotated to the tangent."""
    tt, hbf, upem = bundle
    scale = size / upem
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbf, buf)

    glyphset = tt.getGlyphSet()
    order = tt.getGlyphOrder()
    track = track_em * size
    infos, poss = list(buf.glyph_infos), list(buf.glyph_positions)

    advances = [p.x_advance * scale for p in poss]
    total = sum(advances) + track * (len(advances) - 1)
    start = -math.pi / 2 - (total / radius) / 2.0   # centred on the top of the circle

    groups, walked = [], 0.0
    for i, (info, adv) in enumerate(zip(infos, advances)):
        gname = order[info.codepoint]
        theta = start + (walked + adv / 2.0) / radius
        px = cx + radius * math.cos(theta)
        py = cy + radius * math.sin(theta)
        deg = math.degrees(theta) + 90.0

        spen = SVGPathPen(glyphset)
        glyphset[gname].draw(TransformPen(spen, Transform(scale, 0, 0, -scale, 0, 0)))
        d = spen.getCommands()
        if d:
            groups.append(
                '<g transform="translate(%.3f %.3f) rotate(%.3f) translate(%.3f 0)">'
                '<path d="%s"/></g>' % (px, py, deg, -adv / 2.0, d)
            )
        walked += adv + track
    return "\n    ".join(groups)


# ---------------------------------------------------------------- wordmark ---
S = 100.0                      # nominal size of the main wordmark
CAP = CAP_FR * S               # 70
TRACK = -0.02                  # −2%
GAP = 0.24 * S                 # space either side of the ampersand
AMP = S * 1.14                 # the ampersand sits a little larger

SUB = S * 0.226                # "CLEANING"
SUB_TRACK = 0.70
CAP_SUB = CAP_IN * SUB


def wordmark(x0=0.0, y0=0.0):
    """Returns (parts, advance width, ink bounds). Baseline sits at y0."""
    d1, w1, b1 = run(FR600, "NEST", S, TRACK, x0, y0)
    xa = x0 + w1 + GAP
    da, wa, ba = run(FR400, "&", AMP, 0.0, xa, y0)
    x2 = xa + wa + GAP
    d2, w2, b2 = run(FR600, "REST", S, TRACK, x2, y0)
    main_w = (x2 + w2) - x0

    dsub, wsub, _ = run(INTER, "CLEANING", SUB, SUB_TRACK, 0, 0)
    sub_x = x0 + (main_w - wsub) / 2.0
    sub_y = y0 + 0.22 * CAP + CAP_SUB
    dsub, _, bsub = run(INTER, "CLEANING", SUB, SUB_TRACK, sub_x, sub_y)

    parts = {"main": d1 + " " + d2, "amp": da, "sub": dsub}
    bounds = union(union(b1, b2), union(ba, bsub))
    return parts, main_w, bounds


# -------------------------------------------------------------------- icon ---
# Source space is 80 units; the drawn shape occupies x,y 3..77 (74 x 74).
ICON_BODY = ("M15 3 H50 L77 30 V65 A12 12 0 0 1 65 77 H15 "
             "A12 12 0 0 1 3 65 V15 A12 12 0 0 1 15 3 Z")
ICON_FLAP = "M50 3 L77 30 L50 30 Z"
# Inset triangle, strictly inside the body, used as a knockout in one-colour art.
ICON_FLAP_CUT = "M53 10 L71 28 L53 28 Z"
ICON_SPAN = 74.0


def icon_group(x, y, size, two_colour=True, ink=NAVY, accent=CLAY):
    k = size / ICON_SPAN
    tf = "translate(%.3f %.3f) scale(%.5f) translate(-3 -3)" % (x, y, k)
    if two_colour:
        inner = ('<path d="%s" fill="%s"/><path d="%s" fill="%s"/>'
                 % (ICON_BODY, ink, ICON_FLAP, accent))
    else:
        inner = ('<path d="%s %s" fill="%s" fill-rule="evenodd"/>'
                 % (ICON_BODY, ICON_FLAP_CUT, ink))
    return '<g transform="%s">%s</g>' % (tf, inner)


# --------------------------------------------------------------- monogram ---
MONO_STROKES = ["M20 18 V82", "M20 18 L54 82",
                "M54 18 H72 A15 15 0 0 1 72 48 H54", "M54 48 L86 82"]
MONO_STEM = "M54 18 V82"
MONO_VB = "0 0 104 100"


def monogram_inner(ink, stem):
    body = "".join('<path d="%s"/>' % d for d in MONO_STROKES)
    return (
        '<g fill="none" stroke="%s" stroke-width="11" stroke-linecap="round" '
        'stroke-linejoin="round">%s</g>\n'
        '  <path d="%s" fill="none" stroke="%s" stroke-width="11" stroke-linecap="round"/>'
        % (ink, body, MONO_STEM, stem)
    )


def svg(viewbox, width, height, body, title):
    title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" width="%.2f" '
        'height="%.2f" role="img" aria-label="%s">\n  <title>%s</title>\n  %s\n</svg>\n'
        % (viewbox, width, height, title, title, body)
    )


def write(name, text):
    with open(os.path.join(OUTDIR, name), "w") as fh:
        fh.write(text)
    print(name)


def vb(bounds, pad=0.0):
    x0, y0, x1, y1 = bounds
    return ("%.3f %.3f %.3f %.3f" % (x0 - pad, y0 - pad,
                                     (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad),
            (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad)


# ------------------------------------------------------------ build: files ---
# 1 & 2. Wordmark, two-colour and one-colour.
parts, main_w, wb = wordmark()


def wordmark_svg(ink, accent, sub_ink, title):
    body = ('<path d="%s" fill="%s"/>\n  <path d="%s" fill="%s"/>\n  '
            '<path d="%s" fill="%s"/>'
            % (parts["main"], ink, parts["amp"], accent, parts["sub"], sub_ink))
    box, w, h = vb(wb)
    return svg(box, w, h, body, title)


write("nest-rest-wordmark.svg",
      wordmark_svg(NAVY, CLAY, SLATE, "Nest & Rest Cleaning wordmark"))
write("nest-rest-wordmark-black.svg",
      wordmark_svg("#000000", "#000000", "#000000",
                   "Nest & Rest Cleaning wordmark, one colour"))
write("nest-rest-wordmark-white.svg",
      wordmark_svg("#FFFFFF", "#FFFFFF", "#FFFFFF",
                   "Nest & Rest Cleaning wordmark, reversed"))

# 3. Primary lockup: icon + wordmark.
ICON_H = 1.8 * CAP                  # icon height = cap height x 1.8
LOCK_GAP = 0.4 * ICON_H             # gap = icon width x 0.4
text_x = ICON_H + LOCK_GAP
lparts, lmain_w, lwb = wordmark(x0=text_x)
centre_y = (-CAP + (0.22 * CAP + CAP_SUB)) / 2.0
icon_y = centre_y - ICON_H / 2.0
lock_bounds = union(lwb, (0.0, icon_y, ICON_H, icon_y + ICON_H))


def lockup_svg(two_colour, ink, accent, sub_ink, title):
    body = (icon_group(0, icon_y, ICON_H, two_colour, ink, accent) + "\n  "
            + '<path d="%s" fill="%s"/>\n  <path d="%s" fill="%s"/>\n  '
              '<path d="%s" fill="%s"/>'
              % (lparts["main"], ink, lparts["amp"], accent,
                 lparts["sub"], sub_ink))
    box, w, h = vb(lock_bounds)
    return svg(box, w, h, body, title)


write("nest-rest-lockup.svg",
      lockup_svg(True, NAVY, CLAY, SLATE, "Nest & Rest Cleaning logo"))
write("nest-rest-lockup-black.svg",
      lockup_svg(False, "#000000", "#000000", "#000000",
                 "Nest & Rest Cleaning logo, one colour"))
write("nest-rest-lockup-white.svg",
      lockup_svg(False, "#FFFFFF", "#FFFFFF", "#FFFFFF",
                 "Nest & Rest Cleaning logo, reversed"))

# 4. Icon on its own.
write("nest-rest-icon.svg",
      svg("0 0 74 74", 74, 74, icon_group(0, 0, 74, True),
          "Nest & Rest folded corner icon"))
write("nest-rest-icon-black.svg",
      svg("0 0 74 74", 74, 74, icon_group(0, 0, 74, False, "#000000"),
          "Nest & Rest folded corner icon, one colour"))

# 5. Monogram.
write("nest-rest-monogram.svg",
      svg(MONO_VB, 104, 100, monogram_inner(NAVY, CLAY),
          "Nest & Rest N R monogram"))
write("nest-rest-monogram-black.svg",
      svg(MONO_VB, 104, 100, monogram_inner("#000000", "#000000"),
          "Nest & Rest N R monogram, one colour"))
write("nest-rest-monogram-white.svg",
      svg(MONO_VB, 104, 100, monogram_inner("#FFFFFF", "#FFFFFF"),
          "Nest & Rest N R monogram, reversed"))

# 6. Seal.
ring_text = curved_run(INTER, "NEST & REST CLEANING", 11.5, 68, 100, 100,
                       track_em=2.6 / 11.5)
est_d, est_w, _ = run(INTER, "EST. 2026", 9.5, 2.2 / 9.5, 0, 0)
est_d, _, _ = run(INTER, "EST. 2026", 9.5, 2.2 / 9.5, 100 - est_w / 2.0, 162)

seal_body = (
    '<circle cx="100" cy="100" r="95" fill="%s"/>\n  '
    '<circle cx="100" cy="100" r="84" fill="none" stroke="%s" stroke-width="1.5"/>\n  '
    '<g fill="%s">\n    %s\n  </g>\n  '
    '<g transform="translate(63 69) scale(0.7)">%s</g>\n  '
    '<path d="%s" fill="%s"/>'
    % (NAVY, RING, LINEN, ring_text, monogram_inner(LINEN, CLAY_LIGHT),
       est_d, "#9EA5A8")
)
write("nest-rest-seal.svg",
      svg("0 0 200 200", 200, 200, seal_body, "Nest & Rest Cleaning seal"))

print("CAP=%.2f ICON_H=%.2f lockup bounds=%s" % (CAP, ICON_H, lock_bounds))
