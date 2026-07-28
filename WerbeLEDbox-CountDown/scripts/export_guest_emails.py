#!/usr/bin/env python3
"""Export guest emails from UDM → local CSV.

Usage:
  py WerbeLEDbox-CountDown/scripts/export_guest_emails.py
  py WerbeLEDbox-CountDown/scripts/export_guest_emails.py --out path.csv

Pulls /data/hotel-anker/guest-emails/guests.csv (and refreshes SQLite→CSV on UDM).
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import paramiko
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "secrets" / "unifi.hotelanker.yml"
DEFAULT_OUT = ROOT / "guest-email-portal" / "exports" / "guest-emails.csv"

REMOTE_REFRESH = r"""
python3 - <<'PY'
import sys
sys.path.insert(0, '/data/hotel-anker/guest-email-portal')
from storage import GuestStore
p = GuestStore('/data/hotel-anker/guest-emails').export_csv()
print(p)
print('rows', sum(1 for _ in open(p, encoding='utf-8')) - 1)
PY
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Export Hotel Anker guest WiFi emails from UDM")
    ap.add_argument("--out", type=Path, default=None, help="Local CSV path")
    args = ap.parse_args()

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

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = args.out or (DEFAULT_OUT.parent / f"guest-emails-{stamp}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    latest = DEFAULT_OUT

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password, timeout=20, allow_agent=False, look_for_keys=False)
    try:
        _i, stdout, stderr = client.exec_command(REMOTE_REFRESH, timeout=60)
        sys.stdout.write(stdout.read().decode(errors="replace"))
        err = stderr.read().decode(errors="replace")
        if err.strip():
            sys.stderr.write(err)
        sftp = client.open_sftp()
        try:
            sftp.get("/data/hotel-anker/guest-emails/guests.csv", str(out))
            sftp.get("/data/hotel-anker/guest-emails/guests.csv", str(latest))
        finally:
            sftp.close()
    finally:
        client.close()

    text = out.read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    n = max(0, len(lines) - 1)
    print(f"wrote {out} ({n} guests)")
    print(f"also {latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
