#!/usr/bin/env python3
"""Visualize 64x64 → 8×512 serpentine mapping for AnkerPI02."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from layout_64x64_8x512 import FIELD_W, HEIGHT, LUT, N_FIELDS, N_LED, WIDTH, map_panel_to_lines


def font(size: int):
    for name in (
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    scale = 10
    margin = 80
    gap = 24
    panel_w = WIDTH * scale
    panel_h = HEIGHT * scale

    # Right: 8 strips preview (each 8x64 shown as thin columns of LED order color)
    strip_w = 36
    right_w = N_FIELDS * (strip_w + 8) + 40
    w = margin * 2 + panel_w + gap + right_w
    h = margin * 2 + panel_h + 160

    img = Image.new("RGB", (w, h), "#111218")
    d = ImageDraw.Draw(img)
    f_title = font(28)
    f_lab = font(16)
    f_small = font(13)

    d.text((margin, 24), "AnkerPI02 Layout: 64×64 SharedArray → 8×512 WS2812", fill="#F2F2F2", font=f_title)
    d.text(
        (margin, 58),
        "8 Felder à 8×64  |  LED#1 = links unten  |  hoch → rechts → runter → rechts → hoch …",
        fill="#AAB",
        font=f_lab,
    )

    ox, oy = margin, margin + 70

    # Build demo panel: field hue + vertical gradient + LED-index marks
    panel = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    field_colors = [
        (220, 60, 60),
        (240, 140, 40),
        (230, 210, 50),
        (60, 180, 80),
        (50, 140, 230),
        (140, 70, 200),
        (40, 190, 200),
        (220, 60, 140),
    ]
    for f in range(N_FIELDS):
        c0 = f * FIELD_W
        base = np.array(field_colors[f], dtype=np.float32)
        for row in range(HEIGHT):
            # brighter at bottom (start of chain on even cols)
            bright = 0.35 + 0.65 * (row / (HEIGHT - 1))
            panel[row, c0 : c0 + FIELD_W] = (base * bright).astype(np.uint8)

    # Draw panel pixels
    for row in range(HEIGHT):
        for col in range(WIDTH):
            x0 = ox + col * scale
            y0 = oy + row * scale
            color = tuple(int(v) for v in panel[row, col])
            d.rectangle([x0, y0, x0 + scale - 1, y0 + scale - 1], fill=color)

    # Field boundaries
    for f in range(N_FIELDS + 1):
        x = ox + f * FIELD_W * scale
        d.line([(x, oy), (x, oy + panel_h)], fill="#FFFFFF", width=2)
    d.rectangle([ox, oy, ox + panel_w, oy + panel_h], outline="#EEE", width=2)

    for f in range(N_FIELDS):
        cx = ox + f * FIELD_W * scale + FIELD_W * scale // 2
        d.text((cx - 10, oy + panel_h + 8), f"F{f}", fill="#DDD", font=f_lab)

    # Serpentine arrows in field 0
    f0_x = ox + 0 * FIELD_W * scale
    # col0 up
    d.line(
        [(f0_x + scale // 2, oy + panel_h - 4), (f0_x + scale // 2, oy + 4)],
        fill="#FFF",
        width=3,
    )
    d.polygon(
        [
            (f0_x + scale // 2, oy + 2),
            (f0_x + scale // 2 - 6, oy + 14),
            (f0_x + scale // 2 + 6, oy + 14),
        ],
        fill="#FFF",
    )
    # top jog to col1
    d.line(
        [(f0_x + scale // 2, oy + 8), (f0_x + scale + scale // 2, oy + 8)],
        fill="#FFF",
        width=3,
    )
    # col1 down
    d.line(
        [(f0_x + scale + scale // 2, oy + 8), (f0_x + scale + scale // 2, oy + panel_h - 4)],
        fill="#FFD54F",
        width=3,
    )
    d.polygon(
        [
            (f0_x + scale + scale // 2, oy + panel_h - 2),
            (f0_x + scale + scale // 2 - 6, oy + panel_h - 14),
            (f0_x + scale + scale // 2 + 6, oy + panel_h - 14),
        ],
        fill="#FFD54F",
    )

    # Mark LED 0 and LED 63 / 64
    def mark(row, col, label, color):
        x = ox + col * scale + scale // 2
        y = oy + row * scale + scale // 2
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=color, outline="#000")
        d.text((x + 8, y - 8), label, fill=color, font=f_small)

    mark(63, 0, "LED0", "#FFF")
    mark(0, 0, "LED63", "#FFF")
    mark(0, 1, "LED64", "#FFD54F")
    mark(63, 1, "LED127", "#FFD54F")

    # Right: LED order strips (color = panel pixel along chain)
    lines = map_panel_to_lines(panel)
    rx = ox + panel_w + gap
    d.text((rx, oy - 28), "LED-Reihenfolge pro Linie (unten→oben = Index 0→…)", fill="#CCC", font=f_small)
    for f in range(N_FIELDS):
        sx = rx + f * (strip_w + 8)
        d.text((sx, oy - 12), f"L{f}", fill="#EEE", font=f_small)
        # show 64 samples along the 512 chain (every 8th)
        for i in range(0, N_LED, 8):
            yy = oy + (i // 8) * (panel_h / (N_LED // 8))
            color = tuple(int(v) for v in lines[f, i])
            d.rectangle([sx, yy, sx + strip_w - 2, yy + panel_h / (N_LED // 8)], fill=color)
        d.rectangle([sx, oy, sx + strip_w - 2, oy + panel_h], outline="#666")

    # Verify LUT endpoints
    assert LUT[0, 0] == 63 * WIDTH + 0
    assert LUT[0, 63] == 0 * WIDTH + 0
    assert LUT[0, 64] == 0 * WIDTH + 1
    assert LUT[0, 127] == 63 * WIDTH + 1
    assert LUT[7, 0] == 63 * WIDTH + 56

    d.text(
        (margin, h - 50),
        "shm://ws2812 shape (64,64,3)  →  ws2812put_pi02.py  →  Pico USB 8×PIO  |  Hotel Anker",
        fill="#889",
        font=f_small,
    )

    outs = [
        Path(r"C:\Users\Harald Nowak\Documents\Cursor Projects\Hotel Anker\assets\layout-64x64-8x512.png"),
        Path(r"C:\Users\Harald Nowak\Documents\Cursor Projects\Hotel Anker\WerbeLEDbox-CountDown\pico\layout-64x64-8x512.png"),
    ]
    for p in outs:
        p.parent.mkdir(parents=True, exist_ok=True)
        img.save(p)
        print("wrote", p)


if __name__ == "__main__":
    main()
