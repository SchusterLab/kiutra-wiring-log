# Notes for coding agents

`data/versions/` holds the wiring history of a cryostat, one version per file, and the site in `index.html` only reads it.
Read `README.md` first.

## Never overwrite an older version

The version files are append-only.
Make every change by adding one new file, `data/versions/v<n>.json`, with `n` one more than the newest file's, written with four digits.
Never edit, rename or delete an existing version file, even to fix a typo or reformat it.
To undo a change, add a new version that copies an older version's `state`.

Before you commit, run `python scripts/check_log.py`, and check that `git status` shows only the new version file (and any new file in `files/`) as changed.
The script compares every version file with the commit that added it, and CI runs the same check before publishing.
If the check fails because you changed an older version, put that file back as it was; don't change the check.

Write the file with two-space JSON indentation and a final newline, like the existing files.
`data/log.json` is built by `scripts/build_log.py`; don't commit it.

## A version file

```json
{
  "n": 2,
  "ts": "2026-11-20T18:00:00Z",
  "author": "<GitHub username, or null>",
  "message": "<one line: what changed>",
  "notes": "<optional: why, and what was measured>",
  "state": { "meta": {}, "stages": [], "lines": [] }
}
```

- `n` matches the number in the file name.
- `ts` is the time of the change, in UTC.
- `state` is the complete wiring, not a diff. Start from a copy of the newest version's `state` and change only what changed.
- `files`, optional, lists documents that belong to the version as a whole, such as a drawing or a photo, in the attachment format of `README.md`, under Datasheets.

Inside `state`, each line in `lines` has `id`, `group` (`"dc"` or `"rf"`), `name`, `purpose` and `items`.
Each item is one part, listed from the top of the cryostat down: `id`, `type`, `stage` (an `id` from `stages`), `at` (`"plate"` for a part on the plate, `"region"` for one below it), `label`, `detail` and `note`.
The types are `connector`, `cable`, `attenuator`, `filter`, `amplifier`, `isolator`, `coupler`, `diplexer`, `splitter`, `anchor` and `other`.
An item that feeds a port of a part on another line has `"link": {"line": "<line id>", "item": "<item id>", "port": "<port name>"}`.
A part's datasheets go in its `attachments`, in the format of `README.md`, under Datasheets.

Keep the `id` of every part that stays, because the History tab matches parts between versions by `id`.
Give a new part a new `id` that no other part in the version uses.

To see the result, run `python scripts/build_log.py` and `python -m http.server`, and open http://localhost:8000.
