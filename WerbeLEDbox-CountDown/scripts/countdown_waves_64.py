#!/usr/bin/env python3
"""64×64 Hotel Anker countdown — print-ghost 7-seg (888 / 88:88:88).

Baubeginn: 2026-10-01 13:00 Europe/Zurich
Frame: physical 90° CW; defective field 7 → dead band at viewer bottom.
Content authored upright (active 56 rows); SHM gets 90° CCW remap.
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

try:
    from zoneinfo import ZoneInfo

    TZ = ZoneInfo("Europe/Zurich")
except Exception:
    TZ = timezone(timedelta(hours=1))  # Nov = CET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
if not ASSETS.exists():
    ASSETS = ROOT / "assets"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from layout_64x64_8x512 import HEIGHT, WIDTH  # noqa: E402
from layout_countdown_view import (  # noqa: E402
    ACTIVE_H,
    COLON_DOT_FRACS,
    DAY_Y,
    DEAD_ROWS,
    DH,
    DW,
    HMS_BAR_Y,
    LABEL_H,
    LOGO_H,
    LOGO_Y0,
    LOGO_Y1,
    ST,
    TAGE_BAR_Y,
    TIME_Y,
    TITLE_BAR_Y,
    TITLE_H,
    layout_origins_cells,
)

TARGET = datetime(2026, 10, 1, 13, 0, 0, tzinfo=TZ)

# --- Night look — countdown first, chrome secondary but still bright enough ---
NAVY = np.array([0, 12, 48], dtype=np.float32)
NAVY_MID = np.array([0, 55, 170], dtype=np.float32)
NAVY_HI = np.array([20, 120, 255], dtype=np.float32)
# Was 0.25 — too dark through dense textile; Gottlieb 2026-08-07
NON_DIGIT_BRIGHTNESS_NIGHT = 0.55
AMBER = np.array([255, 96, 0], dtype=np.uint8)
AMBER_HI = np.array([255, 140, 20], dtype=np.uint8)  # brighter lit digits at night
GOLD = np.array([200, 110, 24], dtype=np.uint8)
GOLD_HI = np.array([240, 140, 30], dtype=np.uint8)
GOLD_SHINE = np.array([255, 190, 70], dtype=np.uint8)
WHITE = np.array([255, 255, 255], dtype=np.uint8)
DIGIT = AMBER_HI
# Unused 7-seg bars: light milk (never black) — readability through print
MILK_NIGHT = np.array([110, 85, 45], dtype=np.uint8)
GHOST = MILK_NIGHT

# --- Day look — bright overall; countdown absolute priority ---
DAY_NAVY = np.array([0, 70, 120], dtype=np.float32)  # bright troughs (no near-black)
DAY_NAVY_MID = np.array([0, 200, 240], dtype=np.float32)
DAY_NAVY_HI = np.array([160, 255, 255], dtype=np.float32)
NON_DIGIT_BRIGHTNESS_DAY = 1.0
DAY_DIGIT = WHITE
MILK_DAY = np.array([210, 220, 235], dtype=np.uint8)  # leichtes Milch
DAY_GOLD = np.array([255, 120, 0], dtype=np.float32)
DAY_GOLD_HI = np.array([255, 170, 20], dtype=np.float32)
DAY_GOLD_SHINE = np.array([255, 230, 90], dtype=np.float32)
DAY_HOT = np.array([255, 200, 40], dtype=np.float32)

# Rorschach (Hotel Anker) — solar elevation for real daylight fade
RORSCHACH_LAT = 47.4789
RORSCHACH_LON = 9.4902
# Civil twilight (~-6°) → bright day (~+10°): smooth day_factor 0..1
DAY_ELEV_LO = -6.0
DAY_ELEV_HI = 10.0

# Runtime look: "auto" (solar), "day", or "night" — set via --look / COUNTDOWN_LOOK
_LOOK_MODE = "auto"

SHM = "shm://ws2812"
OUT = ASSETS / "kendu-64x64"
# Keep old name for night chrome default (tests / docs)
NON_DIGIT_BRIGHTNESS = NON_DIGIT_BRIGHTNESS_NIGHT

DAYS_X, DAY_Y, TIME_X, TIME_Y, COLONS = layout_origins_cells()
assert DAY_Y + DH <= TIME_Y
assert TIME_Y + DH <= ACTIVE_H
assert HMS_BAR_Y + 1 < ACTIVE_H or HMS_BAR_Y < ACTIVE_H

_DSEG_FONT = None
_DSEG_FONT_PATH: Path | None = None
_DSEG_GLYPH_CACHE: dict[tuple[str, int, int], np.ndarray] = {}

# Hot-path caches (filled lazily)
_YY: np.ndarray | None = None
_XX: np.ndarray | None = None
_GLASS_XX: np.ndarray | None = None
_BP_LINE: np.ndarray | None = None  # ACTIVE_H bool
_BP_DEAD: np.ndarray | None = None  # dead-zone bool
_WHITE_F = WHITE.astype(np.float32)
_AMBER_F = AMBER.astype(np.float32)
_GOLD_F = GOLD.astype(np.float32)
_GOLD_HI_F = GOLD_HI.astype(np.float32)
_GOLD_SHINE_F = GOLD_SHINE.astype(np.float32)
_HOT_F = np.array([255.0, 160.0, 40.0], dtype=np.float32)  # orange-hot, not cream
_AMBER_HI_F = AMBER_HI.astype(np.float32)
_MILK_NIGHT_F = MILK_NIGHT.astype(np.float32)
_MILK_DAY_F = MILK_DAY.astype(np.float32)


def _smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = (x - edge0) / (edge1 - edge0) if edge1 != edge0 else 0.0
    t = 0.0 if t < 0.0 else 1.0 if t > 1.0 else t
    return t * t * (3.0 - 2.0 * t)


def _julian_day_utc(dt_utc: datetime) -> float:
    y, m = dt_utc.year, dt_utc.month
    day = (
        dt_utc.day
        + (dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0) / 24.0
    )
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + day + b - 1524.5


def solar_elevation_deg(
    when: datetime | None = None,
    *,
    lat: float = RORSCHACH_LAT,
    lon: float = RORSCHACH_LON,
) -> float:
    """Apparent solar elevation (degrees) for Rorschach / given lat,lon."""
    if when is None:
        when = datetime.now(TZ)
    elif when.tzinfo is None:
        when = when.replace(tzinfo=TZ)
    utc = when.astimezone(timezone.utc)
    jd = _julian_day_utc(utc)
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360.0
    g = math.radians((357.528 + 0.9856003 * n) % 360.0)
    lam = math.radians((L + 1.915 * math.sin(g) + 0.020 * math.sin(2.0 * g)) % 360.0)
    eps = math.radians(23.439 - 0.0000004 * n)
    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    dec = math.asin(math.sin(eps) * math.sin(lam))
    gmst = (280.46061837 + 360.98564736629 * (jd - 2451545.0)) % 360.0
    lst = math.radians((gmst + lon) % 360.0)
    ha = lst - ra
    lat_r = math.radians(lat)
    elev = math.asin(
        math.sin(lat_r) * math.sin(dec)
        + math.cos(lat_r) * math.cos(dec) * math.cos(ha)
    )
    return math.degrees(elev)


def day_factor(now: datetime | None = None) -> float:
    """0 = night look, 1 = full-power day look. Forced via _LOOK_MODE."""
    mode = (_LOOK_MODE or "auto").strip().lower()
    if mode in ("day", "full", "1"):
        return 1.0
    if mode in ("night", "0"):
        return 0.0
    elev = solar_elevation_deg(now)
    return _smoothstep(DAY_ELEV_LO, DAY_ELEV_HI, elev)


def _lerp_rgb(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    return a * (1.0 - t) + b * t


def _ensure_grids() -> tuple[np.ndarray, np.ndarray]:
    global _YY, _XX
    if _YY is None or _XX is None:
        _YY, _XX = np.mgrid[0:HEIGHT, 0:WIDTH].astype(np.float32)
    return _YY, _XX


def _ensure_glass_xx() -> np.ndarray:
    global _GLASS_XX
    if _GLASS_XX is None:
        _GLASS_XX = np.arange(WIDTH, dtype=np.float32)[None, :] / max(1, WIDTH - 1)
    return _GLASS_XX


def _cache_blueprint_bools() -> None:
    global _BP_LINE, _BP_DEAD
    if _BLUEPRINT_MASK is None:
        _BP_LINE = _BP_DEAD = None
        return
    _BP_LINE = _BLUEPRINT_MASK[:ACTIVE_H] > 0.35
    _BP_DEAD = _BLUEPRINT_MASK[ACTIVE_H:] > 0.5


def _warmup_digit_cache() -> None:
    """Rasterize DSEG 0–9 once so the first live frames stay under budget."""
    for ch in "0123456789":
        _dseg_mask(ch, DW)


def to_hardware(buf: np.ndarray) -> np.ndarray:
    """Viewer-upright → SHM for frame rotated 90° CW (dead bottom → field 7)."""
    return np.ascontiguousarray(np.rot90(buf, k=1))


def remaining(now: datetime | None = None) -> tuple[int, int, int, int]:
    if now is None:
        now = datetime.now(TZ)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=TZ)
    delta = TARGET - now
    if delta.total_seconds() <= 0:
        return 0, 0, 0, 0
    total = int(delta.total_seconds())
    days = total // 86400
    rem = total % 86400
    hours = rem // 3600
    rem %= 3600
    mins = rem // 60
    secs = rem % 60
    return days, hours, mins, secs


def _dseg_font(size: int = 120):
    global _DSEG_FONT, _DSEG_FONT_PATH
    try:
        from PIL import ImageFont
    except ImportError:
        return None
    for path in (
        ROOT / "fonts" / "DSEG7Classic-Bold.ttf",
        ROOT / "fonts" / "DSEG7Classic-Regular.ttf",
    ):
        if path.exists():
            _DSEG_FONT_PATH = path
            _DSEG_FONT = ImageFont.truetype(str(path), size)
            return _DSEG_FONT
    return None


def _dseg_render_ink(ch: str, font):
    """Rasterize one DSEG char and return cropped binary ink (L mode)."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return None
    canvas = Image.new("L", (256, 320), 0)
    d = ImageDraw.Draw(canvas)
    bb = d.textbbox((0, 0), ch, font=font)
    d.text((-bb[0] + 8, -bb[1] + 8), ch, font=font, fill=255)
    ink = canvas.point(lambda v: 255 if v > 40 else 0)
    box = ink.getbbox()
    if not box:
        return None
    return ink.crop(box)


