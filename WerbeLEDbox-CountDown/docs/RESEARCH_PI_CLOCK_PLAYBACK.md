# Research: Pi 4 wall-clock video → framebuffer (AnkerPI02)

Stand: **2026-07-22**. Online-/Forum-Recherche zu unserem Problem (Hotel Anker / AnkerPI02).

## Unser Problem (Kurz)

| Item | Wert |
|------|------|
| Host | Raspberry Pi 4, Bookworm, HDMI `/dev/fb0` RGB565, Panel **3440×1440** |
| Inhalt | 24h-Clock-Video, t=0 = Mitternacht, Sync **Europe/Zurich** |
| Quelle | `st24.mov` ~13 GB, **3840×2160 H.264**, 86400 s, Crop T386/B127 |
| Ziel | Höchste nachhaltige Framerate für wall-clock-synced Playback auf fb0 |
| Gemessen | Soft-Decode ~5–14 s/Frame (~0.1 fps); `h264_v4l2m2m` auf 4K **FAIL**; OpenCV SIGBUS; UV unter Last `0x50000` |

Produktionspfad bereits geplant: `clock_24h.mp4` **860×360** H.264 `-g 25`.

---

## 1. Kernbefund: Pi 4 kann **kein** 4K H.264 in Hardware

Offizielle Spec ([raspberrypi.com/products/raspberry-pi-4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/specifications/)):

- **H.265 / HEVC:** bis **4Kp60** HW-Decode  
- **H.264:** bis **1080p60** HW-Decode / 1080p30 Encode  

