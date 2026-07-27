#!/usr/bin/env python3
"""Verify / refresh Hotel Anker Flowbox print masters (2100×2100 mm).

Canonical production PDF: DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf
- MediaBox 2100×2100 mm
- Bottom solid black ≈ 300 mm (250 module + 50 face rim)
"""

from __future__ import annotations

import sys
from pathlib import Path

import img2pdf
import numpy as np
from PIL import Image, ImageDraw
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
PROJ = ROOT / "WerbeLEDbox-CountDown"
DRUCK = ROOT / "Richnerstutz-Bespannung-Paket" / "02-druckdaten"
OPAZ = ROOT / "Richnerstutz-Bespannung-Paket" / "03-opazitaet"
ASSETS = ROOT / "assets" / "kendu-flowbox-2m-print"

if str(PROJ) not in sys.path:
    sys.path.insert(0, str(PROJ))

from kendu_flowbox_spec import (  # noqa: E402
    FACE_MM,
    OUTER_MM,
    PRINT_DEAD_MM,
    PRINT_DEAD_PX,
    PRINT_MASTER_PX,
    PRINT_MM,
    PROFILE_FACE_W_MM,
)


def pdf_mm(path: Path) -> tuple[float, float]:
    page = PdfReader(str(path)).pages[0]
    w = float(page.mediabox.width) * 25.4 / 72
    h = float(page.mediabox.height) * 25.4 / 72
    return w, h


def measure_bottom_black_mm(img: Image.Image, page_mm: float = PRINT_MM) -> float:
    a = np.asarray(img.convert("RGB"))
    h = a.shape[0]
    lum = a.mean(axis=(1, 2))
    n = 0
    for y in range(h - 1, -1, -1):
        if lum[y] <= 20:
            n += 1
        else:
            break
    return n * page_mm / h


def ensure_opacity_2100(ghost: Image.Image) -> Image.Image:
    """Opacity plate at master resolution; bottom PRINT_DEAD_MM = red blockout."""
    RED = (220, 24, 24)
    size = ghost.size[0]
    op_path = ASSETS / "print-opacity-mask-hires.png"
    if op_path.exists():
        op = Image.open(op_path).convert("RGB").resize((size, size), Image.Resampling.NEAREST)
    else:
        op = Image.new("RGB", (size, size), (0, 0, 0))
    dead_px = int(round(PRINT_DEAD_MM / PRINT_MM * size))
    arr = np.asarray(op).copy()
    arr[-dead_px:] = RED
    return Image.fromarray(arr)


def write_print_spec() -> None:
    text = f"""# Print-Spezifikation — Hotel Anker Countdown

## Kanonisches Druckmaß (verbindlich)

| Angabe | Wert |
|--------|------|
| **Spann-/Druck-PDF** | **{PRINT_MM:.0f} × {PRINT_MM:.0f} mm** (= Außenmaß Rahmen) |
| **Schwarzstreifen unten** | **{PRINT_DEAD_MM:.0f} mm** (= {FACE_MM/8:.0f} Modulreihe + {PROFILE_FACE_W_MM:.0f} Stirn) |
| Master-Datei | `DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` |
| PNG-Master | `print-ghost-hires.png` · **{PRINT_MASTER_PX}×{PRINT_MASTER_PX} px** · 2 px/mm |

**Widerruf:** Frühere 2000×2000‑mm‑Produktion mit nur 250 mm Totzone war **falsch**.

## LED-Physik (nicht das Druckformat)

- LED-Fläche: **{FACE_MM:.0f} × {FACE_MM:.0f} mm** (8×8 × 250 mm)
- Stirn: **{PROFILE_FACE_W_MM:.0f} mm** → Außen **{OUTER_MM:.0f} × {OUTER_MM:.0f} mm**
- Content-Grid live: 64×64, Totzone LED = unterste 8/64 (= 250 mm Module)

## Lieferdateien

- `DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` — Produktion
- `DRUCK-Opazitaet-2100x2100.pdf` — schwarz=lichtdurchlässig, rot=Blockout (Totzone {PRINT_DEAD_MM:.0f} mm)
- `print-ghost-hires.pdf` — Alias des Masters

## Opazität

- Rot: Totzone {PRINT_DEAD_MM:.0f} mm · Logo · Beschriftung · Fassadenlinien · Digit-Konturen
- Schwarz: Glass-Balken · Segmentfüllungen · Navy-Hintergrund
"""
    for dest in (DRUCK / "PRINT_SPEC.md", ASSETS / "PRINT_SPEC.md"):
        dest.write_text(text, encoding="utf-8")


def main() -> None:
    master = DRUCK / "DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf"
    if not master.exists():
        raise SystemExit(f"missing {master}")
    w, h = pdf_mm(master)
    print(f"master PDF {w:.2f}×{h:.2f} mm")
    if abs(w - PRINT_MM) > 1 or abs(h - PRINT_MM) > 1:
        raise SystemExit("PDF is not 2100 mm")

    ghost = Image.open(DRUCK / "print-ghost-hires.png").convert("RGB")
    black_mm = measure_bottom_black_mm(ghost, PRINT_MM)
    print(f"ghost PNG {ghost.size}, bottom black ≈ {black_mm:.1f} mm")
    if abs(black_mm - PRINT_DEAD_MM) > 2:
        raise SystemExit(f"expected ~{PRINT_DEAD_MM} mm black, got {black_mm}")

    op = ensure_opacity_2100(ghost)
    for d in (DRUCK, OPAZ, ASSETS):
        op.save(d / "print-opacity-mask-hires.png")
        op.resize((2100, 2100), Image.Resampling.NEAREST).save(d / "print-opacity-mask-2100.png")

    tmp = OPAZ / "_tmp_op.png"
    op.save(tmp)
    layout = img2pdf.get_layout_fun(
        pagesize=(img2pdf.mm_to_pt(PRINT_MM), img2pdf.mm_to_pt(PRINT_MM))
    )
    data = img2pdf.convert(str(tmp), layout_fun=layout)
    (OPAZ / "DRUCK-Opazitaet-2100x2100.pdf").write_bytes(data)
    (DRUCK / "DRUCK-Opazitaet-2100x2100.pdf").write_bytes(data)
    tmp.unlink(missing_ok=True)

    write_print_spec()
    print("OK 2100/300 print master verified")


if __name__ == "__main__":
    main()
