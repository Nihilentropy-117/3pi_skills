---
name: ticktick
description: Add, search, and list events/tasks on Gray's TickTick calendar via the TickTick Open API. Use when asked to schedule something, add a reminder/event, or check what's on the calendar.
---
# ticktick

Auth: env `TICKTICK_API_KEY` (Bearer token). Stdlib only. Timezone default `America/New_York` (override `TZ_NAME`).
TickTick's Open API has no separate "events"; calendar entries are tasks with a start/due date, so events are created as tasks.

```
python /data/agent/skills/ticktick/tt.py projects
python /data/agent/skills/ticktick/tt.py add "Dentist" --start "2026-10-20 14:30" [--end "2026-10-20 15:30"] [--allday] [--project NAME] [--desc TEXT] [--remind 15]
python /data/agent/skills/ticktick/tt.py update ID [--title T] [--start "2027-06-01" --allday] [--desc TEXT]   # id from search/list
python /data/agent/skills/ticktick/tt.py search "dentist"            # title/content substring, all projects
python /data/agent/skills/ticktick/tt.py list [--from YYYY-MM-DD] [--days 7]   # dated, uncompleted items in range
```
- Times are local (America/New_York), `YYYY-MM-DD[ HH:MM]`. Default project is Inbox.
- `--remind N` = reminder N minutes before (0 = at start).
- Only uncompleted tasks are searched/listed (API limitation of project data).
- Prints one line per item: date, title, project, id.
