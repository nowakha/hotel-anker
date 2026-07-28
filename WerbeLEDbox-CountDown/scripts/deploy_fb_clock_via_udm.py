#!/usr/bin/env python3
"""Watch for AnkerPI02 via UDM jump, deploy smooth fb-clock, enable boot autostart.

The non-stuttering unit uses --max-drift 0.35 / --resync-every 0 (no hard kill
every 120s). Prefer this over Tailscale-only deploy when the Pi is only on
VLAN2 (Windows often cannot route there).

Usage:
  py WerbeLEDbox-CountDown/scripts/deploy_fb_clock_via_udm.py
  py WerbeLEDbox-CountDown/scripts/deploy_fb_clock_via_udm.py --once
"""

from __future__ import annotations

import argparse
import base64
import json
import ssl
import sys
import time
from http.cookiejar import CookieJar
from pathlib import Path
import urllib.request

import paramiko
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "secrets"
PLAYER = ROOT / "fb_clock_play.py"
UNIT = ROOT / "systemd" / "fb_clock.service"
PI02_MAC = "e4:5f:01:e8:92:28"
FALLBACK_IPS = [
    "192.168.2.222",
    "192.168.1.222",
    "192.168.1.106",
    "192.168.2.106",
    "100.103.54.63",
]


def load(name: str) -> dict:
    return yaml.safe_load((SECRETS / name).read_text(encoding="utf-8")) or {}


def unifi_clients() -> list[dict]:
    cfg = load("unifi.hotelanker.yml")
    host = cfg["console_url"].rstrip("/")
    ctx = ssl._create_unverified_context()
    cj = CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ctx),
        urllib.request.HTTPCookieProcessor(cj),
    )

    def call(method: str, url: str, data=None, headers=None):
        hdr = {"Accept": "application/json", "Content-Type": "application/json"}
        if headers:
            hdr.update(headers)
        body = None if data is None else json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, headers=hdr, method=method)
        with opener.open(req, timeout=30) as r:
            return json.loads(r.read().decode())

    call(
        "POST",
        f"{host}/api/auth/login",
        {"username": cfg["ui"]["user"], "password": cfg["ui"]["password"]},
    )
    token = next(c.value for c in cj if c.name == "TOKEN")
    pad = token.split(".")[1] + "=" * (-len(token.split(".")[1]) % 4)
    csrf = json.loads(base64.urlsafe_b64decode(pad.encode()))["csrfToken"]
    return call(
        "GET",
        f"{host}/proxy/network/api/s/default/stat/sta",
        headers={"X-CSRF-Token": csrf},
    )["data"]


def udm_connect() -> paramiko.SSHClient:
    cfg = load("unifi.hotelanker.yml")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(
        cfg["ssh"]["host"],
        username=cfg["ssh"]["user"],
        password=cfg["ssh"]["password"],
        timeout=20,
        allow_agent=False,
        look_for_keys=False,
    )
    return c


def candidate_ips() -> list[str]:
    ips: list[str] = []
    try:
        for s in unifi_clients():
            mac = (s.get("mac") or "").lower()
            hn = s.get("hostname") or ""
            ip = s.get("ip") or ""
            if ip and (mac == PI02_MAC or hn == "AnkerPI02"):
                ips.append(ip)
                print(f"UniFi AnkerPI02 -> {ip} essid={s.get('essid')}", flush=True)
    except Exception as e:
        print(f"UniFi lookup skip: {e}", flush=True)

    try:
        udm = udm_connect()
        try:
            _i, o, _e = udm.exec_command(
                "cat /data/udapi-config/dnsmasq.lease | grep -i e4:5f:01:e8:92:28 || true",
                timeout=15,
            )
            for line in o.read().decode(errors="replace").splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    ips.append(parts[2])
                    print(f"DHCP lease -> {parts[2]}", flush=True)
            _i, o, _e = udm.exec_command(
                "ip neigh show | grep -i e4:5f:01:e8:92:28 || true",
                timeout=10,
            )
            for line in o.read().decode(errors="replace").splitlines():
                parts = line.split()
                if parts and parts[0].count(".") == 3:
                    ips.append(parts[0])
                    print(f"neigh -> {parts[0]}", flush=True)
        finally:
            udm.close()
    except Exception as e:
        print(f"UDM neigh/lease skip: {e}", flush=True)

    ips.extend(FALLBACK_IPS)
    # preserve order, unique
    out: list[str] = []
    seen: set[str] = set()
    for ip in ips:
        if ip not in seen:
            seen.add(ip)
            out.append(ip)
    return out


