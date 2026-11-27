#!/usr/bin/env python3
"""Render the 27 November 2026 one-page world-news poster (entry.png).

Cream-paper broadsheet: giant serif masthead date, nine illustrated feature
cards in a 3x3 grid, a BY THE NUMBERS strip, a dotted world map with numbered
pins, and a numbered two-column also-list. Every picture is drawn from scratch
with PIL primitives; no photographs, no external assets. Deterministic: the
only randomness comes from fixed seeds.
"""

import math
import random

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 24
RIGHT = W - MARGIN

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF = FONT_DIR + "DejaVuSerif.ttf"
SERIF_B = FONT_DIR + "DejaVuSerif-Bold.ttf"
SANS = FONT_DIR + "DejaVuSans.ttf"
SANS_B = FONT_DIR + "DejaVuSans-Bold.ttf"

PAPER = (247, 242, 230)
CARD_BG = (255, 253, 246)
INK = (26, 26, 30)
MUTED = (96, 90, 78)
RULE = (40, 40, 44)
RED = (178, 34, 30)
NAVY = (30, 52, 92)
GOLD = (176, 124, 28)
CARD_LINE = (216, 207, 184)


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, fnt):
    return draw.textlength(s, font=fnt)


def wrap(draw, s, fnt, max_w):
    """Greedy word wrap by pixel width; returns a list of lines."""
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def spaced(s, n=1):
    return (" " * n).join(list(s.replace(" ", "_"))).replace("_", " ")


# --------------------------------------------------------------------------
# Scene painters. Each paints inside box (x, y, w, h) on the shared image.
# --------------------------------------------------------------------------

def clip_scene(img, box):
    """Return a draw object whose drawing is clipped to the scene box."""
    x, y, w, h = box
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([x, y, x + w, y + h], fill=255)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    return d, layer, mask


def paste_scene(img, layer, mask):
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"),
              (0, 0), mask)


