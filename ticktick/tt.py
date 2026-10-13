import os, sys, json, argparse, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
B = "https://api.ticktick.com/open/v1"
TZN = os.environ.get("TZ_NAME", "America/New_York")
TZ = ZoneInfo(TZN)

def api(method, path, body=None):
    r = urllib.request.Request(B + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + os.environ["TICKTICK_API_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=20) as f:
        t = f.read().decode()
        return json.loads(t) if t else None

def parse(s):
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try: return datetime.strptime(s, fmt).replace(tzinfo=TZ)
        except ValueError: pass
    sys.exit("bad date: " + s)

def fmt(d): return d.strftime("%Y-%m-%dT%H:%M:%S%z")

def projects(): return api("GET", "/project")

def all_tasks():
    out = []
    for p in [{"id": "inbox", "name": "Inbox"}] + [p for p in projects() if p["name"] != "Inbox"]:
        try: d = api("GET", f"/project/{p['id']}/data")
        except Exception: continue
        for t in d.get("tasks", []):
            t["_p"] = p["name"]; out.append(t)
    return out

def when(t):
    s = t.get("startDate") or t.get("dueDate")
    if not s: return None
    return datetime.strptime(s.replace(".000", ""), "%Y-%m-%dT%H:%M:%S%z").astimezone(TZ)

def line(t):
    w = when(t)
    ws = "undated" if not w else (w.strftime("%Y-%m-%d") if t.get("isAllDay") else w.strftime("%Y-%m-%d %H:%M"))
    return f"{ws} | {t['title']} | {t['_p']} | {t['id']}"

a = argparse.ArgumentParser()
sp = a.add_subparsers(dest="c", required=True)
sp.add_parser("projects")
x = sp.add_parser("add"); x.add_argument("title"); x.add_argument("--start", required=True)
x.add_argument("--end"); x.add_argument("--allday", action="store_true")
x.add_argument("--project"); x.add_argument("--desc"); x.add_argument("--remind", type=int)
x = sp.add_parser("search"); x.add_argument("q")
x = sp.add_parser("list"); x.add_argument("--from", dest="frm"); x.add_argument("--days", type=int, default=7)
n = a.parse_args()

if n.c == "projects":
    for p in projects(): print(p["id"], p["name"])
elif n.c == "add":
    s = parse(n.start)
    body = {"title": n.title, "startDate": fmt(s), "timeZone": TZN, "isAllDay": n.allday}
    body["dueDate"] = fmt(parse(n.end) if n.end else (s + timedelta(days=1) if n.allday else s + timedelta(hours=1)))
    if n.allday: body["dueDate"] = fmt(s)
    if n.desc: body["content"] = n.desc
    if n.remind is not None: body["reminders"] = ["TRIGGER:PT0S" if n.remind == 0 else f"TRIGGER:-PT{n.remind}M"]
    if n.project:
        m = [p for p in projects() if p["name"].lower() == n.project.lower()]
        if not m: sys.exit("no such project")
        body["projectId"] = m[0]["id"]
    t = api("POST", "/task", body)
    print("created:", t["id"], t["title"], t.get("startDate"))
elif n.c == "search":
    q = n.q.lower()
    for t in all_tasks():
        if q in t["title"].lower() or q in (t.get("content") or "").lower(): print(line(t))
elif n.c == "list":
    f = parse(n.frm) if n.frm else datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    e = f + timedelta(days=n.days)
    r = [(when(t), t) for t in all_tasks() if when(t) and f <= when(t) < e]
    for _, t in sorted(r, key=lambda z: z[0]): print(line(t))
