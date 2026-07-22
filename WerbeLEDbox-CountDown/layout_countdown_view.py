"""Viewer-upright countdown geometry (frame rotated 90° CW on hardware).

Geometry locked to live Canva design DAHQET371rQ (4096×4096, 64 px/cell).
Digits fill the slots between liquid-glass bars. Vertical center of each 8
aligns with the midpoint between the two colon dots.
"""

from __future__ import annotations

WIDTH = 64
HEIGHT = 64
DEAD_ROWS = 8
ACTIVE_H = HEIGHT - DEAD_ROWS  # 56

# Canva digit layers scaled ~1.291× vs kit → ~DW=8 cell bodies on the 64-grid.
DW, DH, ST = 8, 12, 2
COLON_W = 2  # cells for ":" — small dots need little slot width
PHI = 1.6180339887

# Logo band (LED); print may overflow into the title bar like Canva (~12 cells).
LOGO_H = 5
# Canva title liquid-glass ≈ top 9.51 / height 7.77 cells
TITLE_H = 8
LABEL_H = 2

# Explicit Y stack from Canva fills (rounded to integer cells).
# title≈9.51, days≈19.1, tage≈32.6, time≈37.0, hms≈50.4, totzone 56
LOGO_Y0 = 1
LOGO_Y1 = LOGO_Y0 + LOGO_H
# Canva title bar crop-top ≈608 → cell 10 after 32px pad on tight layers
TITLE_BAR_Y = 10
_TITLE_BOT = TITLE_BAR_Y + TITLE_H  # 18
DAY_Y = 19
TAGE_BAR_Y = 32
_TAGE_BOT = TAGE_BAR_Y + LABEL_H  # 34
TIME_Y = 37
HMS_BAR_Y = 50

COLON_DOT_FRACS = (0.34, 0.66)

# Canva day/Tage column center ≈ 2459.7 px (grid mid 2048) → +6.43 cells
DAY_X_SHIFT = 6

# Title lines inside upper liquid-glass bar
TITLE_LINES = (
    "Hotel Anker",
    "SAN-RE-MO CountDown Bistro Caf\u00e9 Bar",
    "Zeit bis Baubeginn:",
)

GAP = TITLE_BAR_Y - LOGO_Y1  # 3

assert LOGO_Y0 >= 0
assert DAY_Y >= _TITLE_BOT
assert TAGE_BAR_Y >= DAY_Y + DH
assert TIME_Y >= _TAGE_BOT
assert HMS_BAR_Y >= TIME_Y + DH
assert HMS_BAR_Y + LABEL_H <= ACTIVE_H
assert abs((COLON_DOT_FRACS[0] + COLON_DOT_FRACS[1]) / 2 - 0.5) < 1e-6


def layout_origins_cells(grid: int = WIDTH):
    """Day group Canva-shifted; time row nearly full-width (Canva HMS scale)."""
    day_w = 3 * DW + 2 * ST
    day_x0 = (grid - day_w) // 2 + DAY_X_SHIFT
    day_x0 = max(0, min(day_x0, grid - day_w))
    days = [day_x0 + i * (DW + ST) for i in range(3)]

    parts: list[tuple[str, int]] = []
    for group in range(3):
        if group:
            parts.append((":", COLON_W))
            parts.append(("gap", 1))
        parts.append(("d", DW))
        parts.append(("gap", 1))
        parts.append(("d", DW))
        if group < 2:
            parts.append(("gap", 1))
    total = sum(w for _, w in parts)
    # Canva HMS left≈1.35 cells — allow tight side margins
    assert total <= grid - 4, f"time row too wide ({total}); need ≥2 cells margin each side"
    x = (grid - total) // 2
    time_digits: list[int] = []
    colons: list[tuple[int, int]] = []
    for kind, w in parts:
        if kind == "d":
            time_digits.append(x)
            x += w
        elif kind == ":":
            colons.append((x, TIME_Y))
            x += w
        else:
            x += w
    return days, DAY_Y, time_digits, TIME_Y, colons
