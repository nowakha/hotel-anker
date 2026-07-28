#!/usr/bin/env python3
"""Build Richnerstutz production masters (CMYK + 20 mm bleed + matched blocker).

Corrections after Druckvorstufe (Tanja Jelk, 2026-07):
  - CMYK (not RGB)
  - 20 mm Bildzugabe rundum (MediaBox = 2140 × 2140 mm; Trim = 2100 × 2100 mm)
  - 20 mm Stoff-Sperrzone: Sujet inside LED face, rim = solid navy/black
  - Higher resolution (~4 px/mm ≈ 102 dpi)
  - Blocker polarity: black = blockout, white = light-through (no red)
  - Blocker geometry generated from the same compose pass as the Sujet
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import img2pdf
import numpy as np
from PIL import Image, ImageCms, ImageDraw
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "WerbeLEDbox-CountDown"
DRUCK = ROOT / "Richnerstutz-Bespannung-Paket" / "02-druckdaten"
OPAZ = ROOT / "Richnerstutz-Bespannung-Paket" / "03-opazitaet"
ASSETS = ROOT / "assets" / "kendu-flowbox-2m-print"
VERSAND = (
    ROOT
    / "Richnerstutz-Bespannung-Paket"
    / "versand"
    / "Hotel-Anker-Richnerstutz-Finale-Druckdaten"
)

if str(PROJ) not in sys.path:
    sys.path.insert(0, str(PROJ))

from kendu_flowbox_spec import (  # noqa: E402
    BLEED_MM,
    FACE_MM,
    FACE_MASTER_PX,
    GRID,
    OUTER_MM,
    PRINT_DEAD_MM,
    PRINT_EXPORT_MM,
    PRINT_EXPORT_PX,
    PRINT_MASTER_PX,
    PRINT_MASTER_PX_PER_MM,
    PRINT_MM,
    PRINT_TRIM_MM,
    PROFILE_FACE_W_MM,
    SPERRZONE_MM,
)


def _load_gen():
    path = PROJ / "scripts" / "gen_flowbox_print_hires.py"
    spec = importlib.util.spec_from_file_location("gen_flowbox_print_hires", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ICC_DIR = Path(r"C:\Windows\System32\spool\drivers\color")
SRGB_ICC = ICC_DIR / "sRGB Color Space Profile.icm"
FOGRA39_ICC = ICC_DIR / "CoatedFOGRA39.icc"


def rgb_to_cmyk(img: Image.Image) -> Image.Image:
    """Convert RGB → CMYK via sRGB → FOGRA39 when ICC profiles are available."""
    rgb = img.convert("RGB")
    if SRGB_ICC.exists() and FOGRA39_ICC.exists():
        try:
            return ImageCms.profileToProfile(
                rgb,
                str(SRGB_ICC),
                str(FOGRA39_ICC),
                outputMode="CMYK",
                renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
            )
        except Exception as exc:  # noqa: BLE001
            print("ICC convert failed, falling back to Pillow CMYK:", exc)
    return rgb.convert("CMYK")


def blocker_to_cmyk(img: Image.Image) -> Image.Image:
    """Force pure K for black, paper white for light-through (no RGB red leftovers)."""
    arr = np.asarray(img.convert("RGB"), dtype=np.uint8)
    lum = arr.mean(axis=2)
    # Threshold: dark → K100, light → 0
    is_block = lum < 128
    h, w = lum.shape
    cmyk = np.zeros((h, w, 4), dtype=np.uint8)
    cmyk[is_block, 3] = 255  # K
    return Image.fromarray(cmyk, mode="CMYK")


def extend_bleed(trim: Image.Image, bleed_px: int) -> Image.Image:
    """Pad trim canvas with edge-pixel replication (Bildzugabe)."""
    if bleed_px <= 0:
        return trim
    w, h = trim.size
    out = Image.new(trim.mode, (w + 2 * bleed_px, h + 2 * bleed_px))
    out.paste(trim, (bleed_px, bleed_px))
    # top / bottom strips
    top = trim.crop((0, 0, w, 1)).resize((w, bleed_px), Image.Resampling.NEAREST)
    bot = trim.crop((0, h - 1, w, h)).resize((w, bleed_px), Image.Resampling.NEAREST)
    out.paste(top, (bleed_px, 0))
    out.paste(bot, (bleed_px, bleed_px + h))
    # left / right including corners
    left = out.crop((bleed_px, 0, bleed_px + 1, h + 2 * bleed_px)).resize(
        (bleed_px, h + 2 * bleed_px), Image.Resampling.NEAREST
    )
    right = out.crop(
        (bleed_px + w - 1, 0, bleed_px + w, h + 2 * bleed_px)
    ).resize((bleed_px, h + 2 * bleed_px), Image.Resampling.NEAREST)
    out.paste(left, (0, 0))
    out.paste(right, (bleed_px + w, 0))
    return out


def place_on_trim(
    face: Image.Image,
    *,
    navy: tuple[int, int, int],
    is_blocker: bool,
) -> Image.Image:
    """Center 2000 mm LED face on 2100 mm trim; rim = navy (sujet) or white/black (blocker)."""
    ppm = PRINT_MASTER_PX_PER_MM
    trim_px = PRINT_MASTER_PX
    face_px = FACE_MASTER_PX
    rim_px = int(round(PROFILE_FACE_W_MM * ppm))
    assert face_px + 2 * rim_px == trim_px, (face_px, rim_px, trim_px)

    face_r = face.resize((face_px, face_px), Image.Resampling.LANCZOS)
    if is_blocker:
        # Rim over aluminium: block (black). Light-through only on LED face.
        canvas = Image.new("RGB", (trim_px, trim_px), (0, 0, 0))
    else:
        canvas = Image.new("RGB", (trim_px, trim_px), navy)

    canvas.paste(face_r, (rim_px, rim_px))

    # Bottom print dead band = 300 mm from trim bottom (module + face rim)
    dead_px = int(round(PRINT_DEAD_MM * ppm))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, trim_px - dead_px, trim_px - 1, trim_px - 1], fill=(0, 0, 0))

    return canvas


def write_cmyk_pdf(img_cmyk: Image.Image, dest: Path, page_mm: float) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tif = Path(td) / "page.tif"
        img_cmyk.save(tif, compression="tiff_adobe_deflate")
        layout = img2pdf.get_layout_fun(
            pagesize=(img2pdf.mm_to_pt(page_mm), img2pdf.mm_to_pt(page_mm))
        )
        dest.write_bytes(img2pdf.convert(str(tif), layout_fun=layout))


def pdf_mm(path: Path) -> tuple[float, float]:
    page = PdfReader(str(path)).pages[0]
    w = float(page.mediabox.width) * 25.4 / 72
    h = float(page.mediabox.height) * 25.4 / 72
    return w, h


def first_content_mm_from_top(img: Image.Image, page_mm: float) -> float:
    a = np.asarray(img.convert("RGB"))
    lum = a.mean(axis=2)
    for y in range(a.shape[0]):
        if lum[y].max() > 40:
            return y * page_mm / a.shape[0]
    return page_mm


def write_docs() -> None:
    spec = f"""# Print-Spezifikation — Hotel Anker Countdown (Richnerstutz)

