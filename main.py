#!/usr/bin/env python3
"""news-image-20261121: draw the front page of Saturday 21 November 2026.

Pure stdlib (zlib/struct/os/math). No network, no PIL, no external fonts:
a hand-built 5x7 bitmap font, flat vector shapes, deterministic PNG
(zlib level 9, no ancillary chunks, no timestamps). Writes entry.png to
$MAKEFUN_OUTPUT_DIR when set (the grader's /output), else to out/
next to this file as a local fallback.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

CREAM = (248, 241, 224)
INK = (28, 28, 28)
RED = (198, 32, 32)
NIGHT = (44, 58, 82)
NIGHT_DARK = (30, 42, 64)
GROUND = (18, 26, 40)
MOON = (240, 230, 180)
LAMP = (240, 200, 80)
SKY_DAY = (168, 196, 214)
STEEL = (90, 110, 130)
WHITE = (250, 250, 250)
GREY = (140, 135, 120)

# ---------------------------------------------------------------- font
# 5x7 bitmap capitals, digits and punctuation. '#' = ink, '.' = empty.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c


def fill_rect(x0, y0, x1, y1, c):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    for y in range(y0, y1):
        base = (y * W + x0) * 3
        for x in range(x0, x1):
            i = base + (x - x0) * 3
            px[i], px[i + 1], px[i + 2] = c


def draw_rect_outline(x0, y0, x1, y1, c, w=2):
    fill_rect(x0, y0, x1, y0 + w, c)
    fill_rect(x0, y1 - w, x1, y1, c)
    fill_rect(x0, y0, x0 + w, y1, c)
    fill_rect(x1 - w, y0, x1, y1, c)


def disc(cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                set_px(x, y, c)


def circle_outline(cx, cy, r, c, w=3):
    for a in range(360):
        t = math.radians(a)
        for k in range(w):
            set_px(int(cx + (r - k) * math.cos(t)),
                   int(cy + (r - k) * math.sin(t)), c)


def draw_line(x0, y0, x1, y1, c, w=1):
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    r = max(1, w // 2)
    for s in range(steps + 1):
        x = x0 + dx * s // steps
        y = y0 + dy * s // steps
        disc(x, y, r, c)


def polyline(points, c, w=1):
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        draw_line(ax, ay, bx, by, c, w)


def fill_poly(points, c):
    ys = [p[1] for p in points]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        xs = []
        n = len(points)
        for i in range(n):
            (ax, ay), (bx, by) = points[i], points[(i + 1) % n]
            if ay == by:
                continue
            if (ay <= y < by) or (by <= y < ay):
                x = ax + (y - ay) * (bx - ax) / (by - ay)
                xs.append(x)
        xs.sort()
        for j in range(0, len(xs) - 1, 2):
            for x in range(max(0, int(xs[j])), min(W, int(xs[j + 1]) + 1)):
                set_px(x, y, c)


def tilted_rect(cx, cy, w, h, angle_deg, c):
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for sx, sy in ((-w / 2, -h / 2), (w / 2, -h / 2),
                   (w / 2, h / 2), (-w / 2, h / 2)):
        pts.append((int(cx + sx * ca - sy * sa),
                    int(cy + sx * sa + sy * ca)))
    fill_poly(pts, c)
    return pts


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    fill_rect(x + gx * scale, y + gy * scale,
                              x + (gx + 1) * scale, y + (gy + 1) * scale, c)
        x += 6 * scale


def draw_text_center(cx, y, s, scale, c):
    draw_text(cx - text_width(s, scale) // 2, y, s, scale, c)


# ---------------------------------------------------------------- layout
def build():
    fill_rect(0, 0, W, H, CREAM)
    draw_rect_outline(6, 6, W - 6, H - 6, INK, 4)

    # --- masthead
    draw_text_center(W // 2, 24, "SATURDAY 21 NOVEMBER 2026", 6, INK)
    fill_rect(24, 86, W - 24, 92, RED)

    # --- hero headline + sublines
    draw_text_center(W // 2, 112, "QUAKE ROCKS PERU", 9, INK)
    draw_text_center(W // 2, 192, "MAGNITUDE 6.8 TREMOR HITS JUNIN", 2, INK)
    draw_text_center(W // 2, 214, "FELT IN LIMA - NO DAMAGE REPORTED", 2, RED)

    # --- hero art: the Andes at night, shaking
    ax0, ay0, ax1, ay1 = 24, 240, 1000, 556
    fill_rect(ax0, ay0, ax1, ay1, NIGHT)
    draw_rect_outline(ax0, ay0, ax1, ay1, INK, 3)
    # stars
    for sx, sy in ((90, 268), (180, 300), (300, 262), (430, 292), (640, 264),
                   (760, 296), (900, 258), (950, 320), (60, 340), (560, 252)):
        disc(sx, sy, 2, WHITE)
    # moon
    disc(880, 306, 34, MOON)
    disc(868, 298, 7, (222, 210, 160))
    disc(892, 318, 5, (222, 210, 160))
    # seismograph trace spiking across the sky
    trace = [(60, 340), (110, 340), (140, 330), (170, 352), (200, 322),
             (230, 360), (260, 310), (285, 368), (310, 330), (340, 342),
             (370, 340), (420, 340), (470, 334), (500, 348), (540, 326),
             (580, 356), (620, 338), (680, 340), (760, 340), (830, 340),
             (920, 340), (968, 340)]
    polyline(trace, RED, 3)
    # far ridge
    fill_poly([(24, 556), (24, 470), (140, 400), (260, 452), (380, 388),
               (520, 460), (640, 396), (780, 458), (900, 410), (1000, 470),
               (1000, 556)], NIGHT_DARK)
    # snow caps on the far ridge
    fill_poly([(140, 400), (112, 428), (168, 428)], WHITE)
    fill_poly([(380, 388), (352, 416), (408, 416)], WHITE)
    fill_poly([(640, 396), (614, 422), (666, 422)], WHITE)
    # near ridge
    fill_poly([(24, 556), (24, 512), (180, 470), (340, 516), (520, 472),
               (700, 518), (860, 476), (1000, 514), (1000, 556)], GROUND)
    # tilted buildings of Lima, windows lit
    for cx, cy, w, h, ang in ((150, 500, 66, 92, -7),
                              (255, 512, 54, 76, 6),
                              (345, 518, 60, 66, -4)):
        tilted_rect(cx, cy, w, h, ang, INK)
        for wy in (cy - h // 4, cy + 2, cy + h // 4):
            for wx in (cx - w // 4, cx + w // 4):
                disc(wx, wy, 3, LAMP)
    # the crack: ground splits open under the shaking
    crack = [(520, 470), (505, 492), (528, 510), (512, 528), (530, 546),
             (518, 556)]
    polyline(crack, RED, 5)
    polyline([(520, 470), (545, 490), (560, 505)], RED, 3)
    # caption inside the art, bottom-right, clear of the buildings and crack
    _cap = "THE ANDES, JUNIN - OVERNIGHT"
    draw_text(ax1 - 14 - text_width(_cap, 2), ay1 - 30, _cap, 2, WHITE)

    # --- divider
    fill_rect(24, 572, W - 24, 578, RED)

    # --- three minis
    cols = [(24, 352), (352, 680), (680, 1000)]
    for (x0, x1) in cols[1:]:
        fill_rect(x0 - 4, 590, x0 - 1, 990, INK)

    # mini 1: missiles over Riyadh (night sky, towers, intercepts)
    x0, x1 = cols[0]
    fill_rect(x0, 590, x1, 790, NIGHT)
    draw_rect_outline(x0, 590, x1, 790, INK, 3)
    for sx, sy in ((x0 + 40, 620), (x0 + 150, 606), (x0 + 250, 626),
                   (x0 + 300, 610)):
        disc(sx, sy, 2, WHITE)
    # skyline towers
    for tx, tw, th in ((x0 + 30, 34, 96), (x0 + 90, 26, 130),
                       (x0 + 140, 40, 88), (x0 + 210, 28, 118),
                       (x0 + 262, 34, 84)):
        fill_rect(tx, 790 - th, tx + tw, 790, INK)
        for wy in range(790 - th + 12, 786, 18):
            disc(tx + tw // 2, wy, 2, LAMP)
    # three missile trails arcing in, bursting apart
    polyline([(x0 + 20, 610), (x0 + 90, 660), (x0 + 150, 706)], LAMP, 3)
    polyline([(x0 + 300, 606), (x0 + 240, 656), (x0 + 190, 700)], LAMP, 3)
    polyline([(x0 + 160, 600), (x0 + 165, 650), (x0 + 170, 692)], WHITE, 3)
    for bx, by in ((x0 + 150, 706), (x0 + 190, 700), (x0 + 170, 692)):
        disc(bx, by, 10, RED)
        disc(bx, by, 5, LAMP)
    draw_text_center((x0 + x1) // 2, 806, "MISSILES OVER", 3, INK)
    draw_text_center((x0 + x1) // 2, 834, "RIYADH", 3, INK)
    draw_text_center((x0 + x1) // 2, 878, "3 HOUTHI MISSILES", 1, INK)
    draw_text_center((x0 + x1) // 2, 892, "INTERCEPTED SATURDAY", 1, INK)
    draw_text_center((x0 + x1) // 2, 906, "3RD DAY OF ALERTS", 1, RED)

    # mini 2: COP31 overruns (globe + clock past the deadline)
    x0, x1 = cols[1]
    fill_rect(x0, 590, x1, 790, SKY_DAY)
    draw_rect_outline(x0, 590, x1, 790, INK, 3)
    cx, cy = (x0 + x1) // 2, 690
    disc(cx, cy, 62, STEEL)
    circle_outline(cx, cy, 62, INK, 3)
    circle_outline(cx, cy, 46, INK, 2)
    draw_line(cx - 62, cy, cx + 62, cy, INK, 2)
    draw_line(cx, cy - 62, cx, cy + 62, INK, 2)
    # clock hands well past six: the deadline has gone
    draw_line(cx, cy, cx + 34, cy - 30, RED, 4)
    draw_line(cx, cy, cx - 26, cy + 22, RED, 4)
    disc(cx, cy, 5, RED)
    # empty chairs: two small chairs below the globe
    for chair_x in (x0 + 60, x1 - 60):
        fill_rect(chair_x - 22, 756, chair_x + 22, 764, INK)
        fill_rect(chair_x - 22, 756, chair_x - 16, 726, INK)
        fill_rect(chair_x - 22, 764, chair_x - 16, 786, INK)
        fill_rect(chair_x + 16, 764, chair_x + 22, 786, INK)
    draw_text_center((x0 + x1) // 2, 806, "CLIMATE TALKS", 3, INK)
    draw_text_center((x0 + x1) // 2, 834, "OVERRUN", 3, INK)
    draw_text_center((x0 + x1) // 2, 878, "DRAFT DROPS FOSSIL", 1, INK)
    draw_text_center((x0 + x1) // 2, 892, "FUELS - NO DEAL YET", 1, INK)
    draw_text_center((x0 + x1) // 2, 906, "DEADLINE PASSES", 1, RED)

    # mini 3: NATO chief to Warsaw (jet + compass over a runway)
    x0, x1 = cols[2]
    fill_rect(x0, 590, x1, 790, SKY_DAY)
    draw_rect_outline(x0, 590, x1, 790, INK, 3)
    # runway
    fill_poly([(x0 + 20, 790), (x0 + 140, 700), (x1 - 140, 700),
               (x1 - 20, 790)], GREY)
    draw_line((x0 + x1) // 2 - 6, 706, (x0 + x1) // 2 - 6, 784, WHITE, 3)
    draw_line((x0 + x1) // 2 + 6, 706, (x0 + x1) // 2 + 6, 784, WHITE, 3)
    # compass rose
    ccx, ccy = (x0 + x1) // 2, 648
    fill_poly([(ccx, ccy - 34), (ccx + 8, ccy), (ccx, ccy + 34),
               (ccx - 8, ccy)], RED)
    fill_poly([(ccx - 34, ccy), (ccx, ccy - 8), (ccx + 34, ccy),
               (ccx, ccy + 8)], INK)
    disc(ccx, ccy, 5, WHITE)
    # jet silhouette above the runway
    jx, jy = (x0 + x1) // 2, 736
    fill_poly([(jx - 46, jy), (jx + 46, jy), (jx + 30, jy - 8),
               (jx - 30, jy - 8)], INK)
    fill_poly([(jx - 6, jy - 8), (jx + 6, jy - 8), (jx + 2, jy - 26),
               (jx - 2, jy - 26)], INK)
    fill_poly([(jx - 20, jy), (jx - 34, jy + 12), (jx - 12, jy + 4)], INK)
    fill_poly([(jx + 20, jy), (jx + 34, jy + 12), (jx + 12, jy + 4)], INK)
    draw_text_center((x0 + x1) // 2, 806, "NATO CHIEF", 3, INK)
    draw_text_center((x0 + x1) // 2, 834, "TO WARSAW", 3, INK)
    draw_text_center((x0 + x1) // 2, 878, "RUTTE DUE IN WARSAW", 1, INK)
    draw_text_center((x0 + x1) // 2, 892, "AFTER POLAND INCIDENT", 1, INK)
    draw_text_center((x0 + x1) // 2, 906, "MORE NATO AIR DEFENCE", 1, RED)


# ---------------------------------------------------------------- png
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(px[y * W * 3:(y + 1) * W * 3])
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


def main():
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.png")
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "out", "entry.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
    write_png(path)


if __name__ == "__main__":
    main()
