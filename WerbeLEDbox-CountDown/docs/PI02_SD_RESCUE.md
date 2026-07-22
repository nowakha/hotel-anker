# AnkerPI02 — SD-Rescue (fb-clock Hang)

Stand: **2026-07-22**. Nur wenn **kein Ethernet** erreichbar ist und der SSH-Watcher trotz Power-Cycles **kein Fenster** bekommt.

## Warum der Watcher scheitert (WiFi)

`fb-clock.service` hat `ExecStartPre` NTP-Wait **≤120 s**, startet danach **trotzdem**.  
Alter Player: `probe_size()` = `ffmpeg … -f null -` auf `st24.mov` (24h 4K) → Hang.

Bei **nur WiFi**: Association/DHCP oft **nach** diesem Fenster (oder IP ≠ `192.168.8.106`).  
SSH/Tailscale kommen erst, wenn der Hang schon da ist → Watcher sieht **nie** TCP/22.

Log-Beweis: `docs/_pi02_rescue.log` nur Startzeile, **kein** `SUCCESS`.

## Vor SD: Ethernet prüfen (bevorzugt)

**Direkt PC↔Pi ohne Switch geht** (Pi 4 auto-MDIX, APIPA `169.254.*`). Anleitung: [`PI02_DIRECT_ETH_RESCUE.md`](./PI02_DIRECT_ETH_RESCUE.md).

1. Ethernet-Kabel Pi ↔ PC (oder Router/Switch, Port am Pi erreichbar?).
2. Watcher: `scripts/pi02_rescue_direct_eth.ps1` (oder `pi02_rescue_watch.ps1` — pollt `.106` + Tailscale + **`169.254.*`**).
3. Power-Cycle → SSH-Fenster während NTP-Wait → Mask + Deploy.

**Serial:** `cmdline` hat `console=serial0,115200` (HDMI-Console aus). Realistisch nur mit UART-Adapter an GPIO — oft schwerer als SD am Decken-Screen. Kein Boot-Experiment nötig.

---

## SD-Rescue — Schritt für Schritt (sicher)

### A) Vorbereitung

- Repo auf dem PC: gepatchtes `WerbeLEDbox-CountDown/fb_clock_play.py` (muss `ffprobe` + Kommentar `Never decode` enthalten).
- Optional WSL-Helper: `scripts/pi02_sd_rescue_wsl.sh` (nach Mount aufrufen).
- Pi **komplett stromlos** (nicht nur reboot — SD nicht unter Last ziehen).

### B) Karte entnehmen & am PC

1. SD aus AnkerPI02 entnehmen, in Reader am Windows-PC stecken.
2. Windows zeigt meist nur die **boot**-Partition (FAT32, oft `bootfs`). Die **root**-Partition ist **ext4** → unter Windows nativ nicht schreibbar → **WSL** nutzen.

### C) In WSL mounten

```bash
# Adapter finden (typisch sdb / sdc — NICHT die Windows-Systemdisk!)
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT

# Beispiel: /dev/sdb1 = boot (vfat), /dev/sdb2 = root (ext4)
sudo mkdir -p /mnt/pi-boot /mnt/pi-root
sudo mount -t vfat /dev/sdX1 /mnt/pi-boot
sudo mount -t ext4 /dev/sdX2 /mnt/pi-root
```

`sdX` durch echte Device-Buchstaben ersetzen. Bei Zweifel: Größe ~SD-Karte prüfen, nie `sda` wenn das die NVMe/SSD ist.

### D) fb-clock maskieren (Boot bleibt intakt)

**Nicht** `cmdline.txt` / `config.txt` anfassen (außer Notfall-Recovery unten).

Mask = Unit zeigt auf `/dev/null` (systemd startet den Service dann nicht):

```bash
ROOT=/mnt/pi-root
# Unit-Datei umbenennen (Backup) falls vorhanden
if [ -f "$ROOT/etc/systemd/system/fb-clock.service" ]; then
  sudo mv "$ROOT/etc/systemd/system/fb-clock.service" \
          "$ROOT/etc/systemd/system/fb-clock.service.DISABLED"
fi
# multi-user Wants-Symlink entfernen
sudo rm -f "$ROOT/etc/systemd/system/multi-user.target.wants/fb-clock.service"
# Mask-Symlink setzen
sudo ln -sfn /dev/null "$ROOT/etc/systemd/system/fb-clock.service"
# Prüfen
ls -la "$ROOT/etc/systemd/system/fb-clock.service"
ls -la "$ROOT/etc/systemd/system/multi-user.target.wants/" | grep -i fb || true
```

### E) Optional: gepatchten Player auf die rootfs legen

Vom Windows-Repo-Pfad (WSL: `/mnt/c/Users/User/Documents/Cursor Projects/Hotel Anker/...`):

```bash
SRC="/mnt/c/Users/User/Documents/Cursor Projects/Hotel Anker/WerbeLEDbox-CountDown/fb_clock_play.py"
DST="/mnt/pi-root/home/user/WerbeLEDbox-CountDown/fb_clock_play.py"
sudo cp "$SRC" "$DST"
sudo chown 1000:1000 "$DST"   # typische Pi-user UID; sonst belassen
grep -n 'ffprobe\|Never decode\|-f null' "$DST" | head
# Erwartung: ffprobe + Never decode; kein aktives -f null Decode
```

### F) Sync & sicher auswerfen

```bash
sync
sudo umount /mnt/pi-boot
sudo umount /mnt/pi-root
```

Dann in Windows „Hardware sicher entfernen“ / Reader auswerfen. SD zurück in den Pi, Strom an.

### G) Nach Boot (SSH wieder da)

```bash
ssh user@192.168.8.106   # oder WiFi-IP / Tailscale
systemctl is-enabled fb-clock    # erwartet: masked
systemctl is-active fb-clock     # erwartet: inactive
grep -n 'ffprobe\|Never decode' ~/WerbeLEDbox-CountDown/fb_clock_play.py | head
```

Erst danach Unit aus Repo deployen, **unmask**, `daemon-reload`, `enable --now` — siehe `docs/NEXT_AGENT.md`.

---

## Was NICHT anfassen

| Datei | Warum |
|--------|--------|
| `/boot/firmware/cmdline.txt` oder `/boot/cmdline.txt` | Boot-Risiko; SD oft nicht erneut entnehmbar |
| `rotate=` / Mode-Experimente | Verboten ohne Recovery-Plan |
| Beliebige `config.txt`-Umbauten ohne Backup | Gleiches Risiko |

**Nur wenn der Pi gar nicht mehr bootet:** Boot-Partition mounten und `cmdline.txt` **1:1** ersetzen durch die eine Zeile aus [`../media/cmdline.recovery.txt`](../media/cmdline.recovery.txt).

## Checkliste Erfolg

- [ ] `fb-clock` masked / nicht in `multi-user.target.wants`
- [ ] Gepatchtes `fb_clock_play.py` auf rootfs (ffprobe)
- [ ] `sync` + sauber unmount
- [ ] Nach Boot: SSH OK, Splash ggf. sichtbar, **kein** Sofort-Hang
- [ ] SESSION_LOG + LEARNINGS aktualisieren → commit → push
