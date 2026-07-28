#!/usr/bin/env python3
"""Repair UniFi Hotspot Landing Page app on Hotel Anker UDM.

When /guest/s/default/ returns HTTP 200 with an empty body and server.log
shows FileNotFoundException for app-unifi-hotspot-portal/index.html, the
SPA package under the site data dir is incomplete. Re-extract the stock
zip embedded in Network Application ace.jar.

Usage (from Windows, Paramiko):
  py WerbeLEDbox-CountDown/scripts/repair_unifi_hotspot_portal.py

Requires secrets/unifi.hotelanker.yml (ssh host/user/password).
Does not reboot the UDM and does not write MongoDB.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

import paramiko
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "secrets" / "unifi.hotelanker.yml"

REMOTE_FIX = r"""
python3 - <<'PY'
import io, os, shutil, zipfile
from pathlib import Path

ace = zipfile.ZipFile('/usr/lib/unifi/lib/ace.jar')
inner = zipfile.ZipFile(io.BytesIO(ace.read('BOOT-INF/lib/internal-dependencies.jar')))
blob = inner.read('app-unifi-hotspot-portal.zip')
dst = Path('/data/unifi/data/sites/default/app-unifi-hotspot-portal')
bak = Path('/data/unifi/data/sites/default/app-unifi-hotspot-portal.bak-repair')
if bak.exists():
    shutil.rmtree(bak)
if dst.exists():
    shutil.move(str(dst), str(bak))
dst.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    z.extractall(dst)
os.system(f'chown -R unifi:unifi {dst}')
print('version', (dst / '.version').read_text().strip())
print('index_bytes', (dst / 'index.html').stat().st_size)
print('ok')
PY
curl -sS -o /tmp/portal_index.html -w "index %{http_code} %{size_download}\n" -m 10 http://127.0.0.1:8880/guest/s/default/
curl -sS -o /tmp/portal_cfg.json -w "config %{http_code} %{size_download}\n" -m 10 http://127.0.0.1:8880/guest/s/default/hotspotconfig
python3 -c "import json;d=json.load(open('/tmp/portal_cfg.json'))['data'][0];print(d.get('title'), d.get('button_text'), d.get('auth'))"
rm -rf /data/unifi/data/sites/default/app-unifi-hotspot-portal.bak-repair
"""


def main() -> int:
    if not SECRETS.is_file():
        print(f"missing secrets: {SECRETS}", file=sys.stderr)
        return 1
    cfg = yaml.safe_load(SECRETS.read_text(encoding="utf-8")) or {}
    ssh = cfg.get("ssh") or {}
    host = ssh.get("host") or "192.168.1.254"
    user = ssh.get("user") or "root"
    password = ssh.get("password")
    if not password:
        print("no ssh.password in secrets", file=sys.stderr)
        return 1

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=20, allow_agent=False, look_for_keys=False)
    try:
        _i, out, err = client.exec_command(REMOTE_FIX, timeout=120)
        sys.stdout.write(out.read().decode(errors="replace"))
        e = err.read().decode(errors="replace")
        if e.strip():
            sys.stderr.write(e)
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