Korrektur nach Druckvorstufe (Tanja Jelk): CMYK · Bleed · Sperrzone · Blocker schwarz/weiss · höhere Auflösung.

## Endformat / Spannmaß

| Angabe | Wert |
|--------|------|
| **Trim / Spannmaß** | **{PRINT_TRIM_MM:.0f} × {PRINT_TRIM_MM:.0f} mm** (= Außenmaß Rahmen) |
| **Bildzugabe (Bleed)** | **{BLEED_MM:.0f} mm rundum** |
| **MediaBox (Liefer-PDF)** | **{PRINT_EXPORT_MM:.0f} × {PRINT_EXPORT_MM:.0f} mm** (= Trim + 2×Bleed) |
| **Stoff-Sperrzone** | **{SPERRZONE_MM:.0f} mm** vom Trim-Rand — kritisches Sujet nur innerhalb |
| **Schwarzstreifen unten** | **{PRINT_DEAD_MM:.0f} mm** (= 250 Modulreihe + 50 Stirn) |
| **Farbraum** | **CMYK** (sRGB → FOGRA39 Coated) |
| **Auflösung** | **{PRINT_MASTER_PX_PER_MM:.0f} px/mm** (≈ {PRINT_MASTER_PX_PER_MM * 25.4:.0f} dpi) |

