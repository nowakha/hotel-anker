# Print-Spezifikation — Hotel Anker Countdown

## Kanonisches Druckmaß (verbindlich)

| Angabe | Wert |
|--------|------|
| **Spann-/Druck-PDF** | **2100 × 2100 mm** (= Außenmaß Rahmen) |
| **Schwarzstreifen unten** | **300 mm** (= 250 Modulreihe + 50 Stirn) |
| Master-Datei | `DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` |
| PNG-Master | `print-ghost-hires.png` · **4200×4200 px** · 2 px/mm |

**Widerruf:** Frühere 2000×2000‑mm‑Produktion mit nur 250 mm Totzone war **falsch**.

## LED-Physik (nicht das Druckformat)

- LED-Fläche: **2000 × 2000 mm** (8×8 × 250 mm)
- Stirn: **50 mm** → Außen **2100 × 2100 mm**
- Content-Grid live: 64×64, Totzone LED = unterste 8/64 (= 250 mm Module)

## Lieferdateien

- `DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` — Produktion
- `DRUCK-Opazitaet-2100x2100.pdf` — schwarz=lichtdurchlässig, rot=Blockout (Totzone 300 mm)
- `print-ghost-hires.pdf` — Alias des Masters

## Opazität

- Rot: Totzone 300 mm · Logo · Beschriftung · Fassadenlinien · Digit-Konturen
- Schwarz: Glass-Balken · Segmentfüllungen · Navy-Hintergrund