def _dseg_mask(ch: str, cells_w: int) -> np.ndarray | None:
    """Binary mask (cells_w × DH) — ghost-8 footprint; narrow digits right-aligned.

    Classic 7-seg / DSEG: ``1`` (and similarly ``7``) uses the right verticals of the
    common 8 box — not centered in empty cell space.
    """
    key = (ch, cells_w, DH)
    if key in _DSEG_GLYPH_CACHE:
        return _DSEG_GLYPH_CACHE[key]
    font = _dseg_font(160)
    if font is None:
        return None
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return None

    ref = _dseg_render_ink("8", font)
    glyph = ref if ch == "8" else _dseg_render_ink(ch, font)
    if ref is None or glyph is None:
        return None

    # Same scale as the full 8 footprint (height-first fit into the digit cell)
    fitted_8 = ImageOps.contain(ref, (cells_w, DH), Image.Resampling.LANCZOS)
    fitted_8 = fitted_8.point(lambda v: 255 if v > 90 else 0)
    ox8 = (cells_w - fitted_8.width) // 2
    oy8 = (DH - fitted_8.height) // 2

    if ch == "8":
        fitted, ox, oy = fitted_8, ox8, oy8
    else:
        scale = min(
            fitted_8.width / max(1, ref.width),
            fitted_8.height / max(1, ref.height),
        )
        gw = max(1, int(round(glyph.width * scale)))
        gh = max(1, int(round(glyph.height * scale)))
        fitted = glyph.resize((gw, gh), Image.Resampling.LANCZOS).point(
            lambda v: 255 if v > 90 else 0
        )
        # Right-align to the 8 footprint (1/7 sit on the right of the ghost-8)
        ox = ox8 + fitted_8.width - fitted.width
        oy = oy8 + (fitted_8.height - fitted.height) // 2

    cell = Image.new("L", (cells_w, DH), 0)
    cell.paste(fitted, (ox, oy))
    m = (np.asarray(cell) > 128).astype(np.uint8)
    _DSEG_GLYPH_CACHE[key] = m
    return m