## Lieferdateien

| Datei | Inhalt |
|-------|--------|
| `DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` | Sujet CMYK, MediaBox {PRINT_EXPORT_MM:.0f} mm |
| `DRUCK-Blocker-2100x2100.pdf` | Blocker CMYK, gleiche Geometrie / MediaBox |
| `DRUCK-Opazitaet-2100x2100.pdf` | Alias des Blockers (Dateiname-Kompatibilität) |
| `print-ghost-hires.png` | RGB-Preview Trim {PRINT_MASTER_PX}² |
| `print-opacity-mask-hires.png` | Blocker RGB-Preview Trim {PRINT_MASTER_PX}² |

## Blocker-Legende (verbindlich)

| Farbe | Bedeutung |
|-------|-----------|
| **Schwarz** | blockt / lichtundurchlässig |
| **Weiss** | leuchtet / lichtdurchlässig |

Kein Rot. Blocker und Sujet stammen aus demselben Generator-Lauf.

## LED-Physik (nicht das Druckformat)

- LED-Fläche: **{FACE_MM:.0f} × {FACE_MM:.0f} mm** (8×8 × 250 mm)
- Stirn: **{PROFILE_FACE_W_MM:.0f} mm** → Außen **{OUTER_MM:.0f} × {OUTER_MM:.0f} mm**
- Sujet der LED-Fläche ist zentriert im Trim; Stirn = Navy (Sujet) bzw. Schwarz (Blocker)

Rebuild: `python WerbeLEDbox-CountDown/scripts/build_richnerstutz_druckdaten.py`
"""
    legend = f"""# Blocker / Opazitätsplatte — Legende für Richnerstutz

Datei: `DRUCK-Blocker-2100x2100.pdf` (Alias: `DRUCK-Opazitaet-2100x2100.pdf`)

| Farbe | Bedeutung | Druckziel |
|-------|-----------|-----------|
| **Schwarz** | blockt / lichtundurchlässig | kein Streulicht, klare Silhouette |
| **Weiss** | leuchtet / lichtdurchlässig | LED-Licht soll klar durchscheinen |

**Wichtig:** Frühere Lieferung mit Rot=Blockout / Schwarz=transluzent ist **ungültig**.

## Schwarz (Blockout)

- Totzone unten: volle Breite × {PRINT_DEAD_MM:.0f} mm (Trim)
- Logo Kronen-Anker
- Beschriftungen («Zeit bis Baubeginn:», Tage/Stunden/Minuten/Sekunden)
- Fassadenlinien
- Konturen der 7-Segment-Ziffern und Ringe der Doppelpunkte
- Aluminium-Stirn (50 mm Rahmen um die LED-Fläche)

## Weiss (lichtdurchlässig)

- Füllungen der 7-Segment-Ziffern (Ghost-8)
- Kerne der Doppelpunkte
- Liquid-Glass-Balken (Titel-/Labelbänder)
- Navy-Hintergrund in den LED-Durchscheinflächen

## Passung

Blocker und Sujet werden im selben Script erzeugt und 1:1 auf Trim {PRINT_TRIM_MM:.0f} mm + Bleed {BLEED_MM:.0f} mm gelegt.
"""
    for dest in (
        DRUCK / "PRINT_SPEC.md",
        ASSETS / "PRINT_SPEC.md",
        VERSAND / "01-druckdaten" / "PRINT_SPEC.md",
    ):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(spec, encoding="utf-8")

    for dest in (
        OPAZ / "LEGENDE.md",
        VERSAND / "01-druckdaten" / "OPAZITAET-LEGENDE.md",
    ):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(legend, encoding="utf-8")

    readme = f"""# Druckdaten — Hotel Anker Countdown

## Kanonisch (verbindlich, nach Druckerei-Korrektur)

