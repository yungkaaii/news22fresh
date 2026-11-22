"""Render the 22 November 2026 world-news poster as poster.png.

Pure Python 3.13 standard library: a small hand-built 5x7 bitmap font,
simple shape drawing on an RGB canvas, and a hand-rolled PNG encoder
(zlib + struct). No network, no third-party packages, deterministic output.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (20, 33, 61)
NAVY = (20, 33, 61)
RED = (192, 57, 43)
TEAL = (14, 124, 123)
GOLD = (201, 162, 39)
GRAY = (96, 96, 96)
WHITE = (255, 255, 255)
LIGHT_BLUE = (214, 228, 240)
LIGHT_RED = (244, 214, 210)
LIGHT_TEAL = (205, 232, 228)
LIGHT_GOLD = (246, 232, 196)
DARK_GRAY = (70, 70, 70)
ORANGE = (230, 126, 34)
SKY = (120, 170, 210)

# 5x7 bitmap font. Each glyph is 7 rows of 5 characters, '#' = ink.
FONT = {
    "A": (" .###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
}


# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = r
                self.px[i + 1] = g
                self.px[i + 2] = b

    def rect_border(self, x, y, w, h, color, t=2):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, length, color, t=1):
        self.fill_rect(x, y, length, t, color)

    def vline(self, x, y, length, color, t=1):
        self.fill_rect(x, y, t, length, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.fill_rect(x, y, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def filled_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    def ring(self, cx, cy, r, color, t=3):
        # outline circle: plot points around the circumference
        steps = max(48, int(2 * math.pi * r))
        for k in range(steps):
            a = 2 * math.pi * k / steps
            for rr in range(r - t + 1, r + 1):
                x = int(cx + rr * math.cos(a))
                y = int(cy + rr * math.sin(a))
                self.set(x, y, color)

    def ellipse_points(self, cx, cy, rx, ry, color):
        steps = max(48, int(2 * math.pi * max(rx, ry)))
        for k in range(steps):
            a = 2 * math.pi * k / steps
            x = int(cx + rx * math.cos(a))
            y = int(cy + ry * math.sin(a))
            self.fill_rect(x, y, 2, 2, color)

    def fill_triangle(self, p0, p1, p2, color):
        pts = sorted([p0, p1, p2], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        if y2 == y0:
            return
        for y in range(y0, y2 + 1):
            if y < y1:
                xa = x0 + (x1 - x0) * (y - y0) / max(1, y1 - y0)
                xb = x0 + (x2 - x0) * (y - y0) / max(1, y2 - y0)
            else:
                xa = x1 + (x2 - x1) * (y - y1) / max(1, y2 - y1)
                xb = x0 + (x2 - x0) * (y - y0) / max(1, y2 - y0)
            lo, hi = sorted([int(xa), int(xb)])
            self.hline(lo, y, hi - lo + 1, color)

    def starburst(self, cx, cy, r, color, spikes=8, inner=0.45):
        for k in range(spikes * 2):
            a = math.pi * k / spikes
            rr = r if k % 2 == 0 else int(r * inner)
            x = int(cx + rr * math.cos(a))
            y = int(cy + rr * math.sin(a))
            a2 = math.pi * (k + 1) / spikes
            rr2 = r if (k + 1) % 2 == 0 else int(r * inner)
            x2 = int(cx + rr2 * math.cos(a2))
            y2 = int(cy + rr2 * math.sin(a2))
            self.fill_triangle((cx, cy), (x, y), (x2, y2), color)


# ---------------------------------------------------------------- text

def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color, bold=False):
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
                    if bold:
                        cv.fill_rect(cx + col * scale + 1,
                                     y + row * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, cx, y, s, scale, color, bold=False):
    x = cx - text_width(s, scale) // 2
    draw_text(cv, x, y, s, scale, color, bold)
    return x


# ---------------------------------------------------------------- PNG

def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def save_png(path, cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- icons
# Each icon draws inside a 120x148 tinted box, centred near (cx, cy).

def icon_missile(cv, cx, cy):
    # flame
    cv.fill_triangle((cx - 12, cy + 34), (cx + 12, cy + 34),
                     (cx, cy + 58), ORANGE)
    cv.fill_triangle((cx - 6, cy + 34), (cx + 6, cy + 34),
                     (cx, cy + 48), RED)
    # body
    cv.fill_rect(cx - 9, cy - 30, 18, 62, DARK_GRAY)
    cv.fill_triangle((cx - 9, cy - 30), (cx + 9, cy - 30), (cx, cy - 52), RED)
    # fins
    cv.fill_triangle((cx - 9, cy + 18), (cx - 22, cy + 34), (cx - 9, cy + 32),
                     DARK_GRAY)
    cv.fill_triangle((cx + 9, cy + 18), (cx + 22, cy + 34), (cx + 9, cy + 32),
                     DARK_GRAY)
    # window
    cv.fill_rect(cx - 4, cy - 14, 8, 8, SKY)


def icon_building(cv, cx, cy):
    cv.fill_rect(cx - 32, cy - 28, 64, 78, (90, 110, 140))
    for r in range(4):
        for c in range(3):
            cv.fill_rect(cx - 24 + c * 20, cy - 18 + r * 18, 10, 10,
                         (255, 240, 180) if (r + c) % 2 else INK)
    cv.starburst(cx + 34, cy - 34, 18, ORANGE)
    cv.starburst(cx + 34, cy - 34, 10, RED)


def icon_ship(cv, cx, cy):
    cv.fill_triangle((cx - 42, cy + 8), (cx + 42, cy + 8),
                     (cx + 26, cy + 34), (70, 50, 40))
    cv.fill_rect(cx - 42, cy - 18, 84, 26, (120, 70, 50))
    cv.fill_rect(cx - 4, cy - 44, 6, 28, DARK_GRAY)
    cv.fill_rect(cx - 26, cy - 10, 18, 10, WHITE)
    cv.starburst(cx + 28, cy - 30, 14, ORANGE)
    cv.starburst(cx + 28, cy - 30, 8, RED)
    for k, yy in enumerate((cy + 42, cy + 52)):
        cv.line(cx - 44, yy, cx + 44, yy, TEAL, 3)
        cv.line(cx - 36 + k * 8, yy + 5, cx - 20 + k * 8, yy + 5, TEAL, 2)


def icon_shield(cv, cx, cy):
    cv.fill_triangle((cx - 30, cy - 40), (cx + 30, cy - 40),
                     (cx, cy + 48), (40, 80, 160))
    cv.fill_rect(cx - 30, cy - 40, 60, 44, (40, 80, 160))
    cv.fill_triangle((cx - 22, cy - 32), (cx + 22, cy - 32),
                     (cx, cy + 36), GOLD)
    cv.fill_rect(cx - 22, cy - 32, 44, 34, GOLD)
    cv.starburst(cx, cy - 8, 13, INK)
    cv.line(cx - 26, cy + 30, cx + 26, cy - 34, RED, 4)


def icon_factory(cv, cx, cy):
    cv.fill_rect(cx - 40, cy - 6, 80, 52, DARK_GRAY)
    for k in range(3):
        x0 = cx - 40 + k * 27
        cv.fill_triangle((x0, cy - 6), (x0 + 27, cy - 6),
                         (x0 + 27, cy - 30), DARK_GRAY)
    cv.fill_rect(cx + 30, cy - 44, 10, 44, DARK_GRAY)
    cv.filled_circle(cx + 35, cy - 52, 7, GRAY)
    cv.filled_circle(cx + 44, cy - 60, 5, GRAY)
    cv.starburst(cx - 8, cy - 22, 16, ORANGE)
    cv.starburst(cx - 8, cy - 22, 9, RED)
    cv.fill_rect(cx - 30, cy + 18, 16, 14, GOLD)
    cv.fill_rect(cx - 6, cy + 18, 16, 14, GOLD)


def icon_truck(cv, cx, cy):
    cv.fill_rect(cx - 44, cy - 22, 56, 34, WHITE)
    cv.rect_border(cx - 44, cy - 22, 56, 34, INK, 3)
    cv.fill_rect(cx + 12, cy - 10, 30, 22, RED)
    cv.fill_rect(cx + 18, cy - 6, 12, 8, SKY)
    cv.filled_circle(cx - 28, cy + 16, 9, INK)
    cv.filled_circle(cx + 26, cy + 16, 9, INK)
    cv.fill_rect(cx - 28, cy + 16, 2, 2, WHITE)
    for k in range(3):
        x = cx - 36 + k * 26
        cv.line(x, cy - 44, x - 8, cy - 30, TEAL, 3)


def icon_robot(cv, cx, cy):
    cv.line(cx, cy - 44, cx, cy - 30, DARK_GRAY, 3)
    cv.filled_circle(cx, cy - 48, 5, RED)
    cv.fill_rect(cx - 30, cy - 30, 60, 48, (150, 160, 175))
    cv.rect_border(cx - 30, cy - 30, 60, 48, INK, 3)
    cv.fill_rect(cx - 20, cy - 18, 12, 10, INK)
    cv.fill_rect(cx + 8, cy - 18, 12, 10, INK)
    cv.fill_rect(cx - 14, cy + 4, 28, 4, INK)
    cv.ring(cx, cy - 6, 42, RED, 5)
    cv.line(cx - 30, cy + 24, cx + 30, cy - 36, RED, 5)


def icon_document(cv, cx, cy):
    cv.fill_rect(cx - 28, cy - 42, 56, 80, WHITE)
    cv.rect_border(cx - 28, cy - 42, 56, 80, INK, 3)
    cv.fill_triangle((cx + 12, cy - 42), (cx + 28, cy - 42),
                     (cx + 28, cy - 26), LIGHT_BLUE)
    for k in range(3):
        cv.fill_rect(cx - 20, cy - 28 + k * 12, 32, 4, INK)
    cv.filled_circle(cx + 12, cy + 26, 13, GOLD)
    cv.ring(cx + 12, cy + 26, 13, (150, 110, 20), 2)
    cv.starburst(cx + 12, cy + 26, 6, (150, 110, 20))


# ---------------------------------------------------------------- layout

CARDS = [
    # (tint, icon, headline lines, sub lines)
    (LIGHT_RED, icon_missile,
     ["IRAN STRIKES", "BAHRAIN"],
     ["MISSILE HITS FACTORY;", "TANKERS ATTACKED IN", "STRAIT OF HORMUZ"]),
    (LIGHT_BLUE, icon_building,
     ["KYIV FLAT BLOCK", "HIT BY DRONE"],
     ["FIVE-STOREY BLOCK", "LEVELLED; SEVEN", "FEARED TRAPPED"]),
    (LIGHT_BLUE, icon_ship,
     ["SHIP ABLAZE IN", "THE BALTIC"],
     ["DRONE HITS RUSSIAN", "CARGO SHIP SPARTA II", "IN GULF OF FINLAND"]),
    (LIGHT_GOLD, icon_shield,
     ["FBI CRIME FILES", "HACKED"],
     ["NATIONAL DATABASE", "BREACH CONFIRMED", "BY TRUMP"]),
    (LIGHT_RED, icon_factory,
     ["SWEETS FACTORY", "FIRE IN JAVA"],
     ["THREE DEAD, 36", "MISSING IN CIKANDE,", "INDONESIA"]),
    (LIGHT_TEAL, icon_truck,
     ["GAZA AID VAN", "STRUCK"],
     ["THREE KILLED AS", "STORMS FLOOD SHELTERS", "FOR A MILLION PEOPLE"]),
    (LIGHT_GOLD, icon_robot,
     ["ROBOT WEAPONS", "TALKS FAIL"],
     ["UN GENEVA TALKS END", "WITH NO BINDING DEAL", "ON AUTONOMOUS ARMS"]),
    (LIGHT_TEAL, icon_document,
     ["EU SIGNS", "INDONESIA DEAL"],
     ["TRADE PACT AFTER", "TEN YEARS OF TALKS"]),
]


def draw_globe(cv, cx, cy, r):
    cv.ring(cx, cy, r, GOLD, 4)
    cv.ellipse_points(cx, cy, int(r * 0.45), r, GOLD)
    cv.ellipse_points(cx, cy, r, int(r * 0.45), GOLD)
    cv.hline(cx - r, cy - r // 2, 2 * r, GOLD, 2)
    cv.hline(cx - r, cy + r // 2, 2 * r, GOLD, 2)
    cv.hline(cx - r, cy, 2 * r, GOLD, 2)
    # small sun
    sx, sy = cx + r + 6, cy - r - 2
    cv.filled_circle(sx, sy, 12, GOLD)
    for k in range(8):
        a = math.pi * k / 4
        cv.line(int(sx + 16 * math.cos(a)), int(sy + 16 * math.sin(a)),
                int(sx + 24 * math.cos(a)), int(sy + 24 * math.sin(a)),
                GOLD, 3)


def build():
    cv = Canvas(W, H, PAPER)

    # masthead
    draw_text_centered(cv, W // 2, 14, "THE WORLD IN ONE DAY", 5, INK, bold=True)
    draw_text_centered(cv, W // 2, 58, "SUNDAY 22 NOVEMBER 2026", 3, RED,
                       bold=True)
    cv.fill_rect(24, 94, 976, 4, RED)

    # lead panel: COP31 climate talks stall in overtime
    cv.fill_rect(24, 108, 976, 252, NAVY)
    draw_text(cv, 48, 126, "LEAD STORY - CLIMATE SUMMIT", 2, GOLD, bold=True)
    draw_text(cv, 48, 156, "COP31 TALKS STALL", 4, WHITE, bold=True)
    draw_text(cv, 48, 192, "IN OVERTIME", 4, WHITE, bold=True)
    draw_text(cv, 48, 240, "CLIMATE SUMMIT IN ANTALYA ENTERS A SECOND", 2,
              PAPER)
    draw_text(cv, 48, 266, "DAY OF OVERTIME AS NATIONS DEADLOCK OVER", 2,
              PAPER)
    draw_text(cv, 48, 292, "FOSSIL FUELS AND THE FINAL DEAL TEXT", 2, PAPER)
    draw_globe(cv, 852, 234, 88)

    # story grid: 2 columns x 4 rows
    for idx, (tint, icon, head, sub) in enumerate(CARDS):
        col = idx % 2
        row = idx // 2
        x = 24 + col * 500
        y = 376 + row * 160
        cv.fill_rect(x, y, 476, 148, WHITE)
        cv.rect_border(x, y, 476, 148, INK, 2)
        cv.fill_rect(x, y, 476, 5, RED)
        cv.fill_rect(x, y + 5, 120, 143, tint)
        cv.vline(x + 120, y + 5, 143, INK, 2)
        icon(cv, x + 60, y + 78)
        tx = x + 134
        hy = y + 16
        for k, line in enumerate(head):
            draw_text(cv, tx, hy + k * 26, line, 3, INK, bold=True)
        sy = hy + len(head) * 26 + 10
        for k, line in enumerate(sub):
            draw_text(cv, tx, sy + k * 18, line, 2, DARK_GRAY)

    # source line
    draw_text_centered(cv, W // 2, 1012,
                       "SOURCES: AP, REUTERS, AL JAZEERA, UN, INDECI",
                       1, GRAY)
    return cv


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "poster.png")
    save_png(out, build())
    print("wrote", out)


if __name__ == "__main__":
    main()
