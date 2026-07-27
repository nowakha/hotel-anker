# Foto-Auswertung — LightBox / Kendu-Rahmen (Neu 2026-07-27)

Originalfotos jetzt im Ordner (Chat-Uploads):

| Datei | Motiv | Mess-/Sichtbefund |
|-------|--------|-------------------|
| `01-gesamtansicht.png` | Frontal, LED-Matrix + untere Controllerschiene | **8 Reihen** LED-Module sichtbar; darunter **leerer Kanal** mit Querprofil + weißen Anschlüssen/Controllern (ohne Textil sichtbar) |
| `02-ecke-keder-nah.png` | Gehrungsecke | Kedernut an **vorderer Innenlippe**, 45°-Gehrung, KENDU-Panels TOP/BOTTOM |
| `03-kendu-controller-diffuser.png` | Profil-Innen / Stack | KENDU-PCB, Diffusor-/Luftstrecke, dunkle Nut/Textil-Ebene |
| `04-profil-tiefe-zollstock.png` | Seitenansicht Z | **Profilgesamttiefe ≈ 80–85 mm** (Zollstock 0 an Außenkante → ~8.0–8.5 cm) |
| `05-rand-led-zu-profil-zollstock.png` | Innenrand → LED | **≈ 25 mm** von Profil-Innenecke bis Beginn der weißen LED-PCB |

## Was die Fotos klar belegen

1. **System:** Kendu Backlit-Panels (Logo auf PCB), SEG-Alurahmen mit Kedernut.
2. **Z-Tiefe:** Gesamtes Profil **~80–85 mm** (Foto 04) — nicht „nur 45 mm Gesamttiefe“. Die frühere Angabe **45 mm** war die **optische Kavität Textil→LED** (Innenmaß), nicht die Außenprofiltiefe.
3. **Rand LED↔Profil:** Innen **~25 mm** Freiraum Profilwand → LED-Board (Foto 05). Das ist der **Innenabstand zur Matrix**, nicht automatisch die Stirnbreite von außen.
4. **Unten ohne Textil:** Unter der untersten Modulreihe liegt ein **Controller-/Versorgungskanal** (Foto 01). Mit aufgespanntem Textil ist das von vorne abgedeckt — dort kommt **kein LED-Licht**, deshalb Blockout/Schwarz sinnvoll.
5. **Modulraster:** Frontal **8 Modulreihen** erkennbar (Annotierung); Spalten je nach Bildausschnitt 6–8 — Nennmaß weiter **8×8 × 250 mm** laut früherer Messung Außen 2100 / Fläche 2000.

## Zwei Ränder — nicht vermischen

| Begriff | Wert | Bedeutung |
|---------|------|-----------|
| Stirnbreite außen (XY) | **50 mm** | (2100−2000)/2 — sichtbarer Alu-Rand von vorne |
| Innenabstand Profil→LED | **≈ 25 mm** | Foto 05, Zollstock |
| Profiltiefe Z | **≈ 80–85 mm** | Foto 04, Zollstock |
| Optische Kavität Textil→LED | **~45 mm** | frühere Innenmessung (weiter gültig als Lichtweg) |
| Totzone Textil (Druck) | **250 mm** | 1 Modulreihe / 8/64 |
| Optisch unten dunkel (Einbau) | **300 mm** | 250 Textil-Totzone + **50** Stirn unten |

## Konsequenz für Druck (kanonisch 2026-07-27)

- Spann-/Druckmaß: **2100×2100 mm** (User-Master-PDF bestätigt).
- Schwarz unten auf dem Druck: **300 mm** (250 Modul + 50 Stirn).
- Offerte AG 461414 nennt noch „Textil 200×200 cm“ — **Nachtrag nötig:** Spannmaß **210×210 cm**.

## Offen / nächste Messung (optional)

- Exakte Höhe des Controllerkanals in mm (Massband frontal, Textil ab).
- Ob 25 mm Innenabstand umlaufend gleich ist (oben/unten/seitlich).
