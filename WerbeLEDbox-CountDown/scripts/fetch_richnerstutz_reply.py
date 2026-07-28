#!/usr/bin/env python3
"""Fetch latest Richnerstutz reply from Gmail via CDP."""

from __future__ import annotations

import json
import urllib.parse
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[2] / "Richnerstutz-Bespannung-Paket" / "versand"
OUT.mkdir(parents=True, exist_ok=True)

QUERIES = [
    "from:richnerstutz.ch newer_than:1d",
    "from:jelk newer_than:2d",
    "from:vogt newer_than:2d",
    "subject:(Druckdaten OR Blocker OR AG 461414) newer_than:2d",
    "richnerstutz newer_than:1d",
]


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = browser.contexts[0]
        page = next(pg for pg in ctx.pages if "mail.google" in pg.url)
        page.bring_to_front()

        found = None
        for q in QUERIES:
            url = "https://mail.google.com/mail/u/0/#search/" + urllib.parse.quote(q)
            print("QUERY", q)
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            page.wait_for_timeout(5000)
            rows = page.locator("tr.zA:visible")
            n = rows.count()
            print(" visible rows", n)
            for i in range(min(6, n)):
                t = rows.nth(i).inner_text().replace("\n", " | ")
                print(f"  {i}: {t[:250]}")
            if n:
                rows.first.click(force=True)
                page.wait_for_timeout(4000)
                subj = page.locator("h2.hP").first.inner_text() if page.locator("h2.hP").count() else ""
                frm = ""
                name = ""
                if page.locator("span.gD").count():
                    el = page.locator("span.gD").first
                    frm = el.get_attribute("email") or ""
                    name = el.get_attribute("name") or ""
                body = ""
                for sel in ("div.a3s.aiL", "div.ii.gt div.a3s", "div.a3s"):
                    loc = page.locator(sel)
                    if loc.count():
                        cand = loc.last.inner_text()
                        if len(cand) > len(body):
                            body = cand
                page.screenshot(path=str(OUT / "_reply_open.png"), full_page=True)
                found = {
                    "query": q,
                    "subject": subj,
                    "from_email": frm,
                    "from_name": name,
                    "body": body,
                    "url": page.url,
                }
                break

        if not found:
            # fallback: inbox top unread today mentioning druck/anker
            page.goto("https://mail.google.com/mail/u/0/#inbox", wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            page.screenshot(path=str(OUT / "_inbox_now.png"))
            rows = page.locator("tr.zA.zE")  # unread
            print("unread", rows.count())
            for i in range(min(15, rows.count())):
                t = rows.nth(i).inner_text().replace("\n", " | ")
                print(f"U{i}: {t[:250]}")
                low = t.lower()
                if any(k in low for k in ("richner", "jelk", "vogt", "druck", "blocker", "461414", "anker")):
                    rows.nth(i).click(force=True)
                    page.wait_for_timeout(4000)
                    subj = page.locator("h2.hP").first.inner_text() if page.locator("h2.hP").count() else ""
                    frm = page.locator("span.gD").first.get_attribute("email") if page.locator("span.gD").count() else ""
                    name = page.locator("span.gD").first.get_attribute("name") if page.locator("span.gD").count() else ""
                    body = ""
                    for sel in ("div.a3s.aiL", "div.a3s"):
                        loc = page.locator(sel)
                        if loc.count():
                            cand = loc.last.inner_text()
                            if len(cand) > len(body):
                                body = cand
                    page.screenshot(path=str(OUT / "_reply_open.png"), full_page=True)
                    found = {"subject": subj, "from_email": frm, "from_name": name, "body": body, "url": page.url}
                    break

        if not found:
            raise SystemExit("no reply found")

        (OUT / "_reply_latest.json").write_text(
            json.dumps(found, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (OUT / "_reply_latest.txt").write_text(
            f"Subject: {found.get('subject')}\nFrom: {found.get('from_name')} <{found.get('from_email')}>\nURL: {found.get('url')}\n\n{found.get('body')}\n",
            encoding="utf-8",
        )
        print("SUBJECT", found.get("subject"))
        print("FROM", found.get("from_name"), found.get("from_email"))
        print("---BODY---")
        print(found.get("body"))


if __name__ == "__main__":
    main()
