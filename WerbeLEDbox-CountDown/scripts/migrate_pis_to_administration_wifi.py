#!/usr/bin/env python3
"""Migrate AnkerPI01/02 WiFi to SSID Administration (HeimatSchutz).

Windows on Default LAN often cannot route to VLAN 2 — this script jumps
through the UDM SSH host, then opens a direct-tcpip channel to each Pi.

Usage:
  py WerbeLEDbox-CountDown/scripts/migrate_pis_to_administration_wifi.py
  py WerbeLEDbox-CountDown/scripts/migrate_pis_to_administration_wifi.py --only pi01

After a failed switch, power-cycle the Pi, wait until it is back on any
reachable SSID, then re-run. HotelAnker stays as autoconnect fallback until
Administration activates successfully.
"""

from __future__ import annotations

import argparse
import base64
import json
import ssl
import sys
import time
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

import paramiko
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "secrets"
SSID = "Administration"
WLAN_PSK = "HeimatSchutz"


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


def find_host(clients: list[dict], hostname: str) -> dict | None:
    for s in clients:
        if (s.get("hostname") or "") == hostname:
            return s
    return None


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


def pi_connect(udm: paramiko.SSHClient, ip: str, password: str) -> paramiko.SSHClient:
    transport = udm.get_transport()
    if transport is None:
        raise RuntimeError("UDM transport missing")
    chan = transport.open_channel("direct-tcpip", (ip, 22), ("127.0.0.1", 0))
    pi = paramiko.SSHClient()
    pi.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    pi.connect(
        ip,
        username="user",
        password=password,
        sock=chan,
        timeout=20,
        allow_agent=False,
        look_for_keys=False,
    )
    return pi


def run(pi: paramiko.SSHClient, cmd: str, timeout: int = 90) -> str:
    _i, o, e = pi.exec_command(cmd, timeout=timeout, get_pty=True)
    out = o.read().decode("utf-8", errors="replace")
    err = e.read().decode("utf-8", errors="replace")
    code = o.channel.recv_exit_status()
    if code != 0:
        raise RuntimeError(f"exit {code}\n{out}\n{err}")
    return out + (("\n" + err) if err.strip() else "")


def migrate(label: str, ip: str, password: str, *, zero_2w: bool) -> None:
    print(f"[{label}] {ip}", flush=True)
    udm = udm_connect()
    try:
        pi = pi_connect(udm, ip, password)
    except Exception as e:
        udm.close()
        raise SystemExit(f"[{label}] SSH failed: {e}") from e

    try:
        print(run(pi, "hostname; ip -4 -br addr; nmcli -t -f NAME,DEVICE,STATE connection show --active"), flush=True)
        # Keep HotelAnker as fallback until Administration is up
        cmd = f"""
set -eux
echo {password!r} | sudo -S true
nmcli device wifi rescan || true
sleep 2
nmcli -t -f IN-USE,SSID,SIGNAL,CHAN device wifi list | grep -i Admin || true
# Create/update Administration
if nmcli -t -f NAME connection show | grep -qx Administration; then
  echo {password!r} | sudo -S nmcli connection modify Administration \
    wifi-sec.psk {WLAN_PSK!r} \
    connection.autoconnect yes \
    connection.autoconnect-priority 100 \
    802-11-wireless.powersave 2 \
    ipv4.method auto ipv4.ignore-auto-dns yes ipv4.dns '1.1.1.1 8.8.8.8' ipv6.method disabled
else
  echo {password!r} | sudo -S nmcli connection add type wifi ifname wlan0 con-name Administration ssid {SSID} \
    wifi-sec.key-mgmt wpa-psk wifi-sec.psk {WLAN_PSK!r} \
    connection.autoconnect yes connection.autoconnect-priority 100 \
    802-11-wireless.powersave 2 \
    ipv4.method auto ipv4.ignore-auto-dns yes ipv4.dns '1.1.1.1 8.8.8.8' ipv6.method disabled
fi
# Prefer Administration but do NOT disable HotelAnker until success
echo {password!r} | sudo -S nmcli connection modify HotelAnker connection.autoconnect-priority 10 || true
"""
        if not zero_2w:
            cmd += f"""
echo {password!r} | sudo -S nmcli connection modify HotelAnker_5G connection.autoconnect-priority 5 || true
"""
        cmd += f"""
# Connect now
echo {password!r} | sudo -S nmcli device wifi connect {SSID} password {WLAN_PSK!r} ifname wlan0 name Administration || \
  echo {password!r} | sudo -S nmcli connection up Administration
sleep 5
ACTIVE=$(nmcli -t -f NAME,DEVICE,STATE connection show --active | grep wlan0 || true)
echo ACTIVE=$ACTIVE
ip -4 -br addr show wlan0
SSID_NOW=$(iwgetid -r || true)
echo SSID_NOW=$SSID_NOW
test "$SSID_NOW" = "{SSID}"
# Only after success: demote Bar SSIDs
echo {password!r} | sudo -S nmcli connection modify HotelAnker autoconnect no || true
"""
        if not zero_2w:
            cmd += f"""
echo {password!r} | sudo -S nmcli connection modify HotelAnker_5G autoconnect no || true
"""
        cmd += f"""
echo {password!r} | sudo -S nmcli connection modify netplan-wlan0-HotelAnker autoconnect no || true
echo OK
"""
        print(run(pi, cmd, timeout=120), flush=True)
    finally:
        try:
            pi.close()
        except Exception:
            pass
        udm.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=("pi01", "pi02", "both"), default="both")
    args = ap.parse_args()

    wifi = load("wifi.hotelanker.yml")
    ssid = wifi.get("ssid_administration") or "Administration"
    wlan_psk = wifi.get("password_administration") or wifi.get("password") or "HeimatSchutz"
    global SSID, WLAN_PSK
    SSID = ssid
    WLAN_PSK = wlan_psk

    p1 = load("ankerpi01.credentials.yml")
    p2 = load("ankerpi02.credentials.yml")
    clients = unifi_clients()
    c1 = find_host(clients, "AnkerPI01")
    c2 = find_host(clients, "AnkerPI02")
    print("UniFi:", "PI01", c1 and (c1.get("ip"), c1.get("essid")), "PI02", c2 and (c2.get("ip"), c2.get("essid")), flush=True)

    if args.only in ("pi01", "both"):
        if not c1 or not c1.get("ip"):
            print("PI01 not online in UniFi — power-cycle then retry", file=sys.stderr)
            if args.only == "pi01":
                return 1
        else:
            migrate("PI01", c1["ip"], p1["ssh_password"], zero_2w=True)

    if args.only in ("pi02", "both"):
        if not c2 or not c2.get("ip"):
            print("PI02 not online in UniFi — power-cycle then retry", file=sys.stderr)
            if args.only == "pi02":
                return 1
        else:
            migrate("PI02", c2["ip"], p2["ssh_password"], zero_2w=False)

    time.sleep(8)
    clients = unifi_clients()
    for name in ("AnkerPI01", "AnkerPI02"):
        c = find_host(clients, name)
        print("AFTER", name, c and (c.get("ip"), c.get("essid"), c.get("network")), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