def scene_storm(img, box):
    x, y, w, h = box
    d, layer, mask = clip_scene(img, box)
    rng = random.Random(27)
    # slate sky, darker at the top
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip((52, 66, 92), (126, 140, 158)))
        d.line([x, y + i, x + w, y + i], fill=c + (255,))
    # storm clouds
    for cx, cy, cw in [(x + 40, y + 12, 90), (x + 150, y + 8, 120), (x + 255, y + 14, 80)]:
        d.ellipse([cx, cy, cx + cw, cy + 26], fill=(38, 46, 64, 255))
        d.ellipse([cx + 18, cy - 8, cx + cw - 14, cy + 18], fill=(44, 54, 74, 255))
    # lightning bolt
    bx = x + 232
    d.polygon([(bx, y + 26), (bx + 12, y + 26), (bx + 4, y + 42), (bx + 13, y + 42),
               (bx - 4, y + 62), (bx + 1, y + 44), (bx - 7, y + 44)],
              fill=(250, 214, 90, 255))
    # rain streaks
    for _ in range(90):
        rx = x + rng.uniform(0, w)
        ry = y + rng.uniform(6, h - 26)
        d.line([rx, ry, rx - 3, ry + 7], fill=(210, 224, 240, 200), width=1)
    # parade balloon in the gap between rooftops, tipped by the wind
    d.ellipse([x + 122, y + 14, x + 176, y + 48], fill=(214, 74, 52, 255))
    d.ellipse([x + 134, y + 20, x + 156, y + 36], fill=(232, 110, 84, 255))
    d.polygon([(x + 176, y + 26), (x + 190, y + 31), (x + 176, y + 36)], fill=(214, 74, 52, 255))
    for hx in (132, 150, 166):
        d.line([x + hx, y + 46, x + hx - 2, y + h - 20], fill=(30, 30, 34, 160), width=1)
        d.ellipse([x + hx - 4, y + h - 22, x + hx + 2, y + h - 16], fill=(24, 24, 28, 255))
    # houses along the bottom, one roof flying off
    gy = y + h - 16
    for hx, hw, col in [(6, 52, (226, 216, 192)), (66, 44, (206, 198, 178)), (196, 56, (222, 210, 186)), (260, 46, (210, 200, 180))]:
        d.rectangle([x + hx, gy - 16, x + hx + hw, gy], fill=col + (255,))
        d.polygon([(x + hx - 3, gy - 16), (x + hx + hw // 2, gy - 27), (x + hx + hw + 3, gy - 16)],
                  fill=(120, 62, 48, 255))
        d.rectangle([x + hx + 8, gy - 11, x + hx + 15, gy - 5], fill=(250, 214, 120, 255))
    d.polygon([(x + 128, gy - 34), (x + 152, gy - 40), (x + 156, gy - 32), (x + 132, gy - 27)],
              fill=(120, 62, 48, 255))
    # flooded street
    d.rectangle([x, gy, x + w, y + h], fill=(74, 104, 138, 255))
    for i in range(7):
        sx = x + rng.uniform(0, w - 26)
        d.line([sx, gy + 4 + i * 2, sx + 22, gy + 4 + i * 2], fill=(150, 180, 210, 160))
    paste_scene(img, layer, mask)


def scene_kuwait(img, box):
    x, y, w, h = box
    d, layer, mask = clip_scene(img, box)
    rng = random.Random(41)
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip((216, 178, 120), (238, 210, 160)))
        d.line([x, y + i, x + w, y + i], fill=c + (255,))
    d.ellipse([x + w - 52, y + 8, x + w - 22, y + 38], fill=(250, 226, 150, 255))
    # desert floor with scrub dots
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(198, 158, 100, 255))
    for _ in range(40):
        sx = x + rng.uniform(0, w)
        d.point((sx, y + h - rng.uniform(2, 16)), fill=(170, 128, 76, 255))
    # radar truck on the left
    tx, ty = x + 18, y + h - 34
    d.rectangle([tx, ty + 10, tx + 62, ty + 24], fill=(84, 92, 70, 255))
    d.rectangle([tx + 44, ty + 2, tx + 62, ty + 12], fill=(70, 78, 58, 255))
    d.ellipse([tx + 6, ty + 20, tx + 18, ty + 32], fill=(30, 30, 30, 255))
    d.ellipse([tx + 42, ty + 20, tx + 54, ty + 32], fill=(30, 30, 30, 255))
    d.line([tx + 16, ty + 10, tx + 8, ty - 8], fill=(50, 54, 44, 255), width=2)
    d.arc([tx - 2, ty - 18, tx + 26, ty + 8], start=300, end=60, fill=(50, 54, 44, 255), width=2)
    # drone diving in from the top right, motion ticks behind it
    dx, dy = x + w - 84, y + 16
    for k in range(3):
        d.line([dx + 34 + k * 9, dy - 2 + k * 5, dx + 46 + k * 9, dy + 2 + k * 5],
               fill=(90, 84, 70, 200), width=2)
    d.polygon([(dx, dy + 12), (dx + 30, dy), (dx + 38, dy + 10), (dx + 30, dy + 16)],
              fill=(52, 52, 58, 255))
    d.polygon([(dx + 8, dy + 12), (dx - 6, dy + 22), (dx + 12, dy + 20)], fill=(52, 52, 58, 255))
    d.polygon([(dx + 24, dy + 13), (dx + 36, dy + 24), (dx + 18, dy + 21)], fill=(52, 52, 58, 255))
    # explosion burst where the drone is heading
    ex, ey = x + w - 128, y + h - 30
    for ang in range(0, 360, 30):
        r1, r2 = 5, 17 + (ang % 60 == 0) * 6
        d.line([ex + r1 * math.cos(math.radians(ang)), ey + r1 * math.sin(math.radians(ang)),
                ex + r2 * math.cos(math.radians(ang)), ey + r2 * math.sin(math.radians(ang))],
               fill=(214, 92, 32, 255), width=3)
    d.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], fill=(246, 178, 60, 255))
    # smoke column
    for k in range(4):
        d.ellipse([ex - 10 + k * 5, ey - 20 - k * 9, ex + 12 + k * 6, ey - 6 - k * 8],
                  fill=(110, 104, 98, 190))
    paste_scene(img, layer, mask)


