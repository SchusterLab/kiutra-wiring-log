# Kiutra wiring log

This repository is the wiring record of the Schuster Lab kiutra L-Type Rapid cryostat, with every past version kept.
The site at https://schusterlab.github.io/kiutra-wiring-log/ draws the wiring stage by stage and is read-only.
To change the wiring, you add a new version to `data/log.json` and push it to `main`.

## Never change an older version

Each entry in `versions` in `data/log.json` is the wiring as it was on a date, and the site's History tab shows them all.
Add each change as a new version at the end of the list.
Don't edit or delete an existing version, not even to fix a typo; fix it in a new version.
To undo a change, add a new version whose `state` is a copy of the older version's `state`.

Every push and pull request runs `scripts/check_log.py`, which compares each version with the commit that first added it.
If a version was changed or removed, the check fails and the site is not republished.
To recover, revert the commit that changed it (`git revert <commit>`) and push.

## How to add a version

You can edit the wiring on the page itself, on your own computer:

1. Clone the repository and open `index.html` from disk in a browser.
2. Click *Import JSON* in the footer and choose `data/log.json`.
3. Click *Edit*, make the change, then click *Review & save*, describe the change, and save.
4. Click *Export history (JSON)* and save the file over `data/log.json`.
5. Check that only a new version was added: `git diff data/log.json` should show only the new version added at the end, and `python scripts/check_log.py` should pass.
6. Commit and push to `main`.

The site shows the new version about a minute after the push.
A page opened from disk keeps its history in that browser, so step 2 imports the current one first.

You can also edit `data/log.json` by hand, as `AGENTS.md` describes.

## Datasheets

`files/` holds the vendor datasheets and test certificates that the parts link to.
To attach a new one, add the PDF to `files/` and, in the new version, give the part an attachment `{"id": "<unique id>", "kind": "file", "name": "<name>", "asset": "files/<file name>"}`.
A link to a web page is `{"id": "<unique id>", "kind": "link", "name": "<name>", "url": "https://..."}`.

## Publishing

`.github/workflows/pages.yml` runs the check and then publishes the repository with GitHub Pages.
Version 1 is the wiring on the vendor drawings (DC wiring tree J001245, update 2026-10-16; RF wiring tree J001245, update 2026-10-21).
The drawings themselves are not in this repository.
