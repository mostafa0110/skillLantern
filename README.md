---
type: implementation
status: local-website
created: 2026-11-09
updated: 2026-11-14
tags: [website, skilllantern]
---

# SkillLantern website

Open [dist/index.html](dist/index.html) in a browser. The site works directly from disk:
navigation, search, filters, source notes, prompt copying, demo downloads and the 3D lantern.
It uses local assets with no package installation, external fonts, accounts or analytics.

The eight authored pages include home, catalogue, guide index, first tested guide, comparisons,
methodology, about/privacy and an Arabic comparison. Six of seven capability entries are research
candidates; Motion Design has one scoped paired task test. No skill has a fabricated tier.

## Update the catalogue

From the vault root, edit **`website/content/catalogue.json`**: this is the only manually
maintained catalogue. Add a unique slug, source kind (`skill`, `harness`, `plugin`, `workflow`
or `feature`), plain-text description, task keywords, requirements, dated source review and
limits. Use HTTPS source URLs. Public availability does not establish free model access,
production readiness or verified task results. DeepSeek Harness remains an untested developer
preview, with advertised document/data/slide/research outcomes labelled accordingly.

Do not author `evidenceStatus`. Tested entries reference the private evidence ledger by
`evidenceRecordId`; Motion Design uses `SL-0004` in `03_Product/Data-Pilot.json`. The build
derives its tested status, pinned source and result summary, and refuses unsupported or stale
passing-result claims. The ledger itself is never copied to the website. Historical evidence
is not changed by a catalogue edit. `content/skills.json` and `dist/assets/skills-data.js` are
generated compatibility projections; do not edit them manually.

For a possible weekly review, copy `content/proposal-template.json` to a descriptively named
JSON file under `content/drafts/` (create that folder when needed). Record source URLs,
observed date, task outcome, attributed claims and unknowns. Keep `state` as `draft`.
Drafts are **not read by the build**, rendered or automatically promoted. A reviewer selects
and checks a proposal before manually adding it to the catalogue. Do not paste external HTML
into editorial pages: catalogue strings are escaped; `editorial.json` is trusted, locally
authored page HTML, not an ingestion endpoint. No recurring schedule is installed.

Run `python website/build.py` to validate/project the catalogue and rebuild the preview.
The script checks required fields, unique IDs, source kinds, HTTPS links and supporting task
artifacts; it is not a security scanner, output benchmark or external-link availability test.
Review changed source notes, guide links and counts before using the local preview.

Rebuild the page HTML and selected demo assets with `python website/build.py` from the vault
root. Content lives in `content/`; shared styles and scripts live in `dist/assets/`. The build
copies only an explicit list of review artifacts. It never publishes the private vault.

For an optional HTTP preview, run `node website/serve.mjs` and open the printed loopback URL.
Stop it with Ctrl+C. The server serves only `dist/` and binds to 127.0.0.1. Publishing/domain
registration remains unperformed. Local preview pages deliberately use noindex metadata and
a blocking robots.txt; set the real domain and review release configuration before deployment.

[[Website-Review-2026-11-09]] · [[Home]]

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
