#!/usr/bin/env python3
"""smartvec — query Smart Connections (smart-env) embeddings outside Obsidian.

Reads a vault's .smart-env folder directly:
  smart_sources/smart_sources.ajson   metadata; each embedded note/block carries
                                      embedding.default.<file>.file_i = row index
  smart_sources/<file>                note vectors   (float32 LE, 384 dims, no header)
  smart_blocks/<file>                 block vectors  (same layout)
  embedding_models/embedding_models.ajson  model id (TaylorAI/bge-micro-v2)

Rows with no metadata pointing at them are stale (deleted/changed notes) and are ignored.

Usage:
  smartvec.py ENV info
  smartvec.py ENV search "query text" [-k 10] [--notes]
  smartvec.py ENV near "Folder/Note.md" [-k 10] [--notes]
  smartvec.py ENV export out.jsonl [--notes]

ENV is the .smart-env folder. Default collection is blocks (sections); --notes uses whole-note vectors.
"""
import argparse, json, os, sys
import numpy as np


def read_ajson(path):
    """ajson = JSON object body appended line by line; later lines win, null deletes."""
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip().rstrip(",")
            if not line:
                continue
            try:
                obj = json.loads("{" + line + "}")
            except json.JSONDecodeError:
                continue
            for k, v in obj.items():
                if v is None:
                    out.pop(k, None)
                else:
                    out[k] = v
    return out


def pointer(entry):
    """Return (file, row) from an entry's embedding.default, or None."""
    default = (entry.get("embedding") or {}).get("default") or {}
    for p in default.values():
        if isinstance(p, dict) and "file_i" in p:
            return p.get("file"), p["file_i"]
    return None


def model_key(env):
    p = os.path.join(env, "embedding_models", "embedding_models.ajson")
    if os.path.exists(p):
        for v in read_ajson(p).values():
            return v.get("model_key", "TaylorAI/bge-micro-v2"), v.get("dims", 384)
    return "TaylorAI/bge-micro-v2", 384


def load(env, notes):
    _, dims = model_key(env)
    sources = read_ajson(os.path.join(env, "smart_sources", "smart_sources.ajson"))
    keys, ptrs = [], []
    for skey, s in sources.items():
        path = s.get("path") or skey.split(":", 1)[-1]
        if notes:
            p = pointer(s)
            if p:
                keys.append(path); ptrs.append(p)
        else:
            for b in (s.get("blocks_data") or {}).values():
                p = pointer(b)
                if p:
                    keys.append(b.get("key", path)); ptrs.append(p)
    folder = os.path.join(env, "smart_sources" if notes else "smart_blocks")
    cache, rows = {}, []
    for f, i in ptrs:
        if f not in cache:
            raw = np.fromfile(os.path.join(folder, f), dtype="<f4")
            cache[f] = raw.reshape(-1, dims)
        rows.append(cache[f][i])
    M = np.asarray(rows, dtype=np.float32)
    M /= np.linalg.norm(M, axis=1, keepdims=True)
    total = sum(len(m) for m in cache.values())
    return keys, M, total


def show(M, keys, q, k, skip=None):
    s = M @ q
    if skip is not None:
        s[skip] = -np.inf
    for i in np.argsort(-s)[:k]:
        print(f"{s[i]:.4f}  {keys[i]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("env")
    ap.add_argument("cmd", choices=["info", "search", "near", "export"])
    ap.add_argument("arg", nargs="?")
    ap.add_argument("-k", type=int, default=10)
    ap.add_argument("--notes", action="store_true", help="use whole-note vectors instead of blocks")
    a = ap.parse_args()

    keys, M, total = load(a.env, a.notes)

    if a.cmd == "info":
        kind = "notes" if a.notes else "blocks"
        print(f"{len(keys)} {kind} mapped / {total} rows in file ({total - len(keys)} stale), model {model_key(a.env)[0]}")
    elif a.cmd == "search":
        from sentence_transformers import SentenceTransformer
        q = SentenceTransformer(model_key(a.env)[0]).encode([a.arg], normalize_embeddings=True)[0]
        show(M, keys, q, a.k)
    elif a.cmd == "near":
        if a.notes:
            hits = [i for i, k in enumerate(keys) if k == a.arg]
            if not hits:
                sys.exit(f"not found: {a.arg}")
            q, skip = M[hits[0]], hits
        else:
            # blocks: average the note's block vectors (or match an exact block key)
            hits = [i for i, k in enumerate(keys) if k == a.arg or k.startswith(a.arg + "#")]
            if not hits:
                sys.exit(f"not found: {a.arg}")
            q = M[hits].mean(0); q /= np.linalg.norm(q); skip = hits
        show(M, keys, q, a.k, skip=skip)
    elif a.cmd == "export":
        with open(a.arg, "w", encoding="utf-8") as fh:
            for k, v in zip(keys, M):
                fh.write(json.dumps({"key": k, "vec": [round(float(x), 7) for x in v]}) + "\n")
        print(f"wrote {len(keys)} rows to {a.arg}")


if __name__ == "__main__":
    main()