Engineer-Bestätigung ([linux#3484](https://github.com/raspberrypi/linux/issues/3484), [Forum t=243414](https://forums.raspberrypi.com/viewtopic.php?t=243414)):

> *4k H264? That's never going to be supported as the hardware can't do it.*  
> Max H.264 HW ≈ **1920×1920**; 4K nur über **HEVC**.

**Für uns:** `st24.mov` (4K H.264) **muss** software-dekodiert werden → erklärt 5–14 s/Frame und warum Bench `D_v4l2m2m` FAIL. `ffmpeg -hwaccel drm` hilft bei H.264-4K nicht sinnvoll; DRM-hwaccel ist vor allem der HEVC-Stateless-Pfad.

---

## 2. Was andere machen (nach Thema)

### 2.1 Hardware-Decode → Display (Bookworm / Pi 4)

| Ansatz | Kurz | Links |
|--------|------|-------|
| **mpv + DRM/KMS** | `--vo=gpu --gpu-context=drm` oder `--vo=drm` + `--hwdec=v4l2m2m-copy` (H.264 ≤1080p) bzw. `--hwdec=drm` / `drm-copy` (HEVC) | [Forum t=266123](https://forums.raspberrypi.com/viewtopic.php?t=266123), [t=345598](https://forums.raspberrypi.com/viewtopic.php?t=345598), [mpv#10773](https://github.com/mpv-player/mpv/issues/10773) |
| **ffmpeg `h264_v4l2m2m`** | Stateful V4L2; guter Decode, aber Output meist YUV → RGB oft noch CPU; RPiOS-ffmpeg ist gepatcht | [SO 108613](https://raspberrypi.stackexchange.com/questions/108613/rpi-4-ffmpeg-how-to-get-hardware-h-264-decoding-to-work), [Forum t=343593](https://forums.raspberrypi.com/viewtopic.php?t=343593), [linux#6837](https://github.com/raspberrypi/linux/issues/6837) |
| **GStreamer → fbdev** | Signage-Praxis (Anthias/Screenly): `v4l2h264dec` → `v4l2convert` (ISP scale+CSC) → `fbdevsink` — HW bis RGB565, ~40 fps auf Pi3 @1080p | [Anthias PR #2972](https://github.com/Screenly/Anthias/pull/2972) |
| **ffmpeg → `-f fbdev`** | Anthias hat das **verworfen**: HW-Decode ok, aber YUV→RGB565 auf ARM nur ~**6 fps** (kein NEON-rgb565) | gleiches PR |
| **omxplayer / MMAL** | Legacy, 32-bit; auf Bookworm 64-bit / Pi4 **obsolet** | Forum-Threads 2019–2022 |

**Gilt für uns:** Wir brauchen fb0 RGB565 ohne X. Anthias-Pfad (GStreamer ISP→fbdev) ist das nächste „Produktions-Muster“ — aber nur sinnvoll, wenn die Datei **≤1080p H.264** ist. mpv `--vo=drm` braucht DRM-Master (Konflikt, wenn schon etwas card0 hält).

### 2.2 Seek / Einzelbild-Performance (v4l2m2m)

Stateful V4L2-Seek war jahrelang kaputt/fragil (Header nach Seek, Buffer-Leaks). Kernel-Fixes (u. a. [PR #3790](https://github.com/raspberrypi/linux/pull/3790), [Forum t=281979](https://forums.raspberrypi.com/viewtopic.php?t=281979)); FFmpeg-Seek mit stateful Decoder gilt weiter als **unzuverlässig** für „jeder Seek ein frisches Frame“.

**Gilt für uns:** Unser aktuelles Modell (pro Tick: `-ss` + 1 Frame) ist der **teuerste** Pfad. Community-Konsens für Timed Playback: **kontinuierlich abspielen** und periodisch gegen Wall-Clock resyncen — nicht jedes Frame neu seeken.

### 2.3 Video ohne X auf dem Framebuffer

- mpv DRM: [t=266123](https://forums.raspberrypi.com/viewtopic.php?t=266123), [t=354884](https://forums.raspberrypi.com/viewtopic.php?t=354884) (DRM-Master / Connector-Fallen)
- Anthias: GStreamer fbdevsink (siehe oben)
- VLC Bookworm: ohne MMAL oft black / braucht Lease oder DRM-Master

### 2.4 Wall-clock / „Video-Clock“ Sync

Niemand hat exakt „86400 s 4K → fb0 RGB565, t=midnight“ als fertiges Produkt. Nächste Verwandte:

| Projekt | Idee | Relevanz |
|---------|------|----------|
| [XtendedGreg/digital-clock-with-video](https://github.com/XtendedGreg/digital-clock-with-video) | Clock-Overlay + **vorgescaltes** Loop-Video auf fb; warnt: lange/hohe Bitrate → RAM-Kill | Pre-scale = unser `clock_24h`; Overlay ≠ unser „Video ist die Uhr“ |
| [mpv#1272](https://github.com/mpv-player/mpv/issues/1272) | Vorschlag `--wallclock-start=TIMESTAMP` (nie nativ) | Konzept: Position = now − midnight |
| Syncplay / raspi-video-sync / FleetSign | Multi-Pi Sync via NTP + IPC | Wir brauchen nur **einen** Pi + NTP; Muster: `--start=HH:MM:SS` + Resync |
| Adafruit pi_video_looper | Loop-Signage, früher omxplayer | Kein Wall-Clock-Offset |

**Praktisches Muster (Community):** NTP ok → `mpv --start=$(date +%H:%M:%S)` (oder IPC `seek`) auf **24h-Datei**, dann alle N Minuten Position korrigieren. Kein Frame-für-Frame-Extract.

### 2.5 OpenCV VideoCapture auf dem Pi

- Schwer/langsam; apt-OpenCV zieht riesige Deps (bei uns OOM/Reboot)
- SIGBUS auf ARM oft Alignment/Backend (GStreamer vs FFmpeg), nicht „Pi-spezifisch einzigartig“ — [opencv#28921](https://github.com/opencv/opencv/issues/28921) (Alignment), Forum-Latenz-Threads
- Community-Empfehlung für Signage: **OpenCV nicht** als Video-Player; ffmpeg/mpv/gstreamer

**Gilt für uns:** OpenCV als Capture-Loop ad acta; Hybrid ffmpeg→PIL/numpy→fb bleibt Interim.

### 2.6 Undervoltage / 4K-Last

- `0x50000` = Under-voltage **has occurred** (History), aktuell ok möglich — [peppe8o](https://peppe8o.com/raspberry-pi-undervoltage-detected/)
- Spec: **5 V / ≥3 A** (ideal 5.1 V), offizielles USB-C-PSU; dünne Kabel = Drop
- Signage-Guides: aktives Cooling bei 24/7 Video; Underclock nur Symptom-Linderung

**Gilt für uns:** PSU fixen bleibt Pflicht; Underclock während Play ist Workaround, kein Ersatz. Idle `0x0` (2026-07-22) ≠ Last ok.

### 2.7 Pre-Transcode Best Practice (Signage)

Übereinstimmend PiSignage / ScreenTinker / LibreELEC / Forum:

1. **Auflösung ≈ Display-Pipeline** (nicht Roh-4K speichern, wenn Panel/Upscale ohnehin soft ist)
2. **H.264** für maximale HW-Kompatibilität auf Pi0–4 (≤1080p)
3. Kurzes GOP für Seek (`-g` ≈ fps) — wir: `-g 25`
4. 4K nur als **HEVC**, wenn wirklich 4K HW nötig — und dann DRM/rpi-ffmpeg

**Gilt für uns:** `860×360` H.264 ist exakt die Community-Empfehlung „transcode down before the Pi“, nur aggressiver (Panel bekommt NEAREST-Upscale).

---

## 3. Was trifft AnkerPI02 konkret?

| Fremd-Lösung | Passt? | Warum |
|--------------|--------|-------|
| 4K H.264 + v4l2m2m | **Nein** | HW-Limit 1080p |
| 4K HEVC + mpv drm | Theoretisch | Re-Encode 13 GB nötig; Seek/Stateful-Themen; DRM vs fb0-Pfad |
| Seek jedes Frame (ffmpeg -ss) | Schlecht | Teuerster Pfad; Community meidet das |
| Pre-transcode 860×360 + continuous play | **Ja** | Signage-Standard; passt zu unserem Encode |
| GStreamer v4l2h264dec→v4l2convert→fbdev | **Ja nach Encode** | Bewährt für RGB565 fb0; HW scale/CSC |
| mpv --vo=drm + --start=wall | **Ja nach Encode** | Einfach; DRM-Master klären |
| OpenCV VideoCapture | **Nein** | SIGBUS/Deps/Last |
| apt python3-opencv auf 2 GB | **Nein** | OOM |

---

## 4. Ranked Recommendations (AnkerPI02)

### R1 — Sofort (höchste Hebelwirkung): `clock_24h.mp4` 860×360 fertigstellen & deployen

Ohne das bleibt jede Hardware-Pipeline am 4K-H.264-Limit hängen. Encode auf Workstation (NVENC) → scp/rsync → `VIDEO=` umstellen. Erwartung: Seek-Extract von Sekunden → **Subsekunden** (GOP 1 s); Continuous Play → **nahe Echtzeit**.

### R2 — Nächstes Experiment: Continuous wall-clock play (nicht Frame-Extract)

Statt `ffmpeg -ss` pro Tick:

```bash
# Konzept — nach Deploy von clock_24h.mp4 (860×360 H.264)
START=$(python3 -c "from datetime import datetime; from zoneinfo import ZoneInfo; \
n=datetime.now(ZoneInfo('Europe/Zurich')); \
print(f'{n.hour:02d}:{n.minute:02d}:{n.second:02d}')")

# Variante A: mpv DRM (kein X; Connector prüfen)
mpv --vo=drm --hwdec=v4l2m2m-copy --start="$START" --loop-file=inf \
  --no-audio media/clock_24h.mp4

# Variante B: GStreamer → fb0 (Anthias-Muster; Caps an fb0 anpassen)
# gst-launch-1.0 playbin uri=file://… video-sink="… v4l2convert ! video/x-raw,format=RGB16 ! fbdevsink device=/dev/fb0"
```

Resync: alle 60–300 s Position = Sekunden seit Mitternacht (NTP vorausgesetzt). Flip 180° ggf. `videoflip` / mpv `--video-rotate=180`.

### R3 — PSU + Last-Verify

Offizielles **5.1 V / 3 A** (oder gemessen ≥4.75 V unter Decode). Unter Play erneut `vcgencmd get_throttled` — Ziel dauerhaft `0x0` inkl. Sticky-Bits nach frischem Boot.

### R4 — Optional später: HEVC-4K nur wenn Qualitätsbedarf

Nur wenn 860×360 optisch nicht reicht: `st24` → HEVC 3440×1440 (oder Panel-nativ), rpi-ffmpeg/`-hwaccel drm`, mpv drm. Deutlich mehr Aufwand; Seek-Resync testen. **Nicht** Priorität gegenüber R1/R2.

### R5 — Vermeiden

- OpenCV als Decoder  
- apt `python3-opencv` auf diesem Pi  
- `ffmpeg … -f null -` auf 24h-4K  
- Häufiges Hard-Seek auf 4K-H.264  
- Autostart unmask solange nur `st24.mov` + schwaches PSU  

---

## 5. Empfohlenes nächstes Experiment (konkret)

1. Warten bis `media/clock_24h.mp4` fertig (Workstation-Encode).  
2. Auf PI02 kopieren; `fb-clock` **masked** lassen.  
3. **Bench A:** `ffmpeg -ss <now> -i clock_24h.mp4 -frames:v 1 -f null -` Timing (Soll ≪ 1 s).  
4. **Bench B:** 60 s Continuous `mpv --vo=drm --hwdec=v4l2m2m-copy --start=…` **oder** GStreamer→fbdevsink; FPS + `get_throttled` loggen.  
5. Wenn B stabil & `0x0`: kleinen Resync-Wrapper (alle 60 s) bauen; erst dann Unit unmasken mit konservativem Intervall.

Erfolgskriterium: nachhaltig **≥1 fps** wall-synced (besser: flüssig ≥10–25 fps continuous), throttled `0x0`, kein Reboot.

---

## 6. Quellen (Auswahl)

- [Pi 4 Specs — H.264 1080p / HEVC 4K](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/specifications/)
- [linux#3484 — no 4K H.264 HW](https://github.com/raspberrypi/linux/issues/3484)
- [SO — h264_v4l2m2m + YUV→RGB CPU](https://raspberrypi.stackexchange.com/questions/108613/rpi-4-ffmpeg-how-to-get-hardware-h-264-decoding-to-work)
- [Forum t=343593 — v4l2m2m / drm HEVC](https://forums.raspberrypi.com/viewtopic.php?t=343593)
- [Forum t=266123 — mpv DRM hwdec](https://forums.raspberrypi.com/viewtopic.php?t=266123)
- [Anthias #2972 — GStreamer fbdev RGB565](https://github.com/Screenly/Anthias/pull/2972)
- [mpv#1272 — wallclock sync Idee](https://github.com/mpv-player/mpv/issues/1272)
- [linux#6554 / #6837 — v4l2m2m Kernel/ffmpeg](https://github.com/raspberrypi/linux/issues/6554)
- [Undervoltage / 0x50000](https://peppe8o.com/raspberry-pi-undervoltage-detected/)
- Interne Messungen: `docs/SESSION_LOG.md` (Bench C2/D, Max-FPS ~0.1 auf st24)

---

*Recherche für Handoff; keine Boot-/cmdline-Änderungen empfohlen.*