def pi_connect(udm: paramiko.SSHClient, ip: str, password: str) -> paramiko.SSHClient:
    transport = udm.get_transport()
    if transport is None:
        raise RuntimeError("UDM transport missing")
    # Tailscale IPs: connect direct from this host if possible, else still try jump
    if ip.startswith("100."):
        pi = paramiko.SSHClient()
        pi.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pi.connect(
            ip,
            username="user",
            password=password,
            timeout=12,
            allow_agent=False,
            look_for_keys=False,
        )
        return pi
    chan = transport.open_channel(
        "direct-tcpip", (ip, 22), ("127.0.0.1", 0), timeout=8
    )
    pi = paramiko.SSHClient()
    pi.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pi.connect(
        ip,
        username="user",
        password=password,
        sock=chan,
        timeout=12,
        allow_agent=False,
        look_for_keys=False,
    )
    return pi


def sftp_put(pi: paramiko.SSHClient, local: Path, remote: str) -> None:
    sftp = pi.open_sftp()
    try:
        sftp.put(str(local), remote)
    finally:
        sftp.close()


def run(pi: paramiko.SSHClient, cmd: str, timeout: int = 120) -> str:
    _i, o, e = pi.exec_command(cmd, timeout=timeout, get_pty=True)
    out = o.read().decode("utf-8", errors="replace")
    err = e.read().decode("utf-8", errors="replace")
    code = o.channel.recv_exit_status()
    text = out + (("\n" + err) if err.strip() else "")
    if code != 0:
        raise RuntimeError(f"exit {code}\n{text}")
    return text


def deploy(ip: str, password: str) -> None:
    if not PLAYER.is_file() or not UNIT.is_file():
        raise SystemExit(f"missing {PLAYER} or {UNIT}")

    print(f"deploy smooth fb-clock -> {ip}", flush=True)
    udm = udm_connect()
    try:
        pi = pi_connect(udm, ip, password)
    except Exception:
        udm.close()
        raise

    try:
        print(
            run(
                pi,
                "hostname; date; ip -4 -br addr; "
                "systemctl is-active fb-clock 2>/dev/null || true; "
                "systemctl is-enabled fb-clock 2>/dev/null || true",
            ),
            flush=True,
        )
        sftp_put(pi, PLAYER, "/home/user/WerbeLEDbox-CountDown/fb_clock_play.py")
        sftp_put(pi, UNIT, "/tmp/fb-clock.service")
        apply = f"""
set -eux
echo {password!r} | sudo -S true
test -f /home/user/WerbeLEDbox-CountDown/media/clock_24h.mp4
echo {password!r} | sudo -S cp /tmp/fb-clock.service /etc/systemd/system/fb-clock.service
echo {password!r} | sudo -S systemctl unmask fb-clock || true
echo {password!r} | sudo -S systemctl daemon-reload
echo {password!r} | sudo -S systemctl enable fb-clock
echo {password!r} | sudo -S systemctl restart fb-clock
sleep 3
systemctl is-active fb-clock
systemctl is-enabled fb-clock
systemctl show fb-clock -p ActiveEnterTimestamp -p NRestarts -p FragmentPath --no-pager
vcgencmd get_throttled || true
journalctl -u fb-clock -n 20 --no-pager
pgrep -af fb_clock_play || true
"""
        print(run(pi, apply, timeout=90), flush=True)
        print("OK: smooth fb-clock active + enabled (boot autostart)", flush=True)
    finally:
        try:
            pi.close()
        except Exception:
            pass
        udm.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="single pass, no watch loop")
    ap.add_argument("--poll", type=int, default=20)
    args = ap.parse_args()

    password = load("ankerpi02.credentials.yml")["ssh_password"]

    while True:
        for ip in candidate_ips():
            print(f"probe {ip} ...", flush=True)
            try:
                deploy(ip, password)
                return 0
            except Exception as e:
                print(f"  fail: {type(e).__name__}: {e}", flush=True)
        if args.once:
            print("PI02 not reachable", file=sys.stderr)
            return 2
        print(f"offline â€” retry in {args.poll}s", flush=True)
        time.sleep(args.poll)


if __name__ == "__main__":
    raise SystemExit(main())

