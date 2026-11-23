#!/usr/bin/env python3
"""news-image-20261123 — front-page renderer (Phase 1b rewrite).

Draws "THE WORLD TODAY", a dense 1024x1024 newspaper front page summing up
Monday 23 November 2026: 3 hero stories, 9 briefs, a 24-item numbered list,
a world map with story markers, a stat strip and a date-check box.

Everything on the page is drawn from the story data below with Pillow; the
output is fully deterministic (no clock, no randomness), so re-running this
script always produces the same bytes.

Usage: python3 compose.py   -> writes entry.png next to this file.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "entry.png")

PAGE_W, PAGE_H = 1024, 1024

# --- palette -------------------------------------------------------------
PAPER = (246, 241, 229)
INK = (18, 18, 18)
RED = (176, 30, 30)
NAVY = (31, 58, 95)
GREY = (90, 86, 76)
LIGHT_RULE = (220, 212, 192)
OCEAN = (214, 228, 238)
LAND = (216, 200, 160)
LAND_EDGE = (150, 128, 92)
BODY = (40, 38, 34)
CARD = (250, 248, 242)
PICTO = (245, 242, 233)

# --- fonts ---------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(filename, size):
    """DejaVu from the system font dir, falling back to Pillow's default."""
    path = os.path.join(FONT_DIR, filename)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def load_serif_italic(size):
    """Serif italic if installed, otherwise plain serif."""
    name = "DejaVuSerif-Italic.ttf"
    if not os.path.exists(os.path.join(FONT_DIR, name)):
        name = "DejaVuSerif.ttf"
    return load_font(name, size)


MASTHEAD = load_font("DejaVuSerif-Bold.ttf", 56)
DATELINE = load_font("DejaVuSans-Bold.ttf", 15)
TICKER = load_serif_italic(13)
STAT_NUM = load_font("DejaVuSerif-Bold.ttf", 21)
STAT_LBL = load_font("DejaVuSans.ttf", 10)
COUNTS = load_font("DejaVuSans-Bold.ttf", 11)
KICKER = load_font("DejaVuSans-Bold.ttf", 11)
HERO_HEAD = load_font("DejaVuSerif-Bold.ttf", 19)
HERO_DECK = load_font("DejaVuSans.ttf", 11)
BRIEF_KICK = load_font("DejaVuSans-Bold.ttf", 10)
BRIEF_HEAD = load_font("DejaVuSans-Bold.ttf", 12)
BRIEF_DECK = load_font("DejaVuSans.ttf", 10)
SECTION = load_font("DejaVuSans-Bold.ttf", 13)
MAP_TITLE = load_font("DejaVuSans-Bold.ttf", 12)
MAP_CAP = load_font("DejaVuSans.ttf", 9)
CHECK_TITLE = load_font("DejaVuSans-Bold.ttf", 12)
CHECK_BODY = load_font("DejaVuSans.ttf", 11)
CHECK_FOOT = load_serif_italic(10)
LIST_NUM = load_font("DejaVuSans-Bold.ttf", 11)
FOOTER = load_font("DejaVuSans.ttf", 10)

# --- story data ----------------------------------------------------------
# (kicker, headline, deck, artwork key)
HEROES = [
    ("COP31 \u00b7 ANTALYA",
     "COP31 collapses with no deal",
     "The EU and UK reject a draft silent on fossil fuels; the longest "
     "climate summit on record ends empty-handed. Australia's PM calls it "
     "a sign of difficult geopolitical times.",
     "cop31"),
    ("BRUSSELS \u00b7 NATO",
     "NATO meets over Poland missiles",
     "Allies gather on Monday after prosecutors say all three objects "
     "that fell in Poland were Russian Kh-101 cruise missiles, made "
     "in late 2026.",
     "nato"),
    ("CIKANDE \u00b7 INDONESIA",
     "24 body bags after factory fire",
     "Police pull 24 body bags from the burnt candy factory in Banten "
     "as the search for dozens of missing workers resumes on Monday.",
     "fire"),
]

