#!/usr/bin/env python3
"""Canva-ready Kendu Flowbox overlay layers (2×2 m / 64×64 content grid).

CONFIRMED (Kendu public FAQ / product pages):
  - Standard square visual size includes 2 × 2 m
  - Aluminium profile width/depth: 100 mm
  - SEG textile with silicone edge (Smartframe-based Kederschiene)

NOT published by Kendu (marked ASSUMED in legend):
  - Exact LED plate PCB size — proprietary; spare "RGB LED plates" only
  - Exact Keder groove cross-section — industry SEG often 4 × 14 mm

Hotel Anker content mapping (project):
  - Logical LED/print grid 64 × 64 → pitch 31.25 mm
  - 8 × 8 modules of 8 × 8 cells → 250 × 250 mm tiles (tiling assumption)
  - Dead band: bottom 8/64 rows (field 7 after 90° CW mount)
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "WerbeLEDbox-CountDown"
OUT = ROOT / "assets" / "kendu-flowbox-2m-print" / "canva-layers"

if str(PROJ) not in sys.path:
    sys.path.insert(0, str(PROJ))

from kendu_flowbox_spec import (  # noqa: E402
    CELL_PITCH_MM,
    DEAD_ROWS,
    GRID,
    PHYSICAL_MM,
    PRINT_PX_PER_CELL,
    PRINT_PX_PER_MM,
    PRINT_SIZE_PX,
    PROFILE_W_MM,
    cell_to_print_px,
)

# --- Geometry (mm → print px) ---
SIZE = PRINT_SIZE_PX  # 4096
PX_PER_MM = PRINT_PX_PER_MM  # 2.048

# Face = nominal 2000 mm content; frame drawn OUTSIDE as extension band
# Canva artboard = face only; frame overlay drawn inset as 100 mm rim on face
# (outer envelope would be face + profile — shown as rim annotation)
PROFILE_PX = int(round(PROFILE_W_MM * PX_PER_MM))  # ~205 px

# Industry-typical SEG keder groove (ASSUMED — not in Kendu public docs)
KEDER_GROOVE_W_MM = 4.0
KEDER_GROOVE_D_MM = 14.0  # depth into profile (shown as inset band width on face)
KEDER_INSET_MM = 6.0  # groove mouth near face edge (schematic)
KEDER_PX = max(2, int(round(KEDER_GROOVE_W_MM * PX_PER_MM)))

# 8×8 LED modules tiling 64×64 (ASSUMED tiling of content grid)
MODULE_CELLS = 8
MODULE_MM = MODULE_CELLS * CELL_PITCH_MM  # 250 mm
N_MODULES = GRID // MODULE_CELLS  # 8

DEAD_Y0 = cell_to_print_px(GRID - DEAD_ROWS)


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


def blank() -> Image.Image:
    return Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))


def layer_frame() -> Image.Image:
    """Outer aluminium profile rim (100 mm) drawn on face perimeter."""
    im = blank()
    d = ImageDraw.Draw(im)
    # Outer rectangle = full face; inner = face minus profile rim
    d.rectangle([0, 0, SIZE - 1, SIZE - 1], outline=(40, 40, 48, 255), width=max(4, PROFILE_PX // 20))
    inset = PROFILE_PX
    d.rectangle(
        [inset, inset, SIZE - 1 - inset, SIZE - 1 - inset],
        outline=(90, 90, 100, 220),
        width=max(3, PROFILE_PX // 25),
    )
    # Fill rim lightly so it reads as frame
    rim = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.rectangle([0, 0, SIZE - 1, SIZE - 1], fill=(55, 58, 66, 70))
    rd.rectangle(
        [inset, inset, SIZE - 1 - inset, SIZE - 1 - inset],
        fill=(0, 0, 0, 0),
    )
    # cut hole
    clear = Image.new("L", (SIZE, SIZE), 0)
    cd = ImageDraw.Draw(clear)
    cd.rectangle([0, 0, SIZE - 1, SIZE - 1], fill=255)
    cd.rectangle([inset, inset, SIZE - 1 - inset, SIZE - 1 - inset], fill=0)
    rim.putalpha(clear)
    im = Image.alpha_composite(rim, im)
    d = ImageDraw.Draw(im)
    d.text(
        (inset + 12, inset // 2 - 10),
        f"RAHMEN Profil {PROFILE_W_MM:.0f} mm (Kendu FAQ · confirmed)",
        fill=(220, 220, 230, 255),
        font=font(28, bold=True),
    )
    return im


def layer_keder() -> Image.Image:
    """Kederschiene / SEG silicone-edge groove (schematic on face)."""
    im = blank()
    d = ImageDraw.Draw(im)
    # Groove runs just inside the profile face edge
    # ASSUMED: groove mouth ~6 mm from outer face edge of textile plane
    o = int(round(KEDER_INSET_MM * PX_PER_MM))
    w = max(2, KEDER_PX)
    col = (0, 200, 180, 230)
    # four sides as thick lines (slot)
    d.rectangle([o, o, SIZE - 1 - o, o + w], fill=col)
    d.rectangle([o, SIZE - 1 - o - w, SIZE - 1 - o, SIZE - 1 - o], fill=col)
    d.rectangle([o, o, o + w, SIZE - 1 - o], fill=col)
    d.rectangle([SIZE - 1 - o - w, o, SIZE - 1 - o, SIZE - 1 - o], fill=col)
    d.text(
        (o + 16, o + w + 8),
        f"KEDERSCHIENE / SEG-Schlitz · ASSUMED {KEDER_GROOVE_W_MM:.0f}×{KEDER_GROOVE_D_MM:.0f} mm "
        f"(Industrie-SEG; Kendu-Exact nicht public)",
        fill=(0, 230, 210, 255),
        font=font(24, bold=True),
    )
    return im


def layer_modules() -> Image.Image:
    """8×8 module grid (250 mm tiles) — ASSUMED tiling of 64×64 content."""
    im = blank()
    d = ImageDraw.Draw(im)
    step = cell_to_print_px(MODULE_CELLS)
    col = (255, 140, 40, 200)
    for i in range(N_MODULES + 1):
        x = i * step
        d.line([(x, 0), (x, SIZE - 1)], fill=col, width=3)
        d.line([(0, x), (SIZE - 1, x)], fill=col, width=3)
    # module labels
    f = font(22, bold=True)
    for r in range(N_MODULES):
        for c in range(N_MODULES):
            x0, y0 = c * step, r * step
            d.text(
                (x0 + 10, y0 + 8),
                f"M{r},{c}",
                fill=(255, 170, 80, 220),
                font=f,
            )
    d.text(
        (16, SIZE - 48),
        f"LED-MODULE 8×8 Zellen = {MODULE_MM:.0f}×{MODULE_MM:.0f} mm · {N_MODULES}×{N_MODULES} Stück · ASSUMED (nicht Kendu-Datenblatt)",
        fill=(255, 160, 60, 255),
        font=font(26, bold=True),
    )
    return im


def layer_pixels() -> Image.Image:
    """64×64 pixel centers as circles (Hotel Anker content grid)."""
    im = blank()
    d = ImageDraw.Draw(im)
    r = max(2, PRINT_PX_PER_CELL // 8)
    # Active pixels cyan; dead-zone pixels red-dim
    for cy in range(GRID):
        for cx in range(GRID):
            px = cell_to_print_px(cx + 0.5)
            py = cell_to_print_px(cy + 0.5)
            dead = cy >= GRID - DEAD_ROWS
            col = (255, 70, 70, 160) if dead else (80, 180, 255, 150)
            d.ellipse([px - r, py - r, px + r, py + r], outline=col, width=max(1, r // 3))
    # every 8th stronger
    r2 = r + 2
    for cy in range(0, GRID, MODULE_CELLS):
        for cx in range(0, GRID, MODULE_CELLS):
            px = cell_to_print_px(cx + 0.5)
            py = cell_to_print_px(cy + 0.5)
            d.ellipse([px - r2, py - r2, px + r2, py + r2], outline=(255, 255, 255, 180), width=2)
    d.text(
        (16, 16),
        f"PIXEL 64×64 · Pitch {CELL_PITCH_MM:.2f} mm · Kreise = Zellmitte · "
        f"rot = Totzone {DEAD_ROWS}/64 (= {DEAD_ROWS * CELL_PITCH_MM:.0f} mm)",
        fill=(120, 200, 255, 255),
        font=font(26, bold=True),
    )
    return im


def layer_deadzone() -> Image.Image:
    im = blank()
    d = ImageDraw.Draw(im)
    d.rectangle([0, DEAD_Y0, SIZE - 1, SIZE - 1], fill=(220, 30, 30, 55))
    d.rectangle([0, DEAD_Y0, SIZE - 1, SIZE - 1], outline=(255, 60, 60, 230), width=4)
    d.text(
        (24, DEAD_Y0 + 24),
        f"TOTZONE / fehlende 8. Zeile (Field 7) · exakt {DEAD_ROWS}/64 Zellen · "
        f"{DEAD_ROWS * CELL_PITCH_MM:.0f} mm von {PHYSICAL_MM:.0f} mm",
        fill=(255, 100, 100, 255),
        font=font(30, bold=True),
    )
    return im


def layer_legend() -> Image.Image:
    im = blank()
    d = ImageDraw.Draw(im)
    box = [24, SIZE // 2 - 220, 980, SIZE // 2 + 220]
    d.rounded_rectangle(box, radius=20, fill=(12, 14, 20, 210), outline=(180, 180, 190, 255), width=2)
    lines = [
        "KENDU FLOWBOX 2×2 m — OVERLAY LEGENDE",
        "",
        f"CONFIRMED: Fläche {PHYSICAL_MM:.0f}×{PHYSICAL_MM:.0f} mm · Profil {PROFILE_W_MM:.0f} mm",
        "CONFIRMED: SEG/Silicone-Edge (Smartframe) · Kederschiene vorhanden",
        "",
        f"PROJECT: Content-Grid {GRID}×{GRID} · Pitch {CELL_PITCH_MM:.2f} mm",
        f"ASSUMED: Module 8×8 Zellen = {MODULE_MM:.0f} mm (Kendu-Plattenmaß nicht public)",
        f"ASSUMED: Keder-Schlitz {KEDER_GROOVE_W_MM:.0f}×{KEDER_GROOVE_D_MM:.0f} mm (Industrie-SEG)",
        "",
        "Print: 4096 px = 64 px/Zelle · Canva: diese Layer importieren",
        "Canva-Account: kein MCP in Cursor — manuell File→Import",
    ]
    y = box[1] + 28
    for i, line in enumerate(lines):
        d.text((box[0] + 28, y), line, fill=(230, 230, 235, 255), font=font(22, bold=(i == 0)))
        y += 32
    return im


def layer_combined() -> Image.Image:
    base = Image.new("RGBA", (SIZE, SIZE), (8, 10, 16, 255))
    for fn in (layer_deadzone, layer_modules, layer_pixels, layer_keder, layer_frame, layer_legend):
        base = Image.alpha_composite(base, fn())
    return base


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    layers = {
        "00-overlay-combined.png": layer_combined(),
        "01-overlay-deadzone.png": layer_deadzone(),
        "02-overlay-modules-8x8.png": layer_modules(),
        "03-overlay-pixels-64.png": layer_pixels(),
        "04-overlay-keder-rail.png": layer_keder(),
        "05-overlay-frame-100mm.png": layer_frame(),
        "06-overlay-legend.png": layer_legend(),
    }
    for name, im in layers.items():
        im.save(OUT / name)
        # Canva-friendly smaller preview
        im.resize((2048, 2048), Image.Resampling.LANCZOS).save(OUT / name.replace(".png", "@2048.png"))

    (OUT / "README_CANVA.md").write_text(
        f"""# Canva Layer-Kit — Kendu Flowbox 2×2 m Overlay

