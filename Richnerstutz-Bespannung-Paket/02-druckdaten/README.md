# Druckdaten — Hotel Anker Countdown

## Kanonisch (verbindlich)

| | |
|--|--|
| **Spann-/Druckmaß** | **2100 × 2100 mm** (= Außenrahmen) |
| **Schwarz unten** | **300 mm** (= 250 Modul + 50 Stirn) |
| **Master-PDF** | `DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` |

Widerruf: 2000×2000 mm mit nur 250 mm Totzone war **falsch**.

## Produktionsdateien (an Richnerstutz)

| Datei | Verwendung |
|-------|------------|
| **`DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf`** | Haupt-Druck-PDF — MediaBox **2100×2100 mm** |
| **`DRUCK-Opazitaet-2100x2100.pdf`** | Opazitätsplatte gleiche Größe |
| `print-ghost-hires.pdf` | Alias des Masters |
| `print-ghost-hires.png` | PNG-Master 4200×4200 (2 px/mm) |
| `PRINT_SPEC.md` | Technische Spezifikation |

Verify: `python WerbeLEDbox-CountDown/scripts/finalize_print_pdfs.py`

## LED-Physik (Hintergrund)

- LED-Fläche innen: 2000×2000 mm (8×8 × 250 mm)
- Stirn: 50 mm → Außen 2100×2100 mm

Opazität: `../03-opazitaet/`
