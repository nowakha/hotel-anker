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

Encode helper (slow for full day; prefer live clock):

```powershell
py -3 scripts/gen_clock_24h.py --seconds 120 --out media/clock_24h_smoke.mp4
py -3 scripts/gen_clock_24h.py --out media/clock_24h.mp4
```

See [`../docs/ANKERPI02.md`](../docs/ANKERPI02.md).

## Do not commit

`*.mov`, large `*.mp4`, encode scratch files — see root `.gitignore`. Splash + recovery cmdline stay tracked.
