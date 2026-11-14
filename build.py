"""Build only the reviewed public-facing files; never copy the vault wholesale."""
from pathlib import Path
from html import escape as esc
from urllib.parse import quote
import json
import re
import shutil
import hashlib
import zipfile

BASE = Path(__file__).resolve().parent
VAULT = BASE.parent
if not (VAULT / "03_Product/Data-Pilot.json").is_file():
    VAULT = BASE / "public-evidence"
    integrity = json.loads((VAULT / "integrity.json").read_text(encoding="utf-8"))
    for relative, expected in integrity["sha256"].items():
        artifact = (VAULT / relative).resolve()
        if not artifact.is_relative_to(VAULT.resolve()) or hashlib.sha256(artifact.read_bytes()).hexdigest() != expected:
            raise ValueError("Bundled public evidence integrity failure: " + relative)
DIST = BASE / "dist"
CATALOGUE = json.loads((BASE / "content/catalogue.json").read_text(encoding="utf-8-sig"))
LEDGER = json.loads((VAULT / "03_Product/Data-Pilot.json").read_text(encoding="utf-8-sig"))
SKILLS = []
for entry in CATALOGUE:
    entry = dict(entry)
    if entry.get("sourceKind") not in {"skill", "harness", "plugin", "workflow", "feature"}:
        raise ValueError("Unknown sourceKind")
    for field in ("id", "name", "publisher", "category", "summary", "reviewedOn", "licenseNote"):
        if not isinstance(entry.get(field), str) or not entry[field]:
            raise ValueError(f"Missing catalogue field: {field}")
    for field in ("requirements", "limitations", "taskKeywords"):
        if not isinstance(entry.get(field), list) or not all(isinstance(v, str) for v in entry[field]):
            raise ValueError(f"Invalid list: {field}")
    if "evidenceStatus" in entry:
        raise ValueError("Tested status is derived, never authored in catalogue.json")
    entry["evidenceStatus"] = "research-candidate"
    if entry.get("evidenceRecordId"):
        record = next((r for r in LEDGER["items"] if r["id"] == entry["evidenceRecordId"]), None)
        if not record or record.get("evidence_level") != "task_tested":
            raise ValueError("Tested editorial record lacks ledger support")
        revision = record["source"].get("revision")
        runs = record.get("evaluations", [])
        if not re.fullmatch(r"[0-9a-f]{40}", revision or "") or not {"baseline", "candidate"} <= {r.get("condition") for r in runs}:
            raise ValueError("Tested record lacks pinned paired runs")
        pairs = {}
        for run in runs:
            for key in ("output_path", "checks_path"):
                path = (VAULT / run[key]).resolve()
                if not path.is_relative_to(VAULT.resolve()) or not path.is_file():
                    raise ValueError("Missing or invalid task artifact")
            if run.get("condition") == "candidate" and run.get("source_revision") != revision:
                raise ValueError("Stale candidate evidence")
            if run.get("critical_checks_passed") is not True or run.get("accepted") is not True:
                raise ValueError("Editorial passing-result claim lacks accepted task evidence")
            checks = json.loads((VAULT / run["checks_path"]).read_text(encoding="utf-8-sig"))
            if not checks.get("checks") or any(v.get("passed") is not True for v in checks["checks"].values()):
                raise ValueError("Recorded browser checks do not support passing-result claim")
            key = (run.get("case_id"), run.get("repeat"), run.get("environment_id"), run.get("input_sha256"))
            pairs.setdefault(key, set()).add(run.get("condition"))
        if not any(p == {"baseline", "candidate"} for p in pairs.values()):
            raise ValueError("No matched task pair supports the editorial claim")
        entry.update(evidenceStatus="task-tested", sourceRevision=revision,
                     sourceUrl=record["source"]["canonical_url"],
                     reviewedOn=record["last_tested_on"],
                     evidenceSummary=record["recommendation"]["rationale"])
    elif entry.get("guidePath"):
        raise ValueError("Tested guide link requires an evidenceRecordId")
    if not entry.get("sourceUrl", "").startswith("https://"):
        raise ValueError("Catalogue sources must use HTTPS")
    if entry.get("guidePath") and not re.fullmatch(r"guides/[a-z0-9-]+\.html", entry["guidePath"]):
        raise ValueError("Invalid guide path")
    SKILLS.append(entry)
if len({s["id"] for s in SKILLS}) != len(SKILLS):
    raise ValueError("Duplicate catalogue ID")
