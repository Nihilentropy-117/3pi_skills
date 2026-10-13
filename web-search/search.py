#!/usr/bin/env python3
"""One bounded web search through OpenRouter: concise answer plus source URLs.

Default: the `web` plugin (exactly one search, predictable cost). --deep: the
`openrouter:web_search` server tool with max_uses=3 so the model can search several times.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

API = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1") + "/chat/completions"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--deep", action="store_true", help="allow up to 3 searches (server tool)")
    ap.add_argument("--max-results", type=int, default=5)
    ap.add_argument("--max-tokens", type=int, default=700)
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("SEARCH_MODEL")
    if not key or not model:
        print("web-search: OPENROUTER_API_KEY and SEARCH_MODEL must be set", file=sys.stderr)
        return 2

    body = {
        "model": model,
        "max_tokens": args.max_tokens,
        "messages": [
            {"role": "system", "content": "Answer concisely for a reader on a phone. Cite sources as markdown links. If the results do not answer the question, say so."},
            {"role": "user", "content": args.query},
        ],
    }
    if args.deep:
        body["tools"] = [{"type": "openrouter:web_search", "parameters": {"max_results": args.max_results, "max_uses": 3, "max_total_results": 15}}]
    else:
        body["plugins"] = [{"id": "web", "max_results": args.max_results}]

    req = urllib.request.Request(
        API,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "X-Title": "3pi web-search"},
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        print(f"web-search: HTTP {e.code}: {e.read()[:500].decode(errors='replace')}", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"web-search: request failed: {e}", file=sys.stderr)
        return 1

    msg = (data.get("choices") or [{}])[0].get("message") or {}
    content = msg.get("content") or ""
    urls = []
    for a in msg.get("annotations") or []:
        u = (a.get("url_citation") or {}).get("url")
        if u and u not in urls:
            urls.append(u)
    for u in re.findall(r"https?://[^\s)\]>\"']+", content):
        if u not in urls:
            urls.append(u)

    print(content.strip())
    if urls:
        print("\nSources:")
        for u in urls[:10]:
            print(f"- {u}")
    usage = data.get("usage") or {}
    if usage:
        print(f"\n[tokens: {usage.get('prompt_tokens', '?')} in / {usage.get('completion_tokens', '?')} out]", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
