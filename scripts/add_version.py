"""Write the new versions from a history the page exported as new files in data/versions.

    python scripts/add_version.py <exported file, e.g. wiring-log-v2.json>

Versions that already have a file must be identical in the export; if one differs, nothing is written.
"""
import json
import sys

from versions import dumps, load_all, path_of, split

export = json.loads(open(sys.argv[1], encoding="utf-8").read())
attached = {}
for f in export.get("versionFiles", []):
    f = dict(f)
    attached.setdefault(f.pop("version"), []).append(f)

existing = {v["n"]: (p, v) for p, v in load_all()}
new, errors = [], []
for v in sorted(export["versions"], key=lambda v: v["n"]):
    v = {k: x for k, x in v.items() if k != "virtual"}
    n = v["n"]
    if attached.get(n):
        v["files"] = attached[n]
    if n in existing:
        p, old = existing[n]
        if v != old:
            errors.append("version %d in the export differs from %s; an existing version must not change" % (n, p.as_posix()))
    else:
        new.append(v)
expected = max(existing, default=0) + 1
for v in new:
    if v["n"] != expected:
        errors.append("the export's version %d does not follow version %d" % (v["n"], expected - 1))
    expected += 1
if errors:
    sys.exit("Nothing written:\n  " + "\n  ".join(errors))
for v in new:
    path_of(v["n"]).write_text(dumps(v), encoding="utf-8")
    print("wrote %s: %s" % (path_of(v["n"]).as_posix(), v["message"]))
if not new:
    print("The export has no new versions.")
