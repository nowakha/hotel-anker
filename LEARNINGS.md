# Hotel Anker — Learnings & Handoff

Stand: **2026-07-22 ~16:10 CEST** (Workstation **MLT-NITRO5-HN**).  
Ziel: eine andere Cursor-Instanz auf einem anderen Rechner kann ohne mündlichen Kontext weiterarbeiten.

Detaillierte Chronik: [`WerbeLEDbox-CountDown/docs/SESSION_LOG.md`](./WerbeLEDbox-CountDown/docs/SESSION_LOG.md).

## Repo & Secrets

- Remote: `https://github.com/nowakha/hotel-anker.git` (**privat halten** — enthält SSH-Passwörter).
- Credentials: `WerbeLEDbox-CountDown/secrets/ankerpi0{1,2}.credentials.yml` — **bewusst getrackt**.
- SSH-User/Passwort beider Pis: `user` / `12345678` (PasswordAuthentication an).
- SSH-Keys gesehen:
  - Historisch: `hotel-anker-dev@TABLETHI10MAX` (Pubkey in `docs/ANKERPI01.md`).
  - Neu 2026-07-22: `hotel-anker-dev@MLT-NITRO5-HN` auf beiden Pis in `authorized_keys`.
- Private Keys **nicht** im Repo. Fragment: `WerbeLEDbox-CountDown/ssh/config.fragment`.
- GitHub: `gh` eingeloggt als `nowakha`. Tailscale Desktop: `nowakha@googlemail.com`.

## Hardware-Wahrheit

1. **AnkerPI01** — Pi Zero 2 W: SPI0 LED putter. mDNS `AnkerPI01.local`. DHCP zuletzt oft **`192.168.8.102`** (Docs nannten auch `.108` — immer mDNS bevorzugen). Tailscale: **noch nicht** zuverlässig installiert.
2. **AnkerPI02** — Pi 4: HDMI **3440×1440@50**, `fb-clock.service`, Splash `media/boot_splash_3440x1440.*`. LAN **`192.168.8.106`**. Tailscale: **`ankerpi02` / `100.103.54.63`** (war gejoint; nach Hang/Reboot ggf. erneut prüfen).
3. **SD-Karte PI02 nicht mehr entnehmbar** → Boot-Schutz oberste Priorität (siehe Workflow-Regel).
4. **Teensy** am PI02 USB: Live-Pfad für 8×512; Pico = Lab.
5. Provisorisches Clock-Video auf PI02: `media/st24.mov` (4K, 24h, t=0 = 00:00). Produktion bleibt `clock_24h.mp4` 860×360 `-g 25`.

## Kritische Falle (2026-07-22)

`fb_clock_play.probe_size()` mit `ffmpeg -i FILE -f null -` dekodiert **die gesamte Datei**. Bei 24h 4K → Pi tot.  
**Fix im Repo:** `ffprobe` / `ffmpeg -i` ohne Output. **Vor dem nächsten `fb-clock`-Start auf den Pi deployen.**

## Encode / Transfer

- Quelle Workstation: `C:\Users\User\Videos\st24.mov` (auch USB-Kopie).
- Crop: Top 386, Bottom 127, Left/Right 0.
- USB→SD rsync: **~13 min @ ~17 MB/s**, Size OK.
- NVENC auf 3080: Driver ≥610 nötig für aktuelles FFmpeg 8.x; Encode-ETA ~6 h bei 860×360.

## Print / Bespannung

Unverändert: `Richnerstutz-Bespannung-Paket/`, Rahmen 2100 mm, Textil→LED 45 mm.

## Offene Arbeit (Priorität)

1. **PI02 wieder online** (Stand 16:08 offline nach Reboot) → patched `fb_clock_play.py` + Unit deployen → Uhr starten.
2. DNS pin (1.1.1.1/8.8.8.8) + Tailscale auf PI01.
3. Produktion `clock_24h.mp4` NVENC encode + Upload.
4. Teensy flash/validate; Countdown-Producer PI01.

## Kontakt (Technik)

Harald Nowak · Modernlight · Harald.Nowak@modernlight.ch · +41 76 579 84 54 · Wangenstrasse 57, 3018 Bern  
Regel: `.cursor/rules/harald-nowak-modernlight.mdc`