## Canva-Account / Cursor
Cursor hat **kein Canva-MCP**. Eine OAuth-Verbindung zu deinem Canva-Account
ist von hier aus **nicht möglich**. Workflow:

1. Canva → Create design → **Custom size 4096 × 4096 px** (oder 2000×2000 mm @ 2.048 px/mm)
2. **File → Upload** die PNGs aus diesem Ordner
3. Jedes Overlay als eigene Ebene stapeln (Transparenz an)
4. Deine Design-Elemente darunter / dazwischen platzieren

## Dateien
| Datei | Inhalt |
|-------|--------|
| `00-overlay-combined.png` | Alles zusammen (Referenz) |
| `01-overlay-deadzone.png` | Totzone 8/64 (= 250 mm) |
| `02-overlay-modules-8x8.png` | 8×8 Module à 250×250 mm |
| `03-overlay-pixels-64.png` | 64×64 Pixelmitten als Kreise |
| `04-overlay-keder-rail.png` | Kederschiene / SEG-Schlitz |
| `05-overlay-frame-100mm.png` | Aluminiumrahmen 100 mm |
| `06-overlay-legend.png` | Legende confirmed vs assumed |

## Masse — was ist sicher?
| Maß | Wert | Quelle |
|-----|------|--------|
| Nennfläche | {PHYSICAL_MM:.0f}×{PHYSICAL_MM:.0f} mm | Kendu Standard Square |
| Profilbreite | {PROFILE_W_MM:.0f} mm | Kendu FAQ „profile width“ |
| Content-Pitch | {CELL_PITCH_MM:.2f} mm | Projekt 64×64 auf 2 m |
| Totzone | {DEAD_ROWS}/64 = {DEAD_ROWS * CELL_PITCH_MM:.0f} mm | AnkerPI02 Field 7 |
| Modul 8×8 | {MODULE_MM:.0f}×{MODULE_MM:.0f} mm | **ASSUMED** (kein Kendu-Datenblatt) |
| Keder-Schlitz | {KEDER_GROOVE_W_MM:.0f}×{KEDER_GROOVE_D_MM:.0f} mm | **ASSUMED** Industrie-SEG |

Kendu veröffentlicht die exakten LED-Platten-PCB-Maße und den exakten
Keder-Querschnitt **nicht** öffentlich. Für Produktion: Maßblatt von
flowbox@kendu.com / eurem CSM anfordern und hier nachziehen.
""",
        encoding="utf-8",
    )
    print("wrote", OUT)
    for name in layers:
        print(" ", name)


if __name__ == "__main__":
    main()
