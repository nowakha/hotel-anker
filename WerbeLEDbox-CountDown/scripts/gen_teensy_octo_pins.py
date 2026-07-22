#!/usr/bin/env python3
"""Teensy OctoWS2811 default pin diagram (inferred for AnkerPI02)."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# PJRC OctoWS2811 defaultPinList / Teensy 3.x fixed + T4 default:
# Strip1..8 = pins 2, 14, 7, 8, 6, 20, 21, 5
STRIPS = [
    (1, 2, "#E53935"),
    (2, 14, "#FB8C00"),
    (3, 7, "#FDD835"),
    (4, 8, "#43A047"),
    (5, 6, "#1E88E5"),
    (6, 20, "#8E24AA"),
    (7, 21, "#00ACC1"),
    (8, 5, "#D81B60"),
]


def font(size: int):
    for name in (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    w, h = 1400, 900
    img = Image.new("RGB", (w, h), "#F5F5F5")
    d = ImageDraw.Draw(img)
    ft, fs, fl = font(32), font(18), font(22)

    d.text((40, 24), "AnkerPI02 — Teensy am USB (kein Pico)", fill="#111", font=ft)
    d.text(
        (40, 68),
        "Erkannt: Teensyduino Serial 16c0:0483  SN=2923720  → /dev/ttyACM0",
        fill="#333",
        font=fs,
    )
    d.text(
        (40, 96),
        "Firmware-Source fehlt · USB-CDC Write-Timeout (kein Banner) · GPIO daher aus OctoWS2811-Default abgeleitet",
        fill="#B71C1C",
        font=fs,
    )

    # Simple Teensy-like board (USB top)
    bx, by, bw, bh = 80, 160, 420, 620
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill="#212121", outline="#000", width=3)
    d.rectangle([bx + 150, by - 35, bx + 270, by], fill="#555", outline="#000")
    d.text((bx + 175, by - 28), "USB", fill="#EEE", font=fs)
    d.text((bx + 130, by + 280), "Teensy", fill="#CCC", font=fl)
    d.text((bx + 90, by + 320), "(OctoWS2811 likely)", fill="#888", font=fs)

    # Left and right pin columns (schematic, not exact pitch)
    left_pins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]  # approx digital edge
    # Highlight used pins with callouts on right table instead of fake geometry

    tx, ty = 560, 160
    d.text((tx, ty), "OctoWS2811 Default-Pinliste (PJRC)", fill="#111", font=fl)
    d.text((tx, ty + 36), "Strip → Teensy digital pin", fill="#555", font=fs)
    y = ty + 80
    d.text((tx, y), "Strip", fill="#555", font=fs)
    d.text((tx + 100, y), "GPIO Pin", fill="#555", font=fs)
    d.text((tx + 240, y), "Rolle", fill="#555", font=fs)
    y += 30
    for strip, pin, col in STRIPS:
        d.ellipse([tx, y + 4, tx + 16, y + 20], fill=col, outline="#000")
        d.text((tx + 28, y), f"#{strip}", fill="#111", font=fl)
        d.text((tx + 100, y), str(pin), fill="#111", font=fl)
        d.text((tx + 240, y), f"WS2812 DATA line {strip - 1}", fill="#111", font=fl)
        y += 40

    y += 20
    d.rounded_rectangle([tx, y, tx + 760, y + 200], radius=10, fill="#FFF", outline="#CCC", width=2)
    notes = [
        "Konfidenz: HOCH für Pinliste, wenn OctoWS2811 / Octo28-Adaptor ohne custom pinList.",
        "Teensy 3.x: Pins fest so. Teensy 4.x: Default identisch, custom pinList möglich.",
        "Octo28-Adaptor: dieselben Signale auf RJ45-Buchsen (Channel 1..8).",
        "Nicht verifiziert: exakte Teensy-Revision (3.2/4.0/4.1) und ob custom pins im Sketch stehen.",
        "USB-Protokoll: unbekannt (CDC antwortet nicht) — Pixel-Format ggf. nicht unser ANKR.",
    ]
    yy = y + 16
    for line in notes:
        d.text((tx + 16, yy), "• " + line, fill="#333", font=fs)
        yy += 34

    d.text(
        (40, h - 40),
        "Hotel Anker / WerbeLEDbox  |  reverse-engineered default, not dumped from flash",
        fill="#666",
        font=fs,
    )

    repo = Path(__file__).resolve().parents[2]
    outs = [
        repo / "assets" / "teensy-octows2811-pins.png",
        repo / "WerbeLEDbox-CountDown" / "docs" / "teensy-octows2811-pins.png",
    ]
    for p in outs:
        p.parent.mkdir(parents=True, exist_ok=True)
        img.save(p)
        print("wrote", p)


if __name__ == "__main__":
    main()
