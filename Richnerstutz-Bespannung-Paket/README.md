# Richnerstutz — Versandpaket Bespannung Hotel Anker

Alles für die Anfrage an **Richnerstutz AG** (Druck + Konfektion mit Kederschienenlippe).

| | |
|--|--|
| **Auftraggeber** | Realia AG (Gottlieb Kündig), Industriestrasse 40b, 9400 Rorschach, UID CHE-113.325.481 |
| **Technische Ansprechperson** | Harald Nowak, Modernlight — Projektleitung \| Videoengineering |
| **E-Mail Technik** | Harald.Nowak@modernlight.ch |
| **Mobil** | +41 76 579 84 54 |
| **Modernlight** | Wangenstrasse 57, 3018 Bern |

## Ordnerstruktur

| Ordner | Inhalt |
|--------|--------|
| `01-anfrage/` | Kopierfertiges Anschreiben + Empfängerdaten |
| `02-druckdaten/` | Produktions-Sujet (hires + 2000 px) und PRINT_SPEC |
| `03-opazitaet/` | Opazitätsplatte + Detailprüfungen (Blockout vs. transluzent) |
| `04-vorlagen-massblatt/` | Keder-/Rahmen-Overlays und Layer-Manifest |
| `05-vorschauen/` | Kleine Previews zum schnellen Anschauen |
| `06-fotos-vom-rahmen/` | Fotos / Auswertung |
| `07-lichtvideo/` | Neu berechnetes LED-Lichtvideo (GIF + Stills) |

## Status (2026-07-28)

Druckvorstufe Richnerstutz (**Tanja Jelk**) hat die angelieferten Daten **abgelehnt**. Korrektur nötig vor Produktion. Antwortentwurf: [`01-anfrage/Antwort-Richnerstutz-2026-07-28-Druckdaten-Korrektur.md`](./01-anfrage/Antwort-Richnerstutz-2026-07-28-Druckdaten-Korrektur.md). **Kein Outbound ohne Harald-Go.**

Beanstandungen: Blocker ≠ Sujet · RGB statt CMYK · keine 2 cm Zugabe / Sperrzone · verpixelt · Blocker-Polarität falsch (soll **schwarz=blockt / weiss=leuchtet**, nicht rot).

## Was Richnerstutz braucht (Priorität — nach Korrektur)

1. Anfrage / Korrespondenz aus `01-anfrage/`
2. **Druck-PDF:** `02-druckdaten/DRUCK-Hotel-Anker-Flowbox-2100x2100.pdf` (**2100×2100 mm**, Schwarz unten **300 mm**) — neu: **CMYK**, **2 cm Zugabe**, höhere Auflösung
3. **Opazitäts-/Blocker-PDF:** neu gemäss Richner-Konvention  
   - **schwarz** = blockt (lichtundurchlässig)  
   - **weiss** = leuchtet (transluzent) — **kein Rot**  
   - (Repo-Alt: schwarz=transluzent / rot=Blockout — **widerrufen für Lieferung**)
4. Fotos aus `06-fotos-vom-rahmen/`
5. Offerte AG 461414: Spannmaß **210×210 cm**

Optional: Massblatt-Overlays in `04-vorlagen-massblatt/`, Vorschauen in `05-vorschauen/`.

## Empfänger

Richnerstutz AG · Nordstrasse 7 · 5612 Villmergen  
info@richnerstutz.ch · +41 56 616 67 67 · https://richnerstutz.ch/kontakt
