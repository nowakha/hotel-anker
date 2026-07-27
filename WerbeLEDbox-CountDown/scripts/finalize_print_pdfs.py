#!/usr/bin/env python3
"""Finalize Hotel Anker Flowbox print PDFs.

- Textile production: 2000×2000 mm, solid black totzone 250 mm (no note text)
- Freigabe Maßblatt: 2100×2100 mm with aluminium rim + optical bottom dark 300 mm
"""

from __future__ import annotations

import sys
from pathlib import Path

import img2pdf
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "WerbeLEDbox-CountDown"
ASSETS = ROOT / "assets" / "kendu-flowbox-2m-print"
PKG = ROOT / "Richnerstutz-Bespannung-Paket"
DRUCK = PKG / "02-druckdaten"
OPAZ = PKG / "03-opazitaet"

if str(PROJ) not in sys.path:
    sys.path.insert(0, str(PROJ))

from kendu_flowbox_spec import (  # noqa: E402
    ACTIVE_H_MM,
    DEAD_H_MM,
    FACE_MM,
    OUTER_MM,
    PRINT_SIZE_PX,
    PROFILE_FACE_W_MM,
    VISUAL_BOTTOM_DARK_MM,
    cell_to_print_px,
)
from layout_countdown_view import ACTIVE_H, DEAD_ROWS  # noqa: E402

DEAD_PX = cell_to_print_px(DEAD_ROWS)
ACTIVE_PX = cell_to_print_px(ACTIVE_H)
assert DEAD_PX == 512
assert ACTIVE_PX + DEAD_PX == PRINT_SIZE_PX


def _font(size: int, bold: bool = False):
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/Library/Fonts/Arial.ttf"),
    ]
    for p in candidates:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except OSError:
                continue
    return ImageFont.load_default()


def solidify_totzone(img: Image.Image) -> Image.Image:
    """Force lower DEAD_PX rows to pure black (textile totzone 250 mm)."""
    out = img.convert("RGB").copy()
    d = ImageDraw.Draw(out)
    d.rectangle([0, ACTIVE_PX, out.width - 1, out.height - 1], fill=(0, 0, 0))
    return out


def verify_totzone(img: Image.Image) -> None:
    a = np.asarray(img.convert("RGB"))
    dead = a[ACTIVE_PX:]
    if dead.max() != 0:
        raise SystemExit(f"totzone not solid black: max={dead.max()} mean={dead.mean():.2f}")
    h = a.shape[0]
    mm_h = DEAD_PX * FACE_MM / h
    if abs(mm_h - DEAD_H_MM) > 0.01:
        raise SystemExit(f"totzone height mismatch: {mm_h} mm vs {DEAD_H_MM}")


def png_to_pdf_physical(png: Path, pdf: Path, width_mm: float, height_mm: float) -> None:
    """Embed PNG in a PDF whose MediaBox matches physical mm."""
    layout = img2pdf.get_layout_fun(
        pagesize=(img2pdf.mm_to_pt(width_mm), img2pdf.mm_to_pt(height_mm))
    )
    pdf.write_bytes(img2pdf.convert(str(png), layout_fun=layout))


