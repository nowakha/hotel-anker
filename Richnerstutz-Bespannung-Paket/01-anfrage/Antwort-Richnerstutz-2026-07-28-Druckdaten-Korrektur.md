# Antwortentwurf — Richnerstutz Druckdaten-Korrektur (2026-07-28)

**Status:** Entwurf — **NICHT gesendet**. Wartet auf Harald-Go.  
**Bezug:** Mail Tanja Jelk, 2026-07-28 09:43 UTC, Betreff «Druckdatei Hotel Anker», Thread/`message_id` `19fa81bceee18dd4`  
**An:** tanja.jelk@richnerstutz.ch  
**Cc:** Frau Vogt (Richnerstutz Vorstufe — Adresse aus Gmail-Thread beibehalten), Harald.Nowak@modernlight.ch  
**Betreff:** Re: Druckdatei Hotel Anker — korrigierte Daten folgen

---

Sehr geehrte Frau Jelk

vielen Dank für die rasche Prüfung der Druckvorstufe und die klare Auflistung.

Wir nehmen alle Punkte an und liefern **korrigierte Druckdaten** nach:

1. **Blocker / Opazitätsplatte** — wir stimmen die Maske 1:1 auf das Sujet ab und liefern sie neu.  
2. **CMYK** — Sujet und Blocker werden in **CMYK** angeliefert (kein RGB mehr).  
3. **Zugabe / Sperrzone** — rundum **2 cm Bildzugabe**; kritische Motivteile (inkl. oberer Rand) aus der **2-cm-Stoff-Sperrzone** herausgerückt.  
4. **Auflösung** — Sujet mit höherer Auflösung / schärferer Quelle neu exportiert.  
5. **Blocker-Polarität** — gemäss Ihrer Vorgabe: **schwarz = blockt**, **weiss = leuchtet** (kein Rot mehr).

Frau Vogt belassen wir im CC.

Kurz zur Masse: verbindliches Spannmaß bleibt **210 × 210 cm** (MediaBox 2100 × 2100 mm), Totzone unten **300 mm** lichtundurchlässig.

Können Sie uns bitte bestätigen, ob die **MediaBox weiterhin 2100 × 2100 mm** bleiben soll und die **2 cm Zugabe innerhalb** dieses Maßes liegt — oder ob die Datei auf **2140 × 2140 mm** (2100 + 2×20) angeliefert werden soll?

Wir melden uns mit dem korrigierten Paket sobald fertig. Bitte kurz Bescheid, falls der Liefertermin dadurch enger wird.

Freundliche Grüsse  

Harald Nowak  
Modernlight — Projektleitung | Videoengineering  
Harald.Nowak@modernlight.ch  
+41 76 579 84 54  
Wangenstrasse 57, 3018 Bern  

---

## Intern (Harald) — To-do vor Versand

| # | Arbeit | Hinweis |
|---|--------|---------|
| A | Opazität invertieren | Repo-Konvention war schwarz=transluzent / rot=Blockout → Richner: schwarz=Block / weiss=Licht |
| B | Maske vs. Sujet matchen | Screenshots in Gmail prüfen (nicht im Zapier-Webhook) |
| C | RGB→CMYK | Beide PDFs; Farbverschiebung prüfen |
| D | +20 mm Bleed / Sperrzone | Layout: Motiv oben + Logo/Text nicht in Sperrzone |
| E | Höhere Auflösung | Canva `DAHQET371rQ` / `print-ghost-hires` neu exportieren |
| F | ZIP + Mail | Erst nach Harald-Go; Frau Vogt im CC |

**Kein Outbound ohne explizites Go von Harald.**
