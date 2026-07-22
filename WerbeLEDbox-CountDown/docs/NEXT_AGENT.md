# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-22 ~17:00. Lies zuerst `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Root cause (bestätigt)

Splash sichtbar + kein Netz = **`fb-clock` mit altem `probe_size()`** (`ffmpeg … -f null -` auf `st24.mov` 24h 4K). Fix im Repo, **nicht** auf dem Pi.

### Warum Power-Cycle + Watcher ~3× scheiterte

PI02 läuft aktuell **nur WiFi**. Netz/SSH/Tailscale kommen oft **erst nach** dem Hang:

1. Boot → Splash  
2. `ExecStartPre` NTP-Wait ≤**120 s** (ohne Netz: kein Sync → Timeout → Start trotzdem)  
3. Alter Player hängt auf Full-Decode  
4. WiFi/DHCP/SSH danach → **kein nutzbares SSH-Fenster** → Watcher kann nichts maskieren  

Beweis: `docs/_pi02_rescue.log` nur Startzeile (`16:27`), **kein** `SUCCESS`. Watcher pollt nur `192.168.8.106` + `100.103.54.63` (LAN/TS — WiFi-DHCP-IP unbekannt).

## Entscheidung JETZT (Parent/User)

1. **Ethernet-Kabel möglich?** → Ja: Kabel stecken, Watcher starten, Power-Cycle. **Schnellster Remote-Rescue.**  
2. **Ethernet unmöglich/unpraktisch (Decke)?** → **SD-Rescue** — User ist bereit. Anleitung: [`PI02_SD_RESCUE.md`](./PI02_SD_RESCUE.md).  
3. Serial (`console=serial0,115200`): nur mit UART an GPIO — meist nicht leichter als SD.

**Nicht** weiter blind Power-Cyclen erwarten, dass der WiFi-Watcher trifft.

## A) Ethernet-Pfad (wenn Port erreichbar)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File WerbeLEDbox-CountDown\scripts\pi02_rescue_watch.ps1
```

Kabel Pi↔Router, dann Strom aus/an. Watcher maskiert `fb-clock` + deployed `fb_clock_play.py`.

Manuell:

```powershell
ssh user@192.168.8.106
echo 12345678 | sudo -S systemctl stop fb-clock
echo 12345678 | sudo -S systemctl disable fb-clock
echo 12345678 | sudo -S systemctl mask fb-clock
```

## B) SD-Pfad (wenn kein Ethernet)

Siehe [`PI02_SD_RESCUE.md`](./PI02_SD_RESCUE.md) + Helper `scripts/pi02_sd_rescue_wsl.sh`.  
Kurz: stromlos → SD → WSL mount root → mask `fb-clock` → optional Player kopieren → sync/umount → zurück → Boot → SSH.

## C) Danach: Patch verifizieren, erst dann Clock

```powershell
scp WerbeLEDbox-CountDown/fb_clock_play.py user@192.168.8.106:~/WerbeLEDbox-CountDown/
ssh user@192.168.8.106 "grep -n 'ffprobe\|Never decode\|-f null' ~/WerbeLEDbox-CountDown/fb_clock_play.py | head"
# Erwartung: ffprobe + Never decode; KEIN -f null
scp WerbeLEDbox-CountDown/systemd/fb_clock.service user@192.168.8.106:/tmp/fb-clock.service
ssh user@192.168.8.106 "echo 12345678 | sudo -S mv /tmp/fb-clock.service /etc/systemd/system/fb-clock.service; echo 12345678 | sudo -S systemctl unmask fb-clock; echo 12345678 | sudo -S systemctl daemon-reload; echo 12345678 | sudo -S systemctl enable --now fb-clock; journalctl -u fb-clock -n 40 -f"
```

## Nicht tun

- Kein `cmdline.txt` rotate-Gefummel  
- Kein Underclock-Reboot nötig  
- Keine 13GB MOV ins Git  
- **Nie** alten Player mit `st24.mov` starten  
- SD nur wenn Ethernet nicht geht  

## Danach

Dokumentieren → commit → push (Workflow-Regel).
