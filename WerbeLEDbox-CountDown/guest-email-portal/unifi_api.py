# -*- coding: utf-8 -*-
"""UniFi Network API helper — login + authorize-guest (local UDM)."""

from __future__ import annotations

import base64
import json
import ssl
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
from typing import Any


class UniFiClient:
    def __init__(
        self,
        *,
        base_url: str,
        username: str,
        password: str,
        site: str = "default",
        verify_tls: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.site = site
        self._ctx = ssl.create_default_context()
        if not verify_tls:
            self._ctx.check_hostname = False
            self._ctx.verify_mode = ssl.CERT_NONE
        self._cj = CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=self._ctx),
            urllib.request.HTTPCookieProcessor(self._cj),
        )
        self._csrf: str | None = None

    def _headers(self) -> dict[str, str]:
        h = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self._csrf:
            h["X-CSRF-Token"] = self._csrf
        return h

    def _request(self, method: str, path: str, data: dict | None = None) -> tuple[int, Any]:
        url = f"{self.base_url}{path}"
        body = None if data is None else json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=self._headers(), method=method)
        try:
            with self._opener.open(req, timeout=12) as resp:
                raw = resp.read()
                try:
                    return resp.status, json.loads(raw.decode("utf-8") or "null")
                except json.JSONDecodeError:
                    return resp.status, raw
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                return e.code, json.loads(raw.decode("utf-8") or "null")
            except Exception:
                return e.code, raw

    def _refresh_csrf(self) -> None:
        token = None
        for c in self._cj:
            if c.name == "TOKEN":
                token = c.value
                break
        if not token:
            self._csrf = None
            return
        parts = token.split(".")
        if len(parts) < 2:
            self._csrf = None
            return
        pad = parts[1] + ("=" * (-len(parts[1]) % 4))
        try:
            payload = json.loads(base64.urlsafe_b64decode(pad.encode("ascii")))
            self._csrf = payload.get("csrfToken")
        except Exception:
            self._csrf = None

    def login(self) -> None:
        code, _ = self._request(
            "POST",
            "/api/auth/login",
            {"username": self.username, "password": self.password},
        )
        if code not in (200, 201):
            raise RuntimeError(f"unifi login failed: HTTP {code}")
        self._refresh_csrf()

    def authorize_guest(self, mac: str, minutes: int) -> None:
        path = f"/proxy/network/api/s/{self.site}/cmd/stamgr"
        payload = {"cmd": "authorize-guest", "mac": mac, "minutes": int(minutes)}
        code, body = self._request("POST", path, payload)
        if code == 401:
            self.login()
            code, body = self._request("POST", path, payload)
        ok = False
        if isinstance(body, dict):
            ok = body.get("meta", {}).get("rc") == "ok"
        if code != 200 or not ok:
            raise RuntimeError(f"authorize-guest failed: HTTP {code} {body!r}")