# (pictogram, kicker, headline, deck)
BRIEFS = [
    ("flag", "KYIV", "14 missing after Kyiv drone strike",
     "Zelenskyy says 14 are unaccounted for after a drone hits a block of flats in Dymer."),
    ("bolt", "SEOUL", "Korea minister quits over AI cheating",
     "Choi Kyo-jin resigns after 111 device cases in the college entrance exam."),
    ("flag", "NEW DELHI", "Nepal PM Shah holds talks with Modi",
     "Shah's first visit to India as premier reviews the full range of ties."),
    ("waves", "LISBON", "Thousands march over living costs",
     "Crowds fill Lisbon as anger grows over the cost of living."),
    ("target", "KHARTOUM", "Drone strikes hit homes, UN building",
     "Four killed near Sudan's capital; witnesses blame the RSF."),
    ("waves", "JUBA", "24 civilians killed in South Sudan",
     "Fresh violence claims 24 lives, AFP reports."),
    ("flag", "YANGON", "Myanmar calls ASEAN ruling \u2018unfair\u2019",
     "The army-backed government rejects the bloc's decision."),
    ("target", "WELLINGTON", "India post record 720/9d in Test",
     "Day five: India push for a famous win over New Zealand."),
    ("flag", "RAMALLAH", "Eisenkot: settler arson is \u2018terrorism\u2019",
     "Israel opens a probe after settlers torch cars in West Bank villages."),
]

# Items 13-36, drawn in three columns (13, 16, 19, ... down column one).
NUMBERED = [
    "Albanese: COP31 failure a hard lesson",
    "UN to keep talking on lethal AI arms",
    "Nvidia aide tied to China chip network",
    "India, Bulgaria talk IMEC, Black Sea",
    "Saudi coalition downs Houthi missile",
    "Iran says it downed a US drone",
    "Gold at $3,538 after worst week in months",
    "Bitcoin slides to $55,150 on Saturday",
    "Flash PMIs due as Fed hike odds near 95%",
    "Tata Steel sells tubes arm in $3.1bn deal",
    "SpiceJet pilots demand urgent safety audit",
    "BJP MP Ramrao Wadkute dies in Delhi",
    "Nine pilgrims killed in Kota road crash",
    "Shah launches Arunachal infra push",
    "Modi opens AI centre at IIT Patna",
    "UP runs air-raid drills in 75 districts",
    "Pakistan A beat India A by 48 runs",
    "Liverpool thrash Man Utd 4\u20130",
    "Messi's Miami stunned by Columbus",
    "Anupama keeps world snooker crown",
    "Guru Nanak Jayanti marked worldwide",
    "Bolsonaro \u2018stable\u2019 in intensive care",
    "Kim: North Korea seeks security, not rule",
    "WHO pleads for peace in Ebola-hit Congo",
]

# (big number, label) across the stat strip.
STAT_STRIP = [
    ("24", "body bags, Indonesia fire"),
    ("14", "missing in Kyiv strike"),
    ("24", "killed in South Sudan"),
    ("9", "pilgrims killed, Kota"),
    ("111", "AI-cheat cases, Korea"),
    ("$3,538", "gold after worst week"),
]

DATE_CHECK_ITEMS = [
    "COP31 \u2018close to a deal\u2019 \u2014 Sun 22 Nov (it then collapsed)",
    "Bahrain strike on civilian plant \u2014 Sat 21\u2013Sun 22 Nov",
    "Russian missiles land in Poland \u2014 Fri 20 Nov",
    "Trump, Xi and Putin meet in Shenzhen \u2014 Thu 19 Nov",
    "Bolsonaro taken to ICU in Brasilia \u2014 Sat 21 Nov",
]

