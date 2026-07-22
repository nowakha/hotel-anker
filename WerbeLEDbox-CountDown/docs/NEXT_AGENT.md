# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-22 ~16:30. Lies zuerst `LEARNINGS.md` + `docs/SESSION_LOG.md`.

## Root cause (high confidence)

Splash sichtbar + kein Netz = **`fb-clock` mit altem `probe_size()`** (`ffmpeg … -f null -` auf `st24.mov` 24h 4K). Fix liegt im Repo, **nicht** auf dem Pi. **SD nicht ziehen.**

## 1) User: Power-Cycle jetzt

Während auf Workstation läuft (falls nicht schon):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File WerbeLEDbox-CountDown\scripts\pi02_rescue_watch.ps1
```

Dann PI02 Strom aus/an. SSH-Fenster: nach Netz-up, **bevor** NTP-Wait endet und der alte Player startet (bis ~120 s). Der Watcher maskiert `fb-clock` und deployed `fb_clock_play.py`.

Manuell falls nötig:

```powershell
ssh user@192.168.8.106
# sofort:
echo 12345678 | sudo -S systemctl stop fb-clock
echo 12345678 | sudo -S systemctl disable fb-clock
echo 12345678 | sudo -S systemctl mask fb-clock
```

## 2) Danach: Patch verifizieren, erst dann Clock

```powershell
scp WerbeLEDbox-CountDown/fb_clock_play.py user@192.168.8.106:~/WerbeLEDbox-CountDown/
ssh user@192.168.8.106 "grep -n 'ffprobe\|Never decode\|-f null' ~/WerbeLEDbox-CountDown/fb_clock_play.py | head"
# Erwartung: ffprobe + Never decode; KEIN -f null
scp WerbeLEDbox-CountDown/systemd/fb_clock.service user@192.168.8.106:/tmp/fb-clock.service
ssh user@192.168.8.106 "echo 12345678 | sudo -S mv /tmp/fb-clock.service /etc/systemd/system/fb-clock.service; echo 12345678 | sudo -S systemctl unmask fb-clock; echo 12345678 | sudo -S systemctl daemon-reload; echo 12345678 | sudo -S systemctl enable --now fb-clock; journalctl -u fb-clock -n 40 -f"
```

## 3) Nicht tun

- Kein `cmdline.txt` rotate-Gefummel / SD-Entnahme außer wirklich letzter Ausweg
- Kein Underclock-Reboot nötig
- Keine 13GB MOV ins Git
- **Nie** alten Player mit `st24.mov` starten

## 4) Danach

Dokumentieren → commit → push (Workflow-Regel).
