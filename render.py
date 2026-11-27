"""Render the one-image world-news poster for news-image-20261127.

"THE WORLD TODAY - FRIDAY, 27 NOVEMBER 2026": a single bold dark
poster page, 1024x1024, drawn with PIL shapes and text only (no
photographs, no network). 31 stories first reported on 26-27 November
2026: one hero, six cards and 24 regional briefs. Sources are listed
in stories.md in the build folder and in the footer of the page.

Deterministic: fixed geometry, fixed text, no randomness, no clock.
Re-running this script reproduces byte-identical entry.png output.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 22
SPAN = W - 2 * MARGIN

BG = (11, 18, 32)
PANEL = (20, 30, 48)
PANEL2 = (26, 38, 60)
WHITE = (245, 246, 248)
MUTED = (168, 178, 196)
LINE = (52, 66, 92)
RED = (224, 49, 37)
AMBER = (240, 165, 32)
TEAL = (38, 166, 154)
SKY = (84, 150, 224)
PINK = (216, 110, 160)
GREEN = (110, 190, 90)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def block(d, x, y, text, fnt, fill, width, leading, max_lines=None):
    lines = wrap(d, text, fnt, width)
    if max_lines:
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ------------------------------------------------------------------ data
HERO_TAG = "UNITED STATES · WEATHER"
HERO_HEAD = "Thanksgiving storm batters both US coasts"
HERO_DEK = ("A major storm tears across the United States on Thanksgiving: "
            "roofs ripped off, streets under water, travel in chaos on the "
            "busiest weekend of the year.")
HERO_STATS = [("~800,000", "homes & businesses without power"),
              ("1,000+", "flights cancelled or delayed"),
              ("100th", "Macy's parade postponed, a first")]

CARDS = [
    ("KUWAIT · CONFLICT", RED,
     "Two Italians killed in drone strike in Kuwait",
     "Italy and Kuwait blame Iran for the strike on Rheinmetall Italia staff. Tehran denies any role."),
    ("UKRAINE · BBC INTERVIEW", SKY,
     "Zelensky: US too focused on Middle East",
     "Kyiv's president tells the BBC Washington is not pushing Russia hard enough, and questions the 'strange' Trump-Putin friendship."),
    ("SPAIN · DISASTER AT SEA", AMBER,
     "Diesel tanker capsizes near Ibiza, one dead",
     "The Med Emre, carrying up to 7,000 tonnes of diesel, capsizes off the island. The rest of the crew are rescued."),
    ("THAILAND · EXPLOSION", RED,
     "Bangkok refinery blast injures nine",
     "Fire tears through Bangchak's Phra Khanong refinery. Nine hurt, several critically; every unit shut down."),
    ("SPACE · TECHNOLOGY", TEAL,
     "SpaceX cleared for a million satellites",
     "US approves orbital data-centre satellites - and Musk pledges two SpaceX shares to every US child, about $18bn."),
    ("BRITAIN · MIGRATION", GREEN,
     "UK net migration falls to 77,000",
     "The lowest figure since 1997 outside the pandemic, down from 204,000 a year earlier, the ONS says."),
]

BRIEF_COLS = [
    ("EUROPE", SKY, [
        "Depardieu to face trial over a 2018 allegation, a French court rules.",
        "New UK-EU treaty carries a 10-year termination clause, BBC understands.",
        "Huntingdon train attacker guilty of all 14 attempted-murder counts.",
        "German dealer suspected of supplying Channel smuggling gangs - BBC.",
        "EU leaders open a Brussels budget summit nobody expects to finish.",
        "France's mainstream risks a presidential debacle, no clear candidate.",
    ], "SPORT & CULTURE", PINK, [
        "Britain beat Germany in the Davis Cup decider - first semi since 2019.",
        "Gukesh and Sindarov draw marathon Game 3 of the chess title match.",
    ]),
    ("MIDDLE EAST & AFRICA", AMBER, [
        "Israeli strikes kill a Hamas official and his wife in Gaza.",
        "Egypt arrests a motorist over the Cairo tanker crash that killed 31.",
        "Congo's Ebola outbreak passes 12,000 cases; responders driven out.",
        "Cheaper HIV prevention jab reaches Africa, hope for millions.",
        "Myanmar refuses to comply with parts of the ICJ genocide ruling.",
    ], "ASIA-PACIFIC", TEAL, [
        "Hong Kong marks one year since the tower fire that killed 168.",
        "Flooded illegal gold mine kills 13 in Indonesia; 13 missing.",
        "North Korea's Kim calls for more warheads at missile plants.",
    ]),
    ("AMERICAS", RED, [
        "China and EU hit back at US tariffs of up to 20% on 14 partners.",
        "Trump seeks probe after growth revised to 4.3%, calls it 'fake'.",
        "FedEx cargo plane overshoots the Miami runway; flights halted.",
        "Judge blocks FCC move on ABC stations; birthright order blocked.",
        "Mexico seeks US talks over suspected SpaceX debris at border.",
    ], "ALSO TODAY", GREEN, [
        "Pacific bloc, ASEAN and EU chiefs meet in Vietnam on tariffs.",
        "Bournemouth fans book Europa final hotels after Celta Vigo win.",
        "Four-time MVP Rodgers released; may have played his last game.",
    ]),
]


def draw():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---------------------------------------------------------- masthead
    d.rectangle([0, 0, W, 6], fill=RED)
    d.text((MARGIN, 20), "THE WORLD TODAY", font=F(SERIF_B, 47), fill=WHITE)
    d.text((MARGIN, 76), "FRIDAY, 27 NOVEMBER 2026  ·  THE DAY'S WORLD NEWS IN ONE IMAGE  ·  31 STORIES",
           font=F(SANS_B, 14), fill=AMBER)
    d.line([MARGIN, 102, W - MARGIN, 102], fill=LINE, width=2)

    # ---------------------------------------------------------- hero
    hy = 116
    d.rectangle([MARGIN, hy, W - MARGIN, hy + 228], fill=PANEL)
    d.rectangle([MARGIN, hy, MARGIN + 8, hy + 228], fill=RED)
    x = MARGIN + 26
    d.text((x, hy + 14), HERO_TAG, font=F(SANS_B, 14), fill=RED)
    y = block(d, x, hy + 38, HERO_HEAD, F(SERIF_B, 37), WHITE, SPAN - 52, 44, 2)
    y = block(d, x, y + 4, HERO_DEK, F(SANS, 15), MUTED, SPAN - 52, 20, 2)
    # stat chips: number on its own line, label underneath
    cw = (SPAN - 52 - 20) // 3
    cy = hy + 166
    for i, (num, label) in enumerate(HERO_STATS):
        cx = x + i * (cw + 10)
        d.rectangle([cx, cy, cx + cw, cy + 48], fill=PANEL2)
        d.text((cx + 12, cy + 5), num, font=F(SANS_B, 19), fill=AMBER)
        d.text((cx + 12, cy + 30), label, font=F(SANS, 11), fill=MUTED)

    # ---------------------------------------------------------- cards
    cy0 = 356
    card_w = (SPAN - 20) // 3
    card_h = 126
    for i, (tag, color, head, dek) in enumerate(CARDS):
        cx = MARGIN + (i % 3) * (card_w + 10)
        cyy = cy0 + (i // 3) * (card_h + 10)
        d.rectangle([cx, cyy, cx + card_w, cyy + card_h], fill=PANEL)
        d.rectangle([cx, cyy, cx + card_w, cyy + 5], fill=color)
        d.text((cx + 14, cyy + 13), tag, font=F(SANS_B, 11), fill=color)
        yy = block(d, cx + 14, cyy + 32, head, F(SANS_B, 17), WHITE, card_w - 28, 21, 2)
        block(d, cx + 14, yy + 3, dek, F(SANS, 12), MUTED, card_w - 28, 16, 3)

    # ---------------------------------------------------------- briefs
    by = 630
    d.line([MARGIN, by, W - MARGIN, by], fill=LINE, width=2)
    d.text((MARGIN, by + 8), "AROUND THE WORLD IN BRIEF", font=F(SANS_B, 15), fill=WHITE)
    col_w = (SPAN - 24) // 3
    top = by + 36
    for ci, (h1, c1, items1, h2, c2, items2) in enumerate(BRIEF_COLS):
        cx = MARGIN + ci * (col_w + 12)
        y = top
        for head, color, items in ((h1, c1, items1), (h2, c2, items2)):
            d.text((cx, y), head, font=F(SANS_B, 12), fill=color)
            y += 18
            for item in items:
                y = block(d, cx, y, item, F(SANS, 11), (214, 220, 232), col_w, 14, 3)
                y += 4
            y += 6

    # ---------------------------------------------------------- footer
    d.line([MARGIN, 984, W - MARGIN, 984], fill=LINE, width=2)
    d.text((MARGIN, 992),
           "Sources: BBC · Reuters · AP · ONS · France 24 · India Today — reporting of 26–27 Nov 2026. Drawn programmatically; no photographs.",
           font=F(SANS, 11), fill=MUTED)
    return img


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    draw().save(out, format="PNG", optimize=True)
    print(out, os.path.getsize(out))
