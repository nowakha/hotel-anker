#!/usr/bin/env python3
"""Generate accurate Pico WS2812 wiring diagram from official pin numbers."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Official Pico pinout, top view, USB on LEFT.
# Bottom row L→R = pins 1..20
# Top row    L→R = pins 40..21
BOTTOM = [
    (1, "GP0"), (2, "GP1"), (3, "GND"), (4, "GP2"), (5, "GP3"),
    (6, "GP4"), (7, "GP5"), (8, "GND"), (9, "GP6"), (10, "GP7"),
    (11, "GP8"), (12, "GP9"), (13, "GND"), (14, "GP10"), (15, "GP11"),
    (16, "GP12"), (17, "GP13"), (18, "GND"), (19, "GP14"), (20, "GP15"),
]
TOP = [
    (40, "VBUS"), (39, "VSYS"), (38, "GND"), (37, "3V3"), (36, "3V3_EN"),
    (35, "ADC_REF"), (34, "GP28"), (33, "GND"), (32, "GP27"), (31, "GP26"),
    (30, "RUN"), (29, "GP22"), (28, "GND"), (27, "GP21"), (26, "GP20"),
    (25, "GP19"), (24, "GP18"), (23, "GND"), (22, "GP17"), (21, "GP16"),
]

# Our firmware PIN_LINES = (28,27,26,22,21,20,19,18)
# Line -> (phys_pin, gpio_name, color)
LINES = {
    34: ("Line0", "GP28", "#E53935"),
    32: ("Line1", "GP27", "#FB8C00"),
    31: ("Line2", "GP26", "#FDD835"),
    29: ("Line3", "GP22", "#43A047"),
    27: ("Line4", "GP21", "#1E88E5"),
    26: ("Line5", "GP20", "#8E24AA"),
    25: ("Line6", "GP19", "#00ACC1"),
    24: ("Line7", "GP18", "#D81B60"),
}
GND_PINS = {28, 33, 38}
SKIP = {30: "RUN — nicht nutzen"}


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in (
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    w, h = 1600, 1000
    img = Image.new("RGB", (w, h), "#F7F7F5")
    d = ImageDraw.Draw(img)
    f_title = font(36)
    f_sub = font(22)
    f_pin = font(15)
    f_lab = font(18)
    f_small = font(14)
    f_table = font(20)

    d.text((40, 24), "Anker Pico — 8×512 WS2812", fill="#111", font=f_title)
    d.text(
        (40, 70),
        "Obere Stiftreihe Richtung Micro-USB  |  USB links  |  Top-Pins: 40 (USB) → 21  |  PIN_LINES GPIO=(28,27,26,22,21,20,19,18)",
        fill="#444",
        font=f_sub,
    )

    # Board geometry
    bx0, by0 = 80, 200
    bw, bh = 980, 420
    # USB tongue on left
    d.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=18, fill="#1B5E20", outline="#0D3B12", width=3)
    d.rectangle([bx0 - 55, by0 + 130, bx0, by0 + 290], fill="#333", outline="#111", width=2)
    d.text((bx0 - 48, by0 + 195), "U\nS\nB", fill="#EEE", font=f_small)

    # Chip
    d.rounded_rectangle([bx0 + 360, by0 + 140, bx0 + 620, by0 + 280], radius=8, fill="#263238", outline="#111")
    d.text((bx0 + 430, by0 + 190), "RP2040", fill="#ECEFF1", font=f_lab)

    n = 20
    margin = 50
    usable = bw - 2 * margin
    step = usable / (n - 1)
    pad_r = 11

    top_y = by0 + 28
    bot_y = by0 + bh - 28

    def pad_x(i: int) -> float:
        return bx0 + margin + i * step

    # Draw top pads (index 0 = pin 40 near USB)
    top_centers: dict[int, tuple[float, float]] = {}
    for i, (pin, name) in enumerate(TOP):
        x, y = pad_x(i), top_y
        top_centers[pin] = (x, y)
        fill = "#CFD8DC"
        outline = "#37474F"
        width = 2
        if pin in LINES:
            fill = LINES[pin][2]
            outline = "#111"
            width = 3
        elif pin in GND_PINS:
            fill = "#212121"
            outline = "#000"
            width = 3
        elif pin in SKIP:
            fill = "#9E9E9E"
            outline = "#C62828"
            width = 3
        d.ellipse([x - pad_r, y - pad_r, x + pad_r, y + pad_r], fill=fill, outline=outline, width=width)
        # pin number above pad
        tw = d.textlength(str(pin), font=f_pin)
        d.text((x - tw / 2, y - 36), str(pin), fill="#111", font=f_pin)
        # short name only on unused pins, below toward center — skip crowded zone
        if pin not in LINES and pin not in GND_PINS and pin not in SKIP:
            label = name
            if len(label) > 5:
                label = label[:5]
            lw = d.textlength(label, font=f_small)
            d.text((x - lw / 2, y + 18), label, fill="#C8E6C9", font=f_small)
        else:
            # GPIO name under used pads
            label = name if pin != 30 else "RUN"
            lw = d.textlength(label, font=f_small)
            d.text((x - lw / 2, y + 18), label, fill="#FFF", font=f_small)

    # Bottom pads (dimmed — not used)
    for i, (pin, name) in enumerate(BOTTOM):
        x, y = pad_x(i), bot_y
        d.ellipse([x - pad_r, y - pad_r, x + pad_r, y + pad_r], fill="#90A4AE", outline="#546E7A", width=1)
        tw = d.textlength(str(pin), font=f_pin)
        d.text((x - tw / 2, y + 16), str(pin), fill="#607D8B", font=f_pin)

    # Callouts above board for used pins
    callouts = [
        (34, "Line0 DATA"),
        (33, "GND"),
        (32, "Line1 DATA"),
        (31, "Line2 DATA"),
        (30, "SKIP RUN"),
        (29, "Line3 DATA"),
        (28, "GND"),
        (27, "Line4 DATA"),
        (26, "Line5 DATA"),
        (25, "Line6 DATA"),
        (24, "Line7 DATA"),
        (38, "GND opt."),
    ]
    # Stagger callout heights to avoid overlap
    base_y = by0 - 20
    for idx, (pin, text) in enumerate(callouts):
        x, y = top_centers[pin]
        # alternate heights
        hy = base_y - 55 - (idx % 3) * 42
        color = "#C62828" if pin == 30 else ("#212121" if pin in GND_PINS else LINES.get(pin, ("", "", "#333"))[2])
        if pin == 38:
            color = "#212121"
        d.line([(x, y - pad_r - 2), (x, hy + 18)], fill=color, width=2)
        # bubble
        tw = d.textlength(text, font=f_lab)
        pad = 8
        d.rounded_rectangle(
            [x - tw / 2 - pad, hy - 6, x + tw / 2 + pad, hy + 26],
            radius=6,
            fill="#FFF",
            outline=color,
            width=2,
        )
        d.text((x - tw / 2, hy), text, fill=color, font=f_lab)

    # Arrow: toward USB
    d.text((bx0 + 10, by0 + bh + 20), "← Richtung Micro-USB (Pin 40)", fill="#111", font=f_lab)
    d.text((bx0 + bw - 280, by0 + bh + 20), "Pin 21 (fern) →", fill="#111", font=f_lab)

    # Right table — exact wiring
    tx, ty = 1120, 180
    d.text((tx, ty), "Anschluss (Top-Reihe)", fill="#111", font=f_table)
    rows = [
        ("Line0", "GP28", "34", LINES[34][2]),
        ("GND", "GND", "33 / 28 / 38", "#212121"),
        ("Line1", "GP27", "32", LINES[32][2]),
        ("Line2", "GP26", "31", LINES[31][2]),
        ("—", "RUN", "30 nicht!", "#C62828"),
        ("Line3", "GP22", "29", LINES[29][2]),
        ("Line4", "GP21", "27", LINES[27][2]),
        ("Line5", "GP20", "26", LINES[26][2]),
        ("Line6", "GP19", "25", LINES[25][2]),
        ("Line7", "GP18", "24", LINES[24][2]),
    ]
    y = ty + 40
    d.text((tx, y), "Signal", fill="#555", font=f_small)
    d.text((tx + 110, y), "GPIO", fill="#555", font=f_small)
    d.text((tx + 220, y), "Pin", fill="#555", font=f_small)
    y += 28
    for sig, gpio, pin, col in rows:
        d.ellipse([tx, y + 4, tx + 14, y + 18], fill=col, outline="#111")
        d.text((tx + 24, y), sig, fill="#111", font=f_lab)
        d.text((tx + 110, y), gpio, fill="#111", font=f_lab)
        d.text((tx + 220, y), pin, fill="#111", font=f_lab)
        y += 32

    d.text(
        (40, h - 70),
        "Offizielles Pinout: USB links · oben Pin40→21 · unten Pin1→20  |  LED-Strips: separates 5V-Netzteil + gemeinsames GND  |  Hotel Anker / WerbeLEDbox",
        fill="#555",
        font=f_small,
    )

    repo = Path(__file__).resolve().parents[2]
    out_dirs = [
        repo / "assets",
        repo / "WerbeLEDbox-CountDown" / "pico",
    ]
    for folder in out_dirs:
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "pico-4x-ws2812-gpio.png"
        img.save(path, "PNG")
        print("wrote", path)


if __name__ == "__main__":
    main()
