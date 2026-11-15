"""Start a new version: copy the newest version file to the next number, with its number, time, author and message filled in.

    python scripts/new_version.py "Replace the RF2 IR filter with a 10 dB attenuator"
    python scripts/new_version.py "..." --notes "Done in cooldown 12" --author <GitHub username>

Then make the change in the new file's `state` and run python scripts/check_log.py. The author defaults to your GitHub
username from the GitHub CLI (gh) if it is installed and logged in, and otherwise to git's user.name.
"""
import sys
import argparse
import datetime
import subprocess

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # part names use symbols such as Ω

from versions import dumps, load_all, path_of, split


def github_user():
    for cmd in (["gh", "api", "user", "--jq", ".login"], ["git", "config", "user.name"]):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            continue
        if out:
            return out
    return None


ap = argparse.ArgumentParser(description="Start a new version from a copy of the newest one.")
ap.add_argument("message", help="one line: what changed")
ap.add_argument("--notes", default="", help="why, and what was measured")
ap.add_argument("--author", default=None, help="your GitHub username")
args = ap.parse_args()

_, newest = load_all()[-1]
v, _ = split(newest)  # files attached to the old version stay with it
n = v["n"] + 1
new = {
    "n": n,
    "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "author": args.author or github_user(),
    "message": args.message.strip(),
    "notes": args.notes.strip(),
    "state": v["state"],
}
path = path_of(n)
if path.exists():
    raise SystemExit("%s already exists" % path.as_posix())
path.write_text(dumps(new), encoding="utf-8", newline="\n")
print("wrote %s, a copy of version %d by %s. Now make the change in its `state`." % (path.as_posix(), n - 1, new["author"]))
