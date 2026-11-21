# SkillLantern website

## Cloudflare Workers Git build · 22 November 2026

The Git-connected Worker is named `skilllantern`. With this website directory as
the repository root, set the build command to `python3 build_cloudflare.py` and
the deploy command to `npx wrangler deploy`. The existing
`npx wrangler deploy --assets ./pages-dist` command also uses the checked-in
`wrangler.toml`, which supplies the Worker name, compatibility date and assets
directory. No Worker script or runtime bindings are needed for this static site.

The build still writes `pages-dist/`; its clean URLs match Workers' default
`auto-trailing-slash` HTML handling. The configuration does not define routes or
custom domains; retain the existing production domain in Cloudflare's Worker
settings. Set `SKILLLANTERN_PUBLIC_ORIGIN` to that exact HTTPS origin in the
production build environment for the intended canonical URLs and indexing.
Workers CI builds on `main` now stop before building when that variable is
missing; set it in Cloudflare Workers build variables and rebuild.
Workers builds do not supply the Pages-specific `CF_PAGES_URL` preview variable;
leave the public-origin variable unset for local or non-main builds intended
to remain noindex.
Git pushes can trigger deployment through the existing connection.

Configuration follows Cloudflare's [static assets configuration](https://developers.cloudflare.com/workers/static-assets/binding/)
and [HTML handling](https://developers.cloudflare.com/workers/static-assets/routing/advanced/html-handling/)
documentation, checked on 22 November 2026. The following Pages instructions
describe the alternative Pages hosting setup.

## Cloudflare Pages Git build · 21 November 2026

For a GitHub repository whose root is this website directory, use Pages **Git
integration**, framework **None**, root directory blank, build command
`python3 build_cloudflare.py`, output directory `pages-dist`, build image **v3**.
The tracked `.python-version` selects Python 3.13.3 (the build requires 3.12+).
[Cloudflare build image documentation](https://developers.cloudflare.com/pages/configuration/build-image/)
was checked on 21 November 2026. No third-party Python packages are needed.

The command builds from an isolated temporary copy using bundled evidence and
leaves ordinary `dist/` and `page-manifest.json` unchanged. `pages-dist/` is ignored.
It aligns canonical/OG URLs and sitemap entries with Pages clean URLs while
retaining `.html` source files for Pages routing.

Leave `SKILLLANTERN_PUBLIC_ORIGIN` unset for preview-safe noindex/robots output.
Cloudflare previews use `CF_PAGES_URL` for their canonical origin while retaining
noindex and disallowed robots; local builds without it retain the private origin.
For an authorised public production build, set it to the actual HTTPS production
origin (the assigned `https://YOUR-PROJECT.pages.dev` is sufficient, or your configured
custom domain) in the Production environment only; keep Preview unset. This environment variable
controls indexing metadata, not access restrictions or publication permission.
Review build/deployment controls before connecting Git: Git pushes can trigger
deployments. These local changes do not connect GitHub or deploy anything.

The `public-evidence/** -text` Git attribute preserves pinned evidence bytes on
Windows and Linux. When preparing the next authorised source commit, stage the
attribute first (`git add .gitattributes`), then force evidence re-staging
with `git add --renormalize -- public-evidence`;
this records the current reviewed bytes rather than older normalized index blobs.
Do not regenerate integrity hashes to accommodate newline transformations.

English-first static product. Root coordinates hosting and publishing; source edits do not
change audience. Navigation is Explore, Guides, Popular and My setup. Visitors search by task,
filter by app/task/kind, read stable capability profiles, save a shortlist locally and copy or
download a setup brief. No accounts, billing or recurring refresh is active.

## Build and data ? 21 November 2026

Run `python build.py`. It validates the existing evidence ledger and emits HTML, static JSON
feeds, the verified Motion Design ZIP and its browser-installer payload. Runtime output is
standalone. `content/catalogue.json` retains the evidence-backed base records;
`content/launch-library.json` supplies the reviewed release profiles and practical guides.
`release_content.py` renders source-led guide content; `discovery_release.py`, `discovery.js`
and `discovery.css` implement discovery, stable profiles and the browser-local shortlist.

Published feeds are `dist/api/top-skills.json` and `dist/api/capabilities.json`. Capability
schemaVersion 1 remains, with additive app/task/setup fields and preserved base record fields.
These are dated static snapshots. `developers.html` links directly to them.

The default build preserves the private preview origin and `noindex,nofollow`; robots disallows
crawling. Only for an explicitly authorised public deployment, set
`SKILLLANTERN_PUBLIC_ORIGIN` to its HTTPS origin (no path) before building. That build uses
that canonical origin, indexable metadata, robots and a sitemap excluding contextual legacy
routes and the browser-local My setup page. Hosting audience is a separate deployment setting.
An isolated website-only temporary build verified this option on 21 November 2026.

`content/popular-registry.json` is the fixed shortlist; `popular-snapshot.json` contains dated
GitHub metadata. Run `refresh_popular.py` manually, review the snapshot and rebuild. The browser
refresh contacts public GitHub only after a click. Counts stay in memory; no client secrets
are used. The source-reviewed catalogue and Popular repository count are separate collections.

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
