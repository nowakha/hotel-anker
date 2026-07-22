"""Generate 64x64 pixel layout mockups for Hotel Anker Countdown Kendu box.

Brand cues from Countdown Bar (Rorschacher Echo / posters):
- Orange #FF6A00 on charcoal black
- Red/white hazard stripes
- Warning-triangle + stopwatch motif
- Technical dashed boxes / crosshair corners
- Bold condensed COUNTDOWN wordmark
- HOTEL ANKER facade: geometric A without crossbar

Target: Baubeginn 2026-10-01 00:00 Europe/Zurich
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[2] / "assets" / "kendu-64x64"
SCALE = 10  # preview = 640x640

# Countdown Bar palette
BLACK = (12, 12, 14)
CHARCOAL = (28, 28, 32)
ORANGE = (255, 106, 0)
ORANGE_DIM = (160, 70, 0)
WHITE = (245, 245, 242)
GREY = (140, 140, 145)
RED = (220, 40, 40)
NAVY = (11, 31, 51)
BRASS = (184, 149, 108)

# 3x5 digits (columns packed as bits top→bottom in 5 rows via string rows)
DIGIT_3x5 = {
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"],
    ":": ["0", "1", "0", "1", "0"],
    " ": ["0", "0", "0", "0", "0"],
    "-": ["000", "000", "111", "000", "000"],
}

# 5x7 digits for larger day readout
DIGIT_5x7 = {
    "0": [
        "01110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110",
    ],
    "1": [
        "00100",
        "01100",
        "00100",
        "00100",
        "00100",
        "00100",
        "01110",
    ],
    "2": [
        "01110",
        "10001",
        "00001",
        "00110",
        "01000",
        "10000",
        "11111",
    ],
    "3": [
        "11110",
        "00001",
        "00001",
        "01110",
        "00001",
        "00001",
        "11110",
    ],
    "4": [
        "10001",
        "10001",
        "10001",
        "11111",
        "00001",
        "00001",
        "00001",
    ],
    "5": [
        "11111",
        "10000",
        "10000",
        "11110",
        "00001",
        "00001",
        "11110",
    ],
    "6": [
        "01110",
        "10000",
        "10000",
        "11110",
        "10001",
        "10001",
        "01110",
    ],
    "7": [
        "11111",
        "00001",
        "00010",
        "00100",
        "01000",
        "01000",
        "01000",
    ],
    "8": [
        "01110",
        "10001",
        "10001",
        "01110",
        "10001",
        "10001",
        "01110",
    ],
    "9": [
        "01110",
        "10001",
        "10001",
        "01111",
        "00001",
        "00001",
        "01110",
    ],
}

# Tiny labels 3x5-ish custom glyphs (uppercase subset)
TINY = {
    "D": ["110", "101", "101", "101", "110"],
    "H": ["101", "101", "111", "101", "101"],
    "M": ["101", "111", "111", "101", "101"],
    "S": ["011", "100", "010", "001", "110"],
    "T": ["111", "010", "010", "010", "010"],
    "A": ["010", "101", "111", "101", "101"],  # with bar
    "N": ["101", "111", "111", "101", "101"],
    "K": ["101", "110", "100", "110", "101"],
    "E": ["111", "100", "110", "100", "111"],
    "R": ["110", "101", "110", "101", "101"],
    "C": ["011", "100", "100", "100", "011"],
    "O": ["010", "101", "101", "101", "010"],
    "U": ["101", "101", "101", "101", "011"],
    "B": ["110", "101", "110", "101", "110"],
    "P": ["110", "101", "110", "100", "100"],
    "I": ["111", "010", "010", "010", "111"],
    "G": ["011", "100", "101", "101", "011"],
    "L": ["100", "100", "100", "100", "111"],
    "W": ["101", "101", "111", "111", "101"],
    "V": ["101", "101", "101", "101", "010"],
    "X": ["101", "101", "010", "101", "101"],
    "Y": ["101", "101", "010", "010", "010"],
    "Z": ["111", "001", "010", "100", "111"],
    "F": ["111", "100", "110", "100", "100"],
    "J": ["001", "001", "001", "101", "010"],
    "Q": ["010", "101", "101", "111", "001"],
    " ": ["000", "000", "000", "000", "000"],
    # Chevron-A (facade style, no crossbar) — used for ANKER
    "Â": ["010", "101", "101", "101", "101"],
}


def new_canvas(bg=BLACK) -> Image.Image:
    return Image.new("RGB", (64, 64), bg)


def px(img: Image.Image, x: int, y: int, c) -> None:
    if 0 <= x < 64 and 0 <= y < 64:
        img.putpixel((x, y), c)


def fill_rect(img, x0, y0, w, h, c) -> None:
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            px(img, x, y, c)


def draw_glyph(img, rows, x, y, color, scale=1) -> int:
    """Draw bitmap glyph; return width in pixels."""
    if not rows:
        return 0
    w = len(rows[0])
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "1":
                if scale == 1:
                    px(img, x + i, y + j, color)
                else:
                    fill_rect(img, x + i * scale, y + j * scale, scale, scale, color)
    return w * scale


def draw_text(img, text, x, y, color, font=DIGIT_3x5, tracking=1, scale=1) -> int:
    cx = x
    for ch in text:
        rows = font.get(ch) or font.get(ch.upper())
        if rows is None:
            rows = TINY.get(ch) or TINY.get(ch.upper()) or TINY[" "]
        w = draw_glyph(img, rows, cx, y, color, scale=scale)
        cx += w + tracking
    return cx - x


def draw_tiny(img, text, x, y, color, tracking=1) -> int:
    return draw_text(img, text, x, y, color, font=TINY, tracking=tracking)


def hazard_stripe(img, y, h=2) -> None:
    for row in range(h):
        for x in range(64):
            # diagonal red/white
            band = ((x + row) // 4) % 2
            px(img, x, y + row, RED if band == 0 else WHITE)


def dashed_box(img, x0, y0, x1, y1, color=ORANGE, dash=2, gap=2) -> None:
    # top/bottom
    x = x0
    while x <= x1:
        for i in range(dash):
            if x + i <= x1:
                px(img, x + i, y0, color)
                px(img, x + i, y1, color)
        x += dash + gap
    y = y0
    while y <= y1:
        for i in range(dash):
            if y + i <= y1:
                px(img, x0, y + i, color)
                px(img, x1, y + i, color)
        y += dash + gap
    # crosshair corners
    for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
        px(img, x0 + dx, y0 + dy, color)
        px(img, x1 + dx, y0 + dy, color)
        px(img, x0 + dx, y1 + dy, color)
        px(img, x1 + dx, y1 + dy, color)


def draw_anchor(img, cx, cy, color=ORANGE, ring=True) -> None:
    """Compact heraldic-ish anchor ~15px tall."""
    # ring
    if ring:
        for dx, dy in (
            (0, -6),
            (-1, -6),
            (1, -6),
            (-2, -5),
            (2, -5),
            (-2, -4),
            (2, -4),
            (-1, -3),
            (1, -3),
            (0, -3),
        ):
            px(img, cx + dx, cy + dy, color)
    # shank
    for y in range(-2, 7):
        px(img, cx, cy + y, color)
        if abs(y) < 4:
            px(img, cx - 1, cy + y, color) if y % 2 == 0 else None
    # stock (crossbar)
    for x in range(-4, 5):
        px(img, cx + x, cy, color)
    # flukes
    for i in range(5):
        px(img, cx - i, cy + 6 - i // 2, color)
        px(img, cx + i, cy + 6 - i // 2, color)
    px(img, cx - 4, cy + 5, color)
    px(img, cx + 4, cy + 5, color)


def countdown_parts(now: datetime | None = None) -> tuple[int, int, int, int]:
    # Baubeginn 2026-10-01 00:00 CEST (UTC+2 in July/Oct before DST end — Oct 1 2026 is CEST)
    target = datetime(2026, 10, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=2)))
    if now is None:
        now = datetime.now(timezone(timedelta(hours=2)))
    delta = target - now
    if delta.total_seconds() < 0:
        return 0, 0, 0, 0
    total = int(delta.total_seconds())
    days = total // 86400
    rem = total % 86400
    hours = rem // 3600
    rem %= 3600
    mins = rem // 60
    secs = rem % 60
    return days, hours, mins, secs


# Demo values so mockups stay readable/stable in docs
DEMO = (71, 14, 32, 8)


# ---------------------------------------------------------------------------
# Layouts
# ---------------------------------------------------------------------------


def layout_A_split(d, h, m, s) -> Image.Image:
    """Top living logo / bottom 2x2 countdown units."""
    img = new_canvas()
    hazard_stripe(img, 0, 2)
    hazard_stripe(img, 62, 2)

    # living logo zone
    fill_rect(img, 0, 2, 64, 28, CHARCOAL)
    draw_tiny(img, "ÂNKER", 18, 5, BRASS, tracking=1)
    draw_anchor(img, 32, 20, ORANGE)

    # four cells
    cells = [
        (2, 32, f"{d:02d}", "D"),
        (33, 32, f"{h:02d}", "H"),
        (2, 48, f"{m:02d}", "M"),
        (33, 48, f"{s:02d}", "S"),
    ]
    for x, y, val, lab in cells:
        dashed_box(img, x, y, x + 28, y + 13, ORANGE_DIM, dash=1, gap=2)
        draw_tiny(img, lab, x + 2, y + 2, GREY)
        draw_text(img, val, x + 12, y + 4, ORANGE, font=DIGIT_3x5, tracking=1)
    return img


def layout_B_big_days(d, h, m, s) -> Image.Image:
    """Big days + HH:MM:SS — poster typography feel."""
    img = new_canvas()
    fill_rect(img, 0, 0, 64, 64, BLACK)
    dashed_box(img, 1, 1, 62, 62, ORANGE, dash=2, gap=2)

    # COUNTDOWN = 9*3 + 8*1 = 35px → center at x=14
    draw_tiny(img, "COUNTDOWN", 14, 4, ORANGE, tracking=1)
    draw_tiny(img, "BAR", 26, 11, GREY, tracking=1)

    # big days (5x7)
    day_str = f"{d:03d}" if d >= 100 else f"{d:02d}"
    # center
    tw = len(day_str) * 6 - 1
    x0 = (64 - tw) // 2
    draw_text(img, day_str, x0, 20, WHITE, font=DIGIT_5x7, tracking=1)
    draw_tiny(img, "TAGE", 24, 29, GREY, tracking=1)

    # HH MM SS row
    row = f"{h:02d}:{m:02d}:{s:02d}"
    draw_text(img, row, 10, 40, ORANGE, font=DIGIT_3x5, tracking=1)
    draw_tiny(img, "H  M  S", 16, 48, GREY, tracking=2)

    hazard_stripe(img, 56, 2)
    draw_tiny(img, "01 10 26", 14, 59, BRASS, tracking=1)
    return img


def layout_C_triangle(d, h, m, s) -> Image.Image:
    """Warning-triangle homage to Countdown Bar logo."""
    img = new_canvas(BLACK)

    # filled triangle outline (approximate equilateral in 64px)
    # apex (32, 4), base y=56 from x=6 to 57
    for y in range(4, 57):
        t = (y - 4) / (56 - 4)
        half = int(1 + t * 25)
        left, right = 32 - half, 32 + half
        px(img, left, y, RED)
        px(img, right, y, RED)
        if y == 56:
            for x in range(left, right + 1):
                px(img, x, y, RED)
        # inner fill dark
        for x in range(left + 1, right):
            if 8 < y < 54:
                px(img, x, y, CHARCOAL)

    # stopwatch ticks (simple ring)
    for dx, dy in (
        (0, -4),
        (3, -3),
        (4, 0),
        (3, 3),
        (0, 4),
        (-3, 3),
        (-4, 0),
        (-3, -3),
    ):
        px(img, 32 + dx, 16 + dy, WHITE)
    px(img, 32, 16, ORANGE)
    px(img, 32, 14, ORANGE)

    # shorter label fits triangle waist
    draw_tiny(img, "COUNT", 22, 24, WHITE, tracking=1)
    draw_text(img, f"{d:02d}", 24, 32, ORANGE, font=DIGIT_3x5, tracking=1)
    draw_text(img, f"{h:02d}:{m:02d}:{s:02d}", 13, 40, WHITE, font=DIGIT_3x5, tracking=1)
    draw_tiny(img, "START", 22, 48, GREY, tracking=1)
    return img


def layout_D_living_ring(d, h, m, s, pulse: int = 0) -> Image.Image:
    """Anchor center with pulse ring; countdown as orbital ticks + bottom readout."""
    img = new_canvas(NAVY)
    hazard_stripe(img, 0, 1)
    hazard_stripe(img, 63, 1)

    # outer pulse ring (radius varies with pulse 0..3)
    r = 22 + (pulse % 4)
    for ang in range(0, 360, 6):
        import math

        rad = math.radians(ang)
        x = int(32 + r * math.cos(rad))
        y = int(28 + r * 0.85 * math.sin(rad))
        c = ORANGE if (ang // 6 + pulse) % 3 == 0 else ORANGE_DIM
        px(img, x, y, c)

    draw_anchor(img, 32, 26, BRASS if pulse % 2 == 0 else ORANGE)
    draw_tiny(img, "ÂNKER", 18, 4, WHITE, tracking=1)

    # bottom countdown strip
    fill_rect(img, 0, 48, 64, 15, BLACK)
    row = f"{d:02d}d {h:02d}:{m:02d}:{s:02d}"
    draw_text(img, row, 4, 52, ORANGE, font=DIGIT_3x5, tracking=1)
    return img


def layout_E_blueprint(d, h, m, s) -> Image.Image:
    """Technical blueprint / Speisekarte poster style."""
    img = new_canvas(BLACK)
    dashed_box(img, 2, 2, 61, 61, ORANGE, dash=3, gap=2)

    draw_tiny(img, "COUNTDOWN BAR", 4, 5, ORANGE, tracking=0)
    # status line like poster
    for x in range(4, 60):
        px(img, x, 12, ORANGE_DIM if x % 2 == 0 else BLACK)

    draw_tiny(img, "STATUS PROJEKT", 8, 15, GREY, tracking=0)

    units = [
        (6, 24, f"{d:02d}", "TAGE"),
        (36, 24, f"{h:02d}", "STD"),
        (6, 40, f"{m:02d}", "MIN"),
        (36, 40, f"{s:02d}", "SEK"),
    ]
    for x, y, val, lab in units:
        fill_rect(img, x, y, 22, 14, CHARCOAL)
        draw_text(img, val, x + 4, y + 2, WHITE, font=DIGIT_3x5, tracking=1)
        draw_tiny(img, lab, x + 2, y + 9, ORANGE, tracking=0)

    draw_tiny(img, "01OKT26", 16, 56, BRASS, tracking=1)
    return img


def save_pair(img: Image.Image, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    native = OUT / f"{name}.png"
    preview = OUT / f"{name}@10x.png"
    img.save(native)
    img.resize((64 * SCALE, 64 * SCALE), Image.Resampling.NEAREST).save(preview)
    print(f"wrote {native.name} + preview")


def main() -> None:
    d, h, m, s = DEMO
    save_pair(layout_A_split(d, h, m, s), "layout-A-split-quad")
    save_pair(layout_B_big_days(d, h, m, s), "layout-B-big-days")
    save_pair(layout_C_triangle(d, h, m, s), "layout-C-warning-triangle")
    save_pair(layout_D_living_ring(d, h, m, s, pulse=1), "layout-D-living-ring")
    save_pair(layout_E_blueprint(d, h, m, s), "layout-E-blueprint")

    # animation strip for living ring (4 frames)
    frames = [layout_D_living_ring(d, h, m, s, pulse=i) for i in range(4)]
    strip = Image.new("RGB", (64 * 4 + 3 * 2, 64), (40, 40, 40))
    for i, fr in enumerate(frames):
        strip.paste(fr, (i * (64 + 2), 0))
    strip.save(OUT / "layout-D-anim-strip.png")
    strip.resize((strip.width * SCALE, strip.height * SCALE), Image.Resampling.NEAREST).save(
        OUT / "layout-D-anim-strip@10x.png"
    )
    print("wrote animation strip")

    # contact sheet
    layouts = [
        layout_A_split(d, h, m, s),
        layout_B_big_days(d, h, m, s),
        layout_C_triangle(d, h, m, s),
        layout_D_living_ring(d, h, m, s, 2),
        layout_E_blueprint(d, h, m, s),
    ]
    labels = ["A", "B", "C", "D", "E"]
    sheet = Image.new("RGB", (64 * 5 + 8 * 4, 64 + 10), (20, 20, 22))
    for i, (im, lab) in enumerate(zip(layouts, labels)):
        x = i * (64 + 8)
        sheet.paste(im, (x, 8))
    sheet_preview = sheet.resize(
        (sheet.width * SCALE, sheet.height * SCALE), Image.Resampling.NEAREST
    )
    sheet.save(OUT / "contact-sheet.png")
    sheet_preview.save(OUT / "contact-sheet@10x.png")
    print(f"done -> {OUT}")


if __name__ == "__main__":
    main()
