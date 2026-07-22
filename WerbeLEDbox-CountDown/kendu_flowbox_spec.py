"""Kendu Flowbox 2×2 m — physical ↔ 64×64 LED/print mapping (Hotel Anker).

Sources (public Kendu):
- Flowbox standard sizes include **2 × 2 m** square
  https://www.kendu.com/flowbox-dynamic-lightbox/
- Aluminium profile width **100 mm**
  https://www.kendu.com/flowbox-dynamic-lightbox/faq/
- FAQ shopfitter threshold mentions **2077 × 2077 mm** for large units
  (outer envelope hint; visual face treated as nominal 2000 × 2000 mm)

Hotel Anker retrofit (AnkerPI02): custom 64×64 WS2812 matrix behind SEG textile
(not stock Kendu LED-plate pitch). Logical content grid is therefore:

    pitch = PHYSICAL_MM / GRID  →  2000 / 64 = 31.25 mm / cell
"""

from __future__ import annotations

# --- Kendu frame (public) ---
PHYSICAL_MM = 2000.0  # nominal square visual / backlight face
PROFILE_W_MM = 100.0  # frame profile section (FAQ)
OUTER_HINT_MM = 2077.0  # FAQ large-unit threshold (not used for content grid)

# --- Hotel Anker LED / print content grid ---
GRID = 64
DEAD_ROWS = 8  # defective field 7 after 90° CW mount → bottom band
ACTIVE_ROWS = GRID - DEAD_ROWS  # 56

CELL_PITCH_MM = PHYSICAL_MM / GRID  # 31.25
ACTIVE_H_MM = ACTIVE_ROWS * CELL_PITCH_MM  # 1750
DEAD_H_MM = DEAD_ROWS * CELL_PITCH_MM  # 250

# Print raster: exact integer cell pixels, 2 m @ ~2 px/mm
# 64 px/cell → 4096 px → 2.048 px/mm (clean 1 cell = 64 px)
PRINT_PX_PER_CELL = 64
PRINT_SIZE_PX = GRID * PRINT_PX_PER_CELL  # 4096
PRINT_PX_PER_MM = PRINT_SIZE_PX / PHYSICAL_MM  # 2.048

# --- ASSUMED (not in public Kendu datasheets) ---
# 8×8 LED modules tiling the 64×64 content grid → 250×250 mm tiles.
# Stock Flowbox RGB plate PCB size is proprietary / unpublished.
MODULE_CELLS = 8
MODULE_PITCH_MM = MODULE_CELLS * CELL_PITCH_MM  # 250.0
N_MODULES_SIDE = GRID // MODULE_CELLS  # 8

# Industry-typical SEG keder groove (Smartframe-class); Kendu exact unpublished
KEDER_GROOVE_W_MM = 4.0
KEDER_GROOVE_D_MM = 14.0


def cell_to_mm(c: float) -> float:
    return c * CELL_PITCH_MM


def mm_to_cell(mm: float) -> float:
    return mm / CELL_PITCH_MM


def cell_to_print_px(c: float) -> int:
    """Pixel origin of cell edge on the hires print canvas."""
    return int(round(c * PRINT_PX_PER_CELL))


def print_px_to_cell(px: float) -> float:
    return px / PRINT_PX_PER_CELL
