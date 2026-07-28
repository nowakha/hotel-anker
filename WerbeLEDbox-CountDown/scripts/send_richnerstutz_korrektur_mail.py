#!/usr/bin/env python3
"""Send Richnerstutz Korrektur mail via Gmail Web (Chrome profile)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIL_MD = ROOT / "Richnerstutz-Bespannung-Paket" / "01-anfrage" / "MAIL-KORREKTUR-Druckdaten.md"
ZIP = (
    ROOT
    / "Richnerstutz-Bespannung-Paket"
    / "versand"
    / "Hotel-Anker-Korrektur-Druckdaten-2026-07-28.zip"
)
BODY_TXT = (
    ROOT
    / "Richnerstutz-Bespannung-Paket"
    / "01-anfrage"
    / "MAIL-KORREKTUR-Druckdaten.txt"
)

TO = "info@richnerstutz.ch"
CC = "tanja.jelk@richnerstutz.ch, melanie.vogt@richnerstutz.ch"
SUBJECT = "AW: Druckdaten Korrektur — Hotel Anker / AG 461414 (CMYK, Bleed, Blocker)"


def body_text() -> str:
    text = BODY_TXT.read_text(encoding="utf-8")
    # strip meta footer lines starting with em-dash An/CC
    lines = []
    for line in text.splitlines():
        if line.startswith("— An:") or line.startswith("— CC:"):
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    from playwright.sync_api import sync_playwright

    if not ZIP.exists():
        raise SystemExit(f"missing zip {ZIP}")
    body = body_text()
    user_data = Path.home() / "AppData/Local/Google/Chrome/User Data"
    if not user_data.exists():
        raise SystemExit(f"missing Chrome profile {user_data}")

    print("launching Chrome (existing profile)…")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(user_data),
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            accept_downloads=True,
        )
        page = context.new_page()
        page.goto("https://mail.google.com/mail/u/0/#inbox", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        # Compose
        compose = page.get_by_role("button", name=lambda n: n and "Verfassen" in n or (n and "Compose" in n))
        if compose.count() == 0:
            # fallback German/English
            for label in ("Verfassen", "Compose", "Schreibe"):
                loc = page.get_by_text(label, exact=True)
                if loc.count():
                    loc.first.click()
                    break
            else:
                page.keyboard.press("c")
        else:
            compose.first.click()

        page.wait_for_timeout(2000)

        # To field
        to_box = page.locator("input[peoplekit-id='BbVjBd'], input[aria-label='An'], input[aria-label='To']").first
        if to_box.count() == 0:
            to_box = page.locator("div[aria-label='An'] input, div[aria-label='To'] input").first
        to_box.click()
        to_box.fill(TO)
        page.keyboard.press("Tab")
        page.wait_for_timeout(500)

        # CC
        cc_btn = page.get_by_text("Cc", exact=True)
        if cc_btn.count():
            cc_btn.first.click()
            page.wait_for_timeout(400)
        cc_box = page.locator("input[aria-label='Cc'], input[aria-label='CC']").first
        if cc_box.count():
            cc_box.fill(CC)
            page.keyboard.press("Tab")

        # Subject
        subj = page.locator("input[name='subjectbox']").first
        subj.fill(SUBJECT)

        # Body
        body_box = page.locator("div[aria-label='Nachrichtentext'], div[aria-label='Message Body']").first
        body_box.click()
        body_box.fill(body)

        # Attach
        page.set_input_files("input[type='file'][name='Filedata'], input[type='file']", str(ZIP))
        page.wait_for_timeout(8000)

        # Send
        send = page.get_by_role("button", name=lambda n: n and ("Senden" in n or "Send" in n))
        if send.count():
            send.first.click()
        else:
            page.keyboard.press("Control+Enter")

        page.wait_for_timeout(8000)
        content = page.content()
        ok = ("Message sent" in content) or ("Nachricht gesendet" in content) or ("sent" in content.lower())
        print("send_ok_heuristic", ok)
        # Keep browser briefly for visual confirm
        page.wait_for_timeout(3000)
        context.close()
        return 0 if ok else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print("SEND FAILED:", exc, file=sys.stderr)
        raise
