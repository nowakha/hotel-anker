# Print-Spezifikation — Hotel Anker Countdown (Richnerstutz)

Korrektur nach Druckvorstufe (Tanja Jelk): CMYK · Bleed · Sperrzone · Blocker schwarz/weiss · höhere Auflösung.

## Endformat / Spannmaß

| Angabe | Wert |
|--------|------|
| **Trim / Spannmaß** | **2100 × 2100 mm** (= Außenmaß Rahmen) |
| **Bildzugabe (Bleed)** | **20 mm rundum** |
| **MediaBox (Liefer-PDF)** | **2140 × 2140 mm** (= Trim + 2×Bleed) |
| **Stoff-Sperrzone** | **20 mm** vom Trim-Rand — kritisches Sujet nur innerhalb |
| **Schwarzstreifen unten** | **300 mm** (= 250 Modulreihe + 50 Stirn) |
| **Farbraum** | **CMYK** (sRGB → FOGRA39 Coated) |
| **Auflösung** | **4 px/mm** (≈ 102 dpi) |

## Lieferdateien

| Datei | Inhalt |
|-------|--------|
| `DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` | Sujet CMYK, MediaBox 2140 mm |
| `DRUCK-Blocker-2100x2100.pdf` | Blocker CMYK, gleiche Geometrie / MediaBox |
| `DRUCK-Opazitaet-2100x2100.pdf` | Alias des Blockers (Dateiname-Kompatibilität) |
| `print-ghost-hires.png` | RGB-Preview Trim 8400² |
| `print-opacity-mask-hires.png` | Blocker RGB-Preview Trim 8400² |

## Blocker-Legende (verbindlich)

| Farbe | Bedeutung |
|-------|-----------|
| **Schwarz** | blockt / lichtundurchlässig |
| **Weiss** | leuchtet / lichtdurchlässig |

Kein Rot. Blocker und Sujet stammen aus demselben Generator-Lauf.

## LED-Physik (nicht das Druckformat)

- LED-Fläche: **2000 × 2000 mm** (8×8 × 250 mm)
- Stirn: **50 mm** → Außen **2100 × 2100 mm**
- Sujet der LED-Fläche ist zentriert im Trim; Stirn = Navy (Sujet) bzw. Schwarz (Blocker)

Rebuild: `python WerbeLEDbox-CountDown/scripts/build_richnerstutz_druckdaten.py`
