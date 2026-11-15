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

## How to add a version

You can edit the wiring on the page itself, on your own computer.
In a clone of the repository:

1. Run `python scripts/build_log.py`, which combines the version files into `data/log.json`.
2. Open `index.html` from disk in a browser, click *Import JSON* in the footer, and choose `data/log.json`.
3. Click *Edit*, make the change, then click *Review & save*, describe the change, and save.
4. Click *Export history (JSON)* to download the history, as `wiring-log-v<number>.json`.
5. Run `python scripts/add_version.py <downloaded file>`. It writes each new version as a new file in `data/versions/`, and writes nothing if the export changes an existing version.
6. Run `python scripts/check_log.py`, then commit the new file and push to `main`.

The site shows the new version about a minute after the push.
`data/log.json` is not committed; the publish workflow builds it.

You can also write the new version file by hand, as `AGENTS.md` describes.
To preview the site with your change, run `python scripts/build_log.py` and then `python -m http.server`, and open http://localhost:8000.

## Datasheets

`files/` holds the vendor datasheets and test certificates that the parts link to.
To attach a new one, add the PDF to `files/` and, in the new version, give the part an attachment `{"id": "<unique id>", "kind": "file", "name": "<name>", "asset": "files/<file name>"}`.
A link to a web page is `{"id": "<unique id>", "kind": "link", "name": "<name>", "url": "https://..."}`.

## Publishing

On every push and pull request, `.github/workflows/pages.yml` runs `scripts/check_log.py`.
On a push to `main` that passes the check, it then builds `data/log.json` and publishes the repository with GitHub Pages.
Version 1 is the wiring on the vendor drawings (DC wiring tree J001245, update 2026-10-16; RF wiring tree J001245, update 2026-10-21).
The drawings themselves are not in this repository.
