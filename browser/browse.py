#!/usr/bin/env python3
"""Load a page in headless Chromium and print its visible text."""
import argparse
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--wait-for", help="CSS selector to wait for")
    ap.add_argument("--screenshot", help="PNG output path")
    ap.add_argument("--html", action="store_true", help="print rendered HTML instead of text")
    ap.add_argument("--timeout", type=int, default=30, help="seconds")
    ap.add_argument("--max-chars", type=int, default=20000)
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("browser: playwright is not installed in the venv (pip install playwright==<image version>)", file=sys.stderr)
        return 2
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-dev-shm-usage"])
        except Exception as e:  # noqa: BLE001
            print(f"browser: cannot launch Chromium: {e}", file=sys.stderr)
            return 2
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.set_default_timeout(a.timeout * 1000)
        try:
            page.goto(a.url, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle", timeout=min(a.timeout, 15) * 1000)
            except Exception:  # noqa: BLE001
                pass
            if a.wait_for:
                page.wait_for_selector(a.wait_for)
            if a.screenshot:
                page.screenshot(path=a.screenshot, full_page=True)
            out = page.content() if a.html else page.evaluate("() => document.body ? document.body.innerText : ''")
        finally:
            browser.close()
    out = (out or "").strip()
    if len(out) > a.max_chars:
        out = out[: a.max_chars] + f"\n\n[truncated at {a.max_chars} chars]"
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
