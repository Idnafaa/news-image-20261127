#!/usr/bin/env python3
"""Render the 27 November 2026 one-page world-news poster (entry.png), v3.

Third edition of the cream-paper broadsheet: a double-ruled masthead with an
edition line, nine illustrated feature cards in a 3x3 grid, a six-figure
BY THE NUMBERS strip, a dotted world map with numbered pins, and a numbered
also-list of 39 further stories in two columns — 48 stories on one page.
Every picture is drawn from scratch with PIL primitives; no photographs, no
external assets. Deterministic: the only randomness comes from fixed seeds.
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
GREEN = (58, 110, 62)
PLUM = (110, 84, 140)
CARD_LINE = (216, 207, 184)


def F(path, size):
    return ImageFont.truetype(path, size)


def tw(d, s, fnt):
    return d.textlength(s, font=fnt)


def wrap(d, s, fnt, max_w):
    """Greedy word wrap by pixel width; returns a list of lines."""
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if tw(d, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def letterspaced(s, n=1):
    return (" " * n).join(list(s.replace(" ", "_"))).replace("_", " ")


def stage(img, box):
    """Open an RGBA layer clipped to a rounded rect over box; returns (layer, draw)."""
    x, y, w, h = box
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([x, y, x + w, y + h], radius=5, fill=255)
    return layer, ImageDraw.Draw(layer), mask


def unstage(img, layer, mask):
    img.paste(layer, (0, 0), mask)


# --------------------------------------------------------------------------
# Poster data: nine feature cards, the numbers strip, the also-list.
# --------------------------------------------------------------------------

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
    ("BRITAIN · MIGRATION", GREEN,
     "UK net migration falls to 77,000",
     "The lowest figure since 1997 outside the pandemic, down from 204,000 a year earlier — ONS."),
    ("FRANCE · COURTS", GOLD,
     "Depardieu to stand trial, court rules",
     "A French court rules the actor faces trial over an alleged rape of an actress in 2018."),
    ("HONG KONG · MEMORIAL", PLUM,
     "Hong Kong marks a year since tower fire",
     "Flowers and prayers at Wang Fuk Court, a year after the blaze that killed 168 people."),
]

FIGURES = [
    ("~800,000", "homes without power in the US storm"),
    ("1,000+", "flights cancelled or delayed"),
    ("77,000", "UK net migration, lowest since 1997"),
    ("12,000", "Ebola cases in the Congo outbreak"),
    ("123", "more deaths in the Kenya cult verdict"),
    ("100th", "Macy's parade postponed, a first"),
]

ALSO = [
    "UK–EU treaty carries a 10-year exit clause.",
    "Huntingdon train attacker guilty on 14 counts.",
    "German dealer suspected of Channel boat supply.",
    "EU budget summit opens; little deal expected.",
    "France's centre risks presidential debacle.",
    "Spain votes Sunday; Sánchez defies the polls.",
    "Israeli strikes kill a Hamas official in Gaza.",
    "US disables second ship defying Iran blockade.",
    "Egypt arrests motorist over Cairo tanker fire.",
    "Congo Ebola outbreak passes 12,000 cases.",
    "Kenyan cult leader convicted over 123 deaths.",
    "Cheaper HIV prevention jab reaches Africa.",
    "Myanmar refuses parts of ICJ genocide ruling.",
    "Indonesia gold-mine flood kills 13, 13 missing.",
    "Kim calls for more warheads at missile plants.",
    "Pacific bloc, ASEAN and EU meet in Vietnam.",
    "China and EU hit back at new US tariffs.",
    "Trump seeks probe as GDP revised up to 4.3%.",
    "Stocks rally on AI relief; Shanghai +3.74%.",
    "FedEx cargo plane overshoots Miami runway.",
    "Judge blocks FCC move against ABC stations.",
    "Hackers breach Air Force Cloud One platform.",
    "Mexico seeks US talks over SpaceX debris.",
    "Canada top court upholds Quebec symbols ban.",
    "Britain reach the Davis Cup semi-finals.",
    "Australia Ashes probe widens to 2017–18.",
    "Gukesh and Sindarov draw marathon Game 3.",
    "Bournemouth fans book Europa final hotels.",
    "Rodgers released; may have played last game.",
    "Sinner withdraws from Australian Open.",
    "EA adds AI John Mötson voice to FC 27.",
    "Hernández de Cos chosen to head the ECB.",
    "Bank of Korea raises key rate to 3.25%.",
    "France slips into technical recession.",
    "FIFA confirms cyberattack on its data.",
    "Almost 2,000 migrants reach Canaries in a day.",
    "Argentina Senate suspends 2027 primaries.",
    "Guinea-Bissau junta delays vote two years.",
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

# Pin positions (col, row) for feature cards 1-9.
PINS = [(12, 6), (29, 7), (27, 4), (21, 7), (34, 9), (8, 7), (21, 4), (24, 5), (36, 8)]


# --------------------------------------------------------------------------
# Scene painters. Each paints inside box (x, y, w, h) on the shared image.
# --------------------------------------------------------------------------

def s_storm(img, box):
    """Slanting rain, bent pines, and a parade balloon held low by its crew."""
    x, y, w, h = box
    layer, d, mask = stage(img, box)
    d.rectangle([x, y, x + w, y + h], fill=(52, 62, 84, 255))
    rng = random.Random(11)
    for _ in range(90):
        rx = x + rng.uniform(0, w)
        ry = y + rng.uniform(0, h)
        d.line([rx, ry, rx - 4, ry + 7], fill=(168, 188, 214, 255), width=1)
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(30, 36, 30, 255))
    for tx in (x + 22, x + 58, x + 252, x + 282):
        d.polygon([(tx, y + h - 12), (tx + 7, y + h - 34), (tx + 16, y + h - 12)],
                  fill=(24, 44, 30, 255))
        d.line([tx + 7, y + h - 34, tx + 13, y + h - 40], fill=(24, 44, 30, 255), width=2)
    bx, by = x + 160, y + 18
    d.ellipse([bx - 27, by - 13, bx + 27, by + 13], fill=(214, 92, 60, 255))
    d.polygon([(bx - 9, by - 13), (bx + 9, by - 13), (bx + 9, by + 13), (bx - 9, by + 13)],
              fill=(228, 116, 78, 255))
    d.rectangle([bx - 4, by + 16, bx + 4, by + 20], fill=(120, 84, 40, 255))
    for gx in (bx - 18, bx, bx + 18):
        d.line([gx, by + 12, bx, by + 16], fill=(226, 220, 200, 255), width=1)
        d.line([bx, by + 20, gx - 4, y + h - 12], fill=(226, 220, 200, 255), width=1)
        d.ellipse([gx - 6, y + h - 15, gx - 3, y + h - 12], fill=(20, 20, 22, 255))
    unstage(img, layer, mask)


def s_kuwait(img, box):
    """Desert sun, a quadcopter drone, and a smoke plume over a low plant."""
    x, y, w, h = box
    layer, d, mask = stage(img, box)
    d.rectangle([x, y, x + w, y + h], fill=(232, 204, 158, 255))
    d.ellipse([x + w - 52, y + 6, x + w - 24, y + 34], fill=(244, 178, 84, 255))
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(198, 158, 104, 255))
    for bx in (x + 30, x + 78, x + 128):
        d.rectangle([bx, y + h - 26, bx + 34, y + h - 14], fill=(150, 128, 96, 255))
    for k in range(7):
        sx = x + 96 + k * 5
        sy = y + h - 30 - k * 4
        d.ellipse([sx - 6 - k, sy - 5 - k // 2, sx + 6 + k, sy + 5 + k // 2],
                  fill=(104, 100, 98, 200))
    dx, dy = x + 216, y + 16
    d.rectangle([dx - 9, dy - 3, dx + 9, dy + 3], fill=(38, 38, 42, 255))
    for ox, oy in [(-14, -8), (14, -8), (-14, 8), (14, 8)]:
        d.ellipse([dx + ox - 5, dy + oy - 2, dx + ox + 5, dy + oy + 2],
                  outline=(38, 38, 42, 255), width=2)
    d.line([dx, dy + 4, dx, y + h - 20], fill=(178, 34, 30, 160), width=1)
    unstage(img, layer, mask)


def s_zelensky(img, box):
    """A speaker at a lectern with two mic flags, blue-and-gold backdrop."""
    x, y, w, h = box
    layer, d, mask = stage(img, box)
    d.rectangle([x, y, x + w, y + h // 2], fill=(66, 104, 178, 255))
    d.rectangle([x, y + h // 2, x + w, y + h], fill=(238, 198, 84, 255))
    cx = x + w // 2
    d.ellipse([cx - 11, y + 12, cx + 11, y + 34], fill=(226, 192, 158, 255))
    d.polygon([(cx - 20, y + h), (cx - 13, y + 34), (cx + 13, y + 34), (cx + 20, y + h)],
              fill=(44, 48, 44, 255))
    d.rectangle([cx - 34, y + h - 12, cx + 34, y + h], fill=(70, 60, 48, 255))
    for mx, col in [(cx - 26, (178, 34, 30, 255)), (cx + 18, (30, 52, 92, 255))]:
        d.line([mx + 4, y + h - 12, mx + 4, y + h - 26], fill=(30, 30, 30, 255), width=2)
        d.rectangle([mx, y + h - 34, mx + 9, y + h - 25], fill=col)
    unstage(img, layer, mask)


def s_ibiza(img, box):
    """A tanker rolled onto its side in a teal sea, rescue boat alongside."""
    x, y, w, h = box
    layer, d, mask = stage(img, box)
    d.rectangle([x, y, x + w, y + h], fill=(196, 222, 224, 255))
    d.rectangle([x, y + 26, x + w, y + h], fill=(58, 122, 138, 255))
    rng = random.Random(7)
    for _ in range(26):
        wx = x + rng.uniform(0, w - 16)
        wy = y + rng.uniform(30, h - 6)
        d.arc([wx, wy, wx + 14, wy + 5], 180, 330, fill=(214, 238, 240, 255), width=1)
    hx, hy = x + 66, y + 40
    d.polygon([(hx, hy), (hx + 130, hy - 4), (hx + 122, hy + 10), (hx + 10, hy + 11)],
              fill=(120, 44, 38, 255))
    d.rectangle([hx + 20, hy - 9, hx + 44, hy - 3], fill=(70, 70, 76, 255))
    d.rectangle([hx + 88, hy - 8, hx + 98, hy - 3], fill=(70, 70, 76, 255))
    bx, by = x + 226, y + 42
    d.polygon([(bx, by + 8), (bx + 8, by), (bx + 40, by), (bx + 46, by + 8)],
              fill=(240, 240, 238, 255))
    d.rectangle([bx + 14, by - 6, bx + 30, by], fill=(178, 34, 30, 255))
    unstage(img, layer, mask)


def s_bangkok(img, box):
    """Refinery columns, a star-burst explosion and a drifting smoke cap."""
    x, y, w, h = box
    layer, d, mask = stage(img, box)
    d.rectangle([x, y, x + w, y + h], fill=(226, 196, 168, 255))
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(120, 104, 92, 255))
    for tx, th in [(x + 30, 30), (x + 62, 40), (x + 236, 34), (x + 264, 26)]:
        d.rectangle([tx, y + h - 10 - th, tx + 12, y + h - 10], fill=(96, 96, 104, 255))
        d.rectangle([tx - 2, y + h - 12 - th, tx + 14, y + h - 9 - th],
                    fill=(70, 70, 78, 255))
    cx, cy = x + 152, y + 30
    for a in range(0, 360, 30):
        r1, r2 = 5, 17 + (a % 60 == 0) * 5
        d.line([cx + r1 * math.cos(math.radians(a)), cy + r1 * math.sin(math.radians(a)),
                cx + r2 * math.cos(math.radians(a)), cy + r2 * math.sin(math.radians(a))],
               fill=(232, 120, 40, 255), width=3)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(246, 190, 70, 255))
    for k in range(6):
        sx = cx + 16 + k * 9
        sy = cy - 16 - k * 2
        d.ellipse([sx - 7, sy - 4, sx + 7, sy + 4], fill=(110, 104, 100, 190))
    unstage(img, layer, mask)


def s_spacex(img, box):
    """Night sky: a rising rocket and a neat grid of small satellites."""
    x, y, w, h = box
    layer, d, mask = stage(img, box)
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 44, 255))
    rng = random.Random(23)
    for _ in range(46):
        sx = x + rng.uniform(2, w - 2)
        sy = y + rng.uniform(2, h - 2)
        d.point((sx, sy), fill=(230, 234, 246, 255))
    for r in range(3):
        for c in range(6):
            sx, sy = x + 168 + c * 21, y + 10 + r * 14
            d.rectangle([sx - 3, sy - 2, sx + 3, sy + 2], fill=(196, 208, 230, 255))
            d.rectangle([sx - 8, sy - 1, sx - 4, sy + 1], fill=(96, 128, 190, 255))
            d.rectangle([sx + 4, sy - 1, sx + 8, sy + 1], fill=(96, 128, 190, 255))
    rx, ry = x + 66, y + h - 8
    d.polygon([(rx - 6, ry), (rx - 6, ry - 26), (rx, ry - 36), (rx + 6, ry - 26), (rx + 6, ry)],
              fill=(238, 238, 240, 255))
    d.rectangle([rx - 6, ry - 14, rx + 6, ry - 9], fill=(178, 34, 30, 255))
    d.polygon([(rx - 4, ry), (rx + 4, ry), (rx, ry + 8)], fill=(246, 168, 60, 255))
    d.line([rx, ry - 36, rx + 96, y + 12], fill=(150, 170, 210, 130), width=1)
    unstage(img, layer, mask)


def s_migration(img, box):
    """Falling bars over a skyline: the net-migration drop, drawn as a chart."""
    x, y, w, h = box
    layer, d, mask = stage(img, box)
    d.rectangle([x, y, x + w, y + h], fill=(238, 240, 234, 255))
    for bx, bh in [(x + 12, 16), (x + 34, 24), (x + 56, 12), (x + 236, 20), (x + 258, 14)]:
        d.rectangle([bx, y + h - 10 - bh, bx + 16, y + h - 10], fill=(178, 182, 172, 255))
    base = y + h - 10
    heights = [38, 33, 27, 20, 13]
    for i, bh in enumerate(heights):
        bx = x + 96 + i * 26
        d.rectangle([bx, base - bh, bx + 18, base], fill=(58, 110, 62, 255))
    d.line([x + 100, y + 12, x + 218, y + 40], fill=(178, 34, 30, 255), width=3)
    d.polygon([(x + 218, y + 40), (x + 208, y + 38), (x + 214, y + 30)],
              fill=(178, 34, 30, 255))
    unstage(img, layer, mask)


def s_depardieu(img, box):
    """Courthouse portico: four columns, a pediment, and a gavel below."""
    x, y, w, h = box
    layer, d, mask = stage(img, box)
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210, 255))
    cx = x + w // 2
    d.polygon([(cx - 74, y + 16), (cx + 74, y + 16), (cx, y + 2)], fill=(150, 138, 112, 255))
    d.rectangle([cx - 74, y + 16, cx + 74, y + 20], fill=(150, 138, 112, 255))
    for i in range(4):
        bx = cx - 60 + i * 34
        d.rectangle([bx, y + 20, bx + 12, y + h - 14], fill=(246, 242, 230, 255))
        d.rectangle([bx - 2, y + 20, bx + 14, y + 24], fill=(150, 138, 112, 255))
    d.rectangle([cx - 78, y + h - 14, cx + 78, y + h - 9], fill=(150, 138, 112, 255))
    d.line([cx + 44, y + h - 24, cx + 62, y + h - 30], fill=(120, 84, 40, 255), width=4)
    d.rectangle([cx + 58, y + h - 36, cx + 70, y + h - 28], fill=(120, 84, 40, 255))
    unstage(img, layer, mask)


def s_hongkong(img, box):
    """A tower block at dusk, windows lit, flowers and candles at its base."""
    x, y, w, h = box
    layer, d, mask = stage(img, box)
    d.rectangle([x, y, x + w, y + h], fill=(74, 66, 92, 255))
    tx, tw_ = x + 108, 92
    d.rectangle([tx, y + 4, tx + tw_, y + h - 12], fill=(52, 48, 62, 255))
    rng = random.Random(5)
    for r in range(5):
        for c in range(6):
            wx, wy = tx + 8 + c * 14, y + 9 + r * 9
            lit = rng.random() < 0.55
            d.rectangle([wx, wy, wx + 8, wy + 5],
                        fill=(246, 205, 110, 255) if lit else (88, 84, 102, 255))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(40, 38, 46, 255))
    for k in range(16):
        fx = x + 96 + (k % 8) * 13 + rng.uniform(-2, 2)
        fy = y + h - 10 + (k // 8) * 5
        col = [(238, 238, 242), (228, 128, 148), (242, 202, 96)][k % 3]
        d.ellipse([fx, fy, fx + 5, fy + 4], fill=col + (255,))
    for k in range(7):
        cxp = x + 226 + k * 9
        d.rectangle([cxp, y + h - 8, cxp + 2, y + h - 4], fill=(250, 246, 230, 255))
        d.ellipse([cxp, y + h - 11, cxp + 2, y + h - 8], fill=(250, 190, 80, 255))
    unstage(img, layer, mask)


SCENES = [s_storm, s_kuwait, s_zelensky, s_ibiza, s_bangkok,
          s_spacex, s_migration, s_depardieu, s_hongkong]


def draw_card(img, d, x, y, w, h, idx):
    kicker, kcol, headline, summary = CARDS[idx]
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=CARD_LINE, width=1)
    scene_box = (x + 6, y + 6, w - 12, 64)
    SCENES[idx](img, scene_box)
    d.rectangle([scene_box[0], scene_box[1], scene_box[0] + scene_box[2],
                 scene_box[1] + scene_box[3]], outline=(190, 180, 152), width=1)
    bx, by = x + 17, y + 80
    d.ellipse([bx - 11, by - 11, bx + 11, by + 11], fill=RED)
    nf = F(SANS_B, 12)
    num = str(idx + 1)
    d.text((bx - tw(d, num, nf) / 2, by - 8), num, font=nf, fill=(255, 255, 255))
    kf = F(SANS_B, 10)
    d.text((x + 36, y + 73), kicker, font=kf, fill=kcol)
    hf = F(SERIF_B, 18)
    ly = y + 90
    for ln in wrap(d, headline, hf, w - 24)[:2]:
        d.text((x + 12, ly), ln, font=hf, fill=INK)
        ly += 20
    sf = F(SANS, 10.5)
    sy = y + 133
    for ln in wrap(d, summary, sf, w - 24)[:2]:
        d.text((x + 12, sy), ln, font=sf, fill=MUTED)
        sy += 12.5


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead: edition line, giant date, double rule -------------------
    ef = F(SANS_B, 12)
    d.text((MARGIN, 13), letterspaced("THE WORLD IN ONE DAY", 1), font=ef, fill=INK)
    ef2 = F(SANS, 11)
    mid = "LATE FINAL EDITION"
    d.text(((W - tw(d, mid, ef2)) / 2, 14), mid, font=ef2, fill=MUTED)
    badge = "48 STORIES · ONE PAGE"
    bf = F(SANS_B, 12)
    bw = tw(d, badge, bf) + 22
    d.rounded_rectangle([RIGHT - bw, 9, RIGHT, 31], radius=11, fill=RED)
    d.text((RIGHT - bw + 11, 14), badge, font=bf, fill=(255, 255, 255))
    mf = F(SERIF_B, 48)
    d.text((MARGIN - 2, 33), "Friday 27 November 2026", font=mf, fill=INK)
    sf = F(SANS, 13.5)
    d.text((MARGIN, 90),
           "A storm shuts down Thanksgiving on both US coasts and a drone strike kills two Italians in Kuwait — "
           "48 stories, one page.",
           font=sf, fill=MUTED)
    d.line([MARGIN, 112, RIGHT, 112], fill=RULE, width=3)
    d.line([MARGIN, 117, RIGHT, 117], fill=RULE, width=1)

    # --- feature cards, 3 x 3 ----------------------------------------------
    cw, ch, gap = 318, 164, 10
    xs = [MARGIN, MARGIN + cw + gap, MARGIN + 2 * (cw + gap)]
    top = 125
    for i in range(9):
        draw_card(img, d, xs[i % 3], top + (i // 3) * (ch + 8), cw, ch, i)
    cards_end = top + 3 * ch + 2 * 8

    # --- by the numbers ------------------------------------------------------
    fy = cards_end + 10
    d.line([MARGIN, fy, RIGHT, fy], fill=RULE, width=2)
    lab = F(SANS_B, 11)
    d.text((MARGIN, fy + 11), "BY THE", font=lab, fill=RED)
    d.text((MARGIN, fy + 25), "NUMBERS", font=lab, fill=RED)
    nf_big = F(SERIF_B, 24)
    nf_small = F(SANS, 9.5)
    fx = MARGIN + 74
    col_w = (RIGHT - fx) // 6
    for val, cap in FIGURES:
        d.text((fx, fy + 6), val, font=nf_big, fill=INK)
        for j, ln in enumerate(wrap(d, cap, nf_small, col_w - 10)[:2]):
            d.text((fx, fy + 35 + j * 11), ln, font=nf_small, fill=MUTED)
        fx += col_w
    fig_end = fy + 58

    # --- map + also list -------------------------------------------------------
    by = fig_end + 8
    d.line([MARGIN, by, RIGHT, by], fill=RULE, width=2)
    hf2 = F(SANS_B, 12)
    d.text((MARGIN, by + 6), "WHERE IT HAPPENED", font=hf2, fill=INK)
    d.text((MARGIN + 306, by + 6), "ALSO ON FRIDAY 27 NOVEMBER — 39 MORE STORIES",
           font=hf2, fill=INK)
    mx, my = MARGIN, by + 30
    cell = 5.9
    for r, spans in enumerate(LAND):
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                px, py = mx + c * cell, my + r * cell
                d.ellipse([px, py, px + 3.2, py + 3.2], fill=(148, 158, 140))
    pf = F(SANS_B, 9)
    for n, (c, r) in enumerate(PINS, start=1):
        px, py = mx + c * cell + 1.6, my + r * cell + 1.6
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED)
        s = str(n)
        d.text((px - tw(d, s, pf) / 2, py - 5.5), s, font=pf, fill=(255, 255, 255))
    capf = F(SANS, 9)
    d.text((mx, my + 23 * cell + 5), "Numbered dots mark stories 1–9.", font=capf, fill=MUTED)
    af = F(SANS, 10.5)
    numf = F(SANS_B, 10.5)
    col_x = [MARGIN + 306, MARGIN + 306 + 334]
    col_w2 = 328
    half = (len(ALSO) + 1) // 2
    for i, item in enumerate(ALSO):
        col = 0 if i < half else 1
        row = i if i < half else i - half
        ly = by + 32 + row * 12.0
        num = f"{i + 10}."
        d.text((col_x[col], ly), num, font=numf, fill=RED)
        nw = tw(d, num, numf)
        lines = wrap(d, item, af, col_w2 - nw - 6)
        d.text((col_x[col] + nw + 5, ly), lines[0] if lines else "", font=af, fill=INK)

    # --- footer ------------------------------------------------------------------
    d.line([MARGIN, 980, RIGHT, 980], fill=RULE, width=1)
    ff = F(SANS, 9.5)
    d.text((MARGIN, 987),
           "Every story was reported on 26–27 November 2026; disputed claims are attributed. Sources: BBC · Reuters · AP · "
           "ONS · France 24 · Al Jazeera · India Today. Original drawings; no photographs.",
           font=ff, fill=MUTED)

    img.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
