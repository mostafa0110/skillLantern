# SkillLantern website

English-first static product, hosted as an owner-private Sites preview. Root coordinates
publishing; source edits do not change its audience. Navigation includes Discover, Guides, Get set up, Updates and More, with Popular prominently
linked from Discover. No billing, accounts or recurring refresh is active.

## Build and data

Run `python build.py`. This validates evidence and emits the page manifest, static JSON feeds,
verified skill ZIP and browser-installer payload. Public source snapshots make a website-only
checkout rebuildable. See the evidence notes below for scope and refresh requirements.

`content/popular-registry.json` is the fixed discovery shortlist; `popular-snapshot.json`
contains dated GitHub metadata. Run the existing `refresh_popular.py` manually when an update
is needed, review the changed snapshot, then rebuild. The browser refresh is optional and
contacts public GitHub only after a click, with at most three requests in flight. Counts stay
in memory. A rate limit restores the published snapshot; no client secrets are used.

Published feeds: `dist/api/top-skills.json` and `dist/api/capabilities.json`. They are static
snapshots with freshness and scope labels. Owner-private hosting access applies. The proposed
paid Developer API is documented on developers.html; keys, metering, history and recommendation
endpoints are planned and not implemented.

## Local file installer

`install.html` requires a top-level secure Chrome/Edge context with the File System Access API.
The user chooses a project and explicitly starts installation. Only the pinned Markdown package
and MIT licence are written under `.agents/skills/motion-design`. Payload and written hashes are
verified. Unmanaged existing folders are refused; same-version owned installs are idempotent.
A bounded in-memory rollback tracks created files on failure. Undo removes only recorded,
unmodified known-package files and leaves unrelated files and directories. Handles and user
inputs are not stored, uploaded or sent to an agent. The browser API does not provide exclusive file creation; nonempty files that appear before
a write are refused, but users should avoid editing the target folder during installation.
Native activation and the real external
folder picker UI remain separate from the isolated OPFS QA evidence.

## Product release · 14 November 2026

The English product build includes the four-step local setup planner, copy/download brief,
source-reviewed catalogue, practical guides and proposed implementation-help model. Planner
inputs are processed in memory only; no browser storage, AI service or form submission is used.

`python build.py` prefers the adjacent venture vault's reviewed ledger and Motion Design
pilot artifacts. Without that vault, it uses `public-evidence/`: one sanitized ledger entry,
the pinned source manifest, paired outputs/browser checks, public demo assets and practice pack.
SHA-256 integrity validation runs before the same task-evidence gates. The generated `dist/`
is standalone at runtime. A no-vault temporary checkout rebuild passed on 14 November 2026,
producing byte-identical HTML and retaining the task-tested status for Motion Design.

To refresh the public snapshot after a reviewed evidence change: export only SL-0004's
`id`, `source`, `evaluations`, `recommendation`, `evidence_level` and `last_tested_on` into
`public-evidence/03_Product/Data-Pilot.json`; retain only the public fields already present
in `source` and `recommendation`. Copy the explicit files listed in
`public-evidence/integrity.json` from their matching vault-relative locations. The fallback
SVG is the original lantern illustration, extracted separately. Regenerate SHA-256 values
for every bundled file except `integrity.json` itself. Do not copy full ledgers, raw research,
scanner logs or vault notes. Review the diff, run the normal build and repeat a build from
a temporary website-only copy; compare HTML and derived evidence status. The practice pack
already contains the upstream MIT notice. The snapshot does not claim a security scan ran.

Arabic editorial source remains archived in `content/editorial.json`; previously generated
Arabic HTML is preserved under `archive/generated-ar/`. Neither is in the English page manifest.
The deployment output excludes Arabic pages. Hosting stays private and pages retain noindex.
