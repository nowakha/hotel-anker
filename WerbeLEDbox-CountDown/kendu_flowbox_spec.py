"""Hotel Anker LightBox — physical ↔ 64×64 LED/print mapping.

Measured on the installed unit (2026-07-22):
- LED panels: **250 × 250 mm** exactly
- Outer frame: **2100 × 2100 mm**
- Profile adds **50 mm** per side → backlight / print face **2000 × 2000 mm**
  (8 × 8 panels: 8 × 250 mm = 2000 mm; 2000 + 2×50 = 2100)

Logical content grid (AnkerPI02 custom WS2812 retrofit):

    pitch = PHYSICAL_MM / GRID  →  2000 / 64 = 31.25 mm / cell
    module = 8 × 8 cells        →  250 × 250 mm (matches panel)
"""

from __future__ import annotations

# --- Measured frame / panels ---
PHYSICAL_MM = 2000.0  # backlight / SEG print face (inside profile)
PROFILE_W_MM = 50.0  # aluminium profile section (measured: +5 cm outer)
OUTER_MM = 2100.0  # outer envelope (confirmed)
MODULE_PITCH_MM_CONFIRMED = 250.0  # LED panel size (confirmed)

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

# 8×8 LED panels tiling the 64×64 content grid
MODULE_CELLS = 8
MODULE_PITCH_MM = MODULE_CELLS * CELL_PITCH_MM  # 250.0
N_MODULES_SIDE = GRID // MODULE_CELLS  # 8

assert abs(MODULE_PITCH_MM - MODULE_PITCH_MM_CONFIRMED) < 1e-9
assert abs(PHYSICAL_MM + 2 * PROFILE_W_MM - OUTER_MM) < 1e-9

# Industry-typical SEG keder groove (Smartframe-class); exact Kendu unpublished
KEDER_GROOVE_W_MM = 4.0
KEDER_GROOVE_D_MM = 14.0

# Back-compat alias (older code / docs)
OUTER_HINT_MM = OUTER_MM


def cell_to_mm(c: float) -> float:
    return c * CELL_PITCH_MM


def mm_to_cell(mm: float) -> float:
    return mm / CELL_PITCH_MM


def cell_to_print_px(c: float) -> int:
    """Pixel origin of cell edge on the hires print canvas."""
    return int(round(c * PRINT_PX_PER_CELL))


def print_px_to_cell(px: float) -> float:
    return px / PRINT_PX_PER_CELL
