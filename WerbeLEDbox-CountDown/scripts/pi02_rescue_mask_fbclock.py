#!/usr/bin/env python3
"""Watch AnkerPI02; on first SSH, stop/disable/mask fb-clock, deploy patched player.

Usage (from repo root or anywhere):
  py -3 WerbeLEDbox-CountDown/scripts/pi02_rescue_mask_fbclock.py

Hard constraint: do not touch cmdline.txt. Prefer LAN then Tailscale.
"""
from __future__ import annotations

import argparse
import socket
import sys
import time
from pathlib import Path

HOSTS = ("192.168.8.106", "100.103.54.63")
USER = "user"
PASSWORD = "12345678"
REPO_PLAYER = Path(__file__).resolve().parents[1] / "fb_clock_play.py"
REMOTE_PLAYER = "/home/user/WerbeLEDbox-CountDown/fb_clock_play.py"
MASK_CMD = (
    "set -e; "
    "echo MASK_START; "
    "echo '{pw}' | sudo -S systemctl stop fb-clock 2>/dev/null || true; "
    "echo '{pw}' | sudo -S systemctl disable fb-clock 2>/dev/null || true; "
    "echo '{pw}' | sudo -S systemctl mask fb-clock 2>/dev/null || true; "
    "systemctl is-enabled fb-clock 2>&1 || true; "
    "systemctl is-active fb-clock 2>&1 || true; "
    "hostname; uptime; "
    "echo MASK_DONE"
)


def port_open(host: str, port: int = 22, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def ssh_exec(host: str, command: str, timeout: float = 20.0) -> tuple[int, str, str]:
    try:
        import paramiko
    except ImportError:
        # Fallback: OpenSSH BatchMode (key only)
        import subprocess

        proc = subprocess.run(
            [
                "ssh",
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "ConnectTimeout=5",
                "-o",
                "BatchMode=yes",
                f"{USER}@{host}",
                command,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            host,
            username=USER,
            password=PASSWORD,
            timeout=timeout,
            allow_agent=True,
            look_for_keys=True,
            banner_timeout=timeout,
            auth_timeout=timeout,
        )
        _stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        rc = stdout.channel.recv_exit_status()
        return rc, out, err
    finally:
        client.close()


def scp_put(host: str, local: Path, remote: str) -> None:
    try:
        import paramiko
    except ImportError:
        import subprocess

        subprocess.run(
            [
                "scp",
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "ConnectTimeout=5",
                str(local),
                f"{USER}@{host}:{remote}",
            ],
            check=True,
            timeout=60,
        )
        return

    transport = paramiko.Transport((host, 22))
    transport.connect(username=USER, password=PASSWORD)
    try:
        sftp = paramiko.SFTPClient.from_transport(transport)
        assert sftp is not None
        sftp.put(str(local), remote)
        sftp.close()
    finally:
        transport.close()


def verify_probe_safe(host: str) -> bool:
    # Grep remote file: patched player must mention ffprobe and must not full-decode via -f null
    rc, out, err = ssh_exec(
        host,
        f"grep -n ffprobe {REMOTE_PLAYER}; "
        f"grep -n 'f\", \"null\"\\|\"-f\", \"null\"\\|-f null' {REMOTE_PLAYER} || echo NO_NULL_DECODE; "
        f"head -n 72 {REMOTE_PLAYER} | tail -n 40",
    )
    text = out + err
    print(text)
    has_ffprobe = "ffprobe" in text
    has_null = ("-f null" in text) or ('"null"' in text and "-f" in text and "Never decode" not in text)
    # Safer: require ffprobe and explicit "Never decode" comment from patched file
    return has_ffprobe and ("Never decode the whole file" in text) and ("NO_NULL_DECODE" in text or "-f null" not in text)


def rescue_one(host: str, deploy: bool) -> bool:
    print(f"[{time.strftime('%H:%M:%S')}] SSH open on {host} — masking fb-clock", flush=True)
    cmd = MASK_CMD.format(pw=PASSWORD)
    rc, out, err = ssh_exec(host, cmd)
    print(out or err, flush=True)
    ok = "MASK_DONE" in (out + err) and ("masked" in (out + err) or "inactive" in (out + err))
    if not ok and rc != 0:
        print(f"mask rc={rc} err={err}", flush=True)
        # still try deploy if we got any shell
    if deploy and REPO_PLAYER.is_file():
        print(f"deploying {REPO_PLAYER} → {REMOTE_PLAYER}", flush=True)
        try:
            scp_put(host, REPO_PLAYER, REMOTE_PLAYER)
            safe = verify_probe_safe(host)
            print(f"probe_safe={safe}", flush=True)
        except Exception as exc:  # noqa: BLE001
            print(f"deploy failed: {exc}", flush=True)
            return False
    return "MASK_DONE" in (out + err)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true", help="single probe round then exit")
    p.add_argument("--no-deploy", action="store_true")
    p.add_argument("--interval", type=float, default=2.0)
    p.add_argument("--max-seconds", type=float, default=0, help="0 = forever")
    args = p.parse_args()
    deploy = not args.no_deploy
    t0 = time.time()
    round_n = 0
    print(f"watching {HOSTS} for SSH:22 (deploy={deploy})", flush=True)
    while True:
        round_n += 1
        for host in HOSTS:
            if port_open(host):
                if rescue_one(host, deploy=deploy):
                    print("RESCUE_OK", flush=True)
                    return 0
                print("rescue attempt incomplete; keep watching", flush=True)
        if round_n % 10 == 1:
            print(
                f"[{time.strftime('%H:%M:%S')}] still offline round={round_n}",
                flush=True,
            )
        if args.once:
            return 1
        if args.max_seconds and (time.time() - t0) >= args.max_seconds:
            print("TIMEOUT still offline", flush=True)
            return 1
        time.sleep(args.interval)


if __name__ == "__main__":
    sys.exit(main())
