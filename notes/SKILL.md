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
