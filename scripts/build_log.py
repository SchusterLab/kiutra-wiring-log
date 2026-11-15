"""Combine the version files in data/versions into data/log.json, the one file the page reads.

The publish workflow runs this; data/log.json is built, not stored in the repo. Run it yourself to preview the site:

    python scripts/build_log.py
    python -m http.server        # then open http://localhost:8000
"""
from pathlib import Path

from versions import dumps, load_all, split

versions, files = [], []
for _, v in load_all():
    v, attached = split(v)
    versions.append(v)
    files += [{**f, "version": v["n"]} for f in attached]
Path("data/log.json").write_text(dumps({"versions": versions, "versionFiles": files}), encoding="utf-8")
print("data/log.json: %d versions" % len(versions))
