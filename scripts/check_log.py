"""Check data/log.json before the site is published.

Older versions must never change: each version must be exactly what it was in the first commit that added it, and no
version may be removed. New versions are numbered on from the last one. Run from the repository root, with the full git
history (actions/checkout with fetch-depth: 0):

    python scripts/check_log.py
"""
import json
import subprocess
import sys
from pathlib import Path

LOG = "data/log.json"
errors = []


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", check=True).stdout


def versions_of(text):
    return {v["n"]: v for v in json.loads(text).get("versions", [])}


log = json.loads(Path(LOG).read_text(encoding="utf-8"))
versions = log.get("versions")
if not isinstance(versions, list) or not versions:
    sys.exit(LOG + ": `versions` must be a non-empty list")

# Numbering, required fields, and unique part ids within each version.
for k, v in enumerate(versions, start=1):
    where = "version at position %d" % k
    if v.get("n") != k:
        errors.append("%s has n = %r; versions must be numbered 1, 2, 3, ... in order" % (where, v.get("n")))
    for field, kind in (("ts", str), ("message", str), ("state", dict)):
        if not isinstance(v.get(field), kind):
            errors.append("%s: `%s` is missing or not a %s" % (where, field, kind.__name__))
    state = v.get("state") or {}
    if not isinstance(state.get("lines"), list) or not isinstance(state.get("stages"), list):
        errors.append("%s: `state` needs `stages` and `lines` lists" % where)
        continue
    ids = [it.get("id") for line in state["lines"] for it in line.get("items", [])]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        errors.append("%s: part ids used twice: %s" % (where, ", ".join(map(str, dup))))
    # Files the diagram links to must be in the repo.
    for line in state["lines"]:
        for it in line.get("items", []):
            for a in it.get("attachments", []):
                if a.get("kind") == "file" and "/" in str(a.get("asset")) and not Path(a["asset"]).is_file():
                    errors.append("%s: %s links to %s, which is not in the repo" % (where, it.get("id"), a["asset"]))

# Older versions: compare with the first commit that contained each one.
current = {v.get("n"): v for v in versions}
first_seen = {}
for commit in reversed(git("log", "--format=%H", "--", LOG).split()):
    try:
        old = versions_of(git("show", "%s:%s" % (commit, LOG)))
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        continue
    for n, v in old.items():
        first_seen.setdefault(n, (commit, v))
for n, (commit, v) in sorted(first_seen.items()):
    if n not in current:
        errors.append("version %d was removed (first added in %s)" % (n, commit[:7]))
    elif current[n] != v:
        errors.append("version %d was changed; it must stay as first committed in %s. Add a new version instead" % (n, commit[:7]))

if errors:
    print("data/log.json check failed:\n  " + "\n  ".join(errors))
    sys.exit(1)
print("data/log.json OK: %d versions, latest is version %d (%s)" % (len(versions), versions[-1]["n"], versions[-1]["message"]))
