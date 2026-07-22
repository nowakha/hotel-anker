# media/

## Production clock (AnkerPI02) — default: live

**Default:** live renderer — no video file needed (avoids ffmpeg full-decode hang):

```bash
python3 fb_clock_live.py
# or systemd: bash scripts/install_fb_clock_live_service.sh
```

Preview (PC): `python fb_clock_live.py --preview media/clock_live_preview.png`

## Optional designed MP4 / MOV

```
clock_24h.mp4   # production target: 86400 s, t=0=00:00, H.264 860×360, 25 fps, -g 25
st24.mov        # provisional 4K on Pi disk (not in git); crop top 386 / bottom 127
```

Synthetic helper (no source film; slow for full day):

```powershell
py -3 scripts/gen_clock_24h.py --seconds 120 --out media/clock_24h_smoke.mp4
py -3 scripts/gen_clock_24h.py --out media/clock_24h.mp4
```

From `st24.mov` on workstation (NVENC, crop Premiere L0/T386/R0/B127 → 860×360):

```powershell
# FFmpeg often not on PATH — use WinGet Gyan full_build bin. Probe with ffprobe only (never -f null on 24h).
ffmpeg -y -i $env:USERPROFILE\Videos\st24.mov -an `
  -vf "crop=3840:1647:0:386,scale=860:360:flags=lanczos" -r 25 `
  -c:v h264_nvenc -preset p4 -rc vbr -cq 23 -b:v 0 -g 25 -pix_fmt yuv420p `
  media\clock_24h.mp4
```

Progress/logs when running overnight: `media/_encode_clock_24h.log` / `.progress` (gitignored).

See [`../docs/ANKERPI02.md`](../docs/ANKERPI02.md).

## Do not commit

`*.mov`, large `*.mp4`, encode scratch files — see root `.gitignore`. Splash + recovery cmdline stay tracked.
