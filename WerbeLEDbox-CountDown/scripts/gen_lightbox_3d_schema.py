#!/usr/bin/env python3
"""Draw Hotel Anker LightBox 3D geometry schematics from photo + measured data."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "WerbeLEDbox-CountDown"
OUT_PKG = ROOT / "Richnerstutz-Bespannung-Paket" / "06-fotos-vom-rahmen"
OUT_ASSETS = ROOT / "assets" / "kendu-flowbox-2m-print"

if str(PROJ) not in sys.path:
    sys.path.insert(0, str(PROJ))

from kendu_flowbox_spec import (  # noqa: E402
    FACE_MM,
    INNER_DEPTH_MM,
    OUTER_MM,
    PROFILE_DEPTH_MM,
    PROFILE_FACE_W_MM,
    MODULE_PITCH_MM,
    KEDER_GROOVE_W_MM,
    KEDER_GROOVE_D_MM,
)


def font(size: int, bold: bool = False):
    for path in (
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\seguisb.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_front_plan(w: int = 1400, h: int = 1500) -> Image.Image:
    im = Image.new("RGB", (w, h), (245, 246, 248))
    d = ImageDraw.Draw(im)
    d.text((40, 24), "Hotel Anker LightBox — Front / XY (Fotos 01+02)", fill=(20, 24, 32), font=font(28, True))

    # Scale: outer 2100 → 1100 px
    scale = 1100 / OUTER_MM
    ox, oy = 150, 120
    outer = OUTER_MM * scale
    face = FACE_MM * scale
    rim = PROFILE_FACE_W_MM * scale

    # Outer frame
    d.rectangle([ox, oy, ox + outer, oy + outer], outline=(120, 130, 140), width=3, fill=(210, 214, 220))
    # Face / LED area
    d.rectangle(
        [ox + rim, oy + rim, ox + rim + face, oy + rim + face],
        outline=(40, 90, 160),
        width=3,
        fill=(255, 255, 255),
    )
    # Keder groove indication (inner lip)
    inset = max(3, int(6 * scale))
    d.rectangle(
        [ox + rim + inset, oy + rim + inset, ox + rim + face - inset, oy + rim + face - inset],
        outline=(200, 80, 40),
        width=2,
    )

    # 8×8 panel grid
    for i in range(9):
        x = ox + rim + i * (MODULE_PITCH_MM * scale)
        y = oy + rim + i * (MODULE_PITCH_MM * scale)
        d.line([x, oy + rim, x, oy + rim + face], fill=(180, 200, 220), width=1)
        d.line([ox + rim, y, ox + rim + face, y], fill=(180, 200, 220), width=1)

    # Labels
    d.text((ox, oy + outer + 20), f"Außen {OUTER_MM:.0f}×{OUTER_MM:.0f} mm (gemessen)", fill=(40, 40, 48), font=font(20, True))
    d.text((ox, oy + outer + 50), f"Fläche {FACE_MM:.0f}×{FACE_MM:.0f} mm · 8×8 Panels à {MODULE_PITCH_MM:.0f} mm", fill=(40, 90, 160), font=font(18))
    d.text((ox, oy + outer + 78), f"Stirnbreite Profil {PROFILE_FACE_W_MM:.0f} mm (= (+5 cm) außen)", fill=(80, 80, 90), font=font(18))
    d.text((ox, oy + outer + 106), "Orange: Kedernut an Profil-Innenlippe (Foto 02, Gehrung)", fill=(180, 70, 30), font=font(18))
    d.text((ox, oy + outer + 134), "Controller unten am Querprofil (Foto 01/03 · Kendu DC24V/DMX)", fill=(60, 60, 70), font=font(18))

    # Corner callout
    cx, cy = ox + outer - 40, oy + 40
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], outline=(200, 80, 40), width=3)
    d.text((ox + outer - 280, oy + 70), "Gehrung 45°\n+ Kedernut", fill=(160, 50, 20), font=font(16, True))
    return im


def draw_cross_section(w: int = 1400, h: int = 900) -> Image.Image:
    """Side view: textile → gap → LED → back (from photos + FAQ depth)."""
    im = Image.new("RGB", (w, h), (245, 246, 248))
    d = ImageDraw.Draw(im)
    d.text((40, 24), "Querschnitt Z — optischer Stack (Fotos 01–03)", fill=(20, 24, 32), font=font(28, True))
    d.text(
        (40, 64),
        f"Innen {INNER_DEPTH_MM:.0f} mm gemessen (Zollstock): Vorderkante/Textil-Ebene → LED-Fläche · Stirnbreite XY {PROFILE_FACE_W_MM:.0f} mm",
        fill=(70, 70, 80),
        font=font(18),
    )

    # Draw a horizontal section: left = front (viewer), right = back
    # Scale so measured 45 mm cavity fills most of the diagram depth
    front_x = 180
    depth_px = 720
    scale_z = depth_px / INNER_DEPTH_MM
    top = 180
    bot = 720
    mid = (top + bot) // 2

    alu = (170, 178, 188)
    # Cavity extent (front lip → LED)
    led_x = front_x + int(INNER_DEPTH_MM * scale_z)
    back_x = led_x + 120  # panel + reflector schematic behind LED face

    d.rectangle([front_x - 40, top, back_x + 40, bot], fill=(230, 232, 236), outline=(140, 145, 155), width=2)

    # Front face rim + keder groove
    d.rectangle([front_x - 8, top, front_x + 28, bot], fill=alu, outline=(100, 105, 115), width=2)
    groove_y0 = mid - 40
    groove_y1 = mid + 40
    d.rectangle([front_x + 4, groove_y0, front_x + 18, groove_y1], fill=(40, 40, 48))
    d.text((front_x - 10, top - 36), "Vorne", fill=(40, 40, 48), font=font(18, True))

    # Textile plane
    d.line([front_x + 12, top + 20, front_x + 12, bot - 20], fill=(30, 90, 180), width=4)
    d.text((front_x + 20, top + 30), "SEG-Textil\n(Druckfläche)", fill=(30, 90, 180), font=font(16, True))

    # Silicone keder bulb in groove
    d.ellipse([front_x + 2, mid - 14, front_x + 22, mid + 14], fill=(220, 90, 50), outline=(160, 50, 20))
    d.text((front_x - 160, mid - 10), "Kederlippe\nin Nut", fill=(180, 60, 20), font=font(15, True))

    # Air / diffusion gap = measured Innen 45 mm
    d.rectangle([front_x + 30, top + 40, led_x - 8, bot - 40], fill=(255, 252, 230))
    d.text(
        ((front_x + 30 + led_x) // 2 - 70, mid - 50),
        f"Luft / Diffusion\n{INNER_DEPTH_MM:.0f} mm innen\n(gemessen)",
        fill=(140, 120, 40),
        font=font(16, True),
    )

    # LED panel plane
    d.rectangle([led_x, top + 30, led_x + 36, bot - 30], fill=(255, 255, 255), outline=(220, 180, 40), width=3)
    for y in range(top + 50, bot - 50, 28):
        d.ellipse([led_x + 10, y, led_x + 26, y + 10], fill=(255, 210, 80))
    d.text((led_x - 10, bot - 20), "LED-Panels\n250×250", fill=(160, 120, 20), font=font(15, True))

    # White reflector / back behind LEDs
    d.rectangle([led_x + 40, top + 20, back_x, bot - 20], fill=(250, 250, 252), outline=(160, 160, 170), width=2)
    d.text((led_x + 50, mid - 50), "Reflexions-\nrückwand", fill=(90, 90, 100), font=font(15))

    d.rectangle([led_x + 50, bot - 100, back_x - 20, bot - 40], fill=(245, 245, 245), outline=(80, 80, 90), width=2)
    d.text((led_x + 58, bot - 90), "Kendu Ctrl\nDC24V / DMX", fill=(40, 40, 48), font=font(14, True))

    d.text((back_x - 30, top - 36), "Hinten", fill=(40, 40, 48), font=font(18, True))

    # Depth dimension: front → LED (= Innen 45 mm)
    y_dim = bot + 40
    d.line([front_x + 12, y_dim, led_x, y_dim], fill=(40, 40, 48), width=2)
    d.line([front_x + 12, y_dim - 8, front_x + 12, y_dim + 8], fill=(40, 40, 48), width=2)
    d.line([led_x, y_dim - 8, led_x, y_dim + 8], fill=(40, 40, 48), width=2)
    d.text(
        ((front_x + 12 + led_x) // 2 - 100, y_dim + 12),
        f"{INNER_DEPTH_MM:.0f} mm Innen (Textil → LED)",
        fill=(40, 40, 48),
        font=font(18, True),
    )

    d.text(
        (40, h - 70),
        f"Keder-Nut typ. {KEDER_GROOVE_W_MM:.0f}×{KEDER_GROOVE_D_MM:.0f} mm (Industrie-Annahme) · Foto: Zollstock Innen {INNER_DEPTH_MM:.0f} mm",
        fill=(90, 90, 100),
        font=font(16),
    )
    return im


def main() -> None:
    OUT_PKG.mkdir(parents=True, exist_ok=True)
    OUT_ASSETS.mkdir(parents=True, exist_ok=True)
    front = draw_front_plan()
    cross = draw_cross_section()
    front.save(OUT_PKG / "schema-front-xy.png")
    cross.save(OUT_PKG / "schema-querschnitt-z.png")
    front.save(OUT_ASSETS / "schema-front-xy.png")
    cross.save(OUT_ASSETS / "schema-querschnitt-z.png")
    # Combined contact sheet
    sheet = Image.new("RGB", (front.width, front.height + cross.height + 20), (245, 246, 248))
    sheet.paste(front, (0, 0))
    sheet.paste(cross, (0, front.height + 20))
    sheet.save(OUT_PKG / "schema-3d-geometrie.png")
    sheet.save(OUT_ASSETS / "schema-3d-geometrie.png")
    print("wrote", OUT_PKG / "schema-3d-geometrie.png")


if __name__ == "__main__":
    main()
