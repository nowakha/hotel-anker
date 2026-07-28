"""Hotel Anker LightBox — physical ↔ LED grid ↔ print master (3D-aware).

Canonical PRINT (confirmed 2026-07-27 via user PDF `print-ghost-hires.pdf`):
- Spann-/Druckmaß: **2100 × 2100 mm** (Außenmaß Rahmen)
- Unterer Schwarzstreifen auf dem Druck: **300 mm** (= 250 mm Modulreihe + 50 mm Stirn)

LED / content grid (unchanged physics):
- LED panels: **250 × 250 mm**, 8×8 → face **2000 × 2000 mm**
- Profil-Stirnbreite: **50 mm** → outer **2100 × 2100 mm**
"""

from __future__ import annotations

# --- Measured XY ---
FACE_MM = 2000.0  # LED matrix face (inside profile) — NOT the print canvas
PHYSICAL_MM = FACE_MM  # back-compat: generators that mean LED face
PROFILE_FACE_W_MM = 50.0  # front-view rim (outer − face) / 2
PROFILE_W_MM = PROFILE_FACE_W_MM
OUTER_MM = 2100.0
MODULE_PITCH_MM_CONFIRMED = 250.0

# --- Print / SEG spannmaß (canonical production) ---
PRINT_MM = OUTER_MM  # textile stretch size = outer frame
PRINT_DEAD_MM = 300.0  # solid black on print (= module row 250 + face rim 50)
assert abs(PRINT_DEAD_MM - (MODULE_PITCH_MM_CONFIRMED + PROFILE_FACE_W_MM)) < 1e-9

# --- Z / depth ---
INNER_DEPTH_MM = 45.0  # optical cavity textile → LED
LED_RECESS_MM = INNER_DEPTH_MM
PROFILE_OUTER_DEPTH_MM = 82.0
PROFILE_OUTER_DEPTH_SOURCE = "foto-04-zollstock-2026-07-27"
LED_TO_PROFILE_INNER_MM = 25.0
LED_TO_PROFILE_INNER_SOURCE = "foto-05-zollstock-2026-07-27"
PROFILE_DEPTH_MM = INNER_DEPTH_MM
PROFILE_DEPTH_SOURCE = "measured-innen-45mm-plus-foto-outer-82mm"

# --- Content grid (LED / live) ---
GRID = 64
DEAD_ROWS = 8  # defective bottom module row on LED matrix
ACTIVE_ROWS = GRID - DEAD_ROWS  # 56

CELL_PITCH_MM = FACE_MM / GRID  # 31.25
ACTIVE_H_MM = ACTIVE_ROWS * CELL_PITCH_MM  # 1750
DEAD_H_MM = DEAD_ROWS * CELL_PITCH_MM  # 250 — LED dead row only
# Print black includes the bottom face rim as well:
VISUAL_BOTTOM_DARK_MM = PRINT_DEAD_MM  # 300 — same as print dead band
assert abs(VISUAL_BOTTOM_DARK_MM - 300.0) < 1e-9

# Legacy generator canvas (64 px/cell on LED face) — live/LED tools
PRINT_PX_PER_CELL = 64
PRINT_SIZE_PX = GRID * PRINT_PX_PER_CELL  # 4096 (LED-face tooling)
PRINT_PX_PER_MM = PRINT_SIZE_PX / FACE_MM  # 2.048

# Production raster (Richnerstutz 2026-07): higher dpi + bleed
# ~4 px/mm ≈ 102 dpi — large-format textile; old 2 px/mm was too soft
PRINT_MASTER_PX_PER_MM = 4.0
BLEED_MM = 20.0  # Bildzugabe rundum (Druckerei)
SPERRZONE_MM = 20.0  # Stoff-Sperrzone / safe margin from trim
PRINT_TRIM_MM = PRINT_MM  # 2100 — Endformat / Spannmaß
PRINT_EXPORT_MM = PRINT_TRIM_MM + 2.0 * BLEED_MM  # 2140 — MediaBox inkl. Bleed
PRINT_MASTER_PX = int(round(PRINT_TRIM_MM * PRINT_MASTER_PX_PER_MM))  # 8400
PRINT_EXPORT_PX = int(round(PRINT_EXPORT_MM * PRINT_MASTER_PX_PER_MM))  # 8560
PRINT_DEAD_PX = int(round(PRINT_DEAD_MM * PRINT_MASTER_PX_PER_MM))  # 1200
FACE_MASTER_PX = int(round(FACE_MM * PRINT_MASTER_PX_PER_MM))  # 8000
# Legacy low-res master (pre-correction) kept for reference only
PRINT_MASTER_PX_LEGACY_2PPM = int(round(PRINT_MM * 2.0))  # 4200

MODULE_CELLS = 8
MODULE_PITCH_MM = MODULE_CELLS * CELL_PITCH_MM  # 250.0
N_MODULES_SIDE = GRID // MODULE_CELLS  # 8

assert abs(MODULE_PITCH_MM - MODULE_PITCH_MM_CONFIRMED) < 1e-9
assert abs(FACE_MM + 2 * PROFILE_FACE_W_MM - OUTER_MM) < 1e-9

KEDER_GROOVE_W_MM = 4.0
KEDER_GROOVE_D_MM = 14.0

OUTER_HINT_MM = OUTER_MM


def cell_to_mm(c: float) -> float:
    return c * CELL_PITCH_MM


def mm_to_cell(mm: float) -> float:
    return mm / CELL_PITCH_MM


def cell_to_print_px(c: float) -> int:
    """Pixel origin of cell edge on the legacy 4096 LED-face canvas."""
    return int(round(c * PRINT_PX_PER_CELL))


def print_px_to_cell(px: float) -> float:
    return px / PRINT_PX_PER_CELL
