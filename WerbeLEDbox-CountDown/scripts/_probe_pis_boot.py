import json, ssl, base64, time, sys
from pathlib import Path
from http.cookiejar import CookieJar
import urllib.request
import paramiko
import yaml

ROOT = Path(r"c:\Users\Harald Nowak\Documents\Cursor Projects\Hotel Anker\WerbeLEDbox-CountDown")
cfg = yaml.safe_load((ROOT / "secrets/unifi.hotelanker.yml").read_text(encoding="utf-8"))

MACS = {
    "AnkerPI02": "e4:5f:01:e8:92:28",
    "AnkerPI01": "2c:cf:67:1e:bf:89",
}

def unifi_clients():
    host = cfg["console_url"].rstrip("/")
    ctx = ssl._create_unverified_context()
    cj = CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ctx),
        urllib.request.HTTPCookieProcessor(cj),
    )
    def call(method, url, data=None, headers=None):
        hdr = {"Accept": "application/json", "Content-Type": "application/json"}
        if headers:
            hdr.update(headers)
        body = None if data is None else json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, headers=hdr, method=method)
        with opener.open(req, timeout=30) as r:
            return json.loads(r.read().decode())
    call("POST", f"{host}/api/auth/login", {"username": cfg["ui"]["user"], "password": cfg["ui"]["password"]})
    token = next(c.value for c in cj if c.name == "TOKEN")
    pad = token.split(".")[1] + "=" * (-len(token.split(".")[1]) % 4)
    csrf = json.loads(base64.urlsafe_b64decode(pad.encode()))["csrfToken"]
    return call("GET", f"{host}/proxy/network/api/s/default/stat/sta", headers={"X-CSRF-Token": csrf})["data"]

def udm():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(cfg["ssh"]["host"], username=cfg["ssh"]["user"], password=cfg["ssh"]["password"], timeout=15)
    return c

def probe_ssh_via_udm(ip, label):
    jump = udm()
    try:
        transport = jump.get_transport()
        chan = transport.open_channel("direct-tcpip", (ip, 22), ("127.0.0.1", 0), timeout=8)
        pi = paramiko.SSHClient()
        pi.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pi.connect(ip, username="user", password="12345678", sock=chan, timeout=10, allow_agent=False, look_for_keys=False)
        stdin, stdout, stderr = pi.exec_command(
            "hostname; uptime; ip -4 -br addr; nmcli -t -f NAME,DEVICE,STATE connection show --active; tailscale ip -4 2>/dev/null || echo no-ts",
            timeout=25,
        )
        out = stdout.read().decode(errors="replace")
        pi.close()
        print(f"SSH OK {label} @{ip}\n{out}")
        return True
    except Exception as e:
        print(f"SSH FAIL {label} @{ip}: {type(e).__name__}: {e}")
        return False
    finally:
        jump.close()

for round_i in range(1, 9):
    print(f"\n===== ROUND {round_i} =====")
    clients = unifi_clients()
    found = {}
    for s in clients:
        mac = (s.get("mac") or "").lower()
        hn = s.get("hostname") or ""
        for name, m in MACS.items():
            if mac == m or hn == name:
                found[name] = s
                print(f"ACTIVE {name}: ip={s.get('ip')} essid={s.get('essid')} net={s.get('network')}")
    if not found:
        print("no active AnkerPI clients")
    jump = udm()
    stdin, stdout, stderr = jump.exec_command("cat /data/udapi-config/dnsmasq.lease", timeout=20)
    leases = stdout.read().decode(errors="replace")
    jump.close()
    targets = {}
    for line in leases.splitlines():
        for name, m in MACS.items():
            if m in line or name in line:
                parts = line.split()
                if len(parts) >= 3:
                    targets[name] = parts[2]
                    print(f"LEASE {name}: {line}")
    ips_try = []
    for name in ("AnkerPI01", "AnkerPI02"):
        if name in found and found[name].get("ip"):
            ips_try.append((name, found[name]["ip"]))
        if name in targets:
            ips_try.append((name, targets[name]))
    extra = [("AnkerPI02", "192.168.2.222"), ("AnkerPI01", "192.168.2.91"),
             ("AnkerPI02", "192.168.1.222"), ("AnkerPI01", "192.168.1.91")]
    seen = set()
    ok = {}
    for name, ip in ips_try + extra:
        key = (name, ip)
        if key in seen or not ip:
            continue
        seen.add(key)
        if name in ok:
            continue
        if probe_ssh_via_udm(ip, name):
            ok[name] = ip
    if len(ok) == 2:
        print("BOTH UP", ok)
        sys.exit(0)
    print("status so far:", ok or "none")
    time.sleep(15)
print("TIMEOUT")
sys.exit(2)
