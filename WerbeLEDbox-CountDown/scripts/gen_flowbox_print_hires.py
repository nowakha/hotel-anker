"""High-res Kendu Flowbox 2×2 m PRINT — centered layout, clean 7-seg, new facade.

- Content stack centered L/R and T/B in active 56/64
- New simplified hotel outline (hotel-anker-blueprint-simplified.png)
- Classic 7-seg ghosts: thick gold ring + black core, precise geometry
- Liquid-Glass full-width bars (frost/tint/specular); HOTEL ANKER + Zeit bis Baubeginn
- Dead zone bottom 8/64 opaque black
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "WerbeLEDbox-CountDown"
OUT = ROOT / "assets" / "kendu-flowbox-2m-print"
ASSETS = ROOT / "assets"

if str(PROJ) not in sys.path:
    sys.path.insert(0, str(PROJ))

from kendu_flowbox_spec import (  # noqa: E402
    CELL_PITCH_MM,
    DEAD_H_MM,
    FACE_MM,
    GRID,
    OUTER_MM,
    PHYSICAL_MM,
    PRINT_PX_PER_CELL,
    PRINT_PX_PER_MM,
    PRINT_SIZE_PX,
    PROFILE_FACE_W_MM,
    PROFILE_W_MM,
    VISUAL_BOTTOM_DARK_MM,
    cell_to_print_px,
)
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
    PHI,
    ST,
    TAGE_BAR_Y,
    TIME_Y,
    TITLE_BAR_Y,
    TITLE_H,
    TITLE_LINES,
    layout_origins_cells,
)

# Exact cell grid: 64 px/cell → 4096 px = 2 m @ 2.048 px/mm (LED tooling default).
# Production export bumps CELL via configure_print_resolution() (~125 → 8000 px face).
SIZE = PRINT_SIZE_PX
CELL = PRINT_PX_PER_CELL
DEAD_PX = cell_to_print_px(DEAD_ROWS)
ACTIVE_PX = cell_to_print_px(ACTIVE_H)


def configure_print_resolution(cell_px: int) -> None:
    """Scale the LED-face generator canvas (must call before compose*)."""
    global SIZE, CELL, DEAD_PX, ACTIVE_PX, _DSEG_CACHE
    if cell_px < 32:
        raise ValueError(f"cell_px too small: {cell_px}")
    CELL = int(cell_px)
    SIZE = GRID * CELL
    DEAD_PX = DEAD_ROWS * CELL
    ACTIVE_PX = ACTIVE_H * CELL
    _DSEG_CACHE.clear()

NAVY_DEEP = (2, 6, 18)
ANKER_GOLD = (198, 164, 110)
ANKER_GOLD_HI = (230, 196, 140)
WHITE = (250, 248, 244)
BLACK = (0, 0, 0)
GREY = (160, 164, 170)

FONT_DIR = PROJ / "fonts"
_DSEG_CACHE: dict[int, ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}


def find_font(size: int, bold: bool = False):
    """Title serif — prefer inscriptional/Roman (facade HOTEL ANKER), else Georgia."""
    # Historical roof lettering is Trajan-class Roman capitals. Prefer close
    # system matches that still fit TITLE_H without growing the pixel budget.
    candidates = [
        FONT_DIR / "Cinzel-Bold.ttf",
        FONT_DIR / "CinzelDecorative-Bold.ttf",
        FONT_DIR / "TrajanPro-Bold.ttf",
        Path(r"C:\Windows\Fonts\CASTELAR.TTF"),
        Path(r"C:\Windows\Fonts\Castellar.ttf"),
        Path(r"C:\Windows\Fonts\PER_____.TTF"),  # Perpetua
        Path(r"C:\Windows\Fonts\PERB____.TTF"),
        Path(r"C:\Windows\Fonts\georgiab.ttf") if bold else Path(r"C:\Windows\Fonts\georgia.ttf"),
        Path(r"C:\Windows\Fonts\timesbd.ttf") if bold else Path(r"C:\Windows\Fonts\times.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf") if bold else Path(r"C:\Windows\Fonts\arial.ttf"),
    ]
    for path in candidates:
        try:
            if path.exists():
                return ImageFont.truetype(str(path), size)
        except OSError:
            continue
    return ImageFont.load_default()


def find_sans(size: int, bold: bool = False):
    for path in (
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\seguisb.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def find_dseg(size: int):
    if size in _DSEG_CACHE:
        return _DSEG_CACHE[size]
    for path in (
        FONT_DIR / "DSEG7Classic-Bold.ttf",
        FONT_DIR / "DSEG7Classic-Regular.ttf",
    ):
        if path.exists():
            font = ImageFont.truetype(str(path), size)
            _DSEG_CACHE[size] = font
            return font
    font = find_sans(size, bold=True)
    _DSEG_CACHE[size] = font
    return font


def cell_to_px(c: float) -> int:
    """Map layout cell → print px on the current generator canvas."""
    return int(round(c * CELL))


def _dseg_placement(ox: int, oy: int, ch: str, *, cells_w: int = DW, scale: float = 1.34):
    """Return (font, x, y) — glyph fills digit cell height between glass bars."""
    x0, y0 = cell_to_px(ox), cell_to_px(oy)
    w, h = cells_w * CELL, DH * CELL
    font = find_dseg(max(24, int(h * scale)))
    try:
        bb = font.getbbox(ch)
    except Exception:
        bb = (0, 0, w, h)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    # Prefer height fill; only shrink if width overflows cell badly
    if tw > w * 1.20:
        font = find_dseg(max(24, int(h * scale * (w * 1.12 / max(1, tw)))))
        try:
            bb = font.getbbox(ch)
        except Exception:
            bb = (0, 0, w, h)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = x0 + (w - tw) // 2 - bb[0]
    y = y0 + (h - th) // 2 - bb[1]
    return font, x, y


def _dseg_draw_char(draw, ox: int, oy: int, ch: str, fill, *, cells_w: int = DW) -> None:
    """Draw one DSEG glyph centered in cell."""
    font, x, y = _dseg_placement(ox, oy, ch, cells_w=cells_w)
    draw.text((x, y), ch, font=font, fill=fill)


def _dseg_glyph_layer(
    ox: int,
    oy: int,
    ch: str,
    *,
    cells_w: int = DW,
    stroke: int,
    outline_rgb: tuple[int, int, int] = ANKER_GOLD,
    fill_rgb: tuple[int, int, int] = BLACK,
) -> Image.Image:
    """Rasterize DSEG glyph; core inset so outline keeps clear cell margin.

    Outline ring = outline_rgb; segment fill/core = fill_rgb (print ghost: gold/black;
    opacity plate: red/black).
    """
    x0, y0 = cell_to_px(ox), cell_to_px(oy)
    w, h = cells_w * CELL, DH * CELL
    # Outline expands by ~stroke; leave clear margin so L/R ring is never flat-clipped.
    margin = max(16, CELL // 4)
    inset = stroke + margin
    inner_w = max(8, w - 2 * inset)
    inner_h = max(8, h - 2 * inset)
    font = find_dseg(max(64, int(inner_h * 1.48)))
    big = Image.new("L", (w * 2, h * 2), 0)
    bd = ImageDraw.Draw(big)
    try:
        bb = font.getbbox(ch)
    except Exception:
        bb = (0, 0, w, h)
    bd.text((20 - bb[0], 20 - bb[1]), ch, font=font, fill=255)
    ink = big.point(lambda v: 255 if v > 40 else 0)
    box = ink.getbbox()
    if not box:
        box = (0, 0, inner_w, inner_h)
    fitted = ImageOps.contain(ink.crop(box), (inner_w, inner_h), Image.Resampling.LANCZOS)
    fitted = fitted.point(lambda v: 255 if v > 90 else 0)
    core = Image.new("L", (w, h), 0)
    core.paste(
        fitted,
        ((w - fitted.width) // 2, (h - fitted.height) // 2),
    )

    # Outer pad so MaxFilter outline is not truncated at layer edge.
    pad = max(4, stroke // 2)
    layer = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    layer.paste(core, (pad, pad))
    alpha = layer
    k = stroke * 2 + 1
    if k % 2 == 0:
        k += 1
    outline_a = alpha.filter(ImageFilter.MaxFilter(k))
    # Allow a few px into the digit gap (not into neighbors); preserves chamfers.
    spill = max(2, margin // 3)
    cell_mask = Image.new("L", layer.size, 0)
    ImageDraw.Draw(cell_mask).rectangle(
        [pad - spill, pad - spill, pad + w - 1 + spill, pad + h - 1 + spill], fill=255
    )
    outline_a = Image.composite(outline_a, Image.new("L", layer.size, 0), cell_mask)
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ring = Image.new("RGBA", layer.size, (*outline_rgb, 255))
    fill = Image.new("RGBA", layer.size, (*fill_rgb, 255))
    out = Image.composite(ring, out, outline_a)
    out = Image.composite(fill, out, alpha)
    out.info["ox"] = x0 - pad
    out.info["oy"] = y0 - pad
    return out


def paint_digit(draw, ox, oy, value: int | None, *, ghost: bool, lit: bool, overlay: Image.Image | None = None):
    """DSEG7: gold outline + opaque black ghost-8; fills inter-bar slot height."""
    stroke = max(12, CELL // 4)
    glyph = _dseg_glyph_layer(ox, oy, "8", stroke=stroke)
    if overlay is not None:
        overlay.paste(glyph, (glyph.info["ox"], glyph.info["oy"]), glyph)
    if lit and value is not None:
        _dseg_draw_char(draw, ox, oy, str(value), (*ANKER_GOLD_HI, 255))


def paint_colon(draw, ox, oy, lit: bool, overlay: Image.Image | None = None):
    """Two balanced dots (~6% of digit height); midpoint == center of the 8s."""
    if overlay is None:
        return
    from layout_countdown_view import COLON_W

    fill = (*ANKER_GOLD_HI, 255) if lit else (0, 0, 0, 255)
    ring = (*ANKER_GOLD, 255)
    x0 = cell_to_px(ox)
    cw = COLON_W * CELL
    # ~6% DH core + modest gold ring — readable, not dominant disks
    ring_w = max(6, CELL // 10)
    dot_r = int(DH * CELL * 0.06)
    # Fit in slot with a few px air; do not force oversized floor
    max_r = max(10, cw // 2 - ring_w - max(6, CELL // 16))
    dot_r = min(max(dot_r, CELL // 5), max_r)
    ld = ImageDraw.Draw(overlay)
    for frac in COLON_DOT_FRACS:
        cy = cell_to_px(TIME_Y) + int(DH * CELL * frac)
        cx = x0 + cw // 2
        ld.ellipse(
            [cx - dot_r - ring_w, cy - dot_r - ring_w, cx + dot_r + ring_w, cy + dot_r + ring_w],
            fill=ring,
        )
        ld.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=fill)


def load_blueprint() -> Image.Image:
    """Full-bleed facade via shared placement (888 in sign↔Erker gap)."""
    from facade_place import find_blueprint_path, load_facade_content_mask, place_facade_mask

    path = find_blueprint_path(ASSETS, PROJ / "assets")
    if path is None:
        for p in (
            ASSETS / "hotel-anker-blueprint-historic-tower.png",
            ASSETS / "hotel-anker-blueprint-simplified.png",
        ):
            if p.exists():
                path = p
                break
    if path is None:
        return Image.new("RGB", (SIZE, SIZE), NAVY_DEEP)

    content = load_facade_content_mask(path)
    fitted = place_facade_mask(content, out_w=SIZE, grid=GRID)

    # Active = navy, dead = black; facade drawn on both (thin totzone bite)
    canvas = Image.new("RGB", (SIZE, SIZE), BLACK)
    navy = Image.new("RGB", (SIZE, ACTIVE_PX), NAVY_DEEP)
    canvas.paste(navy, (0, 0))
    line = Image.new("RGB", (SIZE, fitted.height), (245, 248, 252))
    facade = Image.composite(line, Image.new("RGB", (SIZE, fitted.height), (0, 0, 0)), fitted)
    canvas.paste(facade, (0, 0), fitted)
    arr = np.asarray(canvas).copy()
    mask = np.asarray(fitted)
    if mask.shape[0] >= ACTIVE_PX:
        active_m = mask[:ACTIVE_PX]
    else:
        active_m = np.zeros((ACTIVE_PX, SIZE), dtype=np.uint8)
        active_m[: mask.shape[0]] = mask
    navy_arr = np.asarray(Image.new("RGB", (SIZE, ACTIVE_PX), NAVY_DEEP))
    sel = active_m < 128
    arr[:ACTIVE_PX][sel] = navy_arr[sel]
    return Image.fromarray(arr, "RGB")


def resize_crisp(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    """High-quality down/up for logos: 2× LANCZOS then target (less soft than 1-step)."""
    w, h = size
    if im.size == size:
        return im
    hi = im.resize((max(w * 2, im.width), max(h * 2, im.height)), Image.Resampling.LANCZOS)
    out = hi.resize((w, h), Image.Resampling.LANCZOS)
    if out.mode == "RGBA":
        r, g, b, a = out.split()
        # Harden alpha so logo edge is print-sharp (no mushy fringe)
        a = a.point(lambda v: 255 if v >= 140 else 0)
        out = Image.merge("RGBA", (r, g, b, a))
    return out


def extract_anchor_mark() -> Image.Image:
    """Historic Grand Hotel Anker Rorschach mark: crown + admiralty anchor."""
    dedicated = [
        ASSETS / "hotel-anker-historic-anchor.png",
    ]
    for p in dedicated:
        if p.exists():
            logo = Image.open(p).convert("RGBA")
            bbox = logo.split()[-1].getbbox()
            return logo.crop(bbox) if bbox else logo

    for p in (
        ASSETS / "hotel-anker-countdown-logo-dark.png",
    ):
        if p.exists():
            logo = Image.open(p).convert("RGBA")
            break
    else:
        return Image.new("RGBA", (200, 200), (0, 0, 0, 0))

    px = logo.load()
    w, h = logo.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r < 40 and g < 50 and b < 70:
                px[x, y] = (r, g, b, 0)
    crop = logo.crop((0, 0, w, int(h * 0.72)))
    bbox = crop.getbbox()
    return crop.crop(bbox) if bbox else crop


def paint_liquid_glass_bar(img: Image.Image, y0: int, y1: int, *, phase: float = 0.35) -> None:
    """Full-width bar in Apple Liquid Glass spirit: frost, tint, lens, specular."""
    y1 = max(y0 + 1, y1)
    h = y1 - y0
    pad = max(6, h // 2)
    ys, ye = max(0, y0 - pad), min(img.height, y1 + pad)
    sample = img.crop((0, ys, SIZE, ye)).convert("RGB")
    frosted = sample.filter(ImageFilter.GaussianBlur(radius=max(4, h // 3)))
    # mild lensing: squash sample into bar height (concentrates light)
    frosted = frosted.resize((SIZE, h), Image.Resampling.BICUBIC)

    arr = np.asarray(frosted, dtype=np.float32)
    gold = np.array(ANKER_GOLD, dtype=np.float32)
    gold_hi = np.array(ANKER_GOLD_HI, dtype=np.float32)
    white = np.array([255.0, 252.0, 248.0], dtype=np.float32)
    # translucent glass: scene shows through, warm Anker tint adapts
    tinted = arr * 0.48 + gold * 0.34 + white * 0.10
    tinted[..., 0] = np.clip(tinted[..., 0] * 1.06, 0, 255)
    tinted[..., 2] = np.clip(tinted[..., 2] * 0.92, 0, 255)

    yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    xx = np.linspace(0.0, 1.0, SIZE, dtype=np.float32)[None, :]
    # thickness / depth: brighter top catch-light, richer base
    tinted *= (1.14 - 0.32 * yy)[..., None]

    # Fresnel-like rims
    rim_top = np.exp(-((yy / 0.16) ** 2))
    rim_bot = np.exp(-(((1.0 - yy) / 0.20) ** 2))
    rim = (0.62 * rim_top + 0.28 * rim_bot)[..., None]
    tinted = tinted * (1.0 - rim * 0.40) + gold_hi * rim * 0.70 + white * rim * 0.30

    # liquid specular blob (static print pose)
    cx = 0.28 + 0.20 * math.sin(phase * 2.0)
    cy = 0.32
    blob = np.exp(-(((xx - cx) / 0.20) ** 2) - (((yy - cy) / 0.45) ** 2))
    tinted = tinted + (gold_hi - tinted) * (blob[..., None] * 0.38)

    # side edge glints
    edge = np.minimum(xx, 1.0 - xx)
    edge_f = np.clip(1.0 - edge / 0.035, 0.0, 1.0) * 0.18
    tinted = tinted + white * edge_f[..., None] * 0.35

    orig = np.asarray(img.crop((0, y0, SIZE, y1)).convert("RGB"), dtype=np.float32)
    # keep facade faintly readable through the glass
    out = np.clip(orig * 0.22 + tinted * 0.78, 0, 255)
    # hairline specular rim
    out[0, :] = np.clip(out[0, :] * 0.25 + gold_hi * 0.55 + white * 0.20, 0, 255)
    if h > 3:
        out[1, :] = np.clip(out[1, :] * 0.65 + gold_hi * 0.35, 0, 255)
        out[-1, :] = np.clip(out[-1, :] * 0.50 + np.array([28.0, 22.0, 16.0]) * 0.50, 0, 255)
    img.paste(Image.fromarray(out.astype(np.uint8), "RGB"), (0, y0))


def text_centered(draw, text, cx, cy, font, fill, *, shadow: tuple[int, int, int] | None = None):
    """cy = vertical center of text block."""
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = cx - tw // 2
    y = cy - th // 2 - bb[1]
    if shadow is not None:
        draw.text((x + 2, y + 2), text, font=font, fill=shadow)
    draw.text((x, y), text, font=font, fill=fill)


def compose(lit: bool, days_n=71, h=12, m=0, s=0) -> Image.Image:
    base = load_blueprint().convert("RGB")
    days, day_y, time_digits, time_y, colons = layout_origins_cells()
    cx = SIZE // 2

    # --- Liquid Glass bars first (refract facade underneath) ---
    ty0, ty1 = cell_to_px(TITLE_BAR_Y), cell_to_px(TITLE_BAR_Y + TITLE_H)
    paint_liquid_glass_bar(base, ty0, ty1, phase=0.40)
    for y_cell, phase in ((TAGE_BAR_Y, 1.1), (HMS_BAR_Y, 2.0)):
        y0, y1 = cell_to_px(y_cell), cell_to_px(y_cell + LABEL_H)
        paint_liquid_glass_bar(base, y0, y1, phase=phase)

    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    # --- Logo: tall, centered, overlaps title bar; keep inside face (Sperrzone) ---
    anchor = extract_anchor_mark()
    # Legacy Canva fill was top≈-40 on 4096 (= into rim). Clamp to face top so
    # after 50 mm Stirn-Pad the mark stays ≥ SPERRZONE from trim.
    ah = int(round(783.1648448692365 * CELL / PRINT_PX_PER_CELL))
    aspect = anchor.width / max(1, anchor.height)
    aw = int(round(ah * aspect))
    max_w = int(SIZE * 0.20)
    if aw > max_w:
        aw, ah = max_w, int(max_w / aspect)
    anchor = resize_crisp(anchor, (aw, ah))
    ax = (SIZE - aw) // 2
    ay = max(0, int(round(-40.0 * CELL / PRINT_PX_PER_CELL)))
    overlay.paste(anchor, (ax, ay), anchor)

    # --- Title bar: Hotel Anker / SAN-RE-MO… / Zeit bis Baubeginn: ---
    # Canva scaled title layer ~1.60×; keep inside TITLE_H (no metric change).
    font_title = find_font(max(96, int(CELL * 2.85)), bold=True)
    font_sub = find_sans(max(52, int(CELL * 1.55)), bold=True)
    font_bis = find_sans(max(64, int(CELL * 1.90)), bold=True)
    fonts = (font_title, font_sub, font_bis)
    fills = (WHITE, WHITE, None)  # last line opaque black on final RGB
    heights = []
    for line, fnt in zip(TITLE_LINES, fonts):
        bb = od.textbbox((0, 0), line, font=fnt)
        heights.append(bb[3] - bb[1])
    gap = max(6, CELL // 8)
    block = sum(heights) + gap * (len(TITLE_LINES) - 1)
    mid = (ty0 + ty1) // 2
    y_cursor = mid - block // 2
    shadow = (12, 16, 28, 160)
    zeit_cy = mid
    for i, (line, fnt, fill) in enumerate(zip(TITLE_LINES, fonts, fills)):
        cy = y_cursor + heights[i] // 2
        if fill is not None:
            text_centered(od, line, cx, cy, fnt, fill, shadow=shadow)
        else:
            zeit_cy = cy
        y_cursor += heights[i] + gap

    # --- Digits (thick outlined DSEG on segment layer) ---
    seg = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    sd = ImageDraw.Draw(seg)
    d_vals = [days_n // 100, (days_n // 10) % 10, days_n % 10]
    t_vals = [h // 10, h % 10, m // 10, m % 10, s // 10, s % 10]
    for ox, val in zip(days, d_vals):
        paint_digit(sd, ox, day_y, val if lit else None, ghost=True, lit=lit, overlay=seg)
    for ox, val in zip(time_digits, t_vals):
        paint_digit(sd, ox, time_y, val if lit else None, ghost=True, lit=lit, overlay=seg)
    for cox, coy in colons:
        paint_colon(sd, cox, coy, lit=lit, overlay=seg)
    overlay = Image.alpha_composite(overlay, seg)
    od = ImageDraw.Draw(overlay)

    # --- Label text on glass ---
    font_label = find_sans(max(64, int(CELL * 1.7)), bold=True)
    day_mid_px = (cell_to_px(days[0]) + cell_to_px(days[-1] + DW)) // 2
    for y_cell, label, multi in (
        (TAGE_BAR_Y, "Tage", False),
        (HMS_BAR_Y, None, True),
    ):
        y0, y1 = cell_to_px(y_cell), cell_to_px(y_cell + LABEL_H)
        mid_y = (y0 + y1) // 2
        if not multi:
            text_centered(od, label, day_mid_px, mid_y, font_label, WHITE, shadow=shadow)
        else:
            pairs = [
                (time_digits[0], time_digits[1] + DW, "Stunden"),
                (time_digits[2], time_digits[3] + DW, "Minuten"),
                (time_digits[4], time_digits[5] + DW, "Sekunden"),
            ]
            for x_a, x_b, name in pairs:
                midx = (cell_to_px(x_a) + cell_to_px(x_b)) // 2
                text_centered(od, name, midx, mid_y, font_label, WHITE, shadow=shadow)

    out = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    fd = ImageDraw.Draw(out)
    # Opaque black last title line — drawn on final RGB
    text_centered(fd, TITLE_LINES[-1], cx, zeit_cy, font_bis, BLACK)
    # Totzone: solid opaque black on textile (250 mm = 8/64). No text, no facade
    # overhang — production print must measure cleanly. Visual 300 mm at install =
    # this 250 mm + 50 mm aluminium face rim (not printed).
    fd.rectangle([0, ACTIVE_PX, SIZE - 1, SIZE - 1], fill=BLACK)
    return out


def compose_opacity_mask() -> Image.Image:
    """Blocker plate for Richnerstutz: black = blockout, white = light-through.

    Same geometry as compose() so Sujet and Blocker stay aligned.
    (Legacy delivery used red=block / black=transmit — Druckerei rejected that.)
    """
    BLOCK = (0, 0, 0)  # schwarz = blockt
    CLEAR = (255, 255, 255)  # weiss = leuchtet / lichtdurchlässig
    plate = Image.new("RGB", (SIZE, SIZE), CLEAR)
    pd = ImageDraw.Draw(plate)

    # Facade line mask (keep for re-apply after glass punch-out)
    bp = load_blueprint()
    arr = np.asarray(bp)
    facade_lines = (arr[..., 0] > 180) & (arr[..., 1] > 180) & (arr[..., 2] > 180)
    blk_arr = np.asarray(plate).copy()
    blk_arr[facade_lines] = BLOCK
    plate = Image.fromarray(blk_arr, "RGB")
    pd = ImageDraw.Draw(plate)

    # Liquid-glass / label bars → WHITE (transmissive body)
    for y_cell, h in (
        (TITLE_BAR_Y, TITLE_H),
        (TAGE_BAR_Y, LABEL_H),
        (HMS_BAR_Y, LABEL_H),
    ):
        y0, y1 = cell_to_px(y_cell), cell_to_px(y_cell + h)
        pd.rectangle([0, y0, SIZE - 1, max(y0, y1 - 1)], fill=CLEAR)

    # Re-paint facade chrome over glass bands (Zwiebelturm / roof must stay continuous)
    blk_arr = np.asarray(plate).copy()
    blk_arr[facade_lines] = BLOCK
    plate = Image.fromarray(blk_arr, "RGB")
    pd = ImageDraw.Draw(plate)

    # Logo → opaque block
    anchor = extract_anchor_mark()
    ah = int(round(783.1648448692365 * CELL / PRINT_PX_PER_CELL))
    aspect = anchor.width / max(1, anchor.height)
    aw = int(round(ah * aspect))
    max_w = int(SIZE * 0.20)
    if aw > max_w:
        aw, ah = max_w, int(max_w / aspect)
    anchor = resize_crisp(anchor, (aw, ah))
    a = np.asarray(anchor)
    rgb = a[..., :3].copy()
    alpha = a[..., 3]
    rgb[:] = BLOCK
    blk_logo = Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), "RGBA")
    ax = (SIZE - aw) // 2
    ay = max(0, int(round(-40.0 * CELL / PRINT_PX_PER_CELL)))
    plate_rgba = plate.convert("RGBA")
    plate_rgba.paste(blk_logo, (ax, ay), blk_logo)
    plate = plate_rgba.convert("RGB")
    pd = ImageDraw.Draw(plate)

    days, day_y, time_digits, time_y, colons = layout_origins_cells()
    from layout_countdown_view import COLON_W as _COLON_W

    # Digits/colons: ONLY paint exact glyph geometry (no full-cell white pads).
    # Full-cell CLEAR rects caused white light boxes that did not match Sujet
    # outlines (Melanie Vogt: nicht deckungsgleich um die Zahlen).
    stroke = max(12, CELL // 4)
    plate_rgba = plate.convert("RGBA")
    for ox in days:
        glyph = _dseg_glyph_layer(
            ox, day_y, "8", stroke=stroke, outline_rgb=BLOCK, fill_rgb=CLEAR
        )
        plate_rgba.paste(glyph, (glyph.info["ox"], glyph.info["oy"]), glyph)
    for ox in time_digits:
        glyph = _dseg_glyph_layer(
            ox, time_y, "8", stroke=stroke, outline_rgb=BLOCK, fill_rgb=CLEAR
        )
        plate_rgba.paste(glyph, (glyph.info["ox"], glyph.info["oy"]), glyph)

    # Colons: identical geometry to paint_colon()
    ring_w = max(6, CELL // 10)
    dot_r = int(DH * CELL * 0.06)
    ld = ImageDraw.Draw(plate_rgba)
    for cox, coy in colons:
        x0 = cell_to_px(cox)
        cw = _COLON_W * CELL
        max_r = max(10, cw // 2 - ring_w - max(6, CELL // 16))
        r = min(max(dot_r, CELL // 5), max_r)
        for frac in COLON_DOT_FRACS:
            cy = cell_to_px(TIME_Y) + int(DH * CELL * frac)
            cx = x0 + cw // 2
            ld.ellipse(
                [cx - r - ring_w, cy - r - ring_w, cx + r + ring_w, cy + r + ring_w],
                fill=(*BLOCK, 255),
            )
            ld.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*CLEAR, 255))

    plate = plate_rgba.convert("RGB")
    pd = ImageDraw.Draw(plate)

    # Texts on glass bars → BLOCK (opaque lettering)
    cx = SIZE // 2
    font_label = find_sans(max(64, int(CELL * 1.7)), bold=True)
    ty0, ty1 = cell_to_px(TITLE_BAR_Y), cell_to_px(TITLE_BAR_Y + TITLE_H)
    font_title = find_font(max(96, int(CELL * 2.85)), bold=True)
    font_sub = find_sans(max(52, int(CELL * 1.55)), bold=True)
    font_bis = find_sans(max(64, int(CELL * 1.90)), bold=True)
    fonts_t = (font_title, font_sub, font_bis)
    heights = []
    for line, fnt in zip(TITLE_LINES, fonts_t):
        bb = pd.textbbox((0, 0), line, font=fnt)
        heights.append(bb[3] - bb[1])
    gap = max(6, CELL // 8)
    block = sum(heights) + gap * (len(TITLE_LINES) - 1)
    mid = (ty0 + ty1) // 2
    y_cursor = mid - block // 2
    for line, fnt, hh in zip(TITLE_LINES, fonts_t, heights):
        text_centered(pd, line, cx, y_cursor + hh // 2, fnt, BLOCK)
        y_cursor += hh + gap

    day_mid_px = (cell_to_px(days[0]) + cell_to_px(days[-1] + DW)) // 2
    for y_cell, label, multi in (
        (TAGE_BAR_Y, "Tage", False),
        (HMS_BAR_Y, None, True),
    ):
        y0, y1 = cell_to_px(y_cell), cell_to_px(y_cell + LABEL_H)
        mid_y = (y0 + y1) // 2
        if not multi:
            text_centered(pd, label, day_mid_px, mid_y, font_label, BLOCK)
        else:
            pairs = [
                (time_digits[0], time_digits[1] + DW, "Stunden"),
                (time_digits[2], time_digits[3] + DW, "Minuten"),
                (time_digits[4], time_digits[5] + DW, "Sekunden"),
            ]
            for x_a, x_b, name in pairs:
                midx = (cell_to_px(x_a) + cell_to_px(x_b)) // 2
                text_centered(pd, name, midx, mid_y, font_label, BLOCK)

    # Totzone fully opaque (LED dead row on face canvas)
    pd.rectangle([0, ACTIVE_PX, SIZE - 1, SIZE - 1], fill=BLOCK)
    return plate


def add_caption(img: Image.Image, title: str, sub: str) -> Image.Image:
    preview = img.resize((1200, 1200), Image.Resampling.LANCZOS)
    pad = 40
    canvas = Image.new("RGB", (preview.width + pad * 2, preview.height + pad * 2 + 90), (16, 18, 22))
    canvas.paste(preview, (pad, pad + 50))
    d = ImageDraw.Draw(canvas)
    d.text((pad, 14), title, fill=WHITE, font=find_sans(26, bold=True))
    d.text((pad, pad + preview.height + 58), sub, fill=GREY, font=find_sans(16))
    return canvas


def write_print_spec() -> None:
    (OUT / "PRINT_SPEC.md").write_text(
        f"""# Print-Spezifikation — Hotel Anker Countdown (Kendu Flowbox)

