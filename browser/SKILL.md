---
name: browser
description: Headless Chromium through Playwright for pages that need JavaScript, logins, clicks, or screenshots. Last resort after web-search and web-fetch.
---

# browser

```bash
python /data/agent/skills/browser/browse.py "https://example.com" [--wait-for "css selector"] [--screenshot /workspace/out/page.png] [--html]
```

Prints the page's visible text after load (networkidle, 30 s cap). `--screenshot` saves a PNG
you can send with `telegram_attach`. `--html` prints the rendered DOM instead of text.

For interaction (click, type, multi-step), write a short Python script with
`playwright.sync_api` (import from the venv; Chromium is preinstalled at
`$PLAYWRIGHT_BROWSERS_PATH`). Launch with `chromium.launch(args=["--no-sandbox"])`.
Keep every script bounded with timeouts. If Playwright reports a missing browser, the image
was built without `INSTALL_BROWSER=1`; say so instead of trying to download one.