# Compatibility projection: generated, never maintain this file manually.
(BASE / "content/skills.json").write_text(json.dumps(SKILLS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
EDITORIAL = json.loads((BASE / "content/editorial.json").read_text(encoding="utf-8-sig"))
PILOT = VAULT / "06_Build/Pilots/motion-001"
DIST.mkdir(exist_ok=True)


def card(skill):
    tested = skill['evidenceStatus'] == 'task-tested'
    search = ' '.join([skill['name'], skill['category'], skill['summary'], *skill['taskKeywords']])
    action = f'<a class="button secondary" href="{esc(skill["guidePath"])}">Open guide →</a>' if skill.get('guidePath') else f'<button class="button secondary" data-skill-id="{esc(skill["id"])}">View capability →</button>'
    return f'''<article class="skill-card" data-card data-category="{esc(skill['category'])}" data-evidence="{skill['evidenceStatus']}" data-search="{esc(search)}"><span class="badge {'tested' if tested else 'candidate'}">{'One task tested' if tested else 'Source reviewed'}</span><h3>{esc(skill['name'])}</h3><p>{esc(skill['summary'])}</p><div class="skill-meta"><span>{esc(skill['publisher'])}</span><span>{esc(skill['sourceKind'])}</span></div>{action}<p class="small"><button class="inline-button" data-skill-id="{esc(skill['id'])}">Requirements &amp; evidence</button></p></article>'''


def wrap(page):
    path = Path(page['path']); root = '../' * (len(path.parts)-1)
    nav = ''.join(f'<a href="{root}{url}"'+(' aria-current="page"' if key==page.get('activeNav') else '')+f'>{label}</a>' for key,url,label in [('skills','skills.html','Explore'),('guides','guides.html','Guides'),('setup','setup.html','Setup help'),('method','how-we-test.html','How we choose')])
    wordmark=f'<img src="{root}assets/logo.svg" width="34" height="44" alt=""><span>SkillLantern</span>'
    title=esc(page['title']); description=esc(page['description'])
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · SkillLantern</title><meta name="description" content="{description}"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#151b1a"><meta property="og:title" content="{title} · SkillLantern"><meta property="og:description" content="{description}"><meta property="og:type" content="website"><meta property="og:url" content="https://skilllantern.happymoth22.chatgpt.site/{page["path"]}"><link rel="canonical" href="https://skilllantern.happymoth22.chatgpt.site/{page["path"]}"><link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{root}assets/site.css"><link rel="stylesheet" href="{root}assets/app.css"><script defer src="{root}assets/skills-data.js"></script><script defer src="{root}assets/product-data.js"></script><script defer src="{root}assets/app.js"></script>{'<script defer src="'+root+'assets/lantern.js"></script>' if page.get('lantern') else ''}</head><body data-root="{root}"><a class="skip-link" href="#main">Skip to content</a><div class="shell"><header class="site-header"><a class="brand" href="{root}index.html" aria-label="SkillLantern home">{wordmark}</a><button class="menu-button" id="menu-button" type="button" aria-controls="site-nav" aria-expanded="false" hidden>Menu</button><nav class="site-nav" id="site-nav" aria-label="Main navigation">{nav}</nav></header><main id="main">{page['body'].replace('{{root}}',root)}</main><footer class="site-footer"><div><a class="brand" href="{root}index.html">{wordmark}</a><p>A clearer path from AI possibility to useful work.</p></div><nav aria-label="Footer"><a href="{root}about.html">About &amp; privacy</a><a href="{root}setup-help.html">Implementation help</a><a href="{root}comparisons.html">Test comparison</a><a href="{root}how-we-test.html">Evidence policy</a></nav></footer></div><dialog class="dialog" id="skill-dialog" aria-labelledby="skill-dialog-title"><button class="dialog-close" type="button" aria-label="Close source note">×</button><div id="skill-dialog-content"></div></dialog></body></html>'''
    target=DIST/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(html,encoding='utf-8')

study_path=VAULT/'03_Product/Lantern-3D-Study.html'
fallback=re.search(r'<svg id="fallback".*?</svg>',study_path.read_text(encoding='utf-8'),re.S).group() if study_path.exists() else (VAULT/'lantern-fallback.svg').read_text(encoding='utf-8')
shipfile=BASE/'content/ship-guides.json'
SHIP=json.loads(shipfile.read_text(encoding='utf-8-sig')) if shipfile.exists() else []
if isinstance(SHIP,dict): SHIP=SHIP.get('pages',SHIP.get('guides',[]))
INSTALL=json.loads((BASE/'content/install-guide.json').read_text(encoding='utf-8-sig'))
INSTALL.update(outcome='motion',coverKey='motion',cardSummary='Copy the pinned skill into your project, check discovery and try a small task.')
GUIDES=[dict(path='guides/motion-design.html',title='Make interface feedback feel clear',cardSummary='Build loading, success and retry states. Includes a practice pack and a tested comparison.',coverKey='motion',outcome='motion'),*SHIP,INSTALL]
for g in GUIDES:
    g['hostLabel'] = 'Codex / Claude Code project installation; activation not exercised' if g['path']=='guides/install-motion-design.html' else 'Claude Desktop walkthrough; brief can be adapted to other agents' if g.get('outcome') == 'website' else ('Browser notebook workflow; separate from your coding agent' if g.get('outcome') == 'marketing' else 'Explicit local source context')
def guidecard(g):
    cover=g.get('coverKey','website'); cover=cover if cover in {'website','marketing','spreadsheet','motion'} else 'website'
    return f'''<a class="guide-card" href="{esc(g['path'])}"><img class="guide-cover" src="assets/covers/{cover}.svg" width="720" height="450" alt="" loading="lazy"><div class="guide-body"><span class="eyebrow">{'One paired task test' if g['path']=='guides/motion-design.html' else 'Source-led guide'}</span><h3>{esc(g['title'])}</h3><p>{esc(g.get('cardSummary',g.get('description','A practical workflow, with requirements and checks.')))}</p><span class="text-link">Follow the guide →</span></div></a>'''
home=f'''<div class="hero-shell"><section class="hero cinematic"><div class="hero-copy"><p class="eyebrow">Make your agent useful</p><h1>Your agent.<br>Ready for the job.</h1><p class="lede">Find the right capabilities and a clear setup plan for what you want to make.</p><div class="hero-actions"><a class="button" href="setup.html">Find my setup →</a><a class="button text" href="guides.html">Explore the guides</a></div></div><div class="hero-art"><div class="lantern-stage" id="stage"><div class="floor" aria-hidden="true"></div><canvas id="scene" aria-hidden="true" hidden></canvas>{fallback}</div><div class="lantern-controls"><button id="motion" type="button" disabled>Animation unavailable</button><p id="status" role="status">A still lantern while 3D support loads.</p></div></div></section></div><section class="section"><div class="section-head"><div><p class="eyebrow">Start with the work</p><h2>What will you make?</h2></div><p>One useful outcome. A manageable next step.</p></div><div class="task-links"><a class="filter-chip" href="setup.html?outcome=website">A distinctive website ↗</a><a class="filter-chip" href="setup.html?outcome=marketing">Better marketing content ↗</a><a class="filter-chip" href="setup.html?outcome=data">A reliable spreadsheet ↗</a><a class="filter-chip" href="setup.html?outcome=motion">An interface that feels right ↗</a></div></section><section class="section"><div class="section-head"><h2>Less guessing.<br>More making.</h2><a href="guides.html">All guides →</a></div><div class="grid three">{''.join(guidecard(g) for g in GUIDES[:3])}</div></section><section class="section trust-note"><h2>Know what you’re working with.</h2><p>Original sources, clear requirements and visible test limits. No mystery rankings.</p><a href="how-we-test.html">How we choose →</a></section>'''
categories=list(dict.fromkeys(s['category'] for s in SKILLS))
chips='<button class="filter-chip" data-filter-category="all" aria-pressed="true">All tasks</button>'+''.join(f'<button class="filter-chip" data-filter-category="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in categories)
catalogue=f'''<header class="page-intro"><p class="eyebrow">Explore</p><h1>A capability for<br>the work ahead.</h1><p class="lede">Browse {len(SKILLS)} sourced starting points. Check the requirements before adding anything to your agent.</p></header><div class="filters"><div class="search-field"><label for="skill-search">Find a capability</label><input id="skill-search" type="search" placeholder="Try animation, spreadsheets or React"></div><div class="search-field"><label for="evidence-filter">Evidence</label><select id="evidence-filter"><option value="all">All reviews</option><option value="task-tested">Task tested</option><option value="research-candidate">Source reviewed</option></select></div><button class="button secondary" id="clear-filters">Clear filters</button></div><div class="task-links">{chips}</div><p id="result-count" role="status" aria-live="polite">{len(SKILLS)} capabilities</p><div class="grid three" id="skill-grid">{''.join(card(s) for s in SKILLS)}<div id="empty-state" class="empty-state" hidden><h2>No matches yet.</h2><p>Try a broader task.</p><button class="button secondary" data-clear-filters>Show all</button></div></div><p class="trust-note">Source reviewed means documentation inspected; setup and task performance remain untested. <a href="how-we-test.html">Read the evidence policy.</a></p>'''
guides='<header class="page-intro"><p class="eyebrow">Practical guides</p><h1>A clear path<br>to your next result.</h1><p class="lede">Know what you need, follow a bounded setup, and check the result.</p></header><div class="grid three">'+''.join(guidecard(g) for g in GUIDES)+'</div><section class="section trust-note"><p>New source-led guides are not installation tests. Each guide explains what was reviewed and what you still need to verify.</p><a href="setup.html">Help me choose a setup →</a></section>'
setup='''<header class="page-intro"><p class="eyebrow">Your setup brief</p><h1>Give your agent<br>a clear starting point.</h1><p class="lede">Four short steps. A practical plan based on reviewed workflows.</p></header><form id="setup-form" class="setup-planner planner"><p id="planner-progress" class="eyebrow" role="status">Step 1 of 4</p><fieldset class="planner-step" data-step="0"><legend>What do you want to make?</legend><div class="choice-grid"><label class="choice"><input type="radio" name="outcome" value="website" checked>A distinctive website</label><label class="choice"><input type="radio" name="outcome" value="marketing">Marketing content</label><label class="choice"><input type="radio" name="outcome" value="data">A reliable spreadsheet</label><label class="choice"><input type="radio" name="outcome" value="motion">Better interface motion</label></div></fieldset><fieldset class="planner-step" data-step="1" hidden><legend>Which agent do you already use?</legend><div class="choice-grid"><label class="choice"><input type="radio" name="agent" value="Codex" checked>Codex</label><label class="choice"><input type="radio" name="agent" value="Claude Code">Claude Code</label><label class="choice"><input type="radio" name="agent" value="Other / undecided">Other / undecided</label></div><p class="small">Use your existing access. This plan does not install tools or assume a paid subscription.</p></fieldset><fieldset class="planner-step" data-step="2" hidden><legend>What should the result feel like?</legend><label for="setup-vision">Your vision or top priority</label><textarea id="setup-vision" name="vision" rows="4" maxlength="1500" placeholder="For example: a calm, premium website for a small ceramics studio"></textarea><label for="setup-priority">Focus first on</label><select id="setup-priority" name="priority"><option>A small, working first version</option><option>Visual quality and brand</option><option>Accuracy and verification</option><option>Learning the workflow</option></select></fieldset><fieldset class="planner-step" data-step="3" hidden><legend>What boundaries should the agent respect?</legend><label for="setup-constraints">Tools, time, budget or things to avoid</label><textarea id="setup-constraints" name="constraints" rows="4" maxlength="1500" placeholder="For example: existing tools only, no new subscriptions, one afternoon"></textarea><p class="small">Keep private credentials out of your brief. Your answers stay in this page; nothing is sent or saved automatically.</p></fieldset><div class="planner-actions"><button class="button secondary" id="planner-back" type="button" hidden>Back</button><button class="button" id="planner-next" type="button">Continue →</button><button class="button" id="planner-submit" type="submit" hidden>Build my setup brief →</button></div></form><section id="setup-result" class="plan-result setup-result section" hidden tabindex="-1" aria-labelledby="result-title"></section><noscript><p>This planner needs JavaScript. You can still <a href="guides.html">follow a guide</a> and use its requirements checklist.</p></noscript>'''
helpbody='''<header class="page-intro"><p class="eyebrow">Implementation help</p><h1>The value is in<br>making it work.</h1><p class="lede">Free guides and setup briefs are available now. Hands-on implementation support is a proposed next step.</p></header><div class="grid three"><article class="offer-card"><span class="eyebrow">Available now</span><h2>Choose a path</h2><p>Use sourced guides and a tailored setup brief to make a bounded first attempt.</p><a class="button" href="setup.html">Create my brief →</a></article><article class="offer-card"><span class="eyebrow">Proposed service</span><h2>Adapt and configure</h2><p>Help connecting the right capabilities to your existing agent, project and constraints.</p></article><article class="offer-card"><span class="eyebrow">Proposed service</span><h2>Verify the result</h2><p>Acceptance checks, a usable handoff and a clear account of remaining limitations.</p></article></div><section class="section prose"><h2>How this could earn money</h2><p>The proposed path is free practical guidance followed by scoped implementation help. Paid value would come from configuration, adaptation and verification, rather than repackaging public skill files.</p><p>The service pilot is not open. Scope, pricing and payment arrangements remain undecided; no booking or purchase is available.</p></section>'''
pages=[dict(path='index.html',title='Your agent. Ready for the job.',description='Find AI capabilities, follow practical guides and build a setup brief for your existing agent.',body=home,lantern=True),dict(path='skills.html',title='Explore AI capabilities',description='Find sourced AI skills and workflows for websites, writing, spreadsheets and motion.',body=catalogue,activeNav='skills'),dict(path='guides.html',title='Practical AI workflow guides',description='Clear requirements, setup steps and verification for useful AI workflows.',body=guides,activeNav='guides'),dict(path='setup.html',title='Find your agent setup',description='Build a practical setup brief for your AI agent in four short steps.',body=setup,activeNav='setup'),dict(path='setup-help.html',title='Implementation help',description='The proposed path from free AI guidance to scoped configuration and verification support.',body=helpbody),*[p for p in EDITORIAL if p.get('lang')!='ar' and not p['path'].startswith('ar/')],*SHIP,INSTALL]
for page in pages:
    if page['path']=='guides/motion-design.html':
        page['body']=page['body'].replace('<article class="prose">','<article class="prose"><aside class="callout warm"><h2>Want to add it to your agent?</h2><p>Copy the reviewed skill folder into a Codex or Claude Code project. File layout and documentation checked; native activation not exercised.</p><a class="button" href="{{root}}guides/install-motion-design.html">Install Motion Design ?</a></aside>',1)
    wrap(page)
(DIST/'assets/skills-data.js').write_text('window.SKILLLANTERN_SKILLS = '+json.dumps(SKILLS,ensure_ascii=False)+';\n',encoding='utf-8')
PRODUCT={'guides':[{k:g[k] for k in ('path','title','outcome','hostLabel') if k in g} for g in GUIDES], 'matches':{'website':['webapp-testing','react-best-practices'],'marketing':['doc-coauthoring'],'data':['xlsx'],'motion':['motion-design','emil-animate']}}
(BASE/'content/product.json').write_text(json.dumps(PRODUCT,indent=2)+'\n',encoding='utf-8')
(DIST/'assets/product-data.js').write_text('window.SKILLLANTERN_PRODUCT = '+json.dumps(PRODUCT)+';\n',encoding='utf-8')
copies={VAULT/'03_Product/Guides/motion-design-demo.zip':'downloads/motion-design-demo.zip',PILOT/'input/index.html':'demos/motion/start.html',PILOT/'runs/baseline-01/index.html':'demos/motion/baseline.html',PILOT/'runs/candidate-01/index.html':'demos/motion/candidate.html',PILOT/'runs/baseline-01/success.png':'assets/motion/baseline.png',PILOT/'runs/candidate-01/success.png':'assets/motion/candidate.png',PILOT/'comparison-results.json':'evidence/motion-results.json'}
for source,target in copies.items():
    dest=DIST/target; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(source,dest)
# Historical Arabic source remains in editorial.json, outside the deployment output.
ar_dir=(DIST/'ar').resolve()
if ar_dir.is_relative_to(DIST.resolve()) and ar_dir.exists():
    archive=BASE/'archive/generated-ar'; archive.parent.mkdir(exist_ok=True)
    if not archive.exists(): shutil.copytree(ar_dir,archive)
    shutil.rmtree(ar_dir)
# Repack only reviewed Markdown plus its MIT licence; retain upstream bytes.
with zipfile.ZipFile(VAULT/'03_Product/Guides/motion-design-demo.zip') as source_zip:
    payload={}
    for name in source_zip.namelist():
        if name.startswith('source/skills/motion-design/') and not name.endswith('/'):
            relative=name.removeprefix('source/skills/motion-design/')
            if '..' in Path(relative).parts or not relative.endswith('.md'):
                raise ValueError('Unexpected file in installable skill snapshot: '+name)
            payload['motion-design/'+relative]=source_zip.read(name)
    payload['motion-design/LICENSE']=source_zip.read('source/LICENSE')
    if 'motion-design/SKILL.md' not in payload:
        raise ValueError('Missing installable skill entrypoint')
    with zipfile.ZipFile(DIST/'downloads/motion-design-skill.zip','w',zipfile.ZIP_DEFLATED) as target_zip:
        for name,data in sorted(payload.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,11,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            target_zip.writestr(info,data)
    print(f'Packaged {len(payload)} skill files (Markdown and MIT licence only)')
(DIST/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
(BASE/'page-manifest.json').write_text(json.dumps([p['path'] for p in pages],indent=2)+'\n',encoding='utf-8')
print(f'Built {len(pages)} English pages and {len(SKILLS)} capabilities')
