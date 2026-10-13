---
name: web-search
description: Answer questions that need current or external information by running one bounded OpenRouter web search. Use first for any question about news, prices, docs, versions, people, places, or anything you are not certain about.
---

# web-search

Run from anywhere:

```bash
python /data/agent/skills/web-search/search.py "your question here"
python /data/agent/skills/web-search/search.py --deep "complex question needing several searches"
```

`/data/agent` is the Pi agent directory (`$PI_CODING_AGENT_DIR`; `~/.pi/agent` links to it).

Output: a concise answer followed by a `Sources:` list of URLs. Keep those URLs in your reply
when the user would want them. One call costs roughly one search (about $0.007 on the Exa
fallback; native provider search is billed by the provider). `--deep` lets the model run up to
3 searches in one request.

Options: `--max-results N` (default 5), `--timeout S` (default 60), `--max-tokens N` (default 700).
If it fails, retry once; then fall back to `web-fetch` on a likely URL.
