#!/usr/bin/env python3
"""Deprecated entrypoint — use build_richnerstutz_druckdaten.py.

Kept so older docs/commands still rebuild the corrected CMYK+bleed masters.
"""

from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).with_name("build_richnerstutz_druckdaten.py")),
        run_name="__main__",
    )
