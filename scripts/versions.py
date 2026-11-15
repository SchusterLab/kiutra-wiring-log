"""Read and write the version files in data/versions, one wiring version per file (v0001.json, v0002.json, ...)."""
import json
import re
from pathlib import Path

VERSIONS = Path("data/versions")
NAME = re.compile(r"^v(\d{4})\.json$")


def path_of(n):
    return VERSIONS / ("v%04d.json" % n)


def dumps(obj):
    """The layout of every file under data/: two-space indentation, as the page's export writes it."""
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def load_all():
    """All versions in order of their file names, as (path, version) pairs."""
    return [(p, json.loads(p.read_text(encoding="utf-8"))) for p in sorted(VERSIONS.glob("v*.json"))]


def split(v):
    """A version file holds the version and, under "files", the files attached to it. Return the two apart."""
    v = dict(v)
    return v, v.pop("files", [])
