# AnkerPI02 — Direkt-Ethernet Rescue (ohne DHCP/Switch)

Stand: **2026-07-22**. Bevorzugter Remote-Rescue gegenüber WiFi-Watcher und vor SD-Entnahme.

## Kurzantwort

**Ja — Direktkabel PC↔Pi hilft.** Der Link steht in Sekunden (WiFi oft zu spät). Im NTP-Fenster (≤120 s) kann SSH `fb-clock` maskieren, **bevor** der alte Player den Pi mit Full-Decode aufhängt.

## Technische Wahrheit

| Punkt | Detail |
|-------|--------|
| Kabel | Pi 4 hat **auto-MDIX** → normales Ethernet-Kabel reicht, kein Crossover |
| Ohne DHCP | Beide Enden typisch IPv4 Link-Local **`169.254.x.x`** (APIPA) |
| SSH | Funktioniert auf APIPA, **wenn** `sshd` läuft und der Pi noch nicht hängt |
| Vorteil vs WiFi | Ethernet-Link früh → Watcher kann das NTP-`ExecStartPre`-Fenster (≤120 s) treffen |
| Grenze | Hangt `fb-clock` bereits die CPU (ffmpeg Full-Decode), hilft **kein** Interface — Power-Cycle und Fenster erneut erwischen |
| Static IPs | Optional PC z. B. `192.168.97.1/24` — Pi hat kein Matching, solange nicht vorkonfiguriert. **Praktisch:** APIPA + Scan `169.254.*` |

## Schritte (MLT-NITRO5-HN / Windows)

1. **Kabel** AnkerPI02 Ethernet-Port ↔ Windows-PC (direkt, kein Switch/Router nötig).
2. Am PC: **Ethernet-Adapter aktivieren**. WiFi vorübergehend aus optional (weniger Verwechslung). Kein „getaktetes“/deaktiviertes Ethernet.
3. Watcher starten (bevorzugt Direct-Eth-Wrapper):

```powershell
cd "C:\Users\User\Documents\Cursor Projects\Hotel Anker"
powershell -NoProfile -ExecutionPolicy Bypass -File WerbeLEDbox-CountDown\scripts\pi02_rescue_direct_eth.ps1
```

   Alternativ derselbe Kern: `scripts\pi02_rescue_watch.ps1` (pollt `.106`, Tailscale `100.103.54.63`, mDNS, **und** `169.254.*`-Nachbarn).

4. **Power-Cycle** am Pi (Strom aus/an).
5. Erwartung in den **ersten ~2 Minuten**: TCP/22 offen → Script maskiert `fb-clock`, deployed gepatchtes `fb_clock_play.py`.
6. Log: `WerbeLEDbox-CountDown/docs/_pi02_rescue.log` — Erfolg = Zeile `SUCCESS` / Console `RESCUE_OK`.

### Wenn nichts kommt

- Nochmal Power-Cycle **mit laufendem** Watcher (Hang schon vor SSH → Fenster verpasst).
- PC hat `169.254.*`? (`ipconfig` / `Get-NetIPAddress`). Nachbarn: `Get-NetNeighbor -AddressFamily IPv4 | Where IPAddress -like '169.254.*'`.
- Immer noch tot und kein SSH-Fenster → **SD-Rescue**: [`PI02_SD_RESCUE.md`](./PI02_SD_RESCUE.md).

## Wann SD trotzdem nötig

- Ethernet-Port am Pi **nicht** erreichbar (Decke/Verkabelung).
- Mehrere Direct-Eth-Power-Cycles mit laufendem Watcher → **kein** `SUCCESS` (Hang ohne SSH-Fenster).
- SD physisch schwer, aber User bereit — siehe SD-Doc. **Kein** riskantes `cmdline.txt`-Experiment.

## Danach

1. Verifizieren: Player enthält `ffprobe` / `Never decode`, **kein** `-f null` Full-Decode.
2. Erst dann `fb-clock` unmask/enable (siehe Root [`AGENTS.md`](../../../AGENTS.md) § Status).
