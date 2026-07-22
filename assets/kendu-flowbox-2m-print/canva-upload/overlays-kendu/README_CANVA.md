# Canva Layer-Kit — Kendu Flowbox 2×2 m Overlay

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
| `02-overlay-modules-8x8.png` | 8×8 Module à 250×250 mm |
| `03-overlay-pixels-64.png` | 64×64 Pixelmitten als Kreise |
| `04-overlay-keder-rail.png` | Kederschiene / SEG-Schlitz |
| `05-overlay-frame-100mm.png` | Aluminiumrahmen 100 mm |
| `06-overlay-legend.png` | Legende confirmed vs assumed |

## Masse — was ist sicher?
| Maß | Wert | Quelle |
|-----|------|--------|
| Nennfläche | 2000×2000 mm | Kendu Standard Square |
| Profilbreite | 100 mm | Kendu FAQ „profile width“ |
| Content-Pitch | 31.25 mm | Projekt 64×64 auf 2 m |
| Totzone | 8/64 = 250 mm | AnkerPI02 Field 7 |
| Modul 8×8 | 250×250 mm | **ASSUMED** (kein Kendu-Datenblatt) |
| Keder-Schlitz | 4×14 mm | **ASSUMED** Industrie-SEG |

Kendu veröffentlicht die exakten LED-Platten-PCB-Maße und den exakten
Keder-Querschnitt **nicht** öffentlich. Für Produktion: Maßblatt von
flowbox@kendu.com / eurem CSM anfordern und hier nachziehen.
