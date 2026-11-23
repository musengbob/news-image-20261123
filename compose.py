#!/usr/bin/env python3
"""news-image-20261123 — Phase 1 generator.

Dense newspaper front page: "THE WORLD TODAY", Monday 23 November 2026,
36 verified stories + world map + date-check box. Deterministic:
same input produces the same bytes (no timestamps, no randomness).
Run: python3 compose.py  -> writes entry.png (1024x1024, <=1 MiB).
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (18, 18, 18)
RED = (176, 30, 30)
NAVY = (31, 58, 95)
GREY = (90, 86, 76)
LIGHT = (220, 212, 192)
OCEAN = (214, 228, 238)
LAND = (216, 200, 160)
LAND_EDGE = (150, 128, 92)

FD = "/usr/share/fonts/truetype/dejavu"
def font(name, size):
    p = os.path.join(FD, name)
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

F_MAST = font("DejaVuSerif-Bold.ttf", 56)
F_DATE = font("DejaVuSans-Bold.ttf", 15)
F_TICK = font("DejaVuSerif-Italic.ttf", 13) if os.path.exists(os.path.join(FD, "DejaVuSerif-Italic.ttf")) else font("DejaVuSerif.ttf", 13)
F_STAT_N = font("DejaVuSerif-Bold.ttf", 21)
F_STAT_L = font("DejaVuSans.ttf", 10)
F_COUNTS = font("DejaVuSans-Bold.ttf", 11)
F_KICK = font("DejaVuSans-Bold.ttf", 11)
F_HERO_H = font("DejaVuSerif-Bold.ttf", 19)
F_HERO_D = font("DejaVuSans.ttf", 11)
F_BRIEF_H = font("DejaVuSans-Bold.ttf", 13)
F_BRIEF_K = font("DejaVuSans-Bold.ttf", 10)
F_BRIEF_T = font("DejaVuSans-Bold.ttf", 12)
F_BRIEF_D = font("DejaVuSans.ttf", 10)
F_SEC = font("DejaVuSans-Bold.ttf", 13)
F_MAP_T = font("DejaVuSans-Bold.ttf", 12)
F_MAP_C = font("DejaVuSans.ttf", 9)
F_DC_T = font("DejaVuSans-Bold.ttf", 12)
F_DC = font("DejaVuSans.ttf", 11)
F_DC_F = font("DejaVuSerif-Italic.ttf", 10) if os.path.exists(os.path.join(FD, "DejaVuSerif-Italic.ttf")) else font("DejaVuSerif.ttf", 10)
F_NUM = font("DejaVuSans-Bold.ttf", 11)
F_FOOT = font("DejaVuSans.ttf", 10)

# ---------------------------------------------------------------- stories
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

BRIEF = [
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

STATS = [
    ("24", "body bags, Indonesia fire"),
    ("14", "missing in Kyiv strike"),
    ("24", "killed in South Sudan"),
    ("9", "pilgrims killed, Kota"),
    ("111", "AI-cheat cases, Korea"),
    ("$3,538", "gold after worst week"),
]

DATE_CHECK = [
    "COP31 \u2018close to a deal\u2019 \u2014 Sun 22 Nov (it then collapsed)",
    "Bahrain strike on civilian plant \u2014 Sat 21\u2013Sun 22 Nov",
    "Russian missiles land in Poland \u2014 Fri 20 Nov",
    "Trump, Xi and Putin meet in Shenzhen \u2014 Thu 19 Nov",
    "Bolsonaro taken to ICU in Brasilia \u2014 Sat 21 Nov",
]

# world map: rough stylised continents (lon, lat)
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

MARKERS = [  # (lon, lat) of top stories
    (30.7, 36.9), (4.35, 50.85), (106.3, -6.2), (30.5, 50.45),
    (127.0, 37.5), (77.2, 28.6), (-9.1, 38.7), (32.5, 15.6),
    (96.2, 16.8), (174.8, -41.3), (35.2, 31.9), (31.6, 4.85),
]

# ---------------------------------------------------------------- helpers
def wrap(text, fnt, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_lines(draw, x, y, lines, fnt, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y

def hrule(draw, x0, x1, y, wdt=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=wdt)

def glyph(draw, kind, x, y, s=30):
    """Tiny white pictogram inside a navy square."""
    draw.rectangle([x, y, x + s, y + s], fill=NAVY)
    cx, cy = x + s / 2, y + s / 2
    wht = (245, 242, 233)
    if kind == "flag":
        draw.line([(x + 9, y + 5), (x + 9, y + 25)], fill=wht, width=2)
        draw.polygon([(x + 9, y + 5), (x + 23, y + 9), (x + 9, y + 14)], fill=wht)
    elif kind == "plane":
        draw.polygon([(x + 6, cy), (x + 14, cy - 5), (x + 25, cy - 7),
                      (x + 21, cy), (x + 25, cy + 7), (x + 14, cy + 5)], fill=wht)
        draw.line([(x + 12, cy - 8), (x + 12, cy + 8)], fill=wht, width=2)
    elif kind == "bolt":
        draw.polygon([(x + 17, y + 4), (x + 9, y + 17), (x + 14, y + 17),
                      (x + 12, y + 26), (x + 21, y + 12), (x + 16, y + 12)], fill=wht)
    elif kind == "target":
        draw.ellipse([x + 7, y + 7, x + 23, y + 23], outline=wht, width=2)
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=wht)
    elif kind == "building":
        draw.rectangle([x + 8, y + 10, x + 22, y + 25], fill=wht)
        draw.polygon([(x + 6, y + 10), (x + 15, y + 4), (x + 24, y + 10)], fill=wht)
        for wy in (14, 19):
            for wx in (11, 16):
                draw.rectangle([x + wx, y + wy, x + wx + 2, y + wy + 2], fill=NAVY)
    elif kind == "ballot":
        draw.rectangle([x + 7, y + 12, x + 23, y + 25], outline=wht, width=2)
        draw.line([(x + 10, y + 19), (x + 14, y + 23), (x + 21, y + 14)],
                  fill=wht, width=2)
        draw.line([(x + 7, y + 8), (x + 23, y + 8)], fill=wht, width=2)
    elif kind == "waves":
        for wy in (11, 17, 23):
            draw.arc([x + 6, y + wy - 4, x + 24, y + wy + 4], 200, 340,
                     fill=wht, width=2)
    else:
        draw.ellipse([x + 7, y + 7, x + 23, y + 23], outline=wht, width=2)
        draw.line([(x + 7, cy), (x + 23, cy)], fill=wht, width=1)

def hero_art(draw, kind, x, y, w, h):
    if kind == "cop31":
        draw.rectangle([x, y, x + w, y + h], fill=(207, 224, 238))
        draw.ellipse([x + w - 52, y + 8, x + w - 20, y + 40], fill=(240, 200, 90))
        draw.rectangle([x, y + h - 18, x + w, y + h], fill=(122, 155, 109))
        bx, by, bw, bh = x + 40, y + 34, 150, 48
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(250, 248, 242))
        draw.polygon([(bx - 8, by), (bx + bw / 2, by - 18), (bx + bw + 8, by)],
                     fill=(176, 30, 30))
        for i in range(4):
            cx0 = bx + 14 + i * 36
            draw.rectangle([cx0, by + 10, cx0 + 8, by + bh], fill=(31, 58, 95))
        for i, c in enumerate([(31, 58, 95), (176, 30, 30), (40, 120, 70)]):
            fx = x + w - 78 + i * 24
            draw.line([(fx, y + 30), (fx, y + 58)], fill=INK, width=2)
            draw.polygon([(fx, y + 30), (fx + 16, y + 35), (fx, y + 40)], fill=c)
    elif kind == "bahrain":
        draw.rectangle([x, y, x + w, y + h], fill=(44, 62, 85))
        for i in range(18):
            draw.ellipse([x + 12 + i * 17, y + 6 + (i * 7) % 14,
                          x + 14 + i * 17, y + 8 + (i * 7) % 14], fill=(245, 242, 233))
        base = y + h - 14
        for bx, bw, bh in [(0, 52, 44), (56, 40, 62), (100, 46, 38),
                           (150, 38, 56), (192, 44, 46), (240, 48, 66),
                           (292, 21, 40)]:
            draw.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(20, 28, 42))
            for wy in range(base - bh + 6, base - 6, 10):
                for wx in range(x + bx + 6, x + bx + bw - 6, 12):
                    draw.rectangle([wx, wy, wx + 4, wy + 5], fill=(240, 200, 90))
        cx, cy = x + w - 62, y + 42
        for k in range(8):
            import math
            a = k * 3.14159 / 4
            draw.line([(cx + 12 * math.cos(a), cy + 12 * math.sin(a)),
                       (cx + 24 * math.cos(a), cy + 24 * math.sin(a))],
                      fill=(240, 140, 40), width=3)
        draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(240, 120, 30))
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(250, 220, 120))
        draw.rectangle([x, y + h - 14, x + w, y + h], fill=(18, 24, 36))
    elif kind == "nato":
        draw.rectangle([x, y, x + w, y + h], fill=(31, 58, 95))
        import math
        cx, cy = x + w / 2, y + 42
        for k in range(12):
            a = k * 3.14159 / 6 - 3.14159 / 2
            sx, sy = cx + 34 * math.cos(a), cy + 26 * math.sin(a)
            draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(240, 200, 90))
        draw.rectangle([x + 40, y + h - 26, x + w - 40, y + h - 12], fill=(250, 248, 242))
        for i, c in enumerate([(176, 30, 30), (31, 58, 95), (40, 120, 70), (240, 200, 90)]):
            fx = x + 60 + i * 52
            draw.line([(fx, y + 58), (fx, y + h - 26)], fill=(245, 242, 233), width=2)
            draw.polygon([(fx, y + 58), (fx + 18, y + 63), (fx, y + 68)], fill=c)
    elif kind == "fire":
        draw.rectangle([x, y, x + w, y + h], fill=(30, 30, 34))
        draw.rectangle([x, y + h - 16, x + w, y + h], fill=(18, 18, 22))
        for bx, bw, bh in [(10, 70, 46), (90, 60, 60), (160, 66, 40),
                           (236, 56, 54), (292, 24, 34)]:
            draw.rectangle([x + bx, y + h - 16 - bh, x + bx + bw, y + h - 16],
                           fill=(52, 52, 58))
        import math
        for fx0, fh in [(x + 30, 34), (x + 120, 44), (x + 210, 38), (x + 280, 30)]:
            fy = y + h - 16 - 44
            draw.polygon([(fx0, fy + fh), (fx0 + 14, fy), (fx0 + 28, fy + fh)],
                         fill=(240, 120, 30))
            draw.polygon([(fx0 + 7, fy + fh), (fx0 + 14, fy + 12),
                          (fx0 + 21, fy + fh)], fill=(250, 220, 120))
        for i in range(10):
            draw.ellipse([x + 20 + i * 30, y + 8 + (i * 5) % 10,
                          x + 26 + i * 30, y + 14 + (i * 5) % 10], fill=(120, 120, 128))
    else:  # baltic
        draw.rectangle([x, y, x + w, y + h], fill=(159, 195, 216))
        for wy in (y + h - 34, y + h - 22, y + h - 10):
            for wx in range(x, x + w, 26):
                draw.arc([wx, wy - 5, wx + 26, wy + 5], 180, 360, fill=(90, 130, 160), width=2)
        draw.polygon([(x + 60, y + 62), (x + 250, y + 62), (x + 235, y + 84),
                      (x + 78, y + 84)], fill=(40, 44, 52))
        for i, c in enumerate([(176, 30, 30), (31, 58, 95), (240, 200, 90), (40, 120, 70)]):
            draw.rectangle([x + 84 + i * 38, y + 38, x + 116 + i * 38, y + 62], fill=c)
        draw.rectangle([x + 226, y + 30, x + 238, y + 62], fill=(120, 40, 40))
        for dx, dy in [(x + 96, y + 16), (x + 210, y + 12)]:
            draw.ellipse([dx, dy, dx + 16, dy + 6], fill=(30, 30, 34))
            draw.line([(dx - 6, dy + 2), (dx + 22, dy + 2)], fill=(30, 30, 34), width=1)
            draw.line([(dx + 8, dy - 6), (dx + 8, dy + 10)], fill=(30, 30, 34), width=1)
        draw.ellipse([x + 252, y + 30, x + 268, y + 46], fill=(176, 30, 30))

# ---------------------------------------------------------------- build
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 26
    X0, X1 = M, W - M
    y = 18

    # masthead
    t = "THE WORLD TODAY"
    d.text(((W - d.textlength(t, font=F_MAST)) / 2, y), t, font=F_MAST, fill=INK)
    y += 64
    hrule(d, X0, X1, y, 3)
    y += 8
    t = "MONDAY 23 NOVEMBER 2026  \u00b7  36 STORIES FROM AROUND THE WORLD"
    d.text(((W - d.textlength(t, font=F_DATE)) / 2, y), t, font=F_DATE, fill=RED)
    y += 22
    t = "COP31 collapses  \u00b7  NATO meets on Poland  \u00b7  Indonesia fire toll rises  \u00b7  Gold at $3,538"
    d.text(((W - d.textlength(t, font=F_TICK)) / 2, y), t, font=F_TICK, fill=INK)
    y += 20
    hrule(d, X0, X1, y, 1)
    y += 6

    # stat strip
    cw = (X1 - X0) / 6
    for i, (num, lab) in enumerate(STATS):
        cx = X0 + i * cw
        d.text((cx + (cw - d.textlength(num, font=F_STAT_N)) / 2, y), num,
               font=F_STAT_N, fill=NAVY)
        d.text((cx + (cw - d.textlength(lab, font=F_STAT_L)) / 2, y + 26), lab,
               font=F_STAT_L, fill=GREY)
        if i:
            d.line([(cx, y + 2), (cx, y + 40)], fill=LIGHT, width=1)
    y += 48
    hrule(d, X0, X1, y, 1)
    y += 5
    t = "ASIA-PACIFIC 18  \u00b7  EUROPE 4  \u00b7  AFRICA 3  \u00b7  MIDDLE EAST 3  \u00b7  MARKETS 3  \u00b7  CLIMATE 2  \u00b7  AMERICAS 2  \u00b7  WORLD 1"
    d.text(((W - d.textlength(t, font=F_COUNTS)) / 2, y), t, font=F_COUNTS, fill=NAVY)
    y += 17
    hrule(d, X0, X1, y, 3)
    y += 10

    # heroes
    colw = int((X1 - X0 - 24) / 3)
    art_h = 88
    for i, (kick, head, deck, art) in enumerate(HEROES):
        hx = X0 + i * (colw + 12)
        hero_art(d, art, hx, y, colw, art_h)
        yy = y + art_h + 6
        d.text((hx, yy), kick, font=F_KICK, fill=RED)
        yy += 15
        hl = wrap(head, F_HERO_H, colw, d)[:2]
        yy = draw_lines(d, hx, yy, hl, F_HERO_H, INK, 22)
        dl = wrap(deck, F_HERO_D, colw, d)[:3]
        draw_lines(d, hx, yy + 2, dl, F_HERO_D, (40, 38, 34), 14)
    y += art_h + 6 + 15 + 44 + 2 + 42 + 8

    hrule(d, X0, X1, y, 2)
    y += 7
    d.text((X0, y), "THE DAY IN BRIEF", font=F_SEC, fill=INK)
    t = "9 MORE STORIES"
    d.text((X1 - d.textlength(t, font=F_SEC), y), t, font=F_SEC, fill=RED)
    y += 20

    # brief grid 3 x 3
    cell_h = 58
    for r in range(3):
        for c in range(3):
            kind, kick, head, deck = BRIEF[r * 3 + c]
            bx = X0 + c * (colw + 12)
            by = y + r * cell_h
            glyph(d, kind, bx, by + 2)
            tx = bx + 38
            tw = colw - 38
            d.text((tx, by), kick, font=F_BRIEF_K, fill=RED)
            hl = wrap(head, F_BRIEF_T, tw, d)[:1]
            yy = draw_lines(d, tx, by + 13, hl, F_BRIEF_T, INK, 15)
            dl = wrap(deck, F_BRIEF_D, tw, d)[:2]
            draw_lines(d, tx, yy + 1, dl, F_BRIEF_D, (40, 38, 34), 13)
    y += 3 * cell_h + 6

    hrule(d, X0, X1, y, 2)
    y += 8
    map_h = 152
    map_w = 636
    # world map panel
    d.rectangle([X0, y, X0 + map_w, y + map_h], fill=OCEAN, outline=INK, width=1)
    d.text((X0 + 8, y + 5), "WHERE IT HAPPENED", font=F_MAP_T, fill=NAVY)
    def proj(lon, lat):
        px = X0 + (lon + 170) / 360.0 * map_w
        py = y + 16 + (75 - lat) / 132.0 * (map_h - 28)
        return (px, py)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    for lon, lat in MARKERS:
        mx, my = proj(lon, lat)
        d.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=RED, outline=(255, 255, 255), width=1)
    d.text((X0 + 8, y + map_h - 16), "RED DOTS MARK THE STORY LOCATIONS",
           font=F_MAP_C, fill=NAVY)
    # date check box
    dc_x = X0 + map_w + 12
    dc_w = X1 - dc_x
    d.rectangle([dc_x, y, dc_x + dc_w, y + map_h], outline=RED, width=2)
    d.text((dc_x + 10, y + 7), "DATE CHECK", font=F_DC_T, fill=RED)
    d.text((dc_x + 10, y + 24), "NOT SUNDAY'S NEWS \u2014 LEFT OUT ON PURPOSE:",
           font=F_DC, fill=INK)
    yy = y + 42
    for item in DATE_CHECK:
        d.text((dc_x + 10, yy), "\u2022  " + item, font=F_DC, fill=(40, 38, 34))
        yy += 16
    d.text((dc_x + 10, y + map_h - 18), "Only 23 November stories appear above.",
           font=F_DC_F, fill=GREY)
    y += map_h + 8

    hrule(d, X0, X1, y, 2)
    y += 7
    d.text((X0, y), "ALSO ON MONDAY 23 NOVEMBER", font=F_SEC, fill=INK)
    y += 20
    # numbered list 3 cols x 8 rows
    row_h = 19
    for idx, head in enumerate(NUMBERED):
        r, c = divmod(idx, 3)
        nx = X0 + c * (colw + 12)
        ny = y + r * row_h
        num = "%d." % (idx + 13)
        d.text((nx, ny), num, font=F_NUM, fill=RED)
        nw = d.textlength(num + " ", font=F_NUM)
        hl = wrap(head, F_NUM, colw - nw, d)
        assert len(hl) == 1, "numbered headline wraps: %r -> %r" % (head, hl)
        d.text((nx + nw, ny), hl[0], font=F_NUM, fill=INK)
    y += 8 * row_h + 4

    hrule(d, X0, X1, y, 1)
    y += 6
    d.text((X0, y), "Sources: Reuters \u00b7 AFP \u00b7 BBC \u00b7 The Guardian \u00b7 ObserverVoice \u00b7 The Daily Jagran \u00b7 Korea JoongAng Daily",
           font=F_FOOT, fill=GREY)
    y += 14
    d.text((X0, y), "All stories happened, or were first reported, on Monday 23 November 2026 in some time zone. Figures as reported that day.",
           font=F_FOOT, fill=GREY)
    y += 14
    print("final y =", y, "(canvas 1024)")
    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")

if __name__ == "__main__":
    main()