def build_freigabe_png(sujet: Image.Image, out_png: Path) -> Image.Image:
    """2100×2100 mm preview at 2 px/mm → 4200 px; rim 50 mm = 100 px."""
    px_per_mm = 2.0
    outer_px = int(round(OUTER_MM * px_per_mm))  # 4200
    rim_px = int(round(PROFILE_FACE_W_MM * px_per_mm))  # 100
    face_px = int(round(FACE_MM * px_per_mm))  # 4000
    dead_px = int(round(DEAD_H_MM * px_per_mm))  # 500
    visual_px = int(round(VISUAL_BOTTOM_DARK_MM * px_per_mm))  # 600

    canvas_im = Image.new("RGB", (outer_px, outer_px), (168, 172, 178))  # alu rim
    face = sujet.convert("RGB").resize((face_px, face_px), Image.Resampling.LANCZOS)
    canvas_im.paste(face, (rim_px, rim_px))

    # Dimension overlay strip on the right / bottom (outside content readability)
    overlay = Image.new("RGBA", (outer_px, outer_px), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    font = _font(36, bold=True)
    font_sm = _font(28, bold=True)
    red = (200, 40, 40, 230)
    dark = (20, 20, 24, 240)

    # Outer box outline
    od.rectangle([1, 1, outer_px - 2, outer_px - 2], outline=red, width=4)
    # Face inner outline
    od.rectangle(
        [rim_px, rim_px, rim_px + face_px - 1, rim_px + face_px - 1],
        outline=(40, 120, 220, 220),
        width=3,
    )
    # Textile totzone band (inside face)
    tz_y0 = rim_px + face_px - dead_px
    od.rectangle(
        [rim_px, tz_y0, rim_px + face_px - 1, rim_px + face_px - 1],
        outline=(255, 200, 40, 220),
        width=3,
    )
    # Optical bottom dark (textile totzone + bottom rim)
    od.rectangle(
        [rim_px, tz_y0, rim_px + face_px - 1, outer_px - 1],
        outline=(255, 80, 80, 200),
        width=4,
    )

    labels = [
        (24, 24, f"Aussen {OUTER_MM:.0f} x {OUTER_MM:.0f} mm"),
        (24, 70, f"Textil/LED-Flaeche {FACE_MM:.0f} x {FACE_MM:.0f} mm"),
        (24, 116, f"Stirn Profil {PROFILE_FACE_W_MM:.0f} mm umlaufend"),
        (24, 162, f"Totzone Textil {DEAD_H_MM:.0f} mm (8/64)"),
        (24, 208, f"OPTISCH unten dunkel {VISUAL_BOTTOM_DARK_MM:.0f} mm = {DEAD_H_MM:.0f}+{PROFILE_FACE_W_MM:.0f}"),
        (24, 254, f"Aktiv {ACTIVE_H_MM:.0f} mm (7 Modulreihen)"),
    ]
    for x, y, text in labels:
        od.rectangle([x - 8, y - 6, x + 980, y + 40], fill=(255, 255, 255, 210))
        od.text((x, y), text, font=font_sm, fill=dark)

    # Bottom callout
    call = f"Schwarz Textil {DEAD_H_MM:.0f} mm  |  + Alu-Stirn {PROFILE_FACE_W_MM:.0f} mm  =>  optisch {VISUAL_BOTTOM_DARK_MM:.0f} mm"
    od.rectangle([rim_px + 40, outer_px - 70, outer_px - 40, outer_px - 20], fill=(255, 255, 255, 230))
    od.text((rim_px + 56, outer_px - 60), call, font=font, fill=red)

    out = Image.alpha_composite(canvas_im.convert("RGBA"), overlay).convert("RGB")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    out.save(out_png)
    # sanity
    assert abs(visual_px - (dead_px + rim_px)) < 1
    return out


def write_print_spec() -> None:
    text = f"""# Print-Spezifikation — Hotel Anker Countdown

## Zwei Maßsysteme (nicht vermischen)

| Ebene | Maß | Schwarz unten |
|-------|-----|----------------|
| **Außenrahmen** (Freigabe / Einbau) | **{OUTER_MM:.0f} × {OUTER_MM:.0f} mm** | **optisch {VISUAL_BOTTOM_DARK_MM:.0f} mm** = Totzone Textil {DEAD_H_MM:.0f} + Stirn {PROFILE_FACE_W_MM:.0f} |
| **Drucktextil an Richnerstutz** | **{FACE_MM:.0f} × {FACE_MM:.0f} mm** | **{DEAD_H_MM:.0f} mm** (= 1 Modulreihe / 8/64). Stirn ist Aluminium — nicht mitdrucken. |

## Physik (gemessen)
- Druck-/LED-Fläche: **{FACE_MM:.0f} × {FACE_MM:.0f} mm** (8×8 Panels à **250 × 250 mm**)
- Profil-Stirnbreite (XY): **{PROFILE_FACE_W_MM:.0f} mm**
- Außenmaß Rahmen: **{OUTER_MM:.0f} × {OUTER_MM:.0f} mm** (= {FACE_MM:.0f} + 2×{PROFILE_FACE_W_MM:.0f})
- Innen Textil→LED (Z): **45 mm** (Zollstock)
- Content-Grid: **64 × 64** → Zellpitch **31.25 mm**
- Totzone Textil: untere **{DEAD_ROWS}/64** Zellen (= **{DEAD_H_MM:.0f} mm**)
- Optisch unten dunkel (Einbau): **{VISUAL_BOTTOM_DARK_MM:.0f} mm**

Stack vorne→hinten: SEG-Textil in Kedernut → Diffusion **45 mm** → LED-Panels → Rückwand/Controller  
Details: `Richnerstutz-Bespannung-Paket/06-fotos-vom-rahmen/GEOMETRIE-3D.md`

## Lieferdateien (Produktion)
- `DRUCK-Hotel-Anker-Flowbox-2000x2000.pdf` — MediaBox **{FACE_MM:.0f}×{FACE_MM:.0f} mm**, Totzone deckend schwarz {DEAD_H_MM:.0f} mm
- `DRUCK-Opazitaet-2000x2000.pdf` — gleiche Größe; schwarz=lichtdurchlässig, rot=Blockout
- `FREIGABE-Massblatt-2100.pdf` — MediaBox **{OUTER_MM:.0f}×{OUTER_MM:.0f} mm**, Bemaßung inkl. optisch {VISUAL_BOTTOM_DARK_MM:.0f} mm

## Raster / PNG-Master
- `print-ghost-hires.png` · **{PRINT_SIZE_PX}×{PRINT_SIZE_PX} px** · 2.048 px/mm · **64 px/Zelle**
- Totzone ab Pixelzeile {ACTIVE_PX} (= {ACTIVE_H}/64) — **rein schwarz**, kein Hinweistext

## Ziel
- Countdown endet **1. Oktober 2026, 13:00 Europe/Zurich** (nur live; Print zeigt „Zeit bis Baubeginn:“)
- Logo: historischer Kronen-Anker (Fassadenmarke Hotel Anker Rorschach)

## Opazitätsplatte
- **schwarz** = lichtdurchlässig · **rot** = lichtundurchlässig
- Rot: Totzone · Logo · Beschriftung · Fassadenlinien · DSEG7-Konturen / Colon-Ringe
- Schwarz: Liquid-Glass-Balken · DSEG7-Segmentfüllungen / Colon-Kerne · Navy-Hintergrund
"""
    for dest in (DRUCK / "PRINT_SPEC.md", ASSETS / "PRINT_SPEC.md"):
        dest.write_text(text, encoding="utf-8")


def main() -> None:
    DRUCK.mkdir(parents=True, exist_ok=True)
    OPAZ.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    ghost_src = ASSETS / "print-ghost-hires.png"
    lit_src = ASSETS / "print-lit-hires.png"
    op_src = ASSETS / "print-opacity-mask-hires.png"
    if not ghost_src.exists():
        raise SystemExit(f"missing {ghost_src}")

    ghost = solidify_totzone(Image.open(ghost_src))
    verify_totzone(ghost)
    lit = solidify_totzone(Image.open(lit_src)) if lit_src.exists() else None
    opacity = Image.open(op_src).convert("RGB") if op_src.exists() else None
    if opacity is not None:
        # Keep totzone fully blockout red
        od = ImageDraw.Draw(opacity)
        od.rectangle([0, ACTIVE_PX, opacity.width - 1, opacity.height - 1], fill=(220, 24, 24))

    # Write master PNGs
    for dest_dir in (ASSETS, DRUCK):
        ghost.save(dest_dir / "print-ghost-hires.png")
        ghost.resize((2000, 2000), Image.Resampling.LANCZOS).save(dest_dir / "print-ghost-2000.png")
        if lit is not None:
            lit.save(dest_dir / "print-lit-hires.png")
            lit.resize((2000, 2000), Image.Resampling.LANCZOS).save(dest_dir / "print-lit-2000.png")
    if opacity is not None:
        opacity.save(ASSETS / "print-opacity-mask-hires.png")
        opacity.resize((2000, 2000), Image.Resampling.NEAREST).save(ASSETS / "print-opacity-mask-2000.png")
        opacity.save(OPAZ / "print-opacity-mask-hires.png")
        opacity.resize((2000, 2000), Image.Resampling.NEAREST).save(OPAZ / "print-opacity-mask-2000.png")

    # Production PDFs (physical mm)
    tmp_ghost = DRUCK / "_tmp_ghost_4096.png"
    ghost.save(tmp_ghost)
    png_to_pdf_physical(tmp_ghost, DRUCK / "DRUCK-Hotel-Anker-Flowbox-2000x2000.pdf", FACE_MM, FACE_MM)
    tmp_ghost.unlink(missing_ok=True)

    if opacity is not None:
        tmp_op = OPAZ / "_tmp_opacity_4096.png"
        opacity.save(tmp_op)
        png_to_pdf_physical(tmp_op, OPAZ / "DRUCK-Opazitaet-2000x2000.pdf", FACE_MM, FACE_MM)
        # also copy into druckdaten for one-folder send
        png_to_pdf_physical(tmp_op, DRUCK / "DRUCK-Opazitaet-2000x2000.pdf", FACE_MM, FACE_MM)
        tmp_op.unlink(missing_ok=True)

    # Freigabe Maßblatt 2100
    freigabe_png = DRUCK / "FREIGABE-Massblatt-2100.png"
    build_freigabe_png(ghost, freigabe_png)
    png_to_pdf_physical(freigabe_png, DRUCK / "FREIGABE-Massblatt-2100.pdf", OUTER_MM, OUTER_MM)

    write_print_spec()

    # Verify PDF page sizes (points)
    from pypdf import PdfReader  # optional

    try:
        for path, expect_mm in (
            (DRUCK / "DRUCK-Hotel-Anker-Flowbox-2000x2000.pdf", FACE_MM),
            (DRUCK / "FREIGABE-Massblatt-2100.pdf", OUTER_MM),
        ):
            page = PdfReader(str(path)).pages[0]
            w_pt = float(page.mediabox.width)
            h_pt = float(page.mediabox.height)
            w_mm = w_pt * 25.4 / 72
            h_mm = h_pt * 25.4 / 72
            print(f"{path.name}: {w_mm:.2f} x {h_mm:.2f} mm (expect {expect_mm})")
            if abs(w_mm - expect_mm) > 0.5 or abs(h_mm - expect_mm) > 0.5:
                raise SystemExit(f"PDF size mismatch for {path}")
    except ImportError:
        # fallback: reportlab/img2pdf already set pagesize; spot-check via img2pdf math
        print("pypdf not installed — skipping PDF mediabox assert")

    print("OK totzone", DEAD_H_MM, "mm textile / visual", VISUAL_BOTTOM_DARK_MM, "mm")
    print("wrote", DRUCK)


if __name__ == "__main__":
    main()
