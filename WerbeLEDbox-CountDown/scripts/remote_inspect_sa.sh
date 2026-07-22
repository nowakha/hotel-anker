#!/bin/bash
set -euo pipefail
cd "$HOME/WerbeLEDbox-CountDown"
source .venv/bin/activate
python - <<'PY'
import SharedArray as sa, inspect
print("file", sa.__file__)
print("=== create ===")
print(inspect.getsource(sa.create)[:2000])
print("=== delete ===")
print(inspect.getsource(sa.delete)[:1500])
PY
