# 3D-Geometrie LightBox — aus Fotos + Messung

Schemata: `schema-front-xy.png` · `schema-querschnitt-z.png` · `schema-3d-geometrie.png`

## Maße

| Größe | Wert | Bedeutung | Quelle |
|-------|------|-----------|--------|
| **Stirnbreite** (XY) | **50 mm** | Rahmenrand in der Frontansicht | gemessen: (2100−2000)/2 |
| **Innen** (Z) | **45 mm** | Vorderkante / Textil-Ebene → LED-Oberfläche | Zollstock-Fotos «Innen 4.5 cm» |
| Außenmaß XY | **2100 × 2100 mm** | inkl. Stirnbreite | gemessen |
| Druck-/LED-Fläche XY | **2000 × 2000 mm** | innen, 8×8 Panels | gemessen |
| LED-Panel | **250 × 250 mm** | Module auf Rückwand («REMBRANDT») | gemessen |

**Wichtig:** Die optisch relevante Diffusionsstrecke ist **45 mm innen**, nicht die frühere FAQ-Schätzung ~100 mm Profil-Gesamttiefe.

## Optischer Stack (Vorne → Hinten)

```
[ Betrachter ]
     │
     ▼
1. SEG-Textil (Druck) — in Kedernut der Profil-Innenlippe
2. Kederschienenlippe in umlaufender Nut
3. Luft- / Diffusionsstrecke = **45 mm** (gemessen)
4. LED-Panel-Ebene — 8×8 × 250 mm
5. Reflexionsrückwand / Verstrebungen + Kendu-Controller
```

## Konsequenzen für Druck / Licht

- Lichtweg Textil↔LED nur **45 mm** → LED-Punktraster kann bei zu transparentem Druck sichtbar bleiben (Blockout kritisch).
- Drucksujet: **2000×2000 mm** Fläche.
- Keder an vorderer Nut; Stirnbreite **50 mm**.
