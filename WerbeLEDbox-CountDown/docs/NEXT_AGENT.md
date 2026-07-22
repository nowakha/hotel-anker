# NEXT AGENT — Sofortmaßnahmen

Stand: 2026-07-22 ~16:20. Lies zuerst `LEARNINGS.md` + `docs/SESSION_LOG.md`.

**Blocker:** AnkerPI02 ist offline (LAN + Tailscale). Ohne User-Eingriff (Strom/Boot) kein Deploy möglich. Sobald online: Schritt 2 **vor** `fb-clock`-Start.

## 1) AnkerPI02 online?

```powershell
ping 192.168.8.106
ssh user@192.168.8.106
# oder: ssh user@100.103.54.63
```

Passwort: siehe `secrets/ankerpi02.credentials.yml`.

Wenn offline: User muss Strom/Boot prüfen (SD nicht entnehmbar).

## 2) Vor fb-clock: patched Player deployen

Repo hat den Fix bereits. Auf den Pi:

```powershell
scp WerbeLEDbox-CountDown/fb_clock_play.py user@192.168.8.106:~/WerbeLEDbox-CountDown/
scp WerbeLEDbox-CountDown/systemd/fb_clock.service user@192.168.8.106:/tmp/fb-clock.service
ssh user@192.168.8.106 "sudo mv /tmp/fb-clock.service /etc/systemd/system/fb-clock.service && sudo systemctl daemon-reload && sudo systemctl restart fb-clock && journalctl -u fb-clock -n 40 -f"
```

Erwartung im Log: `crop=T386,B127,...` und bald `ffmpeg` mit `-ss HH:MM:SS` → fbdev — **kein** `ffmpeg … -f null -` Full-Decode.

## 3) Nicht tun

- Kein `cmdline.txt` rotate-Gefummel
- Kein Underclock-Reboot nötig (Block bereits entfernt)
- Keine 13GB MOV ins Git

## 4) Danach

Dokumentieren → commit → push (Workflow-Regel).
