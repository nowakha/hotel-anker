# Print-Spezifikation — Hotel Anker Countdown

## Zwei Maßsysteme (nicht vermischen)

| Ebene | Maß | Schwarz unten |
|-------|-----|----------------|
| **Außenrahmen** (Freigabe / Einbau) | **2100 × 2100 mm** | **optisch 300 mm** = Totzone Textil 250 + Stirn 50 |
| **Drucktextil an Richnerstutz** | **2000 × 2000 mm** | **250 mm** (= 1 Modulreihe / 8/64). Stirn ist Aluminium — nicht mitdrucken. |

## Physik (gemessen)
- Druck-/LED-Fläche: **2000 × 2000 mm** (8×8 Panels à **250 × 250 mm**)
- Profil-Stirnbreite (XY): **50 mm**
- Außenmaß Rahmen: **2100 × 2100 mm** (= 2000 + 2×50)
- Innen Textil→LED (Z): **45 mm** (Zollstock)
- Content-Grid: **64 × 64** → Zellpitch **31.25 mm**
- Totzone Textil: untere **8/64** Zellen (= **250 mm**)
- Optisch unten dunkel (Einbau): **300 mm**

Stack vorne→hinten: SEG-Textil in Kedernut → Diffusion **45 mm** → LED-Panels → Rückwand/Controller  
Details: `Richnerstutz-Bespannung-Paket/06-fotos-vom-rahmen/GEOMETRIE-3D.md`

## Lieferdateien (Produktion)
- `DRUCK-Hotel-Anker-Flowbox-2000x2000.pdf` — MediaBox **2000×2000 mm**, Totzone deckend schwarz 250 mm
- `DRUCK-Opazitaet-2000x2000.pdf` — gleiche Größe; schwarz=lichtdurchlässig, rot=Blockout
- `FREIGABE-Massblatt-2100.pdf` — MediaBox **2100×2100 mm**, Bemaßung inkl. optisch 300 mm

## Raster / PNG-Master
- `print-ghost-hires.png` · **4096×4096 px** · 2.048 px/mm · **64 px/Zelle**
- Totzone ab Pixelzeile 3584 (= 56/64) — **rein schwarz**, kein Hinweistext

## Ziel
- Countdown endet **1. Oktober 2026, 13:00 Europe/Zurich** (nur live; Print zeigt „Zeit bis Baubeginn:“)
- Logo: historischer Kronen-Anker (Fassadenmarke Hotel Anker Rorschach)

## Opazitätsplatte
- **schwarz** = lichtdurchlässig · **rot** = lichtundurchlässig
- Rot: Totzone · Logo · Beschriftung · Fassadenlinien · DSEG7-Konturen / Colon-Ringe
- Schwarz: Liquid-Glass-Balken · DSEG7-Segmentfüllungen / Colon-Kerne · Navy-Hintergrund