# --- world map data ------------------------------------------------------
# Rough stylised continents as (lon, lat) outlines.
CONTINENTS = [
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-110, 68), (-95, 69),
     (-85, 66), (-80, 62), (-65, 60), (-55, 52), (-60, 46), (-70, 43),
     (-75, 38), (-80, 32), (-81, 26), (-86, 21), (-92, 15), (-97, 16),
     (-97, 26), (-105, 20), (-110, 23), (-117, 32), (-124, 40),
     (-124, 48), (-135, 58), (-152, 58), (-162, 55), (-168, 60)],
    [(-58, 64), (-45, 60), (-32, 64), (-22, 70), (-30, 74), (-45, 76),
     (-58, 76), (-62, 70)],
    [(-80, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-40, -5),
     (-35, -9), (-38, -15), (-41, -22), (-48, -27), (-55, -34),
     (-62, -39), (-68, -46), (-70, -52), (-73, -50), (-73, -40),
     (-72, -20), (-77, -12), (-81, -4), (-80, 4)],
    [(-17, 15), (-16, 20), (-10, 30), (-6, 35), (0, 36), (10, 37),
     (11, 34), (20, 32), (30, 31), (33, 27), (37, 22), (40, 15),
     (44, 11), (51, 11), (48, 2), (41, -4), (40, -10), (36, -18),
     (33, -26), (28, -33), (20, -35), (16, -29), (13, -18), (12, -8),
     (9, -1), (9, 4), (4, 6), (-8, 5), (-15, 11)],
    [(-10, 36), (-9, 43), (-2, 48), (-1, 50), (3, 52), (7, 54),
     (8, 57), (10, 59), (13, 56), (18, 56), (21, 55), (24, 58),
     (28, 59), (30, 62), (26, 65), (22, 70), (16, 70), (12, 67),
     (6, 62), (5, 58), (-1, 57), (-5, 50), (-9, 43)],
    [(30, 62), (40, 68), (55, 68), (68, 70), (85, 73), (105, 76),
     (125, 72), (145, 71), (160, 69), (178, 65), (170, 60), (162, 56),
     (156, 51), (150, 45), (142, 44), (140, 39), (135, 34), (130, 33),
     (127, 35), (122, 31), (120, 25), (112, 21), (108, 18), (105, 9),
     (100, 7), (98, 14), (96, 16), (92, 21), (88, 22), (85, 19),
     (80, 13), (77, 8), (74, 15), (70, 21), (66, 25), (61, 25),
     (57, 26), (54, 26), (50, 29), (48, 30), (44, 29), (40, 32),
     (36, 36), (33, 36), (30, 36), (27, 37), (26, 40)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (126, -32),
     (132, -32), (137, -35), (140, -38), (146, -39), (150, -37),
     (153, -27), (150, -22), (146, -19), (142, -11), (136, -12),
     (132, -11), (126, -14), (122, -17), (117, -20), (113, -22)],
]

# (lon, lat) of the stories the map marks with red dots.
MARKERS = [
    (30.7, 36.9), (4.35, 50.85), (106.3, -6.2), (30.5, 50.45),
    (127.0, 37.5), (77.2, 28.6), (-9.1, 38.7), (32.5, 15.6),
    (96.2, 16.8), (174.8, -41.3), (35.2, 31.9), (31.6, 4.85),
]

# --- drawing helpers -----------------------------------------------------


def wrap_text(text, font, max_width, draw):
    """Greedy word wrap: pack as many words per line as fit in max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw, x, y, lines, font, fill, leading):
    """Draw stacked lines, advancing y by leading each time; return new y."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def rule(draw, x0, x1, y, weight=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=weight)


def centred(draw, text, font, y, fill):
    """Draw text centred on the page at height y."""
    x = (PAGE_W - draw.textlength(text, font=font)) / 2
    draw.text((x, y), text, font=font, fill=fill)


