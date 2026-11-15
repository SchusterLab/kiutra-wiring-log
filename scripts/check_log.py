"""Check the version files in data/versions before the site is published.

Older versions must never change: every version file must still exist and be exactly what it was in the commit that
added it. Each version must also be complete enough for the page to draw: every part on a stage that exists, of a
known type, and every connection to a part that exists. Run from the repository root, with the full git history
(actions/checkout with fetch-depth: 0):

    python scripts/check_log.py
"""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # part names use symbols such as Ω

from versions import NAME, VERSIONS, split

# Part types the page draws (TYPES in index.html), and those with more than two ports, which another line can feed.
TYPES = {"connector", "cable", "attenuator", "filter", "amplifier", "isolator", "coupler", "diplexer", "splitter", "anchor", "other"}
MULTIPORT = {"isolator", "coupler", "diplexer", "splitter", "other"}
errors = []


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", check=True).stdout


def check_attachment(where, a):
    if not isinstance(a, dict) or not a.get("id") or a.get("kind") not in ("file", "link"):
        errors.append("%s: an attachment needs an `id` and a `kind` of \"file\" or \"link\": %r" % (where, a))
    elif a["kind"] == "link" and not str(a.get("url", "")).startswith(("https://", "http://")):
        errors.append("%s: link %s needs a `url` starting with https://" % (where, a["id"]))
    elif a["kind"] == "file" and "/" in str(a.get("asset")) and not Path(a["asset"]).is_file():
        errors.append("%s: file %s is %s, which is not in the repo" % (where, a["id"], a.get("asset")))
    elif a["kind"] == "file" and not a.get("asset"):
        errors.append("%s: file %s needs an `asset`, its path such as files/datasheet.pdf" % (where, a["id"]))


def check_state(where, state):
    if not isinstance(state.get("lines"), list) or not isinstance(state.get("stages"), list):
        errors.append("%s: `state` needs `stages` and `lines` lists" % where)
        return
    stages = [s.get("id") for s in state["stages"]]
    for s in state["stages"]:
        if not s.get("id") or not s.get("name"):
            errors.append("%s: every stage needs an `id` and a `name`: %r" % (where, s))
    if len(set(stages)) != len(stages):
        errors.append("%s: stage ids used twice" % where)
    line_ids = [l.get("id") for l in state["lines"]]
    if len(set(line_ids)) != len(line_ids):
        errors.append("%s: line ids used twice" % where)
    parts = {}  # part id -> (line id, type)
    for line in state["lines"]:
        lw = "%s, line %s" % (where, line.get("name") or line.get("id"))
        if not line.get("id") or not line.get("name"):
            errors.append("%s: a line needs an `id` and a `name`" % lw)
        if line.get("group") not in ("dc", "rf"):
            errors.append("%s: `group` must be \"dc\" or \"rf\", not %r" % (lw, line.get("group")))
        if not isinstance(line.get("items"), list):
            errors.append("%s: `items` must be a list" % lw)
            continue
        for it in line["items"]:
            iw = "%s, part %s" % (lw, it.get("id"))
            if not it.get("id"):
                errors.append("%s: a part has no `id`" % lw)
            elif it["id"] in parts:
                errors.append("%s: part id used twice in this version" % iw)
            parts[it.get("id")] = (line.get("id"), it.get("type"))
            if it.get("type") not in TYPES:
                errors.append("%s: unknown `type` %r; use one of %s" % (iw, it.get("type"), ", ".join(sorted(TYPES))))
            if it.get("stage") not in stages:
                errors.append("%s: `stage` %r is not a stage id (%s)" % (iw, it.get("stage"), ", ".join(map(str, stages))))
            if it.get("at") not in ("plate", "region"):
                errors.append("%s: `at` must be \"plate\" or \"region\", not %r" % (iw, it.get("at")))
            for a in it.get("attachments", []):
                check_attachment(iw, a)
    # Connections into another line's multi-port part.
    for line in state["lines"]:
        for it in line.get("items", []):
            link = it.get("link")
            if link is None:
                continue
            iw = "%s, line %s, part %s" % (where, line.get("name"), it.get("id"))
            target = parts.get(link.get("item")) if isinstance(link, dict) else None
            if not target or target[0] != link.get("line"):
                errors.append("%s: `link` points at part %r on line %r, which does not exist" % (iw, link.get("item") if isinstance(link, dict) else link, link.get("line") if isinstance(link, dict) else None))
            elif target[0] == line.get("id"):
                errors.append("%s: `link` must point at a part on another line" % iw)
            elif target[1] not in MULTIPORT:
                errors.append("%s: `link` points at a %s, which has no spare port; use one of %s" % (iw, target[1], ", ".join(sorted(MULTIPORT))))


found = []
for p in sorted(VERSIONS.glob("v*.json")):
    try:
        found.append((p, json.loads(p.read_text(encoding="utf-8"))))
    except json.JSONDecodeError as e:
        errors.append("%s is not valid JSON: %s" % (p.as_posix(), e))
if not found and not errors:
    sys.exit("no version files in %s" % VERSIONS.as_posix())

for k, (p, v) in enumerate(found, start=1):
    where = p.as_posix()
    m = NAME.match(p.name)
    if not m or int(m.group(1)) != k:
        errors.append("%s: version files must be named v0001.json, v0002.json, ... with no gaps" % where)
    if v.get("n") != k:
        errors.append("%s: `n` is %r; it must be %d, the number in the file name" % (where, v.get("n"), k))
    for field, kind in (("ts", str), ("message", str), ("state", dict)):
        if not isinstance(v.get(field), kind):
            errors.append("%s: `%s` is missing or not a %s" % (where, field, kind.__name__))
    if isinstance(v.get("message"), str) and not v["message"].strip():
        errors.append("%s: `message` is empty; say in one line what changed" % where)
    if isinstance(v.get("state"), dict):
        check_state(where, v["state"])
    for a in split(v)[1]:
        check_attachment(where + ", files", a)

# Older versions: each file ever added must still be as it was in the commit that added it.
added = {}
log = git("log", "--reverse", "--diff-filter=A", "--format=commit %H", "--name-only", "--", VERSIONS.as_posix())
commit = None
for line in log.splitlines():
    if line.startswith("commit "):
        commit = line.split()[1]
    elif line.strip():
        added.setdefault(line.strip(), commit)
for path, commit in sorted(added.items()):
    first = json.loads(git("show", "%s:%s" % (commit, path)))
    if not Path(path).is_file():
        errors.append("%s was deleted (added in %s); restore it" % (path, commit[:7]))
    else:
        try:
            now = json.loads(Path(path).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # reported above
        if now != first:
            errors.append("%s was changed; it must stay as added in %s. Add a new version instead" % (path, commit[:7]))

if errors:
    print("Version check failed:\n  " + "\n  ".join(errors))
    sys.exit(1)
p, v = found[-1]
print("OK: %d versions, latest is %s (%s)" % (len(found), p.as_posix(), v["message"]))
