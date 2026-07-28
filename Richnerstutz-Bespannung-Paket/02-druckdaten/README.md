# Druckdaten — Hotel Anker Countdown

## Kanonisch (verbindlich, nach Druckerei-Korrektur)

| | |
|--|--|
| **Trim / Spannmaß** | **2100 × 2100 mm** |
| **Bleed** | **20 mm rundum** → MediaBox **2140 mm** |
| **Farbraum** | **CMYK** |
| **Schwarz unten** | **300 mm** |
| **Blocker** | schwarz=blockt · weiss=leuchtet |

## Produktionsdateien (an Richnerstutz)

| Datei | Verwendung |
|-------|------------|
| **`DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf`** | Sujet CMYK inkl. 20 mm Bleed |
| **`DRUCK-Blocker-2100x2100.pdf`** | Blocker CMYK (geometrietreu zum Sujet) |
| `DRUCK-Opazitaet-2100x2100.pdf` | Alias Blocker |
| `print-ghost-hires.png` | RGB-Preview Trim 8400² |
| `PRINT_SPEC.md` | Technische Spezifikation |

Rebuild: `python WerbeLEDbox-CountDown/scripts/build_richnerstutz_druckdaten.py`