def scene_zelensky(img, box):
    x, y, w, h = box
    d, layer, mask = clip_scene(img, box)
    # studio backdrop: blue over yellow bands
    d.rectangle([x, y, x + w, y + h // 2], fill=(58, 96, 164, 255))
    d.rectangle([x, y + h // 2, x + w, y + h], fill=(232, 196, 64, 255))
    # soft spotlight
    d.ellipse([x + 30, y + 4, x + 150, y + h - 2], fill=(255, 255, 255, 36))
    # bust silhouette: head, shoulders, dark sweater
    cx = x + 88
    d.ellipse([cx - 21, y + 12, cx + 21, y + 54], fill=(38, 36, 34, 255))
    d.pieslice([cx - 46, y + 40, cx + 46, y + 104], start=180, end=360, fill=(38, 36, 34, 255))
    d.rectangle([cx - 46, y + 70, cx + 46, y + h], fill=(38, 36, 34, 255))
    # big quote marks
    qf = font(SERIF_B, 44)
    d.text((x + w - 92, y + 2), "“", font=qf, fill=(255, 255, 255, 210))
    d.text((x + w - 52, y + 2), "”", font=qf, fill=(255, 255, 255, 210))
    # two broadcaster microphones angled at the bust
    for mx, col in [(x + 168, (178, 34, 30)), (x + 214, (30, 52, 92))]:
        d.line([mx + 16, y + h, mx + 4, y + 44], fill=(30, 30, 30, 255), width=4)
        d.rounded_rectangle([mx - 8, y + 18, mx + 18, y + 46], radius=7, fill=col + (255,))
        d.line([mx - 8, y + 28, mx + 18, y + 28], fill=(255, 255, 255, 200), width=2)
    # caption slate
    d.rectangle([x + w - 118, y + h - 20, x + w - 8, y + h - 5], fill=(20, 20, 24, 200))
    cf = font(SANS_B, 9)
    d.text((x + w - 110, y + h - 17), "BBC INTERVIEW", font=cf, fill=(255, 255, 255, 255))
    paste_scene(img, layer, mask)


def scene_ibiza(img, box):
    x, y, w, h = box
    d, layer, mask = clip_scene(img, box)
    rng = random.Random(7)
    d.rectangle([x, y, x + w, y + 26], fill=(196, 220, 234, 255))
    d.ellipse([x + 14, y + 5, x + 44, y + 23], fill=(255, 244, 190, 255))
    # sea with wave strokes
    d.rectangle([x, y + 26, x + w, y + h], fill=(52, 104, 148, 255))
    for _ in range(46):
        sx = x + rng.uniform(0, w - 20)
        sy = y + rng.uniform(30, h - 6)
        d.line([sx, sy, sx + 15, sy], fill=(140, 190, 220, 170), width=1)
    # capsized tanker: hull rolled toward the viewer, keel up
    hx, hy = x + 74, y + 44
    d.pieslice([hx, hy - 6, hx + 148, hy + 46], start=180, end=360, fill=(150, 52, 40, 255))
    d.rectangle([hx, hy + 19, hx + 148, hy + 24], fill=(110, 38, 30, 255))
    d.line([hx + 4, hy + 12, hx + 144, hy + 12], fill=(230, 220, 200, 255), width=2)
    for px in range(14, 140, 21):
        d.ellipse([hx + px, hy + 2, hx + px + 7, hy + 9], fill=(240, 236, 220, 255))
    # bridge tower sticking out sideways, lifeboat in the water
    d.rectangle([hx + 108, hy - 20, hx + 132, hy + 2], fill=(226, 222, 210, 255))
    d.rectangle([hx + 113, hy - 16, hx + 127, hy - 9], fill=(70, 110, 140, 255))
    d.pieslice([x + 36, y + 58, x + 76, y + 76], start=0, end=180, fill=(240, 130, 40, 255))
    # dark diesel sheen trailing right
    for k in range(5):
        d.arc([x + 208 + k * 4, y + 52 + k * 3, x + 292 - k * 3, y + 74 + k * 2],
              start=0, end=180, fill=(30, 40, 60, 150), width=2)
    # rescue helicopter with a winch line
    gx, gy = x + w - 66, y + 8
    d.ellipse([gx - 16, gy, gx + 18, gy + 11], fill=(238, 238, 238, 255))
    d.line([gx - 30, gy + 2, gx + 32, gy + 2], fill=(40, 40, 44, 255), width=3)
    d.line([gx + 16, gy + 4, gx + 30, gy - 2], fill=(40, 40, 44, 255), width=3)
    d.line([gx + 2, gy + 11, gx + 2, gy + 30], fill=(40, 40, 44, 200), width=1)
    d.ellipse([gx - 2, gy + 29, gx + 6, gy + 36], fill=(240, 130, 40, 255))
    paste_scene(img, layer, mask)


def scene_bangkok(img, box):
    x, y, w, h = box
    d, layer, mask = clip_scene(img, box)
    rng = random.Random(13)
    # dusk sky
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip((226, 168, 118), (240, 208, 170)))
        d.line([x, y + i, x + w, y + i], fill=c + (255,))
    gy = y + h - 14
    d.rectangle([x, gy, x + w, y + h], fill=(120, 108, 96, 255))
    # storage tanks row
    for tx, tw in [(10, 56), (74, 48), (238, 58)]:
        d.rectangle([x + tx, gy - 26, x + tx + tw, gy], fill=(214, 208, 196, 255))
        d.ellipse([x + tx, gy - 31, x + tx + tw, gy - 21], fill=(228, 222, 210, 255))
        d.line([x + tx, gy - 12, x + tx + tw, gy - 12], fill=(170, 60, 44, 255), width=2)
    # burning unit centre: flame column and black smoke
    fx = x + 158
    for k, (fw, col) in enumerate([(30, (206, 84, 30)), (20, (232, 128, 36)), (11, (248, 196, 84))]):
        d.polygon([(fx - fw // 2, gy), (fx, gy - 46 + k * 5), (fx + fw // 2, gy)], fill=col + (255,))
    for k in range(5):
        d.ellipse([fx - 14 + k * 7, gy - 62 - k * 6, fx + 18 + k * 9, gy - 40 - k * 5],
                  fill=(52, 48, 46, 200))
    d.rectangle([fx - 26, gy - 18, fx + 26, gy], fill=(90, 84, 78, 255))
    # pipework
    d.line([x + 66, gy - 8, x + 132, gy - 8], fill=(96, 90, 84, 255), width=3)
    d.line([x + 184, gy - 8, x + 238, gy - 8], fill=(96, 90, 84, 255), width=3)
    # fire engine with ladder and flashing light
    ex = x + w - 62
    d.rectangle([ex, gy - 14, ex + 48, gy - 2], fill=(196, 44, 36, 255))
    d.rectangle([ex + 32, gy - 21, ex + 48, gy - 13], fill=(196, 44, 36, 255))
    d.ellipse([ex + 5, gy - 5, ex + 15, gy + 3], fill=(26, 26, 26, 255))
    d.ellipse([ex + 33, gy - 5, ex + 43, gy + 3], fill=(26, 26, 26, 255))
    d.line([ex + 6, gy - 14, ex - 22, gy - 34], fill=(220, 220, 220, 255), width=2)
    d.ellipse([ex + 36, gy - 26, ex + 43, gy - 21], fill=(70, 130, 250, 255))
    for _ in range(12):
        sx = x + rng.uniform(0, w)
        d.point((sx, y + rng.uniform(0, 20)), fill=(90, 84, 78, 160))
    paste_scene(img, layer, mask)


def scene_spacex(img, box):
    x, y, w, h = box
    d, layer, mask = clip_scene(img, box)
    rng = random.Random(99)
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 44, 255))
    for _ in range(70):
        sx, sy = x + rng.uniform(0, w), y + rng.uniform(0, h - 18)
        r = rng.choice([1, 1, 1, 2])
        d.ellipse([sx, sy, sx + r, sy + r], fill=(235, 240, 255, 255))
    # earth curve along the bottom
    d.pieslice([x - 60, y + h - 34, x + w + 60, y + h + 66], start=180, end=360,
               fill=(52, 104, 178, 255))
    d.arc([x - 60, y + h - 34, x + w + 60, y + h + 66], start=180, end=360,
          fill=(150, 200, 250, 255), width=2)
    # orbit arc
    d.arc([x + 18, y - 26, x + w - 8, y + h + 8], start=20, end=150,
          fill=(170, 190, 230, 160), width=1)
    # main satellite: bus, two panel wings, dish
    sx, sy = x + 138, y + 30
    d.rectangle([sx, sy, sx + 34, sy + 20], fill=(216, 220, 228, 255))
    d.rectangle([sx + 4, sy + 4, sx + 14, sy + 10], fill=(120, 170, 220, 255))
    for px, pw in [(sx - 62, 56), (sx + 40, 56)]:
        d.rectangle([px, sy + 2, px + pw, sy + 18], fill=(44, 74, 150, 255))
        for gx in range(px + 8, px + pw - 4, 12):
            d.line([gx, sy + 2, gx, sy + 18], fill=(120, 160, 220, 200), width=1)
        d.line([px, sy + 10, px + pw, sy + 10], fill=(120, 160, 220, 200), width=1)
    d.line([sx + 17, sy + 20, sx + 17, sy + 30], fill=(216, 220, 228, 255), width=2)
    d.arc([sx + 6, sy + 24, sx + 28, sy + 40], start=300, end=120, fill=(216, 220, 228, 255), width=2)
    # two smaller satellites trailing the arc
    for ox, oy, s in [(x + 52, y + 14, 0.5), (x + 246, y + 52, 0.42)]:
        d.rectangle([ox, oy, ox + 16 * s + 8, oy + 10], fill=(200, 204, 214, 255))
        d.rectangle([ox - 16, oy + 1, ox - 2, oy + 9], fill=(44, 74, 150, 255))
        d.rectangle([ox + 20, oy + 1, ox + 34, oy + 9], fill=(44, 74, 150, 255))
    # signal arcs down to earth
    for k in range(3):
        d.arc([sx + 8 - k * 5, sy + 30 - k * 2, sx + 26 + k * 5, sy + 44 + k * 4],
              start=20, end=160, fill=(140, 220, 160, 200), width=2)
    paste_scene(img, layer, mask)


def scene_migration(img, box):
    x, y, w, h = box
    d, layer, mask = clip_scene(img, box)
    d.rectangle([x, y, x + w, y + h], fill=(238, 240, 244, 255))
    # London skyline silhouette behind the bars
    gy = y + h - 8
    sky = (168, 178, 196, 255)
    d.rectangle([x + 196, gy - 34, x + 206, gy], fill=sky)          # Big Ben tower
    d.polygon([(x + 196, gy - 34), (x + 201, gy - 42), (x + 206, gy - 34)], fill=sky)
    d.ellipse([x + 197, gy - 32, x + 205, gy - 24], fill=(238, 240, 244, 255))
    d.rectangle([x + 214, gy - 20, x + 262, gy], fill=sky)          # offices
    d.rectangle([x + 268, gy - 27, x + 282, gy], fill=sky)          # shard-ish
    d.polygon([(x + 268, gy - 27), (x + 275, gy - 38), (x + 282, gy - 27)], fill=sky)
    d.rectangle([x + 150, gy - 15, x + 192, gy], fill=sky)
    # falling bars: 204,000 a year earlier -> 77,000 now
    base = gy
    vals = [(204, (120, 128, 146)), (168, (120, 128, 146)), (121, (120, 128, 146)), (77, RED)]
    bw, gap, x0 = 26, 14, x + 16
    top = y + 8
    for i, (v, col) in enumerate(vals):
        bh = int((base - top - 12) * v / 204.0)
        bx = x0 + i * (bw + gap)
        d.rectangle([bx, base - bh, bx + bw, base], fill=col + (255,))
    # dashed trend line and big down arrow
    pts = [(x0 + 13 + i * (bw + gap), base - int((base - top - 12) * v / 204.0) - 5)
           for i, (v, _) in enumerate(vals)]
    for a, b in zip(pts, pts[1:]):
        d.line([a, b], fill=NAVY + (255,), width=2)
    ax, ay = pts[-1]
    d.polygon([(ax, ay + 8), (ax - 9, ay - 3), (ax + 2, ay - 4)], fill=RED + (255,))
    # value labels
    lf = font(SANS_B, 10)
    d.text((x0, top - 2), "204k", font=lf, fill=MUTED + (255,))
    d.text((ax - 8, ay - 22), "77k", font=font(SANS_B, 13), fill=RED + (255,))
    paste_scene(img, layer, mask)


def scene_depardieu(img, box):
    x, y, w, h = box
    d, layer, mask = clip_scene(img, box)
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210, 255))
    # courthouse: pediment, columns, steps
    cx = x + 96
    d.polygon([(cx - 74, y + 22), (cx, y + 4), (cx + 74, y + 22)], fill=(120, 104, 78, 255))
    d.rectangle([cx - 78, y + 22, cx + 78, y + 27], fill=(140, 124, 96, 255))
    for i in range(5):
        colx = cx - 62 + i * 31
        d.rectangle([colx, y + 27, colx + 9, y + 58], fill=(250, 246, 236, 255))
        d.rectangle([colx - 2, y + 27, colx + 11, y + 30], fill=(140, 124, 96, 255))
    d.rectangle([cx - 80, y + 58, cx + 80, y + 62], fill=(140, 124, 96, 255))
    d.rectangle([cx - 86, y + 62, cx + 86, y + 66], fill=(160, 146, 116, 255))
    d.rectangle([cx - 92, y + 66, cx + 92, y + 70], fill=(176, 162, 132, 255))
    # scales of justice on the right
    sx = x + w - 58
    d.line([sx, y + 12, sx, y + 52], fill=(90, 76, 52, 255), width=3)
    d.line([sx - 26, y + 16, sx + 26, y + 16], fill=(90, 76, 52, 255), width=3)
    for px in (sx - 26, sx + 26):
        d.line([px, y + 16, px - 8, y + 32], fill=(90, 76, 52, 255), width=1)
        d.line([px, y + 16, px + 8, y + 32], fill=(90, 76, 52, 255), width=1)
        d.pieslice([px - 11, y + 28, px + 11, y + 40], start=0, end=180, fill=(176, 124, 28, 255))
    d.rectangle([sx - 12, y + 52, sx + 12, y + 56], fill=(90, 76, 52, 255))
    # press cameras at the steps
    for kx in (x + 14, x + 40):
        d.rectangle([kx, y + 56, kx + 18, y + 66], fill=(36, 36, 40, 255))
        d.polygon([(kx + 18, y + 58), (kx + 27, y + 61), (kx + 18, y + 64)], fill=(36, 36, 40, 255))
        d.ellipse([kx + 3, y + 52, kx + 8, y + 57], fill=(200, 60, 50, 255))
    # gavel resting bottom-right of the steps
    gx, gy = x + w - 96, y + h - 12
    d.line([gx, gy, gx + 26, gy - 12], fill=(110, 78, 44, 255), width=4)
    d.rectangle([gx + 20, gy - 20, gx + 34, gy - 8], fill=(130, 94, 52, 255))
    d.rectangle([gx - 4, gy + 2, gx + 30, gy + 5], fill=(130, 94, 52, 255))
    paste_scene(img, layer, mask)


def scene_hongkong(img, box):
    x, y, w, h = box
    d, layer, mask = clip_scene(img, box)
    rng = random.Random(5)
    # grey morning sky
    for i in range(h):
        t = i / max(h - 1, 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip((168, 172, 178), (206, 204, 198)))
        d.line([x, y + i, x + w, y + i], fill=c + (255,))
    gy = y + h - 16
    # the tower: window grid, blackened upper corner, bamboo scaffolding
    tx, tw = x + 108, 74
    d.rectangle([tx, y + 6, tx + tw, gy], fill=(188, 182, 170, 255))
    for wy in range(y + 11, gy - 6, 9):
        for wx in range(tx + 5, tx + tw - 7, 11):
            burnt = wx > tx + tw - 26 and wy < y + 34
            d.rectangle([wx, wy, wx + 6, wy + 5],
                        fill=(70, 66, 62, 255) if burnt else (226, 222, 208, 255))
    for sx in range(tx - 8, tx + tw + 6, 10):
        d.line([sx, y + 4, sx, gy], fill=(150, 128, 84, 200), width=1)
    d.line([tx - 8, y + 22, tx + tw + 4, y + 22], fill=(150, 128, 84, 200), width=1)
    d.line([tx - 8, y + 44, tx + tw + 4, y + 44], fill=(150, 128, 84, 200), width=1)
    # neighbouring blocks
    d.rectangle([x + 26, y + 26, x + 66, gy], fill=(176, 172, 164, 255))
    d.rectangle([x + w - 62, y + 20, x + w - 24, gy], fill=(180, 176, 168, 255))
    for bx, bw2 in [(x + 26, 40), (x + w - 62, 38)]:
        for wy in range(y + 30, gy - 6, 10):
            for wx in range(bx + 5, bx + bw2 - 6, 10):
                d.rectangle([wx, wy, wx + 5, wy + 5], fill=(224, 220, 206, 255))
    # ground: mourners, flower bank, candles
    d.rectangle([x, gy, x + w, y + h], fill=(148, 144, 136, 255))
    for mx in (x + 84, x + 196, x + 214):
        d.ellipse([mx - 3, gy - 12, mx + 3, gy - 6], fill=(40, 38, 36, 255))
        d.rectangle([mx - 4, gy - 6, mx + 4, gy + 2], fill=(40, 38, 36, 255))
    for k in range(26):
        fx = x + 96 + (k % 13) * 8 + rng.uniform(-2, 2)
        fy = gy + 3 + (k // 13) * 6
        col = [(236, 236, 240), (226, 120, 140), (240, 200, 90)][k % 3]
        d.ellipse([fx, fy, fx + 5, fy + 4], fill=col + (255,))
    for k in range(9):
        cxp = x + 60 + k * 22
        d.rectangle([cxp, gy + 9, cxp + 3, gy + 13], fill=(250, 246, 230, 255))
        d.ellipse([cxp, gy + 6, cxp + 3, gy + 10], fill=(250, 190, 80, 255))
    paste_scene(img, layer, mask)


SCENES = [scene_storm, scene_kuwait, scene_zelensky, scene_ibiza, scene_bangkok,
          scene_spacex, scene_migration, scene_depardieu, scene_hongkong]

CARDS = [
    ("UNITED STATES · WEATHER", RED,
     "Thanksgiving storm batters both US coasts",
     "800,000 homes lose power, 1,000+ flights are hit and the 100th Macy's parade is postponed — a first."),
    ("KUWAIT · CONFLICT", RED,
     "Drone strike in Kuwait kills two Italians",
     "Italy and Kuwait blame Iran for the strike on Rheinmetall Italia staff. Tehran denies any role."),
    ("UKRAINE · BBC INTERVIEW", NAVY,
     "Zelensky: US too focused on Middle East",
     "Kyiv's president tells the BBC Washington is not pushing Russia hard enough on the war."),
    ("SPAIN · DISASTER AT SEA", GOLD,
     "Diesel tanker capsizes near Ibiza, one dead",
     "The Med Emre, with up to 7,000 tonnes of diesel, capsizes off the island. The crew are rescued."),
    ("THAILAND · EXPLOSION", RED,
     "Bangkok refinery blast injures nine",
     "Fire tears through Bangchak's Phra Khanong plant. Nine hurt, several critically; all units shut."),
    ("SPACE · TECHNOLOGY", NAVY,
     "SpaceX cleared for a million satellites",
     "US approves orbital data-centre satellites; Musk pledges two shares to every US child, ~$18bn."),
    ("BRITAIN · MIGRATION", (58, 110, 62),
     "UK net migration falls to 77,000",
     "The lowest figure since 1997 outside the pandemic, down from 204,000 a year earlier — ONS."),
    ("FRANCE · COURTS", GOLD,
     "Depardieu to stand trial, court rules",
     "A French court rules the actor faces trial over an alleged rape of an actress in 2018."),
    ("HONG KONG · MEMORIAL", (110, 84, 140),
     "Hong Kong marks a year since tower fire",
     "Flowers and prayers at Wang Fuk Court, a year after the blaze that killed 168 people."),
]

FIGURES = [
    ("~800,000", "homes & businesses without power"),
    ("1,000+", "flights cancelled or delayed"),
    ("77,000", "UK net migration — lowest since 1997"),
    ("12,000", "Ebola cases in the Congo outbreak"),
    ("100th", "Macy's parade, postponed a first time"),
]

ALSO = [
    "UK–EU treaty carries a 10-year exit clause.",
    "Huntingdon train attacker guilty on 14 counts.",
    "German dealer suspected of Channel boat supply.",
    "EU budget summit opens; little deal expected.",
    "Israeli strikes kill a Hamas official in Gaza.",
    "Egypt arrests motorist over Cairo tanker fire.",
    "Congo Ebola outbreak passes 12,000 cases.",
    "Cheaper HIV prevention jab reaches Africa.",
    "Myanmar refuses parts of ICJ genocide ruling.",
    "Flooded Indonesia gold mine kills 13; 13 missing.",
    "Kim calls for more warheads at missile plants.",
    "Pacific bloc, ASEAN and EU meet in Vietnam.",
    "China and EU hit back at new US tariffs.",
    "Trump seeks probe as GDP revised up to 4.3%.",
    "FedEx cargo plane overshoots Miami runway.",
    "Judge blocks FCC move against ABC stations.",
    "Mexico seeks US talks over SpaceX debris.",
    "Britain reach the Davis Cup semi-finals.",
    "Gukesh and Sindarov draw marathon Game 3.",
    "Bournemouth fans book Europa final hotels.",
    "Rodgers released; may have played last game.",
    "Sinner withdraws from Australian Open.",
    "EA adds AI John Mötson voice to FC 27.",
    "Spain's Hernández de Cos to head the ECB.",
    "Bank of Korea raises key rate to 3.25%.",
    "FIFA confirms cyberattack on its data.",
    "Almost 2,000 migrants reach Canaries in a day.",
    "Argentina's Senate suspends 2027 primaries.",
    "Guinea-Bissau junta delays vote by two years.",
    "UK writes to 100,000 reserve veterans.",
]

# Dotted world map: land spans (col_start, col_end) per row, 46 cols x 23 rows.
LAND = [
    [(3, 10), (24, 42)],
    [(2, 12), (23, 44)],
    [(3, 11), (22, 26), (28, 44)],
    [(4, 10), (21, 27), (29, 42)],
    [(4, 9), (20, 26), (30, 40)],
    [(5, 9), (19, 25), (31, 39), (41, 42)],
    [(5, 10), (18, 24), (27, 36), (41, 41)],
    [(6, 9), (17, 25), (28, 34), (37, 37)],
    [(7, 8), (16, 24), (29, 33), (35, 36)],
    [(10, 12), (17, 23), (30, 30), (34, 36)],
    [(10, 13), (18, 22), (35, 39)],
    [(10, 13), (18, 22), (36, 40), (42, 42)],
    [(11, 13), (19, 22), (38, 41)],
    [(11, 13), (19, 21), (37, 41)],
    [(11, 12), (19, 21), (38, 40)],
    [(11, 12), (19, 20), (38, 40), (44, 44)],
    [(11, 11), (44, 45)],
    [(11, 11), (45, 45)],
    [], [], [], [], [],
]

# Pin positions (col, row) for cards 1-9.
PINS = [(12, 6), (29, 7), (27, 4), (21, 7), (34, 9), (8, 7), (21, 4), (24, 5), (36, 8)]


def draw_card(img, d, x, y, w, h, idx):
    kicker, kcol, headline, summary = CARDS[idx]
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=CARD_LINE, width=1)
    scene_box = (x + 6, y + 6, w - 12, 76)
    SCENES[idx](img, scene_box)
    d.rectangle([scene_box[0], scene_box[1], scene_box[0] + scene_box[2],
                 scene_box[1] + scene_box[3]], outline=(190, 180, 152), width=1)
    # numbered badge overlapping the scene's lower-left corner
    bx, by = x + 17, y + 88
    d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=RED)
    nf = font(SANS_B, 12)
    num = str(idx + 1)
    d.text((bx - text_w(d, num, nf) / 2, by - 8), num, font=nf, fill=(255, 255, 255))
    kf = font(SANS_B, 10)
    d.text((x + 36, y + 82), kicker, font=kf, fill=kcol)
    hf = font(SERIF_B, 19)
    lines = wrap(d, headline, hf, w - 24)
    ly = y + 100
    for ln in lines[:2]:
        d.text((x + 12, ly), ln, font=hf, fill=INK)
        ly += 21
    sf = font(SANS, 11)
    sy = y + 143
    for ln in wrap(d, summary, sf, w - 24)[:2]:
        d.text((x + 12, sy), ln, font=sf, fill=MUTED)
        sy += 13


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead ------------------------------------------------------
    ef = font(SANS_B, 13)
    d.text((MARGIN, 14), spaced("THE WORLD IN ONE DAY", 1), font=ef, fill=INK)
    badge = "39 STORIES · ONE PAGE"
    bf = font(SANS_B, 12)
    bw = text_w(d, badge, bf) + 22
    d.rounded_rectangle([RIGHT - bw, 10, RIGHT, 32], radius=11, fill=RED)
    d.text((RIGHT - bw + 11, 15), badge, font=bf, fill=(255, 255, 255))
    mf = font(SERIF_B, 50)
    d.text((MARGIN - 2, 34), "Friday 27 November 2026", font=mf, fill=INK)
    sf = font(SANS, 14)
    d.text((MARGIN, 92),
           "A storm shuts down Thanksgiving on both US coasts, a drone strike kills two Italians "
           "in Kuwait — and Britain's migration falls to a 1997 low.",
           font=sf, fill=MUTED)
    d.line([MARGIN, 116, RIGHT, 116], fill=RULE, width=2)

    # --- feature cards, 3 x 3 ------------------------------------------
    cw, ch, gap = 318, 182, 10
    xs = [MARGIN, MARGIN + cw + gap, MARGIN + 2 * (cw + gap)]
    top = 124
    for i in range(9):
        draw_card(img, d, xs[i % 3], top + (i // 3) * (ch + 8), cw, ch, i)
    cards_end = top + 3 * ch + 2 * 8

    # --- by the numbers --------------------------------------------------
    fy = cards_end + 10
    d.line([MARGIN, fy, RIGHT, fy], fill=RULE, width=2)
    nf_big = font(SERIF_B, 25)
    nf_small = font(SANS, 10)
    lab = font(SANS_B, 11)
    d.text((MARGIN, fy + 10), "BY THE", font=lab, fill=RED)
    d.text((MARGIN, fy + 24), "NUMBERS", font=lab, fill=RED)
    fx = MARGIN + 74
    col_w = (RIGHT - fx) // 5
    for val, cap in FIGURES:
        d.text((fx, fy + 5), val, font=nf_big, fill=INK)
        for j, ln in enumerate(wrap(d, cap, nf_small, col_w - 12)[:2]):
            d.text((fx, fy + 34 + j * 11), ln, font=nf_small, fill=MUTED)
        fx += col_w
    fig_end = fy + 56

    # --- map + also list ---------------------------------------------------
    by = fig_end + 8
    d.line([MARGIN, by, RIGHT, by], fill=RULE, width=2)
    hf2 = font(SANS_B, 12)
    d.text((MARGIN, by + 6), "WHERE IT HAPPENED", font=hf2, fill=INK)
    d.text((MARGIN + 330, by + 6), "ALSO ON FRIDAY 27 NOVEMBER — 30 MORE STORIES",
           font=hf2, fill=INK)
    # dotted map
    mx, my = MARGIN, by + 28
    cell = 6.1
    for r, spans in enumerate(LAND):
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                px, py = mx + c * cell, my + r * cell
                d.ellipse([px, py, px + 3.4, py + 3.4], fill=(148, 158, 140))
    for n, (c, r) in enumerate(PINS, start=1):
        px, py = mx + c * cell + 1.7, my + r * cell + 1.7
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED)
        pf = font(SANS_B, 9)
        s = str(n)
        d.text((px - text_w(d, s, pf) / 2, py - 5.5), s, font=pf, fill=(255, 255, 255))
    capf = font(SANS, 9)
    d.text((mx, my + 23 * cell + 4), "Numbered dots mark stories 1–9.", font=capf, fill=MUTED)
    # also list, two numbered columns
    af = font(SANS, 10.5)
    numf = font(SANS_B, 10.5)
    col_x = [MARGIN + 330, MARGIN + 330 + 322]
    col_w2 = 316
    for i, item in enumerate(ALSO):
        col = 0 if i < 15 else 1
        row = i if i < 15 else i - 15
        ly = by + 30 + row * 12.6
        num = f"{i + 10}."
        d.text((col_x[col], ly), num, font=numf, fill=RED)
        nw = text_w(d, num, numf)
        lines = wrap(d, item, af, col_w2 - nw - 6)
        d.text((col_x[col] + nw + 5, ly), lines[0] if lines else "", font=af, fill=INK)

    # --- footer ------------------------------------------------------------
    d.line([MARGIN, 986, RIGHT, 986], fill=RULE, width=1)
    ff = font(SANS, 9.5)
    d.text((MARGIN, 992),
           "Every story was reported on 26–27 November 2026; disputed claims are attributed. "
           "Sources: BBC · Reuters · AP · ONS · France 24 · NYT · Al Jazeera · India Today. Original drawings; no photographs.",
           font=ff, fill=MUTED)

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
