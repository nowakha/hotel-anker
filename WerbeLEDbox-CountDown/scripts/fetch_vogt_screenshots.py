#!/usr/bin/env python3
"""Download images from the currently open Gmail message via CDP."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parents[2] / "Richnerstutz-Bespannung-Paket" / "versand" / "vogt-feedback"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        ctx = browser.contexts[0]
        page = next(pg for pg in ctx.pages if "mail.google" in pg.url)
        page.bring_to_front()
        page.screenshot(path=str(OUT / "mail_full.png"), full_page=True)

        urls = page.evaluate(
            """() => Array.from(document.querySelectorAll('img'))
                .map(i => ({src: i.src, w: i.naturalWidth, h: i.naturalHeight}))
                .filter(x => x.src && x.w > 200)"""
        )
        print("candidate imgs", len(urls))
        for i, item in enumerate(urls):
            src = item["src"]
            print(i, item["w"], item["h"], src[:100])
            try:
                resp = page.request.get(src)
                data = resp.body()
                ext = "png" if data.startswith(b"\x89PNG") else "jpg"
                path = OUT / f"shot_{i}_{item['w']}x{item['h']}.{ext}"
                path.write_bytes(data)
                print(" wrote", path.name, len(data))
            except Exception as exc:  # noqa: BLE001
                print(" fail", exc)

        # Also try attachment download buttons / googleusercontent hrefs
        hrefs = page.evaluate(
            """() => Array.from(document.querySelectorAll('a[href]'))
                .map(a => a.href)
                .filter(h => h.includes('googleusercontent') || h.includes('attachment') || h.includes('disp=safe'))"""
        )
        print("hrefs", len(hrefs))
        for i, h in enumerate(hrefs[:20]):
            print(i, h[:160])


if __name__ == "__main__":
    main()
