# Kiutra wiring log

This repository is the wiring record of the Schuster Lab kiutra L-Type Rapid cryostat, with every past version kept.
The site at https://schusterlab.github.io/kiutra-wiring-log/ draws the wiring stage by stage and is read-only.
To change the wiring, you add a new version file to `data/versions/` and push it to `main`.

## Never change an older version

Each file in `data/versions/` is the wiring as it was on a date: `v0001.json`, `v0002.json`, and so on.
The site shows the newest as the current wiring and lists all of them in its History tab.
Add each change as a new file with the next number.
Don't edit, rename or delete an existing version file, not even to fix a typo; fix it in a new version.
To undo a change, add a new version whose `state` is a copy of the older version's `state`.

Every push and pull request runs `scripts/check_log.py`, which compares each version file with the commit that added it.
If a version file was changed or deleted, the check fails and the site is not republished.
To recover, revert the commit that changed it (`git revert <commit>`) and push.
Force-pushes to `main` and deleting `main` are blocked, so the history the check compares against can't be rewritten.

## How to add a version

In a clone of the repository:

1. Run `python scripts/new_version.py "<one line: what changed>"`. It copies the newest version file to the next number, such as `data/versions/v0002.json`, and fills in the number, the time and your GitHub username.
2. Make the change in the new file's `state`, which is the complete wiring. `AGENTS.md` describes the format.
3. Run `python scripts/check_log.py`. Besides protecting older versions, it reports any part on a stage that doesn't exist, of an unknown type, or connected to a part that doesn't exist.
4. Preview it: run `python scripts/build_log.py` and then `python -m http.server`, and open http://localhost:8000.
5. Commit the new file and push to `main`.

The site shows the new version about a minute after the push.
`scripts/build_log.py` combines the version files into `data/log.json`, the file the page reads.
That file is not committed; the publish workflow builds it.

## Datasheets

`files/` holds the vendor datasheets and test certificates that the parts link to.
To attach a new one, add the PDF to `files/` and, in the new version, give the part an attachment `{"id": "<unique id>", "kind": "file", "name": "<name>", "asset": "files/<file name>"}`.
A link to a web page is `{"id": "<unique id>", "kind": "link", "name": "<name>", "url": "https://..."}`.

## Publishing

On every push and pull request, `.github/workflows/pages.yml` runs `scripts/check_log.py`.
On a push to `main` that passes the check, it then builds `data/log.json` and publishes the repository with GitHub Pages.
Version 1 is the wiring on the vendor drawings (DC wiring tree J001245, update 2026-10-16; RF wiring tree J001245, update 2026-10-21).
The drawings themselves are not in this repository.
