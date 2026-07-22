#!/usr/bin/env python3
"""64x64 panel → 8×512 WS2812 serpentine layout (AnkerPI02).

Panel (row 0 = top, col 0 = left):
  8 fields left→right, each 8×64 px (= 512 LEDs).

Within one field, chain order:
  start bottom-left, go UP; at top step right and go DOWN;
  at bottom step right and go UP; …
"""

from __future__ import annotations

import numpy as np

HEIGHT = 64
WIDTH = 64
N_FIELDS = 8
FIELD_W = 8  # WIDTH // N_FIELDS
N_LED = FIELD_W * HEIGHT  # 512


def build_lut(height: int = HEIGHT, width: int = WIDTH, n_fields: int = N_FIELDS) -> np.ndarray:
    """Return int32 LUT shape (n_fields, n_led) → ravel index into (height, width)."""
    field_w = width // n_fields
    n_led = field_w * height
    if field_w * n_fields != width:
        raise ValueError("width must divide evenly by n_fields")
    lut = np.empty((n_fields, n_led), dtype=np.int32)
    for f in range(n_fields):
        for i in range(n_led):
            local_col = i // height
            pos = i % height
            # even local_col: bottom→top; odd: top→bottom
            row = (height - 1 - pos) if (local_col % 2 == 0) else pos
            col = f * field_w + local_col
            lut[f, i] = row * width + col
    return lut


# Module-level LUT for hot path
LUT = build_lut()


def map_panel_to_lines(panel: np.ndarray, lut: np.ndarray | None = None) -> np.ndarray:
    """panel (H,W,3) uint8 → lines (8, 512, 3) uint8."""
    if lut is None:
        lut = LUT
    if panel.shape != (HEIGHT, WIDTH, 3):
        raise ValueError(f"expected panel {(HEIGHT, WIDTH, 3)}, got {panel.shape}")
    flat = np.ascontiguousarray(panel).reshape(HEIGHT * WIDTH, 3)
    return flat[lut]


def map_panel_to_frame_rgb(panel: np.ndarray, lut: np.ndarray | None = None) -> bytes:
    """Packed RGB for Pico: line0[512]||line1[512]||…||line7[512]."""
    lines = map_panel_to_lines(panel, lut)
    return lines.reshape(-1).tobytes()
