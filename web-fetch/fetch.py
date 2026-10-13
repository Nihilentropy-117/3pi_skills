#!/usr/bin/env python3
"""Fetch a URL and print readable text."""
import argparse
import subprocess
import sys
import tempfile

import requests

UA = "Mozilla/5.0 (X11; Linux x86_64) 3pi-assistant/1.0"


def html_to_text(html: str, raw: bool) -> str:
    import html2text
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.body_width = 0
    if raw:
        return h.handle(html)
    from readability import Document
    doc = Document(html)
    title = (doc.short_title() or "").strip()
    text = h.handle(doc.summary(html_partial=True))
    return (f"# {title}\n\n" if title else "") + text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--max-chars", type=int, default=20000)
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--raw", action="store_true")
    a = ap.parse_args()
    try:
        r = requests.get(a.url, headers={"User-Agent": UA}, timeout=a.timeout, allow_redirects=True)
    except requests.RequestException as e:
        print(f"web-fetch: {e}", file=sys.stderr)
        return 1
    if r.status_code >= 400:
        print(f"web-fetch: HTTP {r.status_code}", file=sys.stderr)
        return 1
    ctype = r.headers.get("content-type", "")
    if "pdf" in ctype or a.url.lower().endswith(".pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(r.content)
            f.flush()
            out = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True, timeout=120)
            text = out.stdout
    elif "html" in ctype or r.text.lstrip()[:1] == "<":
        text = html_to_text(r.text, a.raw)
    else:
        text = r.text
    text = text.strip()
    if len(text) > a.max_chars:
        text = text[: a.max_chars] + f"\n\n[truncated at {a.max_chars} chars; total {len(text)}]"
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