def pictogram(draw, kind, x, y, size=30):
    """Small white pictogram on a navy square (brief-grid icons)."""
    draw.rectangle([x, y, x + size, y + size], fill=NAVY)
    cx, cy = x + size / 2, y + size / 2
    if kind == "flag":
        draw.line([(x + 9, y + 5), (x + 9, y + 25)], fill=PICTO, width=2)
        draw.polygon([(x + 9, y + 5), (x + 23, y + 9), (x + 9, y + 14)],
                     fill=PICTO)
    elif kind == "bolt":
        draw.polygon([(x + 17, y + 4), (x + 9, y + 17), (x + 14, y + 17),
                      (x + 12, y + 26), (x + 21, y + 12), (x + 16, y + 12)],
                     fill=PICTO)
    elif kind == "waves":
        for wy in (11, 17, 23):
            draw.arc([x + 6, y + wy - 4, x + 24, y + wy + 4], 200, 340,
                     fill=PICTO, width=2)
    elif kind == "target":
        draw.ellipse([x + 7, y + 7, x + 23, y + 23], outline=PICTO, width=2)
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=PICTO)
    else:
        draw.ellipse([x + 7, y + 7, x + 23, y + 23], outline=PICTO, width=2)
        draw.line([(x + 7, cy), (x + 23, cy)], fill=PICTO, width=1)


def hero_artwork(draw, kind, x, y, w, h):
    """Flat illustration panel topping a hero story."""
    if kind == "cop31":
        draw.rectangle([x, y, x + w, y + h], fill=(207, 224, 238))
        draw.ellipse([x + w - 52, y + 8, x + w - 20, y + 40],
                     fill=(240, 200, 90))
        draw.rectangle([x, y + h - 18, x + w, y + h], fill=(122, 155, 109))
        bx, by, bw, bh = x + 40, y + 34, 150, 48
        draw.rectangle([bx, by, bx + bw, by + bh], fill=CARD)
        draw.polygon([(bx - 8, by), (bx + bw / 2, by - 18), (bx + bw + 8, by)],
                     fill=RED)
        for i in range(4):
            cx0 = bx + 14 + i * 36
            draw.rectangle([cx0, by + 10, cx0 + 8, by + bh], fill=NAVY)
        for i, colour in enumerate([(31, 58, 95), (176, 30, 30), (40, 120, 70)]):
            fx = x + w - 78 + i * 24
            draw.line([(fx, y + 30), (fx, y + 58)], fill=INK, width=2)
            draw.polygon([(fx, y + 30), (fx + 16, y + 35), (fx, y + 40)],
                         fill=colour)
    elif kind == "nato":
        draw.rectangle([x, y, x + w, y + h], fill=NAVY)
        cx, cy = x + w / 2, y + 42
        for k in range(12):
            a = k * 3.14159 / 6 - 3.14159 / 2
            sx, sy = cx + 34 * math.cos(a), cy + 26 * math.sin(a)
            draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(240, 200, 90))
        draw.rectangle([x + 40, y + h - 26, x + w - 40, y + h - 12], fill=CARD)
        for i, colour in enumerate([(176, 30, 30), (31, 58, 95),
                                    (40, 120, 70), (240, 200, 90)]):
            fx = x + 60 + i * 52
            draw.line([(fx, y + 58), (fx, y + h - 26)], fill=PICTO, width=2)
            draw.polygon([(fx, y + 58), (fx + 18, y + 63), (fx, y + 68)],
                         fill=colour)
    elif kind == "fire":
        draw.rectangle([x, y, x + w, y + h], fill=(30, 30, 34))
        draw.rectangle([x, y + h - 16, x + w, y + h], fill=(18, 18, 22))
        for bx, bw, bh in [(10, 70, 46), (90, 60, 60), (160, 66, 40),
                           (236, 56, 54), (292, 24, 34)]:
            draw.rectangle([x + bx, y + h - 16 - bh, x + bx + bw, y + h - 16],
                           fill=(52, 52, 58))
        for fx0, fh in [(x + 30, 34), (x + 120, 44), (x + 210, 38), (x + 280, 30)]:
            fy = y + h - 16 - 44
            draw.polygon([(fx0, fy + fh), (fx0 + 14, fy), (fx0 + 28, fy + fh)],
                         fill=(240, 120, 30))
            draw.polygon([(fx0 + 7, fy + fh), (fx0 + 14, fy + 12),
                          (fx0 + 21, fy + fh)], fill=(250, 220, 120))
        for i in range(10):
            draw.ellipse([x + 20 + i * 30, y + 8 + (i * 5) % 10,
                          x + 26 + i * 30, y + 14 + (i * 5) % 10],
                         fill=(120, 120, 128))
    else:
        draw.rectangle([x, y, x + w, y + h], fill=OCEAN)

