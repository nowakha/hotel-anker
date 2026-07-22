"""Kendu Flowbox 2x2m mockups: SEG print + LED backlight segments.

Model:
  - Front: printed textile (SEG) with opaque brand + translucent 7-seg masks
  - Ghost digits printed as 888 / 88:88:88 (always visible, dim)
  - Behind: ~64x64 LED plate grid selectively lights active segments
  - Result: countdown readable only where backlight hits translucent ink

Physical: 2000 x 2000 mm backlight area (Kendu Flowbox max square).
Logical grid: 64 x 64 cells → ~31.25 mm / cell.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[2] / "assets" / "kendu-flowbox-2m"
GRID = 64
PX = 14  # render scale → 896 px square (~0.45 mm/px preview of 2m)
W = GRID * PX

# Countdown Bar / Anker palette
NAVY = (11, 31, 51)
CHARCOAL = (22, 22, 26)
BLACK = (8, 8, 10)
ORANGE = (255, 106, 0)
ORANGE_GLOW = (255, 150, 60)
ORANGE_GHOST = (70, 38, 18)
WHITE = (240, 240, 235)
GREY = (120, 120, 125)
BRASS = (184, 149, 108)
RED = (200, 45, 45)
DIFFUSER = (255, 230, 200)  # translucent segment base (print)

# 7-segment bit masks: a b c d e f g
SEG7 = {
    0: "abcdef",
    1: "bc",
    2: "abdeg",
    3: "abcdg",
    4: "bcfg",
    5: "acdfg",
    6: "acdefg",
    7: "abc",
    8: "abcdefg",
    9: "abcdfg",
}


def cell_rect(cx: int, cy: int, cw: int = 1, ch: int = 1):
    return (
        cx * PX,
        cy * PX,
        (cx + cw) * PX - 1,
        (cy + ch) * PX - 1,
    )


def fill_cells(draw: ImageDraw.ImageDraw, cx, cy, cw, ch, color):
    draw.rectangle(cell_rect(cx, cy, cw, ch), fill=color)


def hazard_band(draw, y_cell: int, h: int = 2):
    for row in range(h):
        for x in range(GRID):
            band = ((x + row) // 2) % 2
            fill_cells(draw, x, y_cell + row, 1, 1, RED if band == 0 else WHITE)


def draw_anchor_print(draw, cx: int, cy: int, color=BRASS):
    """Print-layer anchor (grid cells)."""
    # ring
    for dx, dy in [(-1, -3), (0, -3), (1, -3), (-2, -2), (2, -2), (-2, -1), (2, -1)]:
        fill_cells(draw, cx + dx, cy + dy, 1, 1, color)
    # shank
    for y in range(-1, 5):
        fill_cells(draw, cx, cy + y, 1, 1, color)
    # stock
    for x in range(-3, 4):
        fill_cells(draw, cx + x, cy, 1, 1, color)
    # flukes
    for i in range(4):
        fill_cells(draw, cx - i, cy + 4 - i // 2, 1, 1, color)
        fill_cells(draw, cx + i, cy + 4 - i // 2, 1, 1, color)


# Digit geometry in cells: outer box 7 wide x 13 tall (classic proportions)
# Segment thickness 2 cells
DW, DH = 7, 13
ST = 2  # segment thickness


def segment_cells(origin_x: int, origin_y: int) -> dict[str, list[tuple[int, int, int, int]]]:
    """Return segment name -> list of (cx, cy, cw, ch) rects in cell space."""
    x, y = origin_x, origin_y
    # a top, d bottom, g mid horizontal; b/c right; f/e left
    return {
        "a": [(x + 1, y, DW - 2, ST)],
        "b": [(x + DW - ST, y + 1, ST, DH // 2 - 1)],
        "c": [(x + DW - ST, y + DH // 2 + 1, ST, DH // 2 - 2)],
        "d": [(x + 1, y + DH - ST, DW - 2, ST)],
        "e": [(x, y + DH // 2 + 1, ST, DH // 2 - 2)],
        "f": [(x, y + 1, ST, DH // 2 - 1)],
        "g": [(x + 1, y + DH // 2 - 1, DW - 2, ST)],
    }


def paint_digit(
    draw,
    ox: int,
    oy: int,
    value: int | None,
    *,
    ghost: bool,
    lit_color=ORANGE_GLOW,
    ghost_color=ORANGE_GHOST,
):
    """Paint 7-seg digit. value=None → only ghost 8. value 0-9 → ghost + lit segments."""
    segs = segment_cells(ox, oy)
    active = set(SEG7[8 if value is None else value])
    # always draw full 8 ghost (print mask)
    if ghost:
        for name, rects in segs.items():
            for r in rects:
                fill_cells(draw, *r, ghost_color)
    if value is not None:
        for name in active:
            for r in segs[name]:
                fill_cells(draw, *r, lit_color)


def paint_colon(draw, ox: int, oy: int, lit: bool):
    c = ORANGE_GLOW if lit else ORANGE_GHOST
    fill_cells(draw, ox, oy + 4, 2, 2, c)
    fill_cells(draw, ox, oy + 8, 2, 2, c)


def layout_origins():
    """Cell origins for days (3) and time (6) on 64-grid.

    Time row layout in cells: DD : DD : DD  (digit 7 wide, colon 2, gaps 1)
    Total ≈ 6*7 + 2*2 + 5*1 = 42+4+5 = 51 → center with margin.
    """
    day_w = 3 * DW + 2 * 2
    day_x0 = (GRID - day_w) // 2
    day_y = 18
    days = [day_x0 + i * (DW + 2) for i in range(3)]

    time_y = 40
    # build: d d colon d d colon d d
    parts = []  # ('d'|':' , width)
    for group in range(3):
        if group:
            parts.append((":", 2))
            parts.append(("gap", 1))
        parts.append(("d", DW))
        parts.append(("gap", 1))
        parts.append(("d", DW))
        if group < 2:
            parts.append(("gap", 1))
    total = sum(w for _, w in parts)
    x = (GRID - total) // 2
    time_digits = []
    colons = []
    for kind, w in parts:
        if kind == "d":
            time_digits.append(x)
            x += w
        elif kind == ":":
            colons.append((x, time_y))
            x += w
        else:
            x += w
    return days, day_y, time_digits, time_y, colons


def base_print(draw: ImageDraw.ImageDraw):
    """Opaque brand print + ghost digit masks."""
    draw.rectangle((0, 0, W - 1, W - 1), fill=NAVY)
    hazard_band(draw, 0, 2)
    hazard_band(draw, 62, 2)

    # logo zone
    draw_anchor_print(draw, 32, 9, BRASS)
    # wordmark cells — ANKER chevron-A feel via simple bars
    label = "ANKER"
    # approximate with filled blocks under logo
    # COUNTDOWN BAR small print line
    for i, ch in enumerate("COUNTDOWN"):
        # decorative dots as stand-in for micro type at this scale
        fill_cells(draw, 14 + i * 4, 3, 2, 1, ORANGE)

    days, day_y, time_digits, time_y, colons = layout_origins()
    for ox in days:
        paint_digit(draw, ox, day_y, None, ghost=True)
    for ox in time_digits:
        paint_digit(draw, ox, time_y, None, ghost=True)
    for cx, cy in colons:
        paint_colon(draw, cx, cy, lit=False)

    # label "TAGE" under days — printed (not LED)
    for i in range(8):
        fill_cells(draw, 28 + i, 33, 1, 1, GREY)


def apply_countdown(draw, days_n: int, h: int, m: int, s: int):
    days, day_y, time_digits, time_y, colons = layout_origins()
    d0 = days_n // 100
    d1 = (days_n // 10) % 10
    d2 = days_n % 10
    for ox, val in zip(days, (d0, d1, d2)):
        paint_digit(draw, ox, day_y, val, ghost=True, lit_color=ORANGE_GLOW)
    vals = [h // 10, h % 10, m // 10, m % 10, s // 10, s % 10]
    for ox, val in zip(time_digits, vals):
        paint_digit(draw, ox, time_y, val, ghost=True, lit_color=ORANGE_GLOW)
    for cx, cy in colons:
        paint_colon(draw, cx, cy, lit=True)


def soft_glow_logo(draw, pulse: float = 1.0):
    """Living backlight under printed anchor (diffuse wash)."""
    # dim orange wash behind logo zone
    c = tuple(int(ORANGE[i] * 0.15 * pulse + NAVY[i] * (1 - 0.15 * pulse)) for i in range(3))
    for y in range(5, 15):
        for x in range(24, 41):
            fill_cells(draw, x, y, 1, 1, c)
    draw_anchor_print(draw, 32, 9, BRASS)


def render(mode: str, days_n=71, h=14, m=32, s=8, pulse=1.0) -> Image.Image:
    img = Image.new("RGB", (W, W), NAVY)
    draw = ImageDraw.Draw(img)
    if mode == "print_only":
        base_print(draw)
    elif mode == "lit":
        base_print(draw)
        soft_glow_logo(draw, pulse)
        apply_countdown(draw, days_n, h, m, s)
    elif mode == "zones":
        draw.rectangle((0, 0, W - 1, W - 1), fill=BLACK)
        days, day_y, time_digits, time_y, colons = layout_origins()
        colors = {
            "a": (180, 40, 40),
            "b": (40, 180, 40),
            "c": (40, 40, 180),
            "d": (180, 180, 40),
            "e": (180, 40, 180),
            "f": (40, 180, 180),
            "g": (200, 120, 40),
        }
        for ox in days:
            for name, rects in segment_cells(ox, day_y).items():
                for r in rects:
                    fill_cells(draw, *r, colors[name])
        for ox in time_digits:
            for name, rects in segment_cells(ox, time_y).items():
                for r in rects:
                    fill_cells(draw, *r, colors[name])
        for cx, cy in colons:
            fill_cells(draw, cx, cy + 4, 2, 2, (255, 255, 255))
            fill_cells(draw, cx, cy + 8, 2, 2, (255, 255, 255))
        for i in range(0, GRID + 1, 8):
            p = i * PX
            draw.line((p, 0, p, W), fill=(50, 50, 55))
            draw.line((0, p, W, p), fill=(50, 50, 55))
    elif mode == "grid_overlay":
        base_print(draw)
        soft_glow_logo(draw, 0.7)
        apply_countdown(draw, days_n, h, m, s)
        for i in range(0, GRID + 1, 8):
            p = i * PX
            draw.line((p, 0, p, W), fill=(80, 80, 90))
            draw.line((0, p, W, p), fill=(80, 80, 90))
    return img


def add_caption(img: Image.Image, title: str, subtitle: str) -> Image.Image:
    pad = 48
    out = Image.new("RGB", (img.width + pad * 2, img.height + pad * 2 + 70), (18, 18, 20))
    out.paste(img, (pad, pad + 40))
    d = ImageDraw.Draw(out)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
        font_s = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
        font_s = font
    d.text((pad, 12), title, fill=WHITE, font=font)
    d.text((pad, pad + img.height + 48), subtitle, fill=GREY, font=font_s)
    # thin frame
    d.rectangle(
        (pad - 1, pad + 39, pad + img.width, pad + 40 + img.height),
        outline=(60, 60, 65),
    )
    return out


def count_segment_cells() -> int:
    days, day_y, time_digits, time_y, colons = layout_origins()
    n = 0
    for ox in days:
        for rects in segment_cells(ox, day_y).values():
            for _, _, cw, ch in rects:
                n += cw * ch
    for ox in time_digits:
        for rects in segment_cells(ox, time_y).values():
            for _, _, cw, ch in rects:
                n += cw * ch
    n += 2 * 2 * 2  # two colons, 2x2 each, two dots
    return n


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    demos = {
        "01-print-ghost-888": (
            "print_only",
            "Print only — ghost 888 / 88:88:88 (LEDs off)",
            "SEG textile · opaque navy · translucent segment masks",
        ),
        "02-lit-countdown": (
            "lit",
            "Lit — 071 Tage · 14:32:08 via backlight",
            "Active segments ORANGE · logo soft pulse zone",
        ),
        "03-segment-zones": (
            "zones",
            "LED zone map — 7-seg cells on 64x64 grid",
            f"~{count_segment_cells()} cells in digit segments · cell ≈ 31.25 mm",
        ),
        "04-grid-overlay": (
            "grid_overlay",
            "Lit + 8-cell grid overlay (2m / 64)",
            "Kendu Flowbox square 2000×2000 mm backlight area",
        ),
    }
    sheets = []
    for name, (mode, title, sub) in demos.items():
        raw = render(mode)
        raw.save(OUT / f"{name}-raw.png")
        cap = add_caption(raw, title, sub)
        cap.save(OUT / f"{name}.png")
        sheets.append(raw)
        print("wrote", name)

    # contact: 2x2
    gap = 16
    sheet = Image.new("RGB", (W * 2 + gap * 3, W * 2 + gap * 3), (18, 18, 20))
    for i, im in enumerate(sheets):
        x = gap + (i % 2) * (W + gap)
        y = gap + (i // 2) * (W + gap)
        sheet.paste(im, (x, y))
    sheet.save(OUT / "contact-sheet.png")

    # animation strip: colon blink + logo pulse
    frames = []
    for i in range(4):
        fr = render("lit", pulse=0.5 + 0.5 * (i % 2))
        frames.append(fr)
    strip = Image.new("RGB", (W * 4 + 12, W), (18, 18, 20))
    for i, fr in enumerate(frames):
        strip.paste(fr, (i * (W + 4), 0))
    strip.save(OUT / "anim-pulse-strip.png")

    # mm scale reference card
    meta = Image.new("RGB", (900, 420), (18, 18, 20))
    d = ImageDraw.Draw(meta)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        font_s = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        font = ImageFont.load_default()
        font_s = font
    lines = [
        "Kendu Flowbox 2.0 x 2.0 m — Hotel Anker Countdown",
        "",
        "Print (SEG): navy brand + ghost 7-seg 888 / 88:88:88 + ANKER mark",
        "LEDs: light ONLY active segments (+ soft logo wash + optional hazard scroll)",
        f"Logical grid: 64 x 64 cells  |  cell pitch ≈ 31.25 mm",
        f"Digit body: {DW} x {DH} cells ≈ {DW*31.25:.0f} x {DH*31.25:.0f} mm",
        f"Segment cells (all digits+colons): ~{count_segment_cells()}",
        "Logical segments: 3*7 + 6*7 + 4 colon dots = 67",
        "",
        "Pi note: N_LED=1179 @25fps — map segments to plate groups, not full 4096 1:1",
        "Brand: Countdown Bar orange #FF6A00 · hazard stripes · chevron ANKER",
    ]
    y = 24
    for line in lines:
        d.text((24, y), line, fill=WHITE if line and not line.startswith("Pi") else GREY, font=font if y < 50 else font_s)
        y += 28 if y < 50 else 22
    meta.save(OUT / "00-spec-card.png")
    print("done ->", OUT)


if __name__ == "__main__":
    main()
