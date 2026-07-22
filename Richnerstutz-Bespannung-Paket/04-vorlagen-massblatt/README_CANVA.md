# Canva Layer-Kit — Hotel Anker LightBox Overlay

## Canva-Account / Cursor
Cursor hat **kein Canva-MCP**. Eine OAuth-Verbindung zu deinem Canva-Account
ist von hier aus **nicht möglich**. Workflow:

1. Canva → Create design → **Custom size 4096 × 4096 px** (oder 2000×2000 mm @ 2.048 px/mm)
2. **File → Upload** die PNGs aus diesem Ordner
3. Jedes Overlay als eigene Ebene stapeln (Transparenz an)
4. Deine Design-Elemente darunter / dazwischen platzieren

## Dateien
| Datei | Inhalt |
|-------|--------|
| `00-overlay-combined.png` | Alles zusammen (Referenz) |
| `01-overlay-deadzone.png` | Totzone 8/64 (= 250 mm) |
| `02-overlay-modules-8x8.png` | 8×8 Panels à 250×250 mm |
| `03-overlay-pixels-64.png` | 64×64 Pixelmitten als Kreise |
| `04-overlay-keder-rail.png` | Kederschiene / SEG-Schlitz |
| `05-overlay-frame-50mm.png` | Aluminiumrahmen 50 mm (gemessen) |
| `06-overlay-legend.png` | Legende gemessen vs assumed |

## Masse — gemessen 2026-07-22
| Maß | Wert | Quelle |
|-----|------|--------|
| Druck-/LED-Fläche | 2000×2000 mm | 8×8 Panels |
| Außenmaß Rahmen | 2100×2100 mm | gemessen |
| Profilbreite | 50 mm | (2100−2000)/2 |
| Content-Pitch | 31.25 mm | 64×64 auf 2 m |
| Totzone | 8/64 = 250 mm | AnkerPI02 Field 7 |
| LED-Panel | 250×250 mm | **gemessen** |
| Keder-Schlitz | 4×14 mm | **ASSUMED** Industrie-SEG |

Drucksujet bleibt auf der **2000×2000 mm** Sichtfläche; Kederlippe greift in die 50-mm-Profilnut.
