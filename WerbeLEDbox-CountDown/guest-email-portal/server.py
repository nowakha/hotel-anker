#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hotel Anker guest email captive portal (stdlib HTTP on UDM)."""

from __future__ import annotations

import html
import json
import os
import re
import sys
import traceback
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from i18n import LANG_LABELS, LANGS, pick_lang, t  # noqa: E402
from storage import GuestStore, normalize_mac, valid_email, valid_mac  # noqa: E402
from unifi_api import UniFiClient  # noqa: E402

PORT = int(os.environ.get("GUEST_PORTAL_PORT", "9090"))
DATA_DIR = Path(os.environ.get("GUEST_DATA_DIR", "/data/hotel-anker/guest-emails"))
STATIC_DIR = ROOT / "static"
EXPIRE_MINUTES = int(os.environ.get("GUEST_EXPIRE_MINUTES", "120"))  # 2 hours; known MAC skips email form
UNIFI_URL = os.environ.get("UNIFI_URL", "https://127.0.0.1")
UNIFI_USER = os.environ.get("UNIFI_USER", "admin")
UNIFI_PASS = os.environ.get("UNIFI_PASS", "")
UNIFI_SITE = os.environ.get("UNIFI_SITE", "default")

STORE = GuestStore(DATA_DIR)
UNIFI: UniFiClient | None = None


def get_unifi() -> UniFiClient:
    global UNIFI
    if UNIFI is None:
        if not UNIFI_PASS:
            raise RuntimeError("UNIFI_PASS not set")
        UNIFI = UniFiClient(
            base_url=UNIFI_URL,
            username=UNIFI_USER,
            password=UNIFI_PASS,
            site=UNIFI_SITE,
            verify_tls=False,
        )
        UNIFI.login()
    return UNIFI


def authorize(mac: str) -> None:
    client = get_unifi()
    client.authorize_guest(normalize_mac(mac), EXPIRE_MINUTES)


def qs_mac(query: dict[str, list[str]]) -> str:
    for key in ("id", "mac", "client_mac"):
        vals = query.get(key) or []
        if vals and vals[0]:
            return normalize_mac(vals[0])
    return ""


def parse_qs(path: str) -> tuple[str, dict[str, list[str]]]:
    parsed = urllib.parse.urlparse(path)
    return parsed.path, urllib.parse.parse_qs(parsed.query)


def read_body(handler: BaseHTTPRequestHandler) -> bytes:
    length = int(handler.headers.get("Content-Length") or 0)
    if length <= 0:
        return b""
    return handler.rfile.read(length)


def lang_switcher(lang: str, query: dict[str, list[str]]) -> str:
    """Language chips — JS sets ?lang= on the current URL (keeps /guest/… path)."""
    bits = []
    for code in LANGS:
        label = LANG_LABELS[code]
        active = " active" if code == lang else ""
        aria = ' aria-current="true"' if code == lang else ""
        bits.append(
            f'<button type="button" class="lang-btn{active}" data-lang="{html.escape(code)}"'
            f'{aria}>{html.escape(label)}</button>'
        )
    return (
        '<nav class="lang-row" aria-label="Language">'
        + "".join(bits)
        + "</nav>"
        + """
<script>
(function(){
  function setLang(code){
    try {
      var u = new URL(window.location.href);
      u.searchParams.set('lang', code);
      window.location.assign(u.toString());
    } catch (e) {
      var q = window.location.search || '';
      if (/([?&])lang=/.test(q)) q = q.replace(/([?&])lang=[^&]*/, '$1lang=' + encodeURIComponent(code));
      else q += (q ? '&' : '?') + 'lang=' + encodeURIComponent(code);
      window.location.assign(window.location.pathname + q + window.location.hash);
    }
  }
  document.querySelectorAll('.lang-btn[data-lang]').forEach(function(btn){
    btn.addEventListener('click', function(ev){
      ev.preventDefault();
      setLang(btn.getAttribute('data-lang'));
    });
  });
})();
</script>
"""
    )