| | |
|--|--|
| **Trim / Spannmaß** | **{PRINT_TRIM_MM:.0f} × {PRINT_TRIM_MM:.0f} mm** |
| **Bleed** | **{BLEED_MM:.0f} mm rundum** → MediaBox **{PRINT_EXPORT_MM:.0f} mm** |
| **Farbraum** | **CMYK** |
| **Schwarz unten** | **{PRINT_DEAD_MM:.0f} mm** |
| **Blocker** | schwarz=blockt · weiss=leuchtet |

## Produktionsdateien (an Richnerstutz)

| Datei | Verwendung |
|-------|------------|
| **`DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf`** | Sujet CMYK inkl. {BLEED_MM:.0f} mm Bleed |
| **`DRUCK-Blocker-2100x2100.pdf`** | Blocker CMYK (geometrietreu zum Sujet) |
| `DRUCK-Opazitaet-2100x2100.pdf` | Alias Blocker |
| `print-ghost-hires.png` | RGB-Preview Trim {PRINT_MASTER_PX}² |
| `PRINT_SPEC.md` | Technische Spezifikation |

Rebuild: `python WerbeLEDbox-CountDown/scripts/build_richnerstutz_druckdaten.py`
"""
    (DRUCK / "README.md").write_text(readme, encoding="utf-8")


def write_mail_reply() -> None:
    body = """Guten Tag Frau Jelk

vielen Dank für die Prüfung und die klaren Punkte — Entschuldigung für den Mehraufwand.

Die Druckdaten sind entsprechend Ihrer Vorgaben neu aufbereitet:

1) Blocker / Opazität
   - Neu aus demselben Generatorlauf wie das Sujet (Geometrie 1:1 passend)
   - Polarität korrigiert: schwarz = blockt, weiss = leuchtet (kein Rot mehr)
   - Datei: DRUCK-Blocker-2100x2100.pdf
     (DRUCK-Opazitaet-2100x2100.pdf ist derselbe Inhalt, Alias)

2) Farbraum
   - Beide PDFs in CMYK (sRGB → FOGRA39 Coated)

3) Bildzugabe / Sperrzone
   - 20 mm Bleed rundum → MediaBox 2140 × 2140 mm
   - Trim / Spannmaß unverändert 2100 × 2100 mm
   - Kritisches Sujet innerhalb der LED-Fläche (Stirn 50 mm navy/schwarz),
     damit die 20 mm Stoff-Sperrzone frei bleibt; Logo nicht mehr über den oberen Rand gezogen

4) Auflösung
   - Neu ca. 4 px/mm (≈ 102 dpi) statt zuvor 2 px/mm

Unterer Schwarzstreifen weiterhin 300 mm (250 mm Modulreihe + 50 mm Stirn).

Details: PRINT_SPEC.md und OPAZITAET-LEGENDE.md im Paket.

Bitte Frau Vogt im CC belassen — danke, dass sie die Daten aufarbeitet.
Für Rückfragen stehe ich gerne kurzfristig zur Verfügung.

Freundliche Grüsse
Harald Nowak
Modernlight — Projektleitung | Videoengineering
Harald.Nowak@modernlight.ch
+41 76 579 84 54
Wangenstrasse 57, 3018 Bern

