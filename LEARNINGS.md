# Hotel Anker — Learnings & Handoff

Stand: **2026-07-22**. Ziel: eine andere Cursor-Instanz auf einem anderen Rechner kann ohne mündlichen Kontext weiterarbeiten.

## Repo & Secrets

- Remote: `https://github.com/nowakha/hotel-anker.git` (privat halten — enthält SSH-Passwörter).
- Credentials: `WerbeLEDbox-CountDown/secrets/ankerpi0{1,2}.credentials.yml` — **bewusst getrackt**.
- SSH: Passwort-Login aktiv; optional Key `~/.ssh/id_ed25519` mit Comment `hotel-anker-dev@TABLETHI10MAX`. Pubkey in `docs/ANKERPI01.md`. Fragment: `WerbeLEDbox-CountDown/ssh/config.fragment`.
- Private Key liegt **nicht** im Repo (nur Passwort + Pubkey). Auf neuem Rechner: Key neu erzeugen und `authorized_keys` auf den Pis ergänzen, oder Passwort nutzen.

## Hardware-Wahrheit

1. **AnkerPI01** (`AnkerPI01.local`, DHCP oft `192.168.8.108`): SPI0, `ws2812put.service`, SharedArray `shm://ws2812` Shape `(1179, 3)`.
2. **AnkerPI02** (`192.168.8.106`): HDMI **3440×1440@50**, `fb-clock.service`, Splash `media/boot_splash_3440x1440.*`. Video `media/clock_24h.mp4` fehlt oft lokal — muss auf den Pi.
3. **Teensy** am PI02 USB (`16c0:0483`, SN `2923720`): Ziel-Firmware `teensy/anker_pixel_pusher` (OctoWS2811, `ANKR`-Frames, 8×512). Ersetzt den früheren **Pico**.
4. **Pico**-Tree bleibt als Lab/Protokoll-Referenz; nicht als Live-Pfad dokumentieren.

## Print / Bespannung

- Versandpaket: `Richnerstutz-Bespannung-Paket/` (Anfrage + Druck + Opazität + Overlays).
- Arbeitsmaster: `assets/kendu-flowbox-2m-print/` (Generatoren schreiben hierhin; Paket ist Export-Kopie).
- Rahmen innen **2100 mm**, Textil→LED **45 mm** (siehe `06-fotos-vom-rahmen/GEOMETRIE-3D.md`).
- Original-Rahmenfotos (JPG) fehlen noch im Paket — nur Schemas/Auswertung committed.

## Was 2026-07-22 aufgeräumt wurde

- Entfernt: frühe Mockups `assets/kendu-flowbox-2m/`, Debug-PNGs `_debug/_diag/_proof/_verify`, doppelte `canva-layers/`, Logo-Crop-Experimente, veraltete Anfrage-Kopie unter `docs/`.
- Generator-Scripts: keine absoluten `C:\Users\...` / Cursor-Project-Mirror-Pfade mehr.
- Secrets: gitignore gelockert, PI01-IP auf `.108` korrigiert, PI02-Credentials ergänzt.

## Offene Arbeit

- Countdown-Producer auf PI01 (nach `ws2812put`).
- Teensy-Firmware flashen/validieren vs. Stock-Kendu.
- `clock_24h.mp4` erzeugen/deployen.
- Richnerstutz-Mail inkl. Rahmen-JPGs.

## Kontakt (Technik)

Harald Nowak · Modernlight · Harald.Nowak@modernlight.ch · +41 76 579 84 54 · Wangenstrasse 57, 3018 Bern  
Regel: `.cursor/rules/harald-nowak-modernlight.mdc`