def page_shell(body: str, *, lang: str, title: str) -> bytes:
    doc = f"""<!DOCTYPE html>
<html lang="{html.escape(lang)}">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <meta name="robots" content="noindex"/>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" href="/static/portal.css"/>
</head>
<body>
{body}
<script>
/* Help iOS captive sheet show Done without leaving our success page. */
try {{
  var i = document.createElement('iframe');
  i.style.display = 'none';
  i.src = 'http://captive.apple.com/hotspot-detect.html';
  document.body.appendChild(i);
}} catch (e) {{}}
try {{ fetch('http://captive.apple.com/hotspot-detect.html', {{mode:'no-cors'}}); }} catch (e) {{}}
</script>
</body>
</html>
"""
    return doc.encode("utf-8")


def render_form(
    *,
    lang: str,
    query: dict[str, list[str]],
    error: str | None = None,
    email_value: str = "",
) -> bytes:
    copy = t(lang)
    mac = qs_mac(query)
    hidden = []
    for key in ("id", "ap", "t", "url", "ssid", "mac"):
        vals = query.get(key) or []
        if vals and vals[0]:
            hidden.append(
                f'<input type="hidden" name="{html.escape(key)}" value="{html.escape(vals[0])}"/>'
            )
    hidden.append(f'<input type="hidden" name="lang" value="{html.escape(lang)}"/>')
    err_html = f'<div class="error">{html.escape(error)}</div>' if error else ""
    body = f"""
  <main class="shell">
    <img class="logo" src="/static/logo-anchor-gold.svg" alt="Hotel Anker"/>
    <h1>{html.escape(copy['title'])}</h1>
    <p class="headline">{html.escape(copy['headline'])}</p>
    {lang_switcher(lang, query)}
    <p class="lead">{html.escape(copy['lead'])}</p>
    {err_html}
    <form method="post" action="/connect" autocomplete="email">
      {''.join(hidden)}
      <label for="email">{html.escape(copy['email_label'])}</label>
      <input id="email" name="email" type="email" required maxlength="254"
             placeholder="{html.escape(copy['email_placeholder'])}"
             value="{html.escape(email_value)}"/>
      <label class="consent">
        <input type="checkbox" name="consent" value="1" required/>
        <span>{html.escape(copy['consent'])}</span>
      </label>
      <button type="submit">{html.escape(copy['submit'])}</button>
    </form>
    <p class="hint">{html.escape(copy['iphone_hint'])}</p>
    <p class="hint" style="margin-top:6px">MAC: {html.escape(mac or '—')}</p>
  </main>
"""
    return page_shell(body, lang=lang, title=copy["title"])


def render_success(*, lang: str) -> bytes:
    copy = t(lang)
    body = f"""
  <main class="shell success">
    <img class="logo" src="/static/logo-anchor-gold.svg" alt="Hotel Anker"/>
    <h1>{html.escape(copy['success_title'])}</h1>
    <p class="lead">{html.escape(copy['success_body'])}</p>
  </main>
"""
    return page_shell(body, lang=lang, title=copy["title"])


