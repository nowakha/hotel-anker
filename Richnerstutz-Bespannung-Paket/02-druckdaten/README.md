# Druckdaten — Hotel Anker Countdown

## Zwei Maßsysteme (nicht vermischen)

| Ebene | Maß | Schwarz unten |
|-------|-----|----------------|
| **Außen / Freigabe** | 2100 × 2100 mm | **optisch 300 mm** (= 250 Textil + 50 Stirn) |
| **Drucktextil Richnerstutz** | 2000 × 2000 mm | **250 mm** (eine Modulreihe; Stirn = Alu, nicht drucken) |

## Produktionsdateien (an Richnerstutz)

| Datei | Verwendung |
|-------|------------|
| **`DRUCK-Hotel-Anker-Flowbox-2000x2000.pdf`** | **Haupt-Druck-PDF** — MediaBox exakt 2000×2000 mm, Totzone deckend schwarz 250 mm |
| **`DRUCK-Opazitaet-2000x2000.pdf`** | Opazitätsplatte gleiche Größe (schwarz=lichtdurchlässig, rot=Blockout) |
| `print-ghost-hires.png` | PNG-Master 4096×4096 px |
| `print-ghost-2000.png` | Verkleinerte Ansicht |
| `PRINT_SPEC.md` | Technische Spezifikation |

## Freigabe (für dich / Bauherr)

| Datei | Verwendung |
|-------|------------|
| **`FREIGABE-Massblatt-2100.pdf`** | Außen 2100×2100 mm inkl. Alu-Rahmen, Bemaßung **optisch unten 300 mm** |
| `FREIGABE-Massblatt-2100.png` | Rastervorschau |

Neu erzeugen: `python WerbeLEDbox-CountDown/scripts/finalize_print_pdfs.py`

## Physik (gemessen 2026-07-22)

- Druck-/LED-Fläche: **2000 × 2000 mm** (8×8 Panels à **250 × 250 mm**)
- Außenmaß Rahmen: **2100 × 2100 mm**
- Profil-Stirnbreite: **50 mm**
- Content-Grid: **64 × 64** → Zellpitch **31.25 mm**
- Totzone Textil: **250 mm** (8/64)
- Optisch unten dunkel (Einbau): **300 mm**

Opazitätsplatte: `../03-opazitaet/` · Lichtvideo: `../07-lichtvideo/`