def _dilate_mask(mask: np.ndarray, r: int = 1) -> np.ndarray:
    """Cheap binary dilate for gold outline around segments."""
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx == 0 and dy == 0:
                continue
            out = np.maximum(out, np.roll(np.roll(mask, dy, 0), dx, 1))
    return out


def _blit_mask(buf: np.ndarray, ox: int, oy: int, mask: np.ndarray, color: np.ndarray) -> None:
    h, w = mask.shape
    x0, y0 = max(0, ox), max(0, oy)
    x1, y1 = min(WIDTH, ox + w), min(HEIGHT, oy + h)
    if x0 >= x1 or y0 >= y1:
        return
    mx0, my0 = x0 - ox, y0 - oy
    region = mask[my0 : my0 + (y1 - y0), mx0 : mx0 + (x1 - x0)]
    dest = buf[y0:y1, x0:x1]
    dest[region > 0] = color


def paint_digit_with_ghost(
    buf: np.ndarray,
    ox: int,
    oy: int,
    value: int,
    *,
    digit_color: np.ndarray | None = None,
    milk_color: np.ndarray | None = None,
) -> None:
    """DSEG7: light-milk ghost-8, then lit digit on top (countdown priority)."""
    ghost_m = _dseg_mask("8", DW)
    lit_m = _dseg_mask(str(value), DW)
    if ghost_m is None or lit_m is None:
        return
    color = DIGIT if digit_color is None else digit_color
    milk = GHOST if milk_color is None else milk_color
    _blit_mask(buf, ox, oy, ghost_m, milk)
    _blit_mask(buf, ox, oy, lit_m, color)


