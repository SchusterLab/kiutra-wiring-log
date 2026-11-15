"""Check the version files in data/versions before the site is published.

Older versions must never change: every version file must still exist and be exactly what it was in the commit that
added it. Version files are numbered v0001.json, v0002.json, ... with no gaps, and each one's `n` matches its name.
Run from the repository root, with the full git history (actions/checkout with fetch-depth: 0):

    python scripts/check_log.py
"""
import json
import subprocess
import sys
from pathlib import Path

from versions import NAME, VERSIONS, load_all, split

errors = []


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", check=True).stdout


found = load_all()
if not found:
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
    state = v.get("state") or {}
    if not isinstance(state.get("lines"), list) or not isinstance(state.get("stages"), list):
        errors.append("%s: `state` needs `stages` and `lines` lists" % where)
        continue
    ids = [it.get("id") for line in state["lines"] for it in line.get("items", [])]
    dup = sorted({str(i) for i in ids if ids.count(i) > 1})
    if dup:
        errors.append("%s: part ids used twice: %s" % (where, ", ".join(dup)))
    # Files the diagram links to must be in the repo.
    links = [a for line in state["lines"] for it in line.get("items", []) for a in it.get("attachments", [])] + split(v)[1]
    for a in links:
        if a.get("kind") == "file" and "/" in str(a.get("asset")) and not Path(a["asset"]).is_file():
            errors.append("%s: links to %s, which is not in the repo" % (where, a["asset"]))

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
    elif json.loads(Path(path).read_text(encoding="utf-8")) != first:
        errors.append("%s was changed; it must stay as added in %s. Add a new version instead" % (path, commit[:7]))

if errors:
    print("Version check failed:\n  " + "\n  ".join(errors))
    sys.exit(1)
p, v = found[-1]
print("OK: %d versions, latest is %s (%s)" % (len(found), p.as_posix(), v["message"]))
