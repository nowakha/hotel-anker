# Opazitätsplatte — Legende für Richnerstutz

> **2026-07-28 — Richner-Vorgabe (verbindlich für nächste Lieferung):**  
> **schwarz = blockt** · **weiss = leuchtet** · **kein Rot**.  
> Die bisherige Repo-Legende (schwarz=transluzent / rot=Blockout) gilt nur noch als historische Erklärung der gelieferten Dateien und muss vor dem nächsten Versand umgestellt werden.

Datei: `print-opacity-mask-hires.png` (historisch 4096×4096 / rot-schwarz)

| Farbe (alt, geliefert) | Bedeutung | Druckziel |
|------------------------|-----------|-----------|
| **Schwarz** | lichtdurchlässig / transluzent | LED-Licht soll klar durchscheinen |
| **Rot** | lichtundurchlässig / Blockout | kein Streulicht, klare Silhouette |

| Farbe (neu, Richner 2026-07-28) | Bedeutung |
|---------------------------------|-----------|
| **Schwarz** | blockt / lichtundurchlässig |
| **Weiss** | leuchtet / transluzent |

## Schwarz (transluzent)

- Füllungen der 7-Segment-Ziffern (Ghost-8 / aktive Segmente)
- Kerne der Doppelpunkte
- Liquid-Glass-Balken (Titel-/Labelbänder)
- Navy-Hintergrund in den LED-Durchscheinflächen

## Rot (Blockout)

- Totzone unten: volle Breite × 250 mm (8/64 Zellen)
- Logo Kronen-Anker
- Beschriftungen («Zeit bis Baubeginn:», Tage/Stunden/Minuten/Sekunden)
- Fassadenlinien (auch über Glass-Balken)
- Konturen der 7-Segment-Ziffern und Ringe der Doppelpunkte

## Bitte an die Produktion

Selektiver Blockout auf Backlit-/SEG-Textil (oder gleichwertiges Verfahren), sodass Rot-Zonen streulichtfrei bleiben und Schwarz-Zonen die RGB-LED-Farben brillant wiedergeben.
