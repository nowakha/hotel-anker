#!/usr/bin/env python3
"""Install / repair Hotel Anker guest email portal on the UDM."""

from __future__ import annotations

import base64
import io
import json
import ssl
import sys
import tarfile
import time
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

import paramiko
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / "secrets" / "unifi.hotelanker.yml"
PORTAL_SRC = ROOT / "guest-email-portal"
REMOTE_BASE = "/data/hotel-anker"
REMOTE_APP = f"{REMOTE_BASE}/guest-email-portal"
REMOTE_DATA = f"{REMOTE_BASE}/guest-emails"
SERVICE_NAME = "hotel-anker-guest-portal.service"

NGINX_SNIPPET = r"""# Hotel Anker guest email portal — HTTP entry for UniFi auth=custom
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location /guest/ {
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://127.0.0.1:9090/guest/;
    }

    location /static/ {
        proxy_pass http://127.0.0.1:9090/static/;
    }

    location /connect {
        proxy_pass http://127.0.0.1:9090/connect;
    }

    location /success {
        proxy_pass http://127.0.0.1:9090/success;
    }

    location /health {
        proxy_pass http://127.0.0.1:9090/health;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}
"""

BRIDGE_INDEX = """<!DOCTYPE html>
<html lang="de"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Hotel Anker</title>
<script>
(function(){
  var q = location.search || '';
  location.replace('http://192.168.1.254:9090/' + q);
})();
</script>
<meta http-equiv="refresh" content="0;url=http://192.168.1.254:9090/"/>
</head><body style="background:#0B1C2C;color:#F3EBE0;font-family:sans-serif;text-align:center;padding:40px">
Redirecting to Hotel Anker Wi-Fi portal…
</body></html>
"""

REMOTE_PATCH_NGINX = r'''
import re
from pathlib import Path
conf = Path("/data/unifi-core/config/http/site-local-ip.conf")
snippet = Path("/tmp/hotel-anker-nginx80.conf").read_text(encoding="utf-8").strip() + "\n"
text = conf.read_text(encoding="utf-8")
if "proxy_pass http://127.0.0.1:9090/guest/" in text:
    print("nginx already patched")
else:
    bak = conf.with_suffix(conf.suffix + ".bak-hotel-anker")
    if not bak.exists():
        bak.write_text(text, encoding="utf-8")
    pat = re.compile(
        r"server \{\s*listen 80 default_server;.*?return 301 https://\$host\$request_uri;\s*\}",
        re.S,
    )
    new, n = pat.subn(snippet, text, count=1)
    if n != 1:
        raise SystemExit(f"nginx patch failed matches={n}")
    conf.write_text(new, encoding="utf-8")
    print("nginx patched")
'''


def load_secrets() -> dict:
    if not SECRETS.is_file():
        raise SystemExit(f"missing secrets: {SECRETS}")
    return yaml.safe_load(SECRETS.read_text(encoding="utf-8")) or {}


def make_tarball() -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for path in sorted(PORTAL_SRC.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(PORTAL_SRC).as_posix()
            if rel.startswith("exports/") or rel.endswith(".pyc") or "/__pycache__/" in f"/{rel}/":
                continue
            tar.add(path, arcname=f"guest-email-portal/{rel}")
    return buf.getvalue()


def ssh_connect(cfg: dict) -> paramiko.SSHClient:
    ssh = cfg.get("ssh") or {}
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        ssh.get("host") or "192.168.1.254",
        username=ssh.get("user") or "root",
        password=ssh.get("password"),
        timeout=25,
        allow_agent=False,
        look_for_keys=False,
    )
    return client


def run(client: paramiko.SSHClient, cmd: str, timeout: int = 120) -> tuple[str, str, int]:
    _i, out, err = client.exec_command(cmd, timeout=timeout)
    o = out.read().decode(errors="replace")
    e = err.read().decode(errors="replace")
    code = out.channel.recv_exit_status()
    return o, e, code


def unifi_api(cfg: dict) -> None:
    host = (cfg.get("console_url") or "https://192.168.1.254").rstrip("/")
    ui = cfg.get("ui") or {}
    user = ui.get("user") or "admin"
    password = ui.get("password")
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
        with opener.open(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())

    call("POST", f"{host}/api/auth/login", {"username": user, "password": password})
    token = next(c.value for c in cj if c.name == "TOKEN")
    payload_b64 = token.split(".")[1]
    payload_b64 += "=" * (-len(payload_b64) % 4)
    csrf = json.loads(base64.urlsafe_b64decode(payload_b64.encode()))["csrfToken"]
    _, ga = call(
        "GET",
        f"{host}/proxy/network/api/s/default/rest/setting/guest_access",
        headers={"X-CSRF-Token": csrf},
    )
    gid = ga["data"][0]["_id"]
    payload = {
        "_id": gid,
        "auth": "custom",
        "custom_ip": "192.168.1.254",
        "expire": 120,
        "expire_number": 2,
        "expire_unit": 60,
        "portal_enabled": True,
        "redirect_enabled": False,
        "redirect_url": "",
    }
    _, res = call(
        "PUT",
        f"{host}/proxy/network/api/s/default/set/setting/guest_access",
        payload,
        headers={"X-CSRF-Token": csrf},
    )
    data = res["data"][0]
    print(
        "unifi guest_access:",
        f"auth={data.get('auth')}",
        f"custom_ip={data.get('custom_ip')}",
        f"expire={data.get('expire')}",
    )