def paint_colon(
    buf: np.ndarray,
    ox: int,
    oy: int,
    lit: bool,
    *,
    digit_color: np.ndarray | None = None,
    milk_color: np.ndarray | None = None,
) -> None:
    """Two-dot colon centered in COLON_W; midpoint == vertical center of the 8s."""
    from layout_countdown_view import COLON_W

    base = DIGIT if digit_color is None else digit_color
    milk = GHOST if milk_color is None else milk_color
    color = base if lit else milk
    # Single LED per dot when COLON_W=2; 2×2 only if slot is wider — matches print ~6% DH
    side = 1 if COLON_W <= 2 else 2
    cx0 = ox + max(0, (COLON_W - side) // 2)
    for frac in COLON_DOT_FRACS:
        cy = TIME_Y + int(DH * frac) - (side // 2)
        if 0 <= cy < ACTIVE_H - (side - 1) and 0 <= cx0 < WIDTH - (side - 1):
            buf[cy : cy + side, cx0 : cx0 + side] = color


_BLUEPRINT_MASK: np.ndarray | None = None
_LOGO_MASK: np.ndarray | None = None
_LOGO_CENTER: tuple[float, float] | None = None


def _find_asset(*names: str) -> Path | None:
    for base in (ASSETS, ROOT / "assets", ROOT.parent / "assets"):
        for name in names:
            path = base / name
            if path.exists():
                return path
    return None


def blueprint_mask_64() -> np.ndarray | None:
    """Line-only mask (64×64 float 0..1) from hotel facade outline — not a filled silhouette."""
    global _BLUEPRINT_MASK
    if _BLUEPRINT_MASK is not None:
        return _BLUEPRINT_MASK
    try:
        from PIL import Image

        from facade_place import find_blueprint_path, load_facade_content_mask, place_facade_mask
    except ImportError:
        return None
    path = find_blueprint_path(ASSETS, ROOT / "assets", ROOT.parent / "assets")
    if path is None:
        path = _find_asset(
            "hotel-anker-blueprint-simplified.png",
            "hotel-anker-blueprint-v2.png",
            "hotel-anker-blueprint-facade.png",
        )
    if path is None:
        return None

    # Mid zoom; 888 stays on layout; building shifted so 888 sits in sign↔Erker gap
    content = load_facade_content_mask(path)
    fitted = place_facade_mask(content, out_w=WIDTH, grid=WIDTH)
    box_h = fitted.height
    m = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    m[: min(box_h, HEIGHT), :] = np.where(np.asarray(fitted)[: min(box_h, HEIGHT)] > 90, 1.0, 0.0)
    _BLUEPRINT_MASK = m
    _cache_blueprint_bools()
    return _BLUEPRINT_MASK


def logo_mask_64() -> np.ndarray | None:
    """Crisp binary anchor silhouette only — no soft halo / bounding box."""
    global _LOGO_MASK, _LOGO_CENTER
    if _LOGO_MASK is not None:
        return _LOGO_MASK
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return None
    path = _find_asset(
        "hotel-anker-historic-anchor.png",
        "hotel-anker-countdown-logo-dark.png",
        "hotel-anker-countdown-logo.png",
    )
    if path is None:
        return None

    logo = Image.open(path).convert("RGBA")
    arr = np.asarray(logo, dtype=np.float32)
    rgb = arr[..., :3]
    alpha = arr[..., 3] / 255.0
    # Opaque mark pixels only (drop empty / near-black sheet)
    dark = (rgb[..., 0] < 40) & (rgb[..., 1] < 40) & (rgb[..., 2] < 40)
    ink = (alpha > 0.35) & ~dark
    mark_img = Image.fromarray(np.where(ink, 255, 0).astype(np.uint8), "L")
    if "historic-anchor" not in path.name:
        mark_img = mark_img.crop((0, 0, mark_img.width, int(mark_img.height * 0.72)))
    bbox = mark_img.getbbox()
    if not bbox:
        return None
    mark_img = mark_img.crop(bbox)

    # Canva DAHQET371rQ: logo ≈7.4×12.2 cells, top≈-0.6, centered (overlaps title)
    top = 0
    band_h = 12
    band_w = min(WIDTH - 4, 8)
    fitted = ImageOps.contain(mark_img, (band_w, band_h), method=Image.Resampling.NEAREST)
    # Hard pixels only — no blur/dilate that reads as a rectangle
    fitted = fitted.point(lambda v: 255 if v > 128 else 0)

    canvas = Image.new("L", (WIDTH, HEIGHT), 0)
    ox = (WIDTH - fitted.width) // 2
    oy = top + max(0, (band_h - fitted.height) // 2)
    canvas.paste(fitted, (ox, oy))
    m = (np.asarray(canvas) > 128).astype(np.float32)
    _LOGO_MASK = m
    ys, xs = np.nonzero(m > 0.5)
    if len(xs):
        _LOGO_CENTER = (float(xs.mean()), float(ys.mean()))
    else:
        _LOGO_CENTER = (WIDTH * 0.5, float(top + band_h * 0.45))
    return _LOGO_MASK


def wave_background(t: float, day_f: float = 0.0) -> np.ndarray:
    """Waves: night navy → day luminous cyan; facade lines secondary."""
    yy, xx = _ensure_grids()

    # Soft, slow multi-layer motion (3 layers — enough contrast, cheaper @25 fps)
    drift = t * 0.55
    drift2 = t * 0.32 + 1.1
    drift3 = t * 0.42 + 2.4

    scallop = np.sin(xx * 0.55 - drift + yy * 0.10)
    swell = np.sin(yy * 0.38 - drift2)
    ripple = np.sin(xx * 0.28 + yy * 0.36 - drift3)

    field = 0.48 * scallop + 0.36 * swell + 0.32 * ripple
    field = np.clip((field + 1.05) / 1.85, 0.0, 1.0)
    # Soft curve — keep waves bright; never crush to near-black (countdown must win)
    field = np.power(field, 0.68)

    navy = _lerp_rgb(NAVY, DAY_NAVY, day_f)
    mid = _lerp_rgb(NAVY_MID, DAY_NAVY_MID, day_f)
    hi = _lerp_rgb(NAVY_HI, DAY_NAVY_HI, day_f)

    f = field[..., None]
    mid_w = 0.50 + 0.15 * day_f
    hi_w = 0.90 + 0.20 * day_f
    rgb = (
        navy[None, None, :] * (1.0 - f)
        + mid[None, None, :] * (mid_w * f)
        + hi[None, None, :] * (hi_w * f * f)
    )

    # Hotel facade lines: OFF by day (they fight the countdown); night = soft whisper only
    blueprint_mask_64()
    night_f = 1.0 - day_f
    if night_f > 0.01 and _BP_LINE is not None and _BP_LINE.any():
        act = rgb[:ACTIVE_H]
        # Soft backlight — keep most of the wave, add only a light white ink
        keep, add = 0.88, 0.18
        blended = act[_BP_LINE] * keep + _WHITE_F * add
        act[_BP_LINE] = act[_BP_LINE] * (1.0 - night_f) + blended * night_f

    logo = logo_mask_64()
    if logo is not None:
        # Night amber mark → day hot orange (stays brand, punches through print)
        logo_c = _lerp_rgb(_AMBER_F, DAY_HOT, day_f)
        rgb[logo > 0.5] = logo_c

    if _BP_DEAD is not None:
        dead = rgb[ACTIVE_H:]
        dead[:] = 0
        if night_f > 0.01 and _BP_DEAD.any():
            dead[_BP_DEAD] = _WHITE_F * (0.32 * night_f)
    else:
        rgb[ACTIVE_H:, :, :] = 0
    return np.clip(rgb, 0, 255).astype(np.uint8)


def paint_liquid_glass_bars(
    buf: np.ndarray, t: float, *, final: bool = False, day_f: float = 0.0
) -> None:
    """Liquid Glass bars — title (slower) + narrow label bars (independent motion).

    When final=True, colors are written at display intensity (after chrome dim).
    Narrow 2-row bars use a high-contrast traveling caustic so motion reads clearly.
    Day: very bright orange liquid glass (full LED power through dense textile).
    """
    gold = _lerp_rgb(_GOLD_F, DAY_GOLD, day_f)
    gold_hi = _lerp_rgb(_GOLD_HI_F, DAY_GOLD_HI, day_f)
    shine = _lerp_rgb(_GOLD_SHINE_F, DAY_GOLD_SHINE, day_f)
    hot = _lerp_rgb(_HOT_F, DAY_HOT, day_f)
    xx = _ensure_glass_xx()

    # (y0, h, speed, phase0, pulse_hz, breath_hz) — label bars async vs title
    # Narrow bars: faster sweep so a bead crosses ~1.2–1.5×/s
    bars = (
        (TITLE_BAR_Y, TITLE_H, 0.38, 0.00, 2.4, 1.15),
        (TAGE_BAR_Y, LABEL_H, 1.35, 0.17, 5.2, 2.8),
        (HMS_BAR_Y, LABEL_H, 1.15, 0.61, 4.6, 2.2),
    )

    for y0, h, speed, phase0, pulse_hz, breath_hz in bars:
        y1 = min(ACTIVE_H, y0 + h)
        if y0 >= ACTIVE_H or y1 <= y0:
            continue
        strip = buf[y0:y1].astype(np.float32)
        hh = strip.shape[0]
        narrow = hh <= 2
        yy = np.linspace(0.0, 1.0, hh, dtype=np.float32)[:, None]

        if narrow and final:
            # Dark glass base + near-white traveling caustics (post-dim, absolute)
            base = gold * 0.55 + gold_hi * 0.20
            base = base * (0.78 + 0.22 * (1.0 - yy))[..., None]
            # Keep a whisper of underlying wave so bars don't float as flat slabs
            tinted = strip * 0.18 + base * 0.82
            phase = (t * speed + phase0) % 1.0
            cx = 0.01 + 0.98 * phase
            # Tight primary bead (clear hotspot) + counter-glint + thin caustic
            blob = np.exp(-(((xx - cx) / 0.042) ** 2))
            cx2 = (cx + 0.52 + 0.10 * math.sin(t * 2.1 + phase0 * 7.0)) % 1.0
            blob2 = np.exp(-(((xx - cx2) / 0.090) ** 2)) * 0.85
            cx3 = (cx + 0.28 + 0.04 * math.sin(t * 3.3 + phase0)) % 1.0
            blob3 = np.exp(-(((xx - cx3) / 0.028) ** 2)) * 0.70
            gloss = np.clip(blob + blob2 + blob3, 0.0, 1.5)
            # Row split: top = specular rim, bottom = deeper caustic trail
            row_w = np.where(yy < 0.5, 1.15, 0.92)
            gloss = gloss * row_w
            pulse = 0.78 + 0.22 * math.sin(t * pulse_hz + phase0 * 5.0)
            breath = 0.88 + 0.12 * math.sin(t * breath_hz + phase0 * 3.0)
            tinted = tinted * breath
            # Hard mix toward hot/shine so the bead is unmistakable on 2 LEDs tall
            mix = np.clip(gloss * 1.35 * pulse, 0.0, 1.0)[..., None]
            tinted = tinted * (1.0 - mix) + (hot * 0.55 + shine * 0.45) * mix
            # Soft secondary wash (wider, dimmer) for liquid feel between beads
            wash = np.exp(-(((xx - cx) / 0.18) ** 2)) * 0.35
            tinted = tinted + (shine - tinted) * (wash[..., None] * 0.55)
            out = np.clip(tinted, 0, 255)
            if hh >= 1:
                out[0] = np.clip(out[0] * 0.35 + shine * 0.65, 0, 255)
            if hh >= 2:
                out[-1] = np.clip(out[-1] * 0.55 + gold_hi * 0.45, 0, 255)
            buf[y0:y1] = out.astype(np.uint8)
            continue

        blur = (
            strip
            + np.roll(strip, 1, axis=1)
            + np.roll(strip, -1, axis=1)
            + np.roll(strip, 1, axis=0)
            + np.roll(strip, -1, axis=0)
        ) / 5.0
        tinted = blur * 0.38 + gold * 0.40 + shine * 0.14
        tinted *= (1.20 - 0.38 * yy)[..., None]
        if narrow:
            # Pre-dim path (previews): still favor horizontal travel
            rim = (0.55 + 0.45 * (1.0 - yy))[..., None]
            tinted = tinted * (1.0 - rim * 0.35) + gold_hi * rim * 0.85 + shine * rim * 0.40
            phase = (t * speed + phase0) % 1.0
            cx = 0.02 + 0.96 * phase
            blob = np.exp(-(((xx - cx) / 0.045) ** 2))
            cx2 = (cx + 0.48 + 0.08 * math.sin(t * 1.7 + phase0 * 6.0)) % 1.0
            blob2 = np.exp(-(((xx - cx2) / 0.10) ** 2)) * 0.80
            cx3 = (cx + 0.22) % 1.0
            blob3 = np.exp(-(((xx - cx3) / 0.035) ** 2)) * 0.65
            gloss = np.clip(blob + blob2 + blob3, 0.0, 1.0)
            gloss = gloss * (0.88 + 0.12 * (1.0 - yy))
            pulse = 0.70 + 0.30 * math.sin(t * pulse_hz + phase0 * 5.0)
            breath = 0.86 + 0.14 * math.sin(t * breath_hz + phase0 * 3.0)
            mix = 1.25 * pulse
        else:
            rim_top = np.exp(-((yy / 0.14) ** 2))
            rim_bot = np.exp(-(((1.0 - yy) / 0.20) ** 2))
            rim = (0.90 * rim_top + 0.45 * rim_bot)[..., None]
            tinted = tinted * (1.0 - rim * 0.50) + gold_hi * rim * 0.95 + shine * rim * 0.55
            phase = (t * speed + phase0) % 1.0
            cx = 0.05 + 0.90 * phase
            blob = np.exp(-(((xx - cx) / 0.08) ** 2) - (((yy - 0.35) / 0.42) ** 2))
            cx2 = (cx + 0.38) % 1.0
            blob2 = np.exp(-(((xx - cx2) / 0.14) ** 2) - (((yy - 0.60) / 0.55) ** 2)) * 0.65
            cx3 = (cx + 0.70) % 1.0
            blob3 = np.exp(-(((xx - cx3) / 0.06) ** 2) - (((yy - 0.45) / 0.35) ** 2)) * 0.40
            gloss = np.clip(blob + blob2 + blob3, 0.0, 1.0)
            pulse = 0.72 + 0.28 * math.sin(t * pulse_hz + phase0 * 4.0)
            breath = 0.90 + 0.10 * math.sin(t * breath_hz + phase0 * 2.0)
            mix = 0.95 * pulse
        tinted = tinted * breath + (shine - tinted) * (gloss[..., None] * mix)
        out = np.clip(strip * 0.10 + tinted * 0.90, 0, 255)
        if hh >= 1:
            out[0] = np.clip(out[0] * 0.20 + shine * 0.80, 0, 255)
        if hh >= 2:
            out[-1] = np.clip(out[-1] * 0.40 + gold_hi * 0.60, 0, 255)
        buf[y0:y1] = out.astype(np.uint8)


def render_frame(t: float, now: datetime | None = None) -> np.ndarray:
    """Viewer-upright: chrome by day_factor; countdown digits+milk always undimmed on top."""
    if now is None:
        now = datetime.now(TZ)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=TZ)

    df = day_factor(now)
    chrome = NON_DIGIT_BRIGHTNESS_NIGHT + (
        NON_DIGIT_BRIGHTNESS_DAY - NON_DIGIT_BRIGHTNESS_NIGHT
    ) * df
    dig = np.clip(
        _lerp_rgb(_AMBER_HI_F, DAY_DIGIT.astype(np.float32), df), 0, 255
    ).astype(np.uint8)
    milk = np.clip(_lerp_rgb(_MILK_NIGHT_F, _MILK_DAY_F, df), 0, 255).astype(np.uint8)

    buf = wave_background(t, day_f=df)
    # Glass BEFORE dim — secondary to countdown
    paint_liquid_glass_bars(buf, t, final=False, day_f=df)

    active = buf[:ACTIVE_H].astype(np.float32) * chrome
    buf[:ACTIVE_H] = np.clip(active, 0, 255).astype(np.uint8)

    if _BP_DEAD is not None:
        dead = buf[ACTIVE_H:]
        dead[:] = 0
        night_f = 1.0 - df
        if night_f > 0.01 and _BP_DEAD.any():
            dead[_BP_DEAD] = (_WHITE_F * 0.32 * night_f * chrome).astype(np.uint8)
        buf[ACTIVE_H:] = dead
    else:
        buf[ACTIVE_H:, :, :] = 0

    # Countdown AFTER dim — absolute priority: milk ghost + full-power lit segments
    days, hours, mins, secs = remaining(now)
    d_vals = [days // 100, (days // 10) % 10, days % 10]
    t_vals = [hours // 10, hours % 10, mins // 10, mins % 10, secs // 10, secs % 10]

    for ox, val in zip(DAYS_X, d_vals):
        paint_digit_with_ghost(buf, ox, DAY_Y, val, digit_color=dig, milk_color=milk)
    for ox, val in zip(TIME_X, t_vals):
        paint_digit_with_ghost(buf, ox, TIME_Y, val, digit_color=dig, milk_color=milk)

    for cx, cy in COLONS:
        paint_colon(
            buf, cx, cy, lit=(secs % 2) == 0, digit_color=dig, milk_color=milk
        )

    return buf


def save_previews(path_dir: Path) -> None:
    global _LOOK_MODE
    path_dir.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
    except ImportError as e:
        raise SystemExit(f"Pillow required for preview: {e}") from e

    saved_mode = _LOOK_MODE
    try:
        # Night (legacy filenames) + forced full-power day
        for look, stem in (("night", "countdown-waves-gold"), ("day", "countdown-waves-day")):
            _LOOK_MODE = look
            frames = []
            for i in range(24):
                fr = render_frame(i * 0.2, now=datetime.now(TZ) + timedelta(seconds=i))
                frames.append(fr)
                if i == 0:
                    Image.fromarray(fr, "RGB").resize((640, 640), Image.NEAREST).save(
                        path_dir / f"{stem}.png"
                    )
                    Image.fromarray(fr, "RGB").save(path_dir / f"{stem}-1x.png")
            strip = np.concatenate(frames[::4], axis=1)
            Image.fromarray(strip, "RGB").resize(
                (strip.shape[1] * 6, strip.shape[0] * 6), Image.NEAREST
            ).save(path_dir / f"{stem}-strip.png")
    finally:
        _LOOK_MODE = saved_mode

    elev = solar_elevation_deg()
    df = day_factor()
    d, h, m, s = remaining()
    print(f"preview -> {path_dir}")
    print(f"remaining -> {d}d {h:02d}:{m:02d}:{s:02d} until {TARGET.date()}")
    print(
        f"daylight -> elev={elev:.1f}° day_factor={df:.3f} look_mode={saved_mode}",
        flush=True,
    )


def _attach_shm_panel(timeout_s: float = 90.0):
    """Attach putter-owned SHM only — never create (create unlinks → split-brain LEDs)."""
    import SharedArray as sa

    short = SHM.replace("shm://", "")
    t0 = time.perf_counter()
    last: Exception | None = None
    while True:
        try:
            panel = sa.attach(SHM)
            if tuple(panel.shape) != (HEIGHT, WIDTH, 3):
                raise SystemExit(
                    f"bad shm shape {panel.shape}; want {(HEIGHT, WIDTH, 3)} — "
                    "restart ws2812put-pi02 first"
                )
            return panel
        except SystemExit:
            raise
        except Exception as e:
            last = e
            waited = time.perf_counter() - t0
            if waited >= timeout_s:
                raise SystemExit(
                    f"cannot attach {SHM} after {timeout_s:.0f}s — start "
                    f"ws2812put-pi02 first (producer must never create '{short}'). "
                    f"last={last!r}"
                ) from last
            if int(waited) % 5 == 0:
                print(
                    f"countdown_waves: waiting for putter SHM {SHM} "
                    f"({waited:.0f}s)…",
                    flush=True,
                )
            time.sleep(0.5)


def run_shm(fps: float, seconds: float | None) -> None:
    panel = _attach_shm_panel()

    # Warm caches before the paced loop (blueprint / logo / DSEG / grids)
    _ensure_grids()
    _ensure_glass_xx()
    blueprint_mask_64()
    logo_mask_64()
    _warmup_digit_cache()
    _ = render_frame(0.0)

    period = 1.0 / fps if fps > 0 else 0.04
    t0 = time.perf_counter()
    n = 0
    fps_t0 = t0
    fps_n = 0
    render_ms_acc = 0.0
    elev0 = solar_elevation_deg()
    df0 = day_factor()
    print(
        f"countdown_waves: attached {SHM} target_fps={fps} look={_LOOK_MODE} "
        f"elev={elev0:.1f}° day_factor={df0:.3f}",
        flush=True,
    )
    while True:
        if seconds is not None and (time.perf_counter() - t0) >= seconds:
            break
        t = time.perf_counter() - t0
        r0 = time.perf_counter()
        panel[:] = to_hardware(render_frame(t))
        render_ms_acc += (time.perf_counter() - r0) * 1000.0
        n += 1
        fps_n += 1
        now_m = time.perf_counter()
        elapsed_fps = now_m - fps_t0
        if elapsed_fps >= 10.0:
            actual = fps_n / elapsed_fps
            avg_ms = render_ms_acc / max(1, fps_n)
            elev = solar_elevation_deg()
            df = day_factor()
            print(
                f"countdown_waves: fps={actual:.2f} (target={fps}, "
                f"render_ms={avg_ms:.1f}, frames={fps_n}, window={elapsed_fps:.1f}s, "
                f"elev={elev:.1f}° day_factor={df:.3f})",
                flush=True,
            )
            fps_t0 = now_m
            fps_n = 0
            render_ms_acc = 0.0
        next_t = t0 + n * period
        delay = next_t - now_m
        if delay > 0:
            time.sleep(delay)
    total_elapsed = max(1e-6, time.perf_counter() - t0)
    print(
        f"wrote {n} frames to {SHM} (avg_fps={n / total_elapsed:.2f}, target={fps})",
        flush=True,
    )


def regen_opacity_mask_companion() -> None:
    """Keep black/red print opacity plate in sync with Lichtvideo facade placement."""
    import importlib.util

    from PIL import Image

    path = ROOT / "scripts" / "gen_flowbox_print_hires.py"
    spec = importlib.util.spec_from_file_location("gen_flowbox_print_hires", path)
    if spec is None or spec.loader is None:
        print("skip opacity mask: cannot load", path)
        return
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.OUT.mkdir(parents=True, exist_ok=True)
    opacity = mod.compose_opacity_mask()
    opacity.save(mod.OUT / "print-opacity-mask-hires.png")
    opacity.resize((2000, 2000), Image.Resampling.NEAREST).save(
        mod.OUT / "print-opacity-mask-2000.png"
    )
    mod.add_caption(
        opacity, "Print · Opacity", "schwarz=lichtdurchlässig · rot=lichtundurchlässig"
    ).save(mod.OUT / "preview-opacity-mask.png")
    print("wrote opacity mask", mod.OUT)


def main() -> int:
    import os

    global _LOOK_MODE
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preview", action="store_true")
    p.add_argument("--shm", action="store_true")
    p.add_argument("--fps", type=float, default=25.0)
    p.add_argument("--seconds", type=float, default=None)
    p.add_argument(
        "--look",
        choices=("auto", "day", "night"),
        default=None,
        help="auto=solar day/night fade (Rorschach); day/night force look",
    )
    args = p.parse_args()
    env_look = (os.environ.get("COUNTDOWN_LOOK") or "").strip().lower()
    if args.look:
        _LOOK_MODE = args.look
    elif env_look in ("auto", "day", "night"):
        _LOOK_MODE = env_look
    else:
        _LOOK_MODE = "auto"
    if not args.preview and not args.shm:
        args.preview = True
    if args.preview:
        save_previews(OUT)
        try:
            regen_opacity_mask_companion()
        except Exception as e:
            print("opacity companion failed:", e)
    if args.shm:
        run_shm(args.fps, args.seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
