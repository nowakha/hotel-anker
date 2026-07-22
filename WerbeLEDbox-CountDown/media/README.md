# media/

## Production target

```
clock_24h.mp4
```

Exactly **86400 s**, t=0 = 00:00:00, H.264, **860×360**, 25 fps, `-g 25`.  
See [`../docs/ANKERPI02.md`](../docs/ANKERPI02.md).

## Provisional (2026-07-22)

On AnkerPI02 disk (not in git — too large):

```
st24.mov
```

4K H.264 in MOV, 24h, starts at 00:00. Crop in player: top 386 / bottom 127.  
Service unit currently points here until `clock_24h.mp4` exists.

## Do not commit

`*.mov`, large `*.mp4`, encode scratch files — see root `.gitignore`.