def main() -> int:
    if not PORTAL_SRC.is_dir():
        print(f"missing {PORTAL_SRC}", file=sys.stderr)
        return 1
    cfg = load_secrets()
    ui = cfg.get("ui") or {}
    password = ui.get("password") or ""
    user = ui.get("user") or "admin"
    # escape password for shell single-quoted env file: replace ' with '"'"'
    pass_shell = password.replace("'", "'\"'\"'")

    tarball = make_tarball()
    client = ssh_connect(cfg)
    try:
        sftp = client.open_sftp()
        with sftp.file("/tmp/hotel-anker-guest-portal.tgz", "wb") as rf:
            rf.write(tarball)
        with sftp.file("/tmp/hotel-anker-nginx80.conf", "w") as rf:
            rf.write(NGINX_SNIPPET)
        with sftp.file("/tmp/hotel-anker-patch-nginx.py", "w") as rf:
            rf.write(REMOTE_PATCH_NGINX)
        with sftp.file("/tmp/hotel-anker-bridge-index.html", "w") as rf:
            rf.write(BRIDGE_INDEX)
        sftp.close()
        print(f"uploaded {len(tarball)} bytes")

        script = f"""
set -e
mkdir -p {REMOTE_BASE} {REMOTE_DATA}
tar -xzf /tmp/hotel-anker-guest-portal.tgz -C {REMOTE_BASE}
umask 077
cat > {REMOTE_APP}/portal.env <<'EOF'
GUEST_PORTAL_PORT=9090
GUEST_DATA_DIR={REMOTE_DATA}
GUEST_EXPIRE_MINUTES=120
UNIFI_URL=https://127.0.0.1
UNIFI_USER={user}
UNIFI_PASS={pass_shell}
UNIFI_SITE=default
EOF
# rewrite PASS quoted for systemd EnvironmentFile (# must be inside quotes)
python3 - <<'PY'
from pathlib import Path
p = Path('{REMOTE_APP}/portal.env')
lines = []
for line in p.read_text().splitlines():
    if line.startswith('UNIFI_PASS='):
        pw = {password!r}
        lines.append('UNIFI_PASS="' + pw.strip("'").replace('"', '\\"') + '"')
    elif line.startswith('UNIFI_URL='):
        lines.append('UNIFI_URL=https://127.0.0.1')
    else:
        lines.append(line)
p.write_text('\\n'.join(lines) + '\\n')
p.chmod(0o600)
print('portal.env written')
PY
chmod +x {REMOTE_APP}/server.py || true
cp {REMOTE_APP}/systemd/{SERVICE_NAME} /etc/systemd/system/{SERVICE_NAME}
systemctl daemon-reload
systemctl enable {SERVICE_NAME}
systemctl restart {SERVICE_NAME}
sleep 2
systemctl is-active {SERVICE_NAME}
curl -sS -m 5 -o /dev/null -w "portal_health %{{http_code}}\\n" http://127.0.0.1:9090/health || curl -sS -m 5 -o /dev/null -w "portal_health_retry %{{http_code}}\\n" http://127.0.0.1:9090/health
ipset add UBIOS_guest_portal_ports 9090 2>/dev/null || true
ipset add UBIOS_guest_portal_ports 80 2>/dev/null || true
ipset list UBIOS_guest_portal_ports | head -20
python3 /tmp/hotel-anker-patch-nginx.py
nginx -t
systemctl reload nginx
echo nginx_reloaded
PORTAL_DIR=/data/unifi/data/sites/default/app-unifi-hotspot-portal
if [ -d "$PORTAL_DIR" ]; then
  if [ -f "$PORTAL_DIR/index.html" ] && [ ! -f "$PORTAL_DIR/index.html.pre-email-portal" ]; then
    cp -a "$PORTAL_DIR/index.html" "$PORTAL_DIR/index.html.pre-email-portal"
  fi
  cp /tmp/hotel-anker-bridge-index.html "$PORTAL_DIR/index.html"
  chown unifi:unifi "$PORTAL_DIR/index.html" 2>/dev/null || true
  echo bridged_8880
fi
python3 - <<'PY'
import sys
sys.path.insert(0, '{REMOTE_APP}')
from storage import GuestStore
s = GuestStore('{REMOTE_DATA}')
print('db', s.db_path)
print('csv', s.csv_path)
PY
"""
        o, e, code = run(client, script, timeout=180)
        sys.stdout.write(o)
        if e.strip():
            sys.stderr.write(e)
        if code != 0:
            print(f"remote install failed exit={code}", file=sys.stderr)
            return code or 1
    finally:
        client.close()

    print("configuring UniFi guest_access…")
    unifi_api(cfg)
    time.sleep(2)

    client = ssh_connect(cfg)
    try:
        o, e, _ = run(
            client,
            "ipset add UBIOS_guest_portal_ports 9090 2>/dev/null || true; "
            "ipset add UBIOS_guest_portal_ports 80 2>/dev/null || true; "
            "curl -sS -m 5 -o /dev/null -w 'local9090 %{http_code}\\n' http://127.0.0.1:9090/health; "
            "curl -sS -m 5 -o /tmp/g.html -w 'via80 %{http_code} %{size_download}\\n' "
            "'http://127.0.0.1/guest/s/default/?id=aa:bb:cc:dd:ee:ff&lang=de'; "
            "head -c 200 /tmp/g.html; echo; "
            "systemctl is-active hotel-anker-guest-portal.service; "
            "ipset list UBIOS_guest_portal_ports | head -15",
            timeout=60,
        )
        sys.stdout.write(o)
        if e.strip():
            sys.stderr.write(e)
    finally:
        client.close()

    print("install ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
