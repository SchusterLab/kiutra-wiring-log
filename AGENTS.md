# Notes for coding agents

`data/log.json` is the wiring history of a cryostat, and the site in `index.html` only reads it.
Read `README.md` first.

## Never overwrite an older version

The list `versions` in `data/log.json` is append-only.
Make every change by adding one new version at the end.
Never edit, reorder or delete an existing version, even to fix a typo or reformat the file.
To undo a change, add a new version that copies an older version's `state`.

Before you commit, run `python scripts/check_log.py` and check that `git diff data/log.json` shows only the new version added at the end.
The script compares every version with the commit that first added it, and CI runs the same check before publishing.
If the check fails because you changed an older version, put that version back as it was; don't change the check.

Write the file with two-space JSON indentation, as the page's *Export history (JSON)* does, so that a new version shows in a diff as added lines.
Don't sort keys or reformat existing entries.

## A version

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

- `n` is the previous version's `n` plus 1.
- `ts` is the time of the change, in UTC.
- `state` is the complete wiring, not a diff. Start from a copy of the latest version's `state` and change only what changed.

Inside `state`, each line in `lines` has `id`, `group` (`"dc"` or `"rf"`), `name`, `purpose` and `items`.
Each item is one part, listed from the top of the cryostat down: `id`, `type`, `stage` (an `id` from `stages`), `at` (`"plate"` for a part on the plate, `"region"` for one below it), `label`, `detail` and `note`.
The types are `connector`, `cable`, `attenuator`, `filter`, `amplifier`, `isolator`, `coupler`, `diplexer`, `splitter`, `anchor` and `other`.
An item that feeds a port of a part on another line has `"link": {"line": "<line id>", "item": "<item id>", "port": "<port name>"}`.
Attachments are described in `README.md`, under Datasheets.

Keep the `id` of every part that stays, because the History tab matches parts between versions by `id`.
Give a new part a new `id` that no other part in the version uses.