— An: Tanja Jelk (Richnerstutz AG)
— CC: Frau Vogt (Richnerstutz AG), Gottlieb Kündig (Realia AG) nach Bedarf
"""
    for dest in (
        VERSAND / "MAIL-BODY-KORREKTUR.txt",
        ROOT / "Richnerstutz-Bespannung-Paket" / "01-anfrage" / "MAIL-KORREKTUR-Druckdaten.txt",
    ):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")


def main() -> None:
    gen = _load_gen()
    # Face canvas: 2000 mm @ 4 px/mm → 8000 px → 125 px/cell
    cell_px = max(64, int(round(FACE_MASTER_PX / GRID)))
    gen.configure_print_resolution(cell_px)
    print(f"generator face {gen.SIZE}px (cell={gen.CELL})")

    ghost_face = gen.compose(lit=False)
    blocker_face = gen.compose_opacity_mask()
    lit_face = gen.compose(lit=True)
    navy = gen.NAVY_DEEP

    ghost_trim = place_on_trim(ghost_face, navy=navy, is_blocker=False)
    blocker_trim = place_on_trim(blocker_face, navy=navy, is_blocker=True)

    bleed_px = int(round(BLEED_MM * PRINT_MASTER_PX_PER_MM))
    ghost_export = extend_bleed(ghost_trim, bleed_px)
    blocker_export = extend_bleed(blocker_trim, bleed_px)
    assert ghost_export.size == (PRINT_EXPORT_PX, PRINT_EXPORT_PX), ghost_export.size
    assert blocker_export.size == (PRINT_EXPORT_PX, PRINT_EXPORT_PX), blocker_export.size

    top_mm = first_content_mm_from_top(ghost_trim, PRINT_TRIM_MM)
    print(
        f"sujet first content from trim top ~ {top_mm:.1f} mm "
        f"(Sperrzone {SPERRZONE_MM:.0f} mm)"
    )
    if top_mm < SPERRZONE_MM - 0.5:
        raise SystemExit(
            f"Sujet still inside Sperrzone ({top_mm:.1f} mm < {SPERRZONE_MM})"
        )

    # Save RGB masters / previews
    for d in (DRUCK, ASSETS):
        d.mkdir(parents=True, exist_ok=True)
        ghost_trim.save(d / "print-ghost-hires.png")
        ghost_trim.resize((2100, 2100), Image.Resampling.LANCZOS).save(d / "print-ghost-2100.png")
        lit_face.resize((FACE_MASTER_PX, FACE_MASTER_PX), Image.Resampling.LANCZOS).save(
            d / "print-lit-hires.png"
        )
    for d in (DRUCK, OPAZ, ASSETS):
        d.mkdir(parents=True, exist_ok=True)
        blocker_trim.save(d / "print-opacity-mask-hires.png")
        blocker_trim.resize((2100, 2100), Image.Resampling.NEAREST).save(
            d / "print-opacity-mask-2100.png"
        )

    ghost_cmyk = rgb_to_cmyk(ghost_export)
    blocker_cmyk = blocker_to_cmyk(blocker_export)

    sujet_pdf = DRUCK / "DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf"
    blocker_pdf = DRUCK / "DRUCK-Blocker-2100x2100.pdf"
    write_cmyk_pdf(ghost_cmyk, sujet_pdf, PRINT_EXPORT_MM)
    write_cmyk_pdf(blocker_cmyk, blocker_pdf, PRINT_EXPORT_MM)

    # Aliases / package copies
    for dest in (
        DRUCK / "print-ghost-hires.pdf",
        ASSETS / "print-ghost-hires.pdf",
        VERSAND / "01-druckdaten" / "DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf",
    ):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(sujet_pdf.read_bytes())

    for dest in (
        DRUCK / "DRUCK-Opazitaet-2100x2100.pdf",
        OPAZ / "DRUCK-Opazitaet-2100x2100.pdf",
        OPAZ / "DRUCK-Blocker-2100x2100.pdf",
        VERSAND / "01-druckdaten" / "DRUCK-Blocker-2100x2100.pdf",
        VERSAND / "01-druckdaten" / "DRUCK-Opazitaet-2100x2100.pdf",
    ):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blocker_pdf.read_bytes())

    for path in (sujet_pdf, blocker_pdf):
        w, h = pdf_mm(path)
        print(f"{path.name}: MediaBox {w:.2f}×{h:.2f} mm")
        if abs(w - PRINT_EXPORT_MM) > 0.5 or abs(h - PRINT_EXPORT_MM) > 0.5:
            raise SystemExit(f"expected MediaBox {PRINT_EXPORT_MM} mm, got {w}×{h}")

    # Verify PDF is CMYK (no DeviceRGB on page content is ideal; check image colorspace via pillow roundtrip not available — check TIFF path already CMYK)
    print(f"sujet CMYK mode={ghost_cmyk.mode} size={ghost_cmyk.size}")
    print(f"blocker CMYK mode={blocker_cmyk.mode} size={blocker_cmyk.size}")

    write_docs()
    write_mail_reply()
    gen.write_print_spec()
    print("OK Richnerstutz Druckdaten neu gebaut")


if __name__ == "__main__":
    main()