## Kanonisches Druckmaß (verbindlich)

| Ebene | Maß |
|-------|-----|
| Spann-/Druck-PDF | **{OUTER_MM:.0f} × {OUTER_MM:.0f} mm** |
| Schwarz unten | **{VISUAL_BOTTOM_DARK_MM:.0f} mm** (= 250 Modul + 50 Stirn) |
| Master | `DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` |

LED-Fläche innen: **{FACE_MM:.0f} × {FACE_MM:.0f} mm** (nicht das Druckformat).

Siehe `Richnerstutz-Bespannung-Paket/02-druckdaten/PRINT_SPEC.md` und `finalize_print_pdfs.py`.
""",
        encoding="utf-8",
    )


def generate_led_preview() -> None:
    """Always refresh Lichtvideo previews alongside print plates."""
    import importlib.util

    led_path = PROJ / "scripts" / "countdown_waves_64.py"
    spec = importlib.util.spec_from_file_location("countdown_waves_64", led_path)
    if spec is None or spec.loader is None:
        print("skip LED preview: cannot load", led_path)
        return
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = ASSETS / "kendu-64x64"
    mod.save_previews(out)
    print("wrote LED preview", out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    ghost = compose(lit=False)
    lit = compose(lit=True)
    opacity = compose_opacity_mask()
    ghost.save(OUT / "print-ghost-hires.png")
    lit.save(OUT / "print-lit-hires.png")
    opacity.save(OUT / "print-opacity-mask-hires.png")
    ghost.resize((2000, 2000), Image.Resampling.LANCZOS).save(OUT / "print-ghost-2000.png")
    lit.resize((2000, 2000), Image.Resampling.LANCZOS).save(OUT / "print-lit-2000.png")
    opacity.resize((2000, 2000), Image.Resampling.NEAREST).save(OUT / "print-opacity-mask-2000.png")
    add_caption(ghost, "Print · Ghost 888", "DSEG7 · liquid glass · historic crown-anchor").save(
        OUT / "preview-ghost.png"
    )
    add_caption(lit, "Print · Lit", "LED gold").save(OUT / "preview-lit.png")
    add_caption(
        opacity, "Print · Blocker", "schwarz=blockt · weiss=leuchtet"
    ).save(OUT / "preview-opacity-mask.png")
    write_print_spec()
    generate_led_preview()
    print("wrote", OUT)
    print(f"layout day={DAY_Y} time={TIME_Y} title={TITLE_BAR_Y} pad-stack centered in {ACTIVE_H}")


if __name__ == "__main__":
    main()
