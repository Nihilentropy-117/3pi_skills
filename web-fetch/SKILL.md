---
name: web-fetch
description: Fetch one URL and return its readable text (HTML via readability, PDF via pdftotext). Use when you already know the URL or web-search returned a source worth reading in full.
---

# web-fetch

```bash
python /data/agent/skills/web-fetch/fetch.py "https://example.com/article" [--max-chars 20000] [--raw]
```

Prints clean text (title first). `--raw` skips readability and returns the whole page text.
PDFs are converted with `pdftotext`. Private and LAN addresses are blocked by the sandbox
firewall and fail immediately. Pages that need JavaScript come back thin; use the `browser`
skill for those.
