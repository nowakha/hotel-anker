#!/usr/bin/env python3
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "scripts" / "countdown_waves_64.py"
s = spec_from_file_location("cw", p)
m = module_from_spec(s)
s.loader.exec_module(m)
print("ASSETS", m.ASSETS, m.ASSETS.exists())
print("find_bp", m._find_asset("hotel-anker-blueprint-v2.png"))
print("find_lg", m._find_asset("hotel-anker-countdown-logo-dark.png"))
bp = m.blueprint_mask_64()
lg = m.logo_mask_64()
print("bp", None if bp is None else int((bp > 0.2).sum()))
print("lg", None if lg is None else int((lg > 0.2).sum()))
fr = m.render_frame(0.0)
print(
    "white",
    int(((fr[:, :, 0] > 200) & (fr[:, :, 1] > 200) & (fr[:, :, 2] > 200)).sum()),
    "gold",
    int(((fr[:, :, 0] > 200) & (fr[:, :, 1] > 150) & (fr[:, :, 2] < 100)).sum()),
)
