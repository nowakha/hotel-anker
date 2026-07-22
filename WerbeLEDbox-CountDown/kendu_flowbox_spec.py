"""Hotel Anker LightBox — physical ↔ 64×64 LED/print mapping (3D-aware).

Measured XY (2026-07-22):
- LED panels: **250 × 250 mm**
- Outer frame: **2100 × 2100 mm**
- Face rim / Profil-Stirnbreite: **50 mm** → print/LED face **2000 × 2000 mm**

Photo + measured Z / depth:
- True **backlit** stack (LEDs on rear plane, not edge-lit)
- SEG keder groove on the **front inner lip** of the aluminium profile
- **Innen 45 mm** measured (Zollstock): front lip / textile plane → LED panel face
- Face rim 50 mm (XY) remains distinct from this Z cavity — see GEOMETRIE-3D.md

Logical content grid (AnkerPI02 custom WS2812 retrofit):

    pitch = FACE_MM / GRID  →  2000 / 64 = 31.25 mm / cell
    module = 8 × 8 cells    →  250 × 250 mm (matches panel)
"""

from __future__ import annotations

# --- Measured XY ---
FACE_MM = 2000.0  # SEG print / LED matrix face (inside profile)
PHYSICAL_MM = FACE_MM  # back-compat alias used by generators
PROFILE_FACE_W_MM = 50.0  # front-view rim (outer − face) / 2
PROFILE_W_MM = PROFILE_FACE_W_MM  # back-compat: generators mean face rim
OUTER_MM = 2100.0
MODULE_PITCH_MM_CONFIRMED = 250.0

# --- Z / depth (measured 2026-07-22, Zollstock photos «Innen 4.5 cm») ---
# Optically relevant cavity: front inner lip (≈ textile / keder plane) → LED face
INNER_DEPTH_MM = 45.0  # measured
LED_RECESS_MM = INNER_DEPTH_MM  # alias
# Full outer profile depth may be slightly larger behind the LED plane; cavity is 45 mm.
PROFILE_DEPTH_MM = INNER_DEPTH_MM  # use measured cavity for schematics / light path
PROFILE_DEPTH_SOURCE = "measured-innen-45mm-zollstock"

# Optical stack (front → back), from photos + measurement
# 1) SEG textile in keder groove (front lip)
# 2) air / diffusion gap ≈ 45 mm
# 3) LED panel plane (8×8 × 250 mm) on white reflector
# 4) back braces / controllers (Kendu CH1–4, DC 24V, DMX)

# --- Content grid ---
GRID = 64
DEAD_ROWS = 8
ACTIVE_ROWS = GRID - DEAD_ROWS  # 56

CELL_PITCH_MM = FACE_MM / GRID  # 31.25
ACTIVE_H_MM = ACTIVE_ROWS * CELL_PITCH_MM  # 1750
DEAD_H_MM = DEAD_ROWS * CELL_PITCH_MM  # 250

PRINT_PX_PER_CELL = 64
PRINT_SIZE_PX = GRID * PRINT_PX_PER_CELL  # 4096
PRINT_PX_PER_MM = PRINT_SIZE_PX / FACE_MM  # 2.048

MODULE_CELLS = 8
MODULE_PITCH_MM = MODULE_CELLS * CELL_PITCH_MM  # 250.0
N_MODULES_SIDE = GRID // MODULE_CELLS  # 8

assert abs(MODULE_PITCH_MM - MODULE_PITCH_MM_CONFIRMED) < 1e-9
assert abs(FACE_MM + 2 * PROFILE_FACE_W_MM - OUTER_MM) < 1e-9

# SEG keder groove (industry-typical; exact unpublished — photo: narrow front lip channel)
KEDER_GROOVE_W_MM = 4.0
KEDER_GROOVE_D_MM = 14.0

OUTER_HINT_MM = OUTER_MM  # back-compat


def cell_to_mm(c: float) -> float:
    return c * CELL_PITCH_MM


def mm_to_cell(mm: float) -> float:
    return mm / CELL_PITCH_MM


def cell_to_print_px(c: float) -> int:
    """Pixel origin of cell edge on the hires print canvas."""
    return int(round(c * PRINT_PX_PER_CELL))


def print_px_to_cell(px: float) -> float:
    return px / PRINT_PX_PER_CELL
