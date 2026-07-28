"""Shared Hotel-Anker facade placement for LED (64) and print (hires).

Digits stay on the countdown layout; the building is scaled/shifted so the
day-row 888 sits in the gap between the roof \"HOTEL ANKER\" sign and the Erker.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

# Content-bbox landmarks of hotel-anker-blueprint-simplified.png (after getbbox)
# Roof "HOTEL ANKER" / GRAND crest right edge; Erker body left edge
SIGN_RIGHT = 660
ERKER_LEFT = 1446
GAP_MID = (SIGN_RIGHT + ERKER_LEFT) / 2.0  # ~1053

# Middle zoom between prior too-large (~1.18) and too-small (~0.96)
ZOOM = 1.14
# Thin totzone bite (cells on 64-grid); not deep arch immersion
INTO_DEAD_CELLS = 2
# Positive: shift building left so 888 sits cleaner in the sign↔Erker gap
ALIGN_BIAS_CELLS = 1.5


def day_span_cells(grid: int = 64) -> tuple[float, float, float]:
    """Return (day_left, day_right, day_mid) in cell coordinates (matches layout)."""
    try:
        from layout_countdown_view import DAY_X_SHIFT, DW, ST
    except Exception:
        DW, ST, DAY_X_SHIFT = 8, 2, 6
    day_w = 3 * DW + 2 * ST
    day_left = (grid - day_w) // 2 + DAY_X_SHIFT
    day_left = max(0, min(day_left, grid - day_w))
    day_right = day_left + day_w
    day_mid = (day_left + day_right) / 2.0
    return float(day_left), float(day_right), day_mid


def load_facade_content_mask(path: Path) -> Image.Image:
    src = Image.open(path).convert("L")
    arr = np.asarray(src, dtype=np.float32)
    m0 = Image.fromarray(np.where(arr > 90, 255, 0).astype(np.uint8), "L")
    bb = m0.getbbox() or (0, 0, m0.width, m0.height)
    return m0.crop(bb)


def place_facade_mask(
    content: Image.Image,
    *,
    out_w: int,
    grid: int = 64,
    zoom: float = ZOOM,
    into_dead_cells: int = INTO_DEAD_CELLS,
) -> Image.Image:
    """Fit facade into out_w × box_h (active+into_dead), tip at top.

    Horizontal crop centers the sign↔Erker gap on the day-digit mid (888).
    """
    cell = out_w / float(grid)
    active_px = int(round((grid - 8) * cell))  # ACTIVE_H = 56
    into_px = max(1, int(round(into_dead_cells * cell)))
    box_h = active_px + into_px

    _, _, day_mid = day_span_cells(grid)
    # Align gap mid to (day mid − bias) → building shifts left on panel
    target_px = (day_mid - ALIGN_BIAS_CELLS) * cell

    scale = (box_h * zoom) / max(1, content.height)
    nw = max(1, int(round(content.width * scale)))
    nh = max(1, int(round(content.height * scale)))

    if scale > 1.02:
        # Supersample line art (Druckerei: kein weiches Hochrechnen).
        hi = content.resize((nw * 2, nh * 2), Image.Resampling.NEAREST)
        hi = hi.filter(ImageFilter.MaxFilter(5)).point(lambda v: 255 if v > 128 else 0)
        scaled = hi.resize((nw, nh), Image.Resampling.LANCZOS).point(
            lambda v: 255 if v > 140 else 0
        )
    elif scale < 0.98:
        scaled = content.resize((nw, nh), Image.Resampling.LANCZOS).point(
            lambda v: 255 if v > 128 else 0
        )
    else:
        scaled = content.resize((nw, nh), Image.Resampling.NEAREST).point(
            lambda v: 255 if v > 128 else 0
        )

    # Map content gap mid → target under the fixed 888 row
    gap_mid_px = GAP_MID * scale
    x0 = int(round(gap_mid_px - target_px))
    x0 = max(0, min(x0, max(0, scaled.width - out_w)))

    fitted = scaled.crop((x0, 0, min(scaled.width, x0 + out_w), min(scaled.height, box_h)))
    if fitted.width < out_w or fitted.height < box_h:
        pad = Image.new("L", (out_w, box_h), 0)
        pad.paste(fitted, ((out_w - fitted.width) // 2, 0))
        fitted = pad

    thicken = max(3, int(round(cell / 18)) | 1)
    fitted = fitted.filter(ImageFilter.MaxFilter(thicken)).point(lambda v: 255 if v > 128 else 0)
    return fitted

def find_blueprint_path(*bases: Path) -> Path | None:
    names = (
        # Prefer highest-res masters first (avoid soft upscale from 1k/2k)
        "kendu-flowbox-2m-print/canva-upload/01-facade-blueprint.png",
        "hotel-anker-blueprint-simplified.png",
        "hotel-anker-blueprint-v2.png",
        "hotel-anker-blueprint-facade.png",
        "hotel-anker-blueprint-historic-tower.png",
    )
    for base in bases:
        if base is None:
            continue
        for name in names:
            p = base / name
            if p.exists():
                return p
    return None