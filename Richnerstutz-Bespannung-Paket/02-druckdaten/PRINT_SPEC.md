# Print-Spezifikation — Hotel Anker Countdown

## Physik (gemessen 2026-07-22)
- Druck-/LED-Fläche: **2000 × 2000 mm** (8×8 Panels à **250 × 250 mm**)
- Profilbreite: **50 mm**
- Außenmaß Rahmen: **2100 × 2100 mm** (= 2000 + 2×50)
- Content-Grid: **64 × 64** → Zellpitch **31.25 mm**
- Totzone: untere **8/64** Zellen (= **250 mm**)

## Format
- `print-ghost-hires.png` · **4096×4096 px** · 2.048 px/mm · **64 px/Zelle** (exakt)

## Ziel
- Countdown endet **1. Oktober 2026, 13:00 Europe/Zurich** (nur live; Print zeigt „Zeit bis Baubeginn:“)
- Logo: historischer Kronen-Anker (Fassadenmarke Hotel Anker Rorschach)

## Layout (identisch Lichtvideo)
- 8er füllen Höhe zwischen Liquid-Glass-Balken (`DH=12`)
- Mitte der 8 = Mitte zwischen den Colon-Punkten
- Tage y=19, Zeit y=37, Totzone ab 56

## Opazitätsplatte
- `print-opacity-mask-hires.png` · **schwarz = lichtdurchlässig**, **rot = lichtundurchlässig**
- Rot: Totzone · Logo · Beschriftung · Fassadenlinien (auch über Glass-Balken) · DSEG7-Konturen / Colon-Ringe
- Schwarz: Liquid-Glass-Balken · DSEG7-Segmentfüllungen / Colon-Kerne · Navy-Hintergrund