# --- page build ----------------------------------------------------------


def build_page():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    d = ImageDraw.Draw(img)
    margin = 26
    left, right = margin, PAGE_W - margin
    y = 18

    # -- masthead ---------------------------------------------------------
    centred(d, "THE WORLD TODAY", MASTHEAD, y, INK)
    y += 64
    rule(d, left, right, y, 3)
    y += 8
    centred(d, "MONDAY 23 NOVEMBER 2026  \u00b7  36 STORIES FROM AROUND THE WORLD",
            DATELINE, y, RED)
    y += 22
    centred(d, "COP31 collapses  \u00b7  NATO meets on Poland  \u00b7  Indonesia fire "
               "toll rises  \u00b7  Gold at $3,538", TICKER, y, INK)
    y += 20
    rule(d, left, right, y, 1)
    y += 6

    # -- stat strip -------------------------------------------------------
    cell_w = (right - left) / 6
    for i, (number, label) in enumerate(STAT_STRIP):
        cx = left + i * cell_w
        d.text((cx + (cell_w - d.textlength(number, font=STAT_NUM)) / 2, y),
               number, font=STAT_NUM, fill=NAVY)
        d.text((cx + (cell_w - d.textlength(label, font=STAT_LBL)) / 2, y + 26),
               label, font=STAT_LBL, fill=GREY)
        if i:
            d.line([(cx, y + 2), (cx, y + 40)], fill=LIGHT_RULE, width=1)
    y += 48
    rule(d, left, right, y, 1)
    y += 5
    centred(d, "ASIA-PACIFIC 18  \u00b7  EUROPE 4  \u00b7  AFRICA 3  \u00b7  "
               "MIDDLE EAST 3  \u00b7  MARKETS 3  \u00b7  CLIMATE 2  \u00b7  "
               "AMERICAS 2  \u00b7  WORLD 1", COUNTS, y, NAVY)
    y += 17
    rule(d, left, right, y, 3)
    y += 10

    # -- three hero stories ----------------------------------------------
    col_w = int((right - left - 24) / 3)
    art_h = 88
    for i, (kicker, headline, deck, art) in enumerate(HEROES):
        hx = left + i * (col_w + 12)
        hero_artwork(d, art, hx, y, col_w, art_h)
        yy = y + art_h + 6
        d.text((hx, yy), kicker, font=KICKER, fill=RED)
        yy += 15
        head_lines = wrap_text(headline, HERO_HEAD, col_w, d)[:2]
        yy = draw_wrapped(d, hx, yy, head_lines, HERO_HEAD, INK, 22)
        deck_lines = wrap_text(deck, HERO_DECK, col_w, d)[:3]
        draw_wrapped(d, hx, yy + 2, deck_lines, HERO_DECK, BODY, 14)
    y += art_h + 6 + 15 + 44 + 2 + 42 + 8

    # -- the day in brief (3 x 3) -----------------------------------------
    rule(d, left, right, y, 2)
    y += 7
    d.text((left, y), "THE DAY IN BRIEF", font=SECTION, fill=INK)
    tail = "9 MORE STORIES"
    d.text((right - d.textlength(tail, font=SECTION), y), tail,
           font=SECTION, fill=RED)
    y += 20
    cell_h = 58
    for row in range(3):
        for col in range(3):
            kind, kicker, headline, deck = BRIEFS[row * 3 + col]
            bx = left + col * (col_w + 12)
            by = y + row * cell_h
            pictogram(d, kind, bx, by + 2)
            tx = bx + 38
            tw = col_w - 38
            d.text((tx, by), kicker, font=BRIEF_KICK, fill=RED)
            head_lines = wrap_text(headline, BRIEF_HEAD, tw, d)[:1]
            yy = draw_wrapped(d, tx, by + 13, head_lines, BRIEF_HEAD, INK, 15)
            deck_lines = wrap_text(deck, BRIEF_DECK, tw, d)[:2]
            draw_wrapped(d, tx, yy + 1, deck_lines, BRIEF_DECK, BODY, 13)
    y += 3 * cell_h + 6

    # -- world map + date check -------------------------------------------
    rule(d, left, right, y, 2)
    y += 8
    map_h = 152
    map_w = 636
    d.rectangle([left, y, left + map_w, y + map_h], fill=OCEAN,
                outline=INK, width=1)
    d.text((left + 8, y + 5), "WHERE IT HAPPENED", font=MAP_TITLE, fill=NAVY)

    def project(lon, lat):
        px = left + (lon + 170) / 360.0 * map_w
        py = y + 16 + (75 - lat) / 132.0 * (map_h - 28)
        return (px, py)

    for polygon in CONTINENTS:
        d.polygon([project(lon, lat) for lon, lat in polygon],
                  fill=LAND, outline=LAND_EDGE)
    for lon, lat in MARKERS:
        mx, my = project(lon, lat)
        d.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=RED,
                  outline=(255, 255, 255), width=1)
    d.text((left + 8, y + map_h - 16), "RED DOTS MARK THE STORY LOCATIONS",
           font=MAP_CAP, fill=NAVY)

    check_x = left + map_w + 12
    check_w = right - check_x
    d.rectangle([check_x, y, check_x + check_w, y + map_h],
                outline=RED, width=2)
    d.text((check_x + 10, y + 7), "DATE CHECK", font=CHECK_TITLE, fill=RED)
    d.text((check_x + 10, y + 24),
           "NOT SUNDAY'S NEWS \u2014 LEFT OUT ON PURPOSE:",
           font=CHECK_BODY, fill=INK)
    yy = y + 42
    for item in DATE_CHECK_ITEMS:
        d.text((check_x + 10, yy), "\u2022  " + item, font=CHECK_BODY, fill=BODY)
        yy += 16
    d.text((check_x + 10, y + map_h - 18),
           "Only 23 November stories appear above.", font=CHECK_FOOT, fill=GREY)
    y += map_h + 8

    # -- numbered list 13-36 ----------------------------------------------
    rule(d, left, right, y, 2)
    y += 7
    d.text((left, y), "ALSO ON MONDAY 23 NOVEMBER", font=SECTION, fill=INK)
    y += 20
    row_h = 19
    for idx, headline in enumerate(NUMBERED):
        row, col = divmod(idx, 3)
        nx = left + col * (col_w + 12)
        ny = y + row * row_h
        number = "%d." % (idx + 13)
        d.text((nx, ny), number, font=LIST_NUM, fill=RED)
        num_w = d.textlength(number + " ", font=LIST_NUM)
        lines = wrap_text(headline, LIST_NUM, col_w - num_w, d)
        assert len(lines) == 1, "numbered headline wraps: %r -> %r" % (headline, lines)
        d.text((nx + num_w, ny), lines[0], font=LIST_NUM, fill=INK)
    y += 8 * row_h + 4

    # -- footer -----------------------------------------------------------
    rule(d, left, right, y, 1)
    y += 6
    d.text((left, y), "Sources: Reuters \u00b7 AFP \u00b7 BBC \u00b7 The Guardian "
                      "\u00b7 ObserverVoice \u00b7 The Daily Jagran \u00b7 "
                      "Korea JoongAng Daily", font=FOOTER, fill=GREY)
    y += 14
    d.text((left, y), "All stories happened, or were first reported, on "
                      "Monday 23 November 2026 in some time zone. Figures "
                      "as reported that day.", font=FOOTER, fill=GREY)
    y += 14
    print("final y =", y, "(canvas 1024)")
    img.save(OUT_PATH, "PNG", optimize=True)
    print("wrote", OUT_PATH, os.path.getsize(OUT_PATH), "bytes")


if __name__ == "__main__":
    build_page()