class Handler(BaseHTTPRequestHandler):
    server_version = "HotelAnkerGuestPortal/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str, code: int = 302) -> None:
        self.send_response(code)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path, query = parse_qs(self.path)
        # UniFi external portal path compatibility
        if path.startswith("/guest/"):
            path = "/"

        if path.startswith("/static/"):
            rel = path[len("/static/") :]
            if ".." in rel or rel.startswith("/"):
                self._send(404, b"not found", "text/plain; charset=utf-8")
                return
            fp = STATIC_DIR / rel
            if not fp.is_file():
                self._send(404, b"not found", "text/plain; charset=utf-8")
                return
            data = fp.read_bytes()
            ctype = "application/octet-stream"
            if rel.endswith(".css"):
                ctype = "text/css; charset=utf-8"
            elif rel.endswith(".svg"):
                ctype = "image/svg+xml"
            elif rel.endswith(".jpg") or rel.endswith(".jpeg"):
                ctype = "image/jpeg"
            elif rel.endswith(".png"):
                ctype = "image/png"
            self._send(200, data, ctype)
            return

        if path in ("/health", "/healthz"):
            self._send(200, b"ok\n", "text/plain; charset=utf-8")
            return

        if path not in ("/", "/index.html", "/success"):
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return

        accept = self.headers.get("Accept-Language")
        lang = pick_lang((query.get("lang") or [None])[0], accept)
        ua = self.headers.get("User-Agent")
        mac = qs_mac(query)

        if path == "/success":
            self._send(200, render_success(lang=lang), "text/html; charset=utf-8")
            return

        # Returning guest: known MAC → authorize + success (no form)
        if mac and valid_mac(mac):
            known = STORE.find_by_mac(mac)
            if known:
                try:
                    STORE.touch_mac(mac, ua)
                    authorize(mac)
                    q = urllib.parse.urlencode({"lang": known.get("lang") or lang})
                    self._redirect(f"/success?{q}")
                    return
                except Exception:
                    traceback.print_exc()
                    # fall through to form with error
                    self._send(
                        200,
                        render_form(
                            lang=lang,
                            query=query,
                            error=t(lang)["error_auth"],
                        ),
                        "text/html; charset=utf-8",
                    )
                    return

        self._send(200, render_form(lang=lang, query=query), "text/html; charset=utf-8")

    def do_POST(self) -> None:  # noqa: N802
        path, _ = parse_qs(self.path)
        if path not in ("/connect", "/guest/s/default/", "/guest/s/default"):
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return

        raw = read_body(self)
        ctype = (self.headers.get("Content-Type") or "").split(";")[0].strip()
        form: dict[str, list[str]] = {}
        if ctype == "application/json":
            try:
                obj = json.loads(raw.decode("utf-8"))
                form = {k: [str(v)] for k, v in obj.items()}
            except Exception:
                form = {}
        else:
            form = urllib.parse.parse_qs(raw.decode("utf-8", errors="replace"))

        accept = self.headers.get("Accept-Language")
        lang = pick_lang((form.get("lang") or [None])[0], accept)
        copy = t(lang)
        email = (form.get("email") or [""])[0]
        consent = (form.get("consent") or [""])[0] in ("1", "true", "on", "yes")
        mac = qs_mac(form)
        if not mac:
            mac = normalize_mac((form.get("id") or [""])[0])
        ua = self.headers.get("User-Agent")

        query = {k: v for k, v in form.items()}

        if not consent:
            self._send(
                400,
                render_form(lang=lang, query=query, error=copy["error_consent"], email_value=email),
                "text/html; charset=utf-8",
            )
            return
        if not valid_email(email):
            self._send(
                400,
                render_form(lang=lang, query=query, error=copy["error_email"], email_value=email),
                "text/html; charset=utf-8",
            )
            return
        if not valid_mac(mac):
            self._send(
                400,
                render_form(lang=lang, query=query, error=copy["error_mac"], email_value=email),
                "text/html; charset=utf-8",
            )
            return

        try:
            STORE.upsert_guest(email=email, mac=mac, lang=lang, user_agent=ua)
            authorize(mac)
        except Exception:
            traceback.print_exc()
            self._send(
                500,
                render_form(lang=lang, query=query, error=copy["error_auth"], email_value=email),
                "text/html; charset=utf-8",
            )
            return

        self._redirect(f"/success?lang={urllib.parse.quote(lang)}")


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    # Do not block listen on UniFi login — authorize() logs in lazily.
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(
        f"guest-email-portal listening on :{PORT} data={DATA_DIR} expire_min={EXPIRE_MINUTES}",
        flush=True,
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
