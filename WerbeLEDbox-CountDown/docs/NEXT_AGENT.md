# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-22 ~17:34. Lies zuerst `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Root cause (bestätigt)

Splash sichtbar + kein Netz = **`fb-clock` mit altem `probe_size()`** (`ffmpeg … -f null -` auf `st24.mov` 24h 4K). Fix im Repo, **auf SD-rootfs deployt + masked**.

## Entscheidung JETZT

**SD-Rescue OK (~17:18).** Post-boot Verify (~17:34): **noch kein SSH** (`.106` / mDNS / TS offline).

1. **Netz herstellen** — WiFi-Assoc prüfen oder Ethernet stecken (Direct-Eth Doc ok).
2. Sobald SSH: Abschnitt **C)** — mask + ffprobe Verify; **Unmask nur nach User-Freigabe**.
3. Kein aggressives Polling.

## A) Direct-Ethernet (bevorzugt)

```powershell
cd "C:\Users\User\Documents\Cursor Projects\Hotel Anker"
powershell -NoProfile -ExecutionPolicy Bypass -File WerbeLEDbox-CountDown\scripts\pi02_rescue_direct_eth.ps1
```

Kabel **PC↔Pi** (auto-MDIX, normales Kabel), Watcher laufen lassen, **dann** Power-Cycle.  
Watcher pollt `.106` + Tailscale + mDNS + **`169.254.*`** (APIPA). Mask + Deploy in den ersten ~2 min.

## B) SD-Pfad (wenn kein Ethernet / kein SSH-Fenster)

Siehe [`PI02_SD_RESCUE.md`](./PI02_SD_RESCUE.md) + `scripts/pi02_sd_rescue_wsl.sh`.

## C) Danach: Patch verifizieren, erst dann Clock

```powershell
scp WerbeLEDbox-CountDown/fb_clock_play.py user@192.168.8.106:~/WerbeLEDbox-CountDown/
ssh user@192.168.8.106 "grep -n 'ffprobe\|Never decode\|-f null' ~/WerbeLEDbox-CountDown/fb_clock_play.py | head"
# Erwartung: ffprobe + Never decode; KEIN -f null
scp WerbeLEDbox-CountDown/systemd/fb_clock.service user@192.168.8.106:/tmp/fb-clock.service
ssh user@192.168.8.106 "echo 12345678 | sudo -S mv /tmp/fb-clock.service /etc/systemd/system/fb-clock.service; echo 12345678 | sudo -S systemctl unmask fb-clock; echo 12345678 | sudo -S systemctl daemon-reload; echo 12345678 | sudo -S systemctl enable --now fb-clock; journalctl -u fb-clock -n 40 -f"
```

(Bei APIPA-Rescue: IP aus Log/`RESCUE_OK` statt `.106`.)

## Nicht tun

- Kein `cmdline.txt` rotate-Gefummel
- Keine 13GB MOV ins Git
- **Nie** alten Player mit `st24.mov` starten
- SD nur wenn Direct-Eth nicht geht / kein Fenster

## Danach

Dokumentieren → commit → push (Workflow-Regel).

