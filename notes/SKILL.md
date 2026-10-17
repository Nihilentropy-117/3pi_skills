---
name: notes
description: Gray's Obsidian vault (Wanderland) at /workspace/Grays Files/Notes — what each folder holds, how to search it, and how to add notes to Intake. Use whenever a request touches Gray's notes, recipes, places, quotes, media lists, or asks you to save something as a note.
---

# notes

`/workspace/Grays Files/Notes` is Gray's Obsidian vault **Wanderland**, kept in sync with Obsidian
Sync by a separate container. Edits Gray makes on any device show up here within seconds.

## Access
- Everything is **read-only** (the mount refuses writes, even with sudo) **except `Intake/`**.
- Everything you create for the vault goes in `Intake/`. Gray files it from there.
- Never try to work around the read-only mount. To change an existing note, write the proposed
  version (or a diff) to `Intake/` and say so.
- Ignore `.obsidian/` (app config) and `.trash/`.

## Folders
<!-- Placeholder descriptions; Gray will replace these. -->
| Folder | Contents |
|---|---|
| `Hexhiker/` | Notes for the Hexhiker project. |
| `Media/` | Books, films, shows, and games: lists, reviews, notes. |
| `Personal/` | Personal notes, journaling, and life admin. |
| `Places/` | Locations: travel notes, places visited or wanted. |
| `Quotes/` | Collected quotes. |
| `Real Gray/` | Notes about Gray. |
| `Recipies/` | Recipes (folder name spelled this way on purpose; keep it). |
| `Intake/` | **Read-write.** Inbox for everything you create. |

## Searching
```bash
rg -i --type md "term" "/workspace/Grays Files/Notes"          # full text
rg -il --type md "term" "/workspace/Grays Files/Notes/Recipies" # one folder, filenames only
find "/workspace/Grays Files/Notes" -name '*.md' -newermt '-7 days'  # recently changed
```
Quote paths: folder names contain spaces. Notes link to each other with `[[Note name]]`;
resolve a link by searching for `Note name.md`.

## Semantic search (smartvec.py)
`smartvec.py` (next to this file) queries the vault's **Smart Connections** embeddings
(`.smart-env/` folder, written by the Obsidian plugin) without Obsidian. Use it for fuzzy or
"related to" questions where `rg` keyword search misses; use `rg` for exact terms.

```bash
S=/data/agent/skills/notes/smartvec.py
python $S .smart-env info                                  # counts, stale rows, model
python $S .smart-env search "copier fuser error" -k 10     # best sections (blocks)
python $S .smart-env search "copier fuser error" --notes   # best whole notes
python $S .smart-env near "Intake/Carlin.md" --notes       # notes related to this one
python $S .smart-env export vectors.jsonl                  # {"key","vec"} per line
```
`ENV` (first arg) is the vault's `.smart-env` folder; give its full path
(`/workspace/Grays Files/Notes/.smart-env`) unless you are in the vault root.

How it works:
- Reads `smart_sources/smart_sources.ajson` (metadata; append-only JSON lines, later lines win,
  `null` deletes). Each note/block entry points at a row in a raw vector file
  (`smart_sources/<file>` for notes, `smart_blocks/<file>` for blocks): float32 little-endian,
  384 dims, no header. Model: `TaylorAI/bge-micro-v2` (from `embedding_models.ajson`).
- Only rows that metadata points at are used; other rows are stale (deleted/edited notes) and
  ignored. `info` reports the stale count.
- Vectors are L2-normalised; ranking is cosine similarity (dot product). Output is
  `score  key`; blocks keys look like `Folder/Note.md#Heading`, notes keys are paths.
- Default is **blocks** (sections); `--notes` uses one vector per whole note.
- `search` embeds the query locally with the same model via `sentence_transformers` (first run
  downloads the model). `near` needs no model: it uses the note's own vector (blocks mode
  averages the note's block vectors, or takes an exact block key) and excludes the note itself.
- `export` dumps normalised vectors as JSONL for other tooling.
- Read-only: it never writes to the vault. Write `export` output under `/workspace/out/`.
- Needs `numpy` (and `sentence_transformers` for `search`); `pip install` if missing.
- Scores only mean something relative to each other; the index lags recent edits until
  Obsidian re-embeds them.

## Writing to Intake
- Obsidian Markdown, one note per file, `.md` extension.
- Filename: the note's title, e.g. `Intake/Lemon Risotto.md`. No dates in filenames unless the
  note is dated by nature. Avoid `/ \ : * ? " < > |` and leading dots.
- Start with YAML frontmatter:
  ```yaml
  ---
  created: 2026-10-16
  source: assistant
  suggested-folder: Recipies
  tags: []
  ---
  ```
- Link to existing notes with `[[Exact Note Name]]` when relevant.
- Never overwrite a file in `Intake/` that you did not create in this conversation; pick a new
  name instead.
- Attachments (images, PDFs) go in `Intake/` too, embedded with `![[file.png]]`.
