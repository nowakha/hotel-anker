# 3D-Geometrie LightBox — aus Fotos + Messung

Schemata: `schema-front-xy.png` · `schema-querschnitt-z.png` · `schema-3d-geometrie.png`

## Zwei verschiedene «Profil»-Maße (nicht verwechseln)

| Größe | Wert | Bedeutung | Quelle |
|-------|------|-----------|--------|
| **Stirnbreite** (XY) | **50 mm** | Rahmenrand in der Frontansicht; Außen − Fläche | gemessen: (2100−2000)/2 |
| **Profil-Tiefe** (Z) | **≈ 100 mm** | Bautiefe vorne→hinten («spessore») | Kendu-FAQ + Foto-Stack |
| Außenmaß XY | **2100 × 2100 mm** | inkl. Stirnbreite | gemessen |
| Druck-/LED-Fläche XY | **2000 × 2000 mm** | innen, 8×8 Panels | gemessen |
| LED-Panel | **250 × 250 mm** | flächige Module auf Rückwand | gemessen |

Früher fälschlich: Kendu-FAQ «profile width 100 mm» als Stirnbreite gelesen.  
Italienische FAQ stellt klar: *spessore* = Dicke/Tiefe ≈ 100 mm. Unsere **50 mm** sind die sichtbare Stirnbreite.

## Optischer Stack (Vorne → Hinten) — aus Fotos 01–03

```
[ Betrachter ]
     │
     ▼
1. SEG-Textil (Druck) — in Kedernut der Profil-Innenlippe eingespannt
2. Kederschienenlippe (Silikon/Flachkeder) in umlaufender Nut (Foto 02, Gehrung)
3. Luft- / Diffusionsstrecke innerhalb der Profil-Tiefe
4. LED-Panel-Ebene — 8×8 × 250 mm, dicht gestoßen, weisse Reflexionsfläche (Foto 01/02)
5. Rückwand / Verstrebungen + Kendu-Controller (DC 24V, DMX, CH1–4) (Foto 03)
```

### Was die Fotos klar zeigen

1. **Gesamtansicht:** Freistehender Alu-Rahmen, volle Matrix sichtbar → Textil abgenommen; echte **Backlit**-Anordnung (LEDs auf der Rückfläche, nicht nur Randlicht).
2. **Ecke:** Gehrung 45°, schmale Kedernut an der **vorderen Innenlippe**; LED-Platten enden knapp vor dem Profil → kleiner Spalt, in dem später das Tuch sitzt.
3. **Controller/Diffusor:** Kendu-Hardware; hinter transluzentem Material bleibt das **LED-Punktraster** erkennbar → Blockout muss streulichtfest sein.

## Konsequenzen für Druck / Bespannung

- Drucksujet bemisst die **2000×2000 mm Fläche** (nicht 2100).
- Keder greift in die Nut der **50-mm-Stirn** / vorderen Lippe; Zugabe laut Richnerstutz-Konfektion.
- Lichtweg ≈ Profil-Tiefe minus Panel-/Textildicke → genug Raum für Diffusion, aber Hotspots bei zu transparentem Druck (Foto 03).
- Totzone unten 250 mm bleibt XY-Maske auf derselben Textil-Ebene.

## Offen / optional nachmessen

- [ ] Profil-Tiefe Z exakt mit Massband von der Seite (`06-seite-tiefe.jpg`)
- [ ] Kedernut-Querschnitt (Breite × Tiefe der Nut)
- [ ] Abstand Textil-Ebene ↔ LED-Oberfläche (Diffusionsluft)
