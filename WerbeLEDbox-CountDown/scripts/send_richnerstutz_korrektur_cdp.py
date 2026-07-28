#!/usr/bin/env python3
"""Send Korrektur mail via existing Chrome CDP (port 9222)."""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
ZIP = (
    ROOT
    / "Richnerstutz-Bespannung-Paket"
    / "versand"
    / "Hotel-Anker-Korrektur-Druckdaten-2026-07-28.zip"
).resolve()
BODY = (
    ROOT
    / "Richnerstutz-Bespannung-Paket"
    / "01-anfrage"
    / "MAIL-KORREKTUR-Druckdaten.txt"
).read_text(encoding="utf-8").strip() + "\n"
SHOT = ROOT / "Richnerstutz-Bespannung-Paket" / "versand"

TO = "info@richnerstutz.ch"
CC = "tanja.jelk@richnerstutz.ch, melanie.vogt@richnerstutz.ch"
SUBJ = "AW: Druckdaten Korrektur — Hotel Anker / AG 461414 (CMYK, Bleed, Blocker)"


def dismiss_popups(page) -> None:
    for label in ("Got it", "No thanks", "Not now", "OK", "Dismiss", "Close", "No"):
        b = page.get_by_role("button", name=label)
        if b.count():
            try:
                b.first.click(timeout=1000)
            except Exception:
                pass


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = next(pg for pg in context.pages if "mail.google.com" in pg.url)
        page.bring_to_front()
        dismiss_popups(page)
        page.wait_for_timeout(500)

        page.get_by_role("button", name="Compose").click()
        page.wait_for_selector("input[name=subjectbox]", timeout=30000)
        print("compose open")

        to = page.locator(
            "textarea[name=to], div[aria-label='To'] input, input[aria-label='To recipients']"
        ).first
        to.click()
        to.fill(TO)
        page.keyboard.press("Tab")
        page.wait_for_timeout(300)

        cc_link = page.get_by_text("Cc", exact=True)
        if cc_link.count():
            try:
                cc_link.first.click(timeout=2000)
            except Exception:
                pass
        page.wait_for_timeout(300)
        cc = page.locator(
            "textarea[name=cc], div[aria-label='Cc'] input, input[aria-label='Cc']"
        )
        if cc.count():
            cc.first.click()
            cc.first.fill(CC)
            page.keyboard.press("Tab")

        page.locator("input[name=subjectbox]").fill(SUBJ)

        body = page.locator("div[aria-label='Message Body']").first
        body.click()
        page.keyboard.insert_text(BODY)

        fi = page.locator("input[type=file]")
        print("file_inputs", fi.count())
        if fi.count():
            fi.first.set_input_files(str(ZIP))
        else:
            with page.expect_file_chooser(timeout=15000) as fc:
                page.locator("div[command='Files']").first.click()
            fc.value.set_files(str(ZIP))

        attached = False
        for i in range(45):
            page.wait_for_timeout(1000)
            if page.get_by_text("Hotel-Anker-Korrektur").count():
                print("attachment visible after", i, "s")
                attached = True
                break
        print("attached", attached)
        page.screenshot(path=str(SHOT / "_gmail_before_send.png"))

        send = page.locator("div[role=button][aria-label*='Send']")
        print("send buttons", send.count())
        if send.count() == 0:
            page.keyboard.press("Control+Enter")
        else:
            send.first.click()

        page.wait_for_timeout(10000)
        page.screenshot(path=str(SHOT / "_gmail_after_send.png"))
        toast = page.get_by_text("Message sent")
        ok = toast.count() > 0
        print("toast", toast.count())
        print("RESULT", "OK" if ok else "UNCONFIRMED")
        return 0 if ok else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print("SEND FAILED:", exc, file=sys.stderr)
        raise
