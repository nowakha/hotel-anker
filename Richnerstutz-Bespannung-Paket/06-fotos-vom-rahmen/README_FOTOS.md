# Fotos vom Rahmen / Kederschiene

Drei Chat-Fotos sind ausgewertet → siehe `FOTO-AUSWERTUNG.md`.

## Technisches Interim (im Repo)

Aus den bestätigten Maßen gerenderte Schemata — für Mail/Anfrage bis die Original-JPGs liegen:

| Datei | Inhalt |
|-------|--------|
| `01-schema-gesamtansicht.png` | Front XY (2100 / 2000 / Module) |
| `02-schema-ecke-keder.png` | 3D-Geometrie / Stack |
| `03-schema-querschnitt-led.png` | Querschnitt Textil→45 mm→LED |

## Originaldateien hier ablegen (für E-Mail-Anhang)

- [ ] `01-gesamtansicht.jpg` — LightBox frontal, LED-Matrix, Ständer
- [ ] `02-ecke-keder-nah.jpg` — Gehrungsecke, Kedernut, LED-Platten
- [ ] `03-kendu-controller-diffuser.jpg` — Kendu-Controller, Diffusor mit LED-Raster

Optional:

- [ ] `05-profilbreite-massstab.jpg` — Massband an der Profilbreite
- [ ] `06-seite-tiefe.jpg` — Rahmen von der Seite

Drop-Skript (kopiert Dateien aus einem Ordner in diese Namen):

```powershell
pwsh -File ..\..\WerbeLEDbox-CountDown\scripts\import_rahmen_fotos.ps1 -SourceDir "D:\Fotos\LightBox"
```

## Tipps

- Massband in mindestens einem Nahfoto.
- Keder-Nahaufnahme ohne starken Blitz (Spiegelungen).
