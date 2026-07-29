# -*- coding: utf-8 -*-
"""SQLite guest-email store + CSV mirror on the UDM."""

from __future__ import annotations

import csv
import os
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAC_RE = re.compile(r"^([0-9a-f]{2}:){5}[0-9a-f]{2}$")

_lock = threading.RLock()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def normalize_mac(mac: str) -> str:
    raw = (mac or "").strip().lower().replace("-", ":")
    if len(raw) == 12 and ":" not in raw:
        raw = ":".join(raw[i : i + 2] for i in range(0, 12, 2))
    return raw


def valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match(normalize_email(email)))


def valid_mac(mac: str) -> bool:
    return bool(MAC_RE.match(normalize_mac(mac)))


class GuestStore:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "guests.sqlite3"
        self.csv_path = self.data_dir / "guests.csv"
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        with _lock:
            conn = self._connect()
            try:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS guests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL,
                        mac TEXT NOT NULL,
                        lang TEXT NOT NULL DEFAULT 'de',
                        consent_at TEXT NOT NULL,
                        first_seen TEXT NOT NULL,
                        last_seen TEXT NOT NULL,
                        user_agent TEXT,
                        source TEXT NOT NULL DEFAULT 'guest_wifi',
                        UNIQUE(email)
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_guests_mac ON guests(mac)"
                )
                conn.commit()
            finally:
                conn.close()
        # CSV mirror outside init lock path (RLock-safe either way)
        self.export_csv()

    def find_by_mac(self, mac: str) -> dict[str, Any] | None:
        mac_n = normalize_mac(mac)
        if not valid_mac(mac_n):
            return None
        with _lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT * FROM guests WHERE mac = ? ORDER BY id DESC LIMIT 1",
                    (mac_n,),
                ).fetchone()
                return dict(row) if row else None
            finally:
                conn.close()

    def touch_mac(self, mac: str, user_agent: str | None = None) -> dict[str, Any] | None:
        mac_n = normalize_mac(mac)
        now = utc_now()
        with _lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT * FROM guests WHERE mac = ? ORDER BY id DESC LIMIT 1",
                    (mac_n,),
                ).fetchone()
                if not row:
                    return None
                conn.execute(
                    "UPDATE guests SET last_seen = ?, user_agent = COALESCE(?, user_agent) WHERE id = ?",
                    (now, user_agent, row["id"]),
                )
                conn.commit()
                out = dict(row)
                out["last_seen"] = now
                if user_agent:
                    out["user_agent"] = user_agent
            finally:
                conn.close()
        self.export_csv()
        return out

    def upsert_guest(
        self,
        *,
        email: str,
        mac: str,
        lang: str,
        user_agent: str | None,
        source: str = "guest_wifi",
    ) -> dict[str, Any]:
        """Insert only if email is new; existing email → update MAC/last_seen, no second row."""
        email_n = normalize_email(email)
        mac_n = normalize_mac(mac)
        if not valid_email(email_n):
            raise ValueError("invalid_email")
        if not valid_mac(mac_n):
            raise ValueError("invalid_mac")
        now = utc_now()
        lang = (lang or "de")[:2].lower()
        with _lock:
            conn = self._connect()
            try:
                by_email = conn.execute(
                    "SELECT * FROM guests WHERE email = ?", (email_n,)
                ).fetchone()
                if by_email:
                    # Known email: never INSERT again — refresh MAC + timestamps only
                    conn.execute(
                        """
                        UPDATE guests
                        SET mac = ?, lang = ?, last_seen = ?, user_agent = ?
                        WHERE id = ?
                        """,
                        (mac_n, lang, now, user_agent, by_email["id"]),
                    )
                    conn.commit()
                    row = conn.execute(
                        "SELECT * FROM guests WHERE id = ?", (by_email["id"],)
                    ).fetchone()
                else:
                    by_mac = conn.execute(
                        "SELECT * FROM guests WHERE mac = ? ORDER BY id DESC LIMIT 1",
                        (mac_n,),
                    ).fetchone()
                    if by_mac:
                        # Known MAC, new/different email: update that row's email once
                        conn.execute(
                            """
                            UPDATE guests
                            SET email = ?, lang = ?, last_seen = ?, user_agent = ?,
                                consent_at = ?
                            WHERE id = ?
                            """,
                            (email_n, lang, now, user_agent, now, by_mac["id"]),
                        )
                        conn.commit()
                        row = conn.execute(
                            "SELECT * FROM guests WHERE id = ?", (by_mac["id"],)
                        ).fetchone()
                    else:
                        cur = conn.execute(
                            """
                            INSERT INTO guests
                            (email, mac, lang, consent_at, first_seen, last_seen, user_agent, source)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (email_n, mac_n, lang, now, now, now, user_agent, source),
                        )
                        conn.commit()
                        row = conn.execute(
                            "SELECT * FROM guests WHERE id = ?", (cur.lastrowid,)
                        ).fetchone()
                result = dict(row)
            finally:
                conn.close()
        self.export_csv()
        return result

    def list_all(self) -> list[dict[str, Any]]:
        with _lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT * FROM guests ORDER BY consent_at DESC, id DESC"
                ).fetchall()
                return [dict(r) for r in rows]
            finally:
                conn.close()

    def export_csv(self) -> Path:
        rows = self.list_all()
        fields = [
            "id",
            "email",
            "mac",
            "lang",
            "consent_at",
            "first_seen",
            "last_seen",
            "user_agent",
            "source",
        ]
        tmp = self.csv_path.with_suffix(".csv.tmp")
        with _lock:
            with open(tmp, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
                w.writeheader()
                for r in rows:
                    w.writerow({k: r.get(k, "") for k in fields})
            os.replace(tmp, self.csv_path)
        return self.csv_path
