"""Build only the reviewed public-facing files; never copy the vault wholesale."""
from pathlib import Path
from html import escape as esc
from urllib.parse import quote
import json
import re
import shutil
import hashlib
import zipfile
import os
from urllib.parse import urlsplit
PUBLIC_ORIGIN=os.environ.get("SKILLLANTERN_PUBLIC_ORIGIN", "").rstrip("/")
if PUBLIC_ORIGIN:
    parsed_origin=urlsplit(PUBLIC_ORIGIN)
    if parsed_origin.scheme!="https" or not parsed_origin.netloc or parsed_origin.path or parsed_origin.query or parsed_origin.fragment or parsed_origin.username or parsed_origin.password:
        raise ValueError("SKILLLANTERN_PUBLIC_ORIGIN must be an HTTPS origin without a path or credentials")
SITE_ORIGIN=PUBLIC_ORIGIN or "https://skilllantern.happymoth22.chatgpt.site"

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
    if entry.get("sourceKind") not in {"skill", "harness", "plugin", "workflow", "feature", "toolkit", "collection"}:
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
    return f'''<article class="skill-card" data-card data-category="{esc(skill['category'])}" data-type="{'skill' if skill['sourceKind'] in {'toolkit','collection'} else skill['sourceKind']}" data-evidence="{skill['evidenceStatus']}" data-search="{esc(search)}"><span class="badge {'tested' if tested else 'candidate'}">{'One task tested' if tested else 'Source reviewed'}</span><h3>{esc(skill['name'])}</h3><p>{esc(skill['summary'])}</p><div class="skill-meta"><span>{esc(skill['publisher'])}</span><span>{esc(skill['sourceKind'])}</span></div>{action}<p class="small"><button class="inline-button" data-skill-id="{esc(skill['id'])}">Requirements &amp; evidence</button></p></article>'''


def wrap(page):
    path = Path(page['path']); root = '../' * (len(path.parts)-1)
    nav = ''.join(f'<a href="{root}{url}"'+(' aria-current="page"' if key==page.get('activeNav') else '')+f'>{label}</a>' for key,url,label in [('skills','skills.html','Explore'),('best','collections.html','Best skills'),('guides','guides.html','Guides'),('popular','popular.html','Popular'),('setup','get-set-up.html','My setup')])
    wordmark=f'<img src="{root}assets/logo.svg" width="34" height="44" alt=""><span>SkillLantern</span>'
    title=esc(page['title']); description=esc(page['description'])
    html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title} · SkillLantern</title><meta name="description" content="{description}"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#151b1a"><meta property="og:title" content="{title} · SkillLantern"><meta property="og:description" content="{description}"><meta property="og:type" content="website"><meta property="og:url" content="https://skilllantern.happymoth22.chatgpt.site/{page["path"]}"><link rel="canonical" href="https://skilllantern.happymoth22.chatgpt.site/{page["path"]}"><link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{root}assets/site.css"><link rel="stylesheet" href="{root}assets/app.css"><script defer src="{root}assets/skills-data.js"></script><script defer src="{root}assets/product-data.js"></script><script defer src="{root}assets/popular-data.js"></script><script defer src="{root}assets/app.js"></script><link rel="stylesheet" href="{root}assets/discovery.css"><script defer src="{root}assets/discovery.js"></script>{'<script defer src="'+root+'assets/lantern.js"></script>' if page.get('lantern') else ''}{'<script defer src="'+root+'assets/installer.js"></script>' if page.get('installer') else ''}</head><body data-root="{root}"><a class="skip-link" href="#main">Skip to content</a><div class="shell"><header class="site-header"><a class="brand" href="{root}index.html" aria-label="SkillLantern home">{wordmark}</a><button class="menu-button" id="menu-button" type="button" aria-controls="site-nav" aria-expanded="false" hidden>Menu</button><nav class="site-nav" id="site-nav" aria-label="Main navigation">{nav}</nav></header><main id="main">{page['body'].replace('{{root}}',root)}</main><footer class="site-footer"><div><a class="brand" href="{root}index.html">{wordmark}</a><p>A clearer path from AI possibility to useful work.</p></div><nav aria-label="Footer"><a href="{root}about.html">About &amp; privacy</a><a href="{root}skills.html">Explore capabilities</a><a href="{root}comparisons.html">Test comparison</a><a href="{root}how-we-test.html">Evidence policy</a><details class="motion-settings"><summary>Motion settings</summary><label><input id="reduce-motion" type="checkbox"> Reduce animation</label></details></nav></footer></div><dialog class="dialog" id="skill-dialog" aria-labelledby="skill-dialog-title"><button class="dialog-close" type="button" aria-label="Close source note">×</button><div id="skill-dialog-content"></div></dialog></body></html>'''
    html=html.replace('https://skilllantern.happymoth22.chatgpt.site',SITE_ORIGIN)
    if PUBLIC_ORIGIN: html=html.replace('name="robots" content="noindex,nofollow"','name="robots" content="index,follow"')
    target=DIST/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(html,encoding='utf-8')

study_path=VAULT/'03_Product/Lantern-3D-Study.html'
fallback=re.search(r'<svg id="fallback".*?</svg>',study_path.read_text(encoding='utf-8'),re.S).group() if study_path.exists() else (VAULT/'lantern-fallback.svg').read_text(encoding='utf-8')
shipfile=BASE/'content/ship-guides.json'
SHIP=json.loads(shipfile.read_text(encoding='utf-8-sig')) if shipfile.exists() else []
if isinstance(SHIP,dict): SHIP=SHIP.get('pages',SHIP.get('guides',[]))
expansion_file=BASE/'content/content-expansion.json'
EXPANSION=json.loads(expansion_file.read_text(encoding='utf-8-sig')) if expansion_file.exists() else []
if isinstance(EXPANSION,dict):EXPANSION=EXPANSION.get('pages',[])
INSTALL=json.loads((BASE/'content/install-guide.json').read_text(encoding='utf-8-sig'))
INSTALL.update(outcome='motion',coverKey='motion',cardSummary='Copy the pinned skill into your project, check discovery and try a small task.')
GUIDES=[dict(path='guides/motion-design.html',title='Make interface feedback feel clear',cardSummary='Build loading, success and retry states. Includes a practice pack and a tested comparison.',coverKey='motion',outcome='motion'),*SHIP,INSTALL,*[g for g in EXPANSION if g['path'].startswith('guides/')]]
for g in GUIDES:
    g['hostLabel'] = 'Eligible paid Claude account; browser finance-plugin workflow' if g['path']=='guides/finance-operations.html' else 'DeepSeek developer-preview desktop workflow; separate model access required' if g['path']=='guides/deepseek-harness.html' else 'Codex / Claude Code project installation; activation not exercised' if g['path']=='guides/install-motion-design.html' else 'Claude Desktop walkthrough; brief can be adapted to other agents' if g.get('outcome') == 'website' else ('Browser notebook workflow; separate from your coding agent' if g.get('outcome') == 'marketing' else 'Explicit local source context')
def guidecard(g):
    cover=g.get('coverKey','website'); cover=cover if cover in {'website','marketing','spreadsheet','motion'} else 'website'
    return f'''<a class="guide-card" href="{esc(g['path'])}"><img class="guide-cover" src="assets/covers/{cover}.svg" width="720" height="450" alt="" loading="lazy"><div class="guide-body"><span class="eyebrow">{'One paired task test' if g['path']=='guides/motion-design.html' else 'Source-led guide'}</span><h3>{esc(g['title'])}</h3><p>{esc(g.get('cardSummary',g.get('description','A practical workflow, with requirements and checks.')))}</p><span class="text-link">Follow the guide →</span></div></a>'''
home=f'''<div class="hero-shell"><section class="hero cinematic"><div class="hero-copy"><p class="eyebrow">Make your agent useful</p><h1>Your agent.<br>Ready for the job.</h1><p class="lede">Find the right capabilities and a clear setup plan for what you want to make.</p><div class="hero-actions"><a class="button" href="setup.html">Find my setup →</a><a class="button text" href="guides.html">Explore the guides</a></div></div><div class="hero-art"><div class="lantern-stage" id="stage"><div class="floor" aria-hidden="true"></div><canvas id="scene" aria-hidden="true" hidden></canvas>{fallback}</div><p id="status" class="sr-only" role="status">A still lantern while 3D support loads.</p></div></section></div><section class="section"><div class="section-head"><div><p class="eyebrow">Start with the work</p><h2>What will you make?</h2></div><p>One useful outcome. A manageable next step.</p></div><div class="task-links"><a class="filter-chip" href="setup.html?outcome=website">A distinctive website ↗</a><a class="filter-chip" href="setup.html?outcome=marketing">Better marketing content ↗</a><a class="filter-chip" href="setup.html?outcome=data">A reliable spreadsheet ↗</a><a class="filter-chip" href="setup.html?outcome=motion">An interface that feels right ↗</a></div></section><section class="section"><div class="section-head"><h2>Less guessing.<br>More making.</h2><a href="guides.html">All guides →</a></div><div class="grid three">{''.join(guidecard(g) for g in GUIDES[:3])}</div></section><section class="section trust-note"><h2>Know what you’re working with.</h2><p>Original sources, clear requirements and visible test limits. No mystery rankings.</p><a href="how-we-test.html">How we choose →</a></section>'''
categories=list(dict.fromkeys(s['category'] for s in SKILLS))
chips='<button class="filter-chip" data-filter-category="all" aria-pressed="true">All tasks</button>'+''.join(f'<button class="filter-chip" data-filter-category="{esc(c)}" aria-pressed="false">{esc(c)}</button>' for c in categories)
catalogue=f'''<header class="page-intro"><p class="eyebrow">Explore</p><h1>A capability for<br>the work ahead.</h1><p class="lede">Browse {len(SKILLS)} sourced starting points. Check the requirements before adding anything to your agent.</p></header><div class="filters"><div class="search-field"><label for="skill-search">Find a capability</label><input id="skill-search" type="search" placeholder="Try animation, spreadsheets or React"></div><div class="search-field"><label for="evidence-filter">Evidence</label><select id="evidence-filter"><option value="all">All reviews</option><option value="task-tested">Task tested</option><option value="research-candidate">Source reviewed</option></select></div><button class="button secondary" id="clear-filters">Clear filters</button></div><div class="task-links">{chips}</div><p id="result-count" role="status" aria-live="polite">{len(SKILLS)} capabilities</p><div class="grid three" id="skill-grid">{''.join(card(s) for s in SKILLS)}<div id="empty-state" class="empty-state" hidden><h2>No matches yet.</h2><p>Try a broader task.</p><button class="button secondary" data-clear-filters>Show all</button></div></div><p class="trust-note">Source reviewed means documentation inspected; setup and task performance remain untested. <a href="how-we-test.html">Read the evidence policy.</a></p>'''
type_tabs='<div class="type-tabs" role="group" aria-label="Capability type">'+''.join(f'<button class="filter-chip" data-filter-type="{key}" aria-pressed="{str(key=="all").lower()}">{label}</button>' for key,label in [('all','All'),('skill','Skills'),('plugin','Plugins'),('harness','Agents & harnesses'),('workflow','Workflows')])+'</div>'
catalogue=catalogue.replace('<div class="filters">','<p class="discover-popular"><a class="button secondary" href="popular.html">Popular on GitHub &rarr;</a> <span class="small">A dated shortlist of 11 repositories</span></p>'+type_tabs+'<div class="filters">',1)
guides='<header class="page-intro"><p class="eyebrow">Practical guides</p><h1>A clear path<br>to your next result.</h1><p class="lede">Know what you need, follow a bounded setup, and check the result.</p></header><div class="grid three">'+''.join(guidecard(g) for g in GUIDES)+'</div><section class="section trust-note"><p>New source-led guides are not installation tests. Each guide explains what was reviewed and what you still need to verify.</p><a href="setup.html">Help me choose a setup →</a></section>'
setup='''<header class="page-intro"><p class="eyebrow">Your setup brief</p><h1>Give your agent<br>a clear starting point.</h1><p class="lede">Four short steps. A practical plan based on reviewed workflows.</p></header><form id="setup-form" class="setup-planner planner"><p id="planner-progress" class="eyebrow" role="status">Step 1 of 4</p><fieldset class="planner-step" data-step="0"><legend>What do you want to make?</legend><div class="choice-grid"><label class="choice"><input type="radio" name="outcome" value="website" checked>A distinctive website</label><label class="choice"><input type="radio" name="outcome" value="marketing">Marketing content</label><label class="choice"><input type="radio" name="outcome" value="data">A reliable spreadsheet</label><label class="choice"><input type="radio" name="outcome" value="motion">Better interface motion</label></div></fieldset><fieldset class="planner-step" data-step="1" hidden><legend>Which agent do you already use?</legend><div class="choice-grid"><label class="choice"><input type="radio" name="agent" value="Codex" checked>Codex</label><label class="choice"><input type="radio" name="agent" value="Claude Code">Claude Code</label><label class="choice"><input type="radio" name="agent" value="Other / undecided">Other / undecided</label></div><p class="small">Use your existing access. This plan does not install tools or assume a paid subscription.</p></fieldset><fieldset class="planner-step" data-step="2" hidden><legend>What should the result feel like?</legend><label for="setup-vision">Your vision or top priority</label><textarea id="setup-vision" name="vision" rows="4" maxlength="1500" placeholder="For example: a calm, premium website for a small ceramics studio"></textarea><label for="setup-priority">Focus first on</label><select id="setup-priority" name="priority"><option>A small, working first version</option><option>Visual quality and brand</option><option>Accuracy and verification</option><option>Learning the workflow</option></select></fieldset><fieldset class="planner-step" data-step="3" hidden><legend>What boundaries should the agent respect?</legend><label for="setup-constraints">Tools, time, budget or things to avoid</label><textarea id="setup-constraints" name="constraints" rows="4" maxlength="1500" placeholder="For example: existing tools only, no new subscriptions, one afternoon"></textarea><p class="small">Keep private credentials out of your brief. Your answers stay in this page; nothing is sent or saved automatically.</p></fieldset><div class="planner-actions"><button class="button secondary" id="planner-back" type="button" hidden>Back</button><button class="button" id="planner-next" type="button">Continue →</button><button class="button" id="planner-submit" type="submit" hidden>Build my setup brief →</button></div></form><section id="setup-result" class="plan-result setup-result section" hidden tabindex="-1" aria-labelledby="result-title"></section><noscript><p>This planner needs JavaScript. You can still <a href="guides.html">follow a guide</a> and use its requirements checklist.</p></noscript>'''
helpbody='''<header class="page-intro"><p class="eyebrow">Implementation help</p><h1>The value is in<br>making it work.</h1><p class="lede">Free guides and setup briefs are available now. Hands-on implementation support is a proposed next step.</p></header><div class="grid three"><article class="offer-card"><span class="eyebrow">Available now</span><h2>Choose a path</h2><p>Use sourced guides and a tailored setup brief to make a bounded first attempt.</p><a class="button" href="setup.html">Create my brief →</a></article><article class="offer-card"><span class="eyebrow">Proposed service</span><h2>Adapt and configure</h2><p>Help connecting the right capabilities to your existing agent, project and constraints.</p></article><article class="offer-card"><span class="eyebrow">Proposed service</span><h2>Verify the result</h2><p>Acceptance checks, a usable handoff and a clear account of remaining limitations.</p></article></div><section class="section prose"><h2>How this could earn money</h2><p>The proposed path is free practical guidance followed by scoped implementation help. Paid value would come from configuration, adaptation and verification, rather than repackaging public skill files.</p><p>The service pilot is not open. Scope, pricing and payment arrangements remain undecided; no booking or purchase is available.</p></section>'''
pages=[dict(path='index.html',title='Your agent. Ready for the job.',description='Find AI capabilities, follow practical guides and build a setup brief for your existing agent.',body=home,lantern=True),dict(path='skills.html',title='Explore AI capabilities',description='Find sourced AI skills and workflows for websites, writing, spreadsheets and motion.',body=catalogue,activeNav='skills'),dict(path='guides.html',title='Practical AI workflow guides',description='Clear requirements, setup steps and verification for useful AI workflows.',body=guides,activeNav='guides'),dict(path='setup.html',title='Find your agent setup',description='Build a practical setup brief for your AI agent in four short steps.',body=setup,activeNav='setup'),dict(path='setup-help.html',title='Implementation help',description='The proposed path from free AI guidance to scoped configuration and verification support.',body=helpbody),*[p for p in EDITORIAL if p.get('lang')!='ar' and not p['path'].startswith('ar/')],*SHIP,INSTALL,*EXPANSION]

def icon(name):
    source=BASE/'content/icons.json'
    icons=json.loads(source.read_text(encoding='utf-8-sig')) if source.exists() else {}
    item=icons.get(name,{'viewBox':'0 0 24 24','body':'<path d="M5 12h14M12 5v14"/>'})
    return f'<svg class="ui-icon step-icon" aria-hidden="true" viewBox="{item["viewBox"]}" fill="none" stroke="currentColor" stroke-width="1.6">{item["body"]}</svg>'
installer_body = f'''<header class="page-intro"><p class="eyebrow">Get set up / Codex on Windows</p><h1>Add Motion Design.<br>Keep control.</h1><p class="lede">Choose your project. Review the files. Install reusable guidance without a command line.</p><div class="requirement-chips"><span class="requirement-chip">Chrome or Edge</span><span class="requirement-chip">Top-level HTTPS tab</span><span class="requirement-chip">Existing Codex access</span></div></header><section id="installer" class="installer-panel"><h2>{icon('folder')} Install files into your project</h2><p>Only <code>.agents/skills/motion-design</code> is used. Your project stays on your computer.</p><div class="install-actions"><button class="button" id="install-select">Choose project folder</button><button class="button" id="install-run" disabled>Install files</button><button class="button secondary" id="install-undo" disabled>Undo verified files</button></div><p id="install-status" class="install-status" role="status" aria-live="polite">Checking the pinned package...</p><details><summary>Preview the exact file plan</summary><p>18 payload files, plus <code>.agents/skills/motion-design/.skilllantern-owned.json</code>, a local ownership record used for safe undo.</p><pre id="install-file-plan" class="file-plan code-block"></pre></details><details><summary>Permissions and limits</summary><p>The browser asks for access to the folder you select. We fetch only same-site pinned text files, verify their SHA-256 hashes before and after writing, and keep a small ownership record inside the skill folder. No commands run, no project files are uploaded, and no folder handle is saved.</p><p>Existing unmanaged folders are refused. Undo removes only recorded files that still match the reviewed package; modified or unrelated files stay. Empty directories remain. This installs files; Codex activation is a separate check.</p></details></section><section class="section"><h2>Then check your agent</h2><div class="grid three"><article class="step-card">{icon('check')}<h3>Open the same project</h3><p>In Codex, use <code>/skills</code> or type <code>$motion-design</code>. Restart if the skill is missing.</p></article><article class="step-card">{icon('play')}<h3>Try one small task</h3><p>Ask for clear loading and success feedback on a practice page. Review changes before accepting them.</p></article><article class="step-card">{icon('folder')}<h3>Prefer manual setup?</h3><p>Use the ZIP and copy-folder instructions for Codex or Claude Code.</p><a href="{{{{root}}}}guides/install-motion-design.html">Open manual guide &rarr;</a></article></div><p><a class="button secondary" href="{{{{root}}}}downloads/motion-design-skill.zip" download>Download verified ZIP</a></p></section>'''
hub=f'''<header class="page-intro"><p class="eyebrow">Get set up</p><h1>A useful setup.<br>Your way.</h1><p class="lede">Start with your goal or add a reviewed skill to a project you already use.</p></header><div class="grid three setup-hub"><article class="route-card">{icon('sliders')}<h2>Find my setup</h2><p>Answer four questions. Leave with capabilities, checks and a brief for your agent.</p><a class="button" href="setup.html">Build my brief &rarr;</a></article><article class="route-card">{icon('folder')}<h2>Install Motion Design</h2><p>A file-only browser installer for a local Codex project. Preview before writing.</p><a class="button" href="install.html">Choose my project &rarr;</a></article><article class="route-card">{icon('check')}<h2>Use manual steps</h2><p>Download the pinned package and copy one folder for Codex or Claude Code.</p><a class="button secondary" href="guides/install-motion-design.html">Follow the guide &rarr;</a></article></div>'''
pages += [dict(path='get-set-up.html',title='Get your agent set up',description='Choose a setup brief, verified file-only installer or manual skill setup.',body=hub,activeNav='setup'),dict(path='install.html',title='Install Motion Design files',description='Preview and install pinned Motion Design guidance into your own Codex project folder.',body=installer_body,activeNav='setup',installer=True)]
sections=[('updates.html','Updates','What changed, and why.','New guide releases and source-review changes will appear here.','A release log is planned; no email subscription or automated publishing is active.'),('collections.html','Collections','Useful paths, brought together.','Curated bundles by goal are coming next.','For now, explore capabilities by task or create a setup brief.'),('community.html','Community','Learn from real attempts.','A place for practical workflow experiences is planned.','Community submissions are not open. No account or posting features are active.'),('for-creators.html','For creators','Make good guidance easier to find.','Source attribution and clear evidence matter here.','Creator submissions and listing tools are planned. No submission form is active.')]
for path,title,headline,summary,note in sections:
    pages.append(dict(path=path,title=title,description=summary,body=f'<header class="page-intro"><p class="eyebrow">{title} / Coming next</p><h1>{headline}</h1><p class="lede">{summary}</p></header><section class="empty-topic"><h2>A considered next step.</h2><p>{note}</p><a class="button" href="guides.html">Find a practical guide &rarr;</a></section>',activeNav='updates' if path=='updates.html' else ''))
(BASE/'content/sections.json').write_text(json.dumps(sections,indent=2)+'\n',encoding='utf-8')
(BASE/'content/navigation.json').write_text(json.dumps({'primary':['Discover','Guides','Get set up','Updates','More'],'types':['All','Skills','Plugins','Agents & harnesses','Workflows']},indent=2)+'\n',encoding='utf-8')
# Reformat existing source-led instructions into scan-friendly cards, keeping original wording.
def guide_steps(body):
    match=re.search(r'<ol class="steps">(.*?)</ol>',body,re.S)
    if not match:return body
    items=re.findall(r'<li>(.*?)</li>',match.group(1),re.S)
    output=[]
    for i,item in enumerate(items):
        heading=re.search(r'<h[23]>(.*?)</h[23]>',item,re.S)
        if not heading:continue
        title=heading.group(1); content=item[heading.end():]
        output.append(f'<section class="step-card">{icon(["folder","sliders","play","check"][i%4])}<span class="step-number">Step {i+1:02d}</span><h2>{title}</h2>{content}<p class="expected-result"><strong>Ready when:</strong> you have completed this step and checked the result before continuing.</p><details class="step-troubleshooting"><summary>If this step does not work</summary><p>Recheck the requirements and the exact file or account you selected. Keep your original unchanged; use the guide&apos;s fix or undo advice.</p></details><label class="step-progress"><input type="checkbox"> Done for this session</label></section>')
    return body[:match.start()]+'<div class="guide-steps">'+''.join(output)+'</div>'+body[match.end():]

SNAPSHOT=json.loads((BASE/'content/popular-snapshot.json').read_text(encoding='utf-8-sig'))
popular_rows=''.join(f'<tr data-popular-row><td><a href="{esc(v["url"])}" target="_blank" rel="noopener noreferrer">{esc(v["name"])}</a><small>{esc(v["repository"])}</small><p>{esc(v.get("description") or "")}</p></td><td>{v["stars"]:,}</td><td>{esc(v["kind"])}</td><td>{esc(v.get("starsCheckedAt") or "Unknown")}<br>{esc(v["fetchStatus"])}</td></tr>' for v in SNAPSHOT['items'])
popular_body=f'''<header class="page-intro"><p class="eyebrow">Popular / GitHub snapshot</p><h1>What developers<br>are watching.</h1><p class="lede">Stars across a curated shortlist of 11 repositories, including UI UX Pro Max and Ponytail. Popularity is a discovery signal, not a quality or safety score.</p></header><div class="filters"><div class="search-field"><label for="popular-search">Find a repository</label><input id="popular-search" type="search" placeholder="Name, kind or repository"></div><div class="search-field"><label for="popular-sort">Sort by</label><select id="popular-sort"><option value="stars">Most stars</option><option value="name">Name A-Z</option></select></div><button class="button secondary" id="popular-refresh">Refresh public counts</button></div><p class="small">The refresh button contacts GitHub&apos;s public API for this fixed list. No credentials or project data are sent. Counts stay in this page&apos;s memory; rate limits may apply.</p><p id="popular-status" role="status">Published snapshot: {esc(SNAPSHOT['generatedAt'])}. Curated shortlist; not a global ranking.</p><div class="table-scroll"><table class="comparison-table"><thead><tr><th scope="col">Repository</th><th scope="col">Stars</th><th scope="col">Kind</th><th scope="col">Checked / status</th></tr></thead><tbody id="popular-rows">{popular_rows}</tbody></table></div><p id="popular-empty" hidden>No matching repositories. Try a broader search.</p><details><summary>Scope and interpretation</summary><p>{esc(SNAPSHOT['scope'])} One entry per repository; stars cover the whole repository rather than each skill. No installation, security certification or paid-demand conclusion follows from a count.</p><p>Counts change. Source licence, freshness and limitations are included in the <a href="api/top-skills.json">published JSON snapshot</a>.</p></details><section class="section"><h2>Build with this data</h2><p>Use the free read-only snapshot today. Richer compatibility and evidence data is a proposed paid developer product.</p><a href="developers.html">Explore the Developer API &rarr;</a></section>'''
api_body='''<header class="page-intro"><p class="eyebrow">For developers</p><h1>Useful data.<br>Clear provenance.</h1><p class="lede">Start with published JSON snapshots. A paid enrichment API is the proposed next product.</p></header><div class="grid three"><article class="route-card"><h2>Repository discovery</h2><p>Stars, repository metadata, source timestamps and per-entry limits from our fixed shortlist.</p><a href="api/top-skills.json">GET /api/top-skills.json &rarr;</a></article><article class="route-card"><h2>Reviewed capabilities</h2><p>Source links, requirements and actual evidence status from the curated catalogue.</p><a href="api/capabilities.json">GET /api/capabilities.json &rarr;</a></article><article class="route-card"><h2>Proposed paid enrichment</h2><p>Compatibility, installation recipes, evidence history and tailored recommendations.</p><span class="badge">Planned / not available</span></article></div><section class="section prose"><h2>Try the current feed</h2><button class="copy-button" data-copy-target="api-example">Copy fetch example</button><pre class="code-block"><code id="api-example">const response = await fetch('/api/top-skills.json');
if (!response.ok) throw new Error(`HTTP ${response.status}`);
const snapshot = await response.json();
console.log(snapshot.generatedAt, snapshot.items);</code></pre><p>These endpoints serve published static snapshots, not a live stream or authenticated API backend. This owner-private preview requires hosting access; external applications should not assume anonymous access or CORS availability. The example runs from this site&apos;s origin.</p><details><summary>Response and freshness</summary><p>The discovery feed includes schemaVersion, generatedAt, scope and items. Each entry includes repository, stars, starsCheckedAt, fetchStatus, licence and limitations. Missing or stale upstream data stays labelled. Capability evidence separates source review from the one bounded task test.</p></details><h2>A possible paid product</h2><p>Free repository discovery could lead to paid maintained enrichment: agent compatibility, reviewed install recipes, source and evidence history, and task recommendations. This model is proposed, with demand, pricing and economics unvalidated.</p><p>API keys, metering, historical and recommendation endpoints are planned. They do not exist yet. No checkout, subscription or key generation is active.</p><a href="popular.html">Explore the current shortlist &rarr;</a></section>'''
pages += [dict(path='popular.html',title='Popular AI skills and agent tooling',description='Dated GitHub stars across a curated shortlist of 11 skill and agent-tooling repositories.',body=popular_body,activeNav='popular'),dict(path='developers.html',title='Developer API and published snapshots',description='Use read-only JSON snapshots; explore the proposed paid compatibility and evidence API.',body=api_body)]
(DIST/'api').mkdir(exist_ok=True)
(DIST/'api/top-skills.json').write_text(json.dumps(SNAPSHOT,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
public_keys=['id','name','publisher','sourceKind','category','summary','sourceUrl','reviewedOn','evidenceStatus','evidenceSummary','requirements','limitations','licenseNote','guidePath']
(DIST/'api/capabilities.json').write_text(json.dumps({'schemaVersion':1,'generatedOn':'2026-11-14','mode':'published snapshot','scope':'Reviewed catalogue; source review is not installation or security certification.','items':[{k:v for k,v in item.items() if k in public_keys} for item in SKILLS]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(DIST/'assets/popular-data.js').write_text('window.SKILLLANTERN_POPULAR = '+json.dumps(SNAPSHOT,ensure_ascii=False)+';\n',encoding='utf-8')
for expansion in EXPANSION:
    for download in expansion.get('downloads',[]):
        source=(BASE/download['source']).resolve();target=(DIST/download['path']).resolve()
        if not source.is_relative_to((BASE/'content/fixtures').resolve()) or not target.is_relative_to((DIST/'downloads').resolve()):raise ValueError('Invalid fixture download')
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)

# Expansion pages can replace a deliberate topic placeholder, never create duplicate routes.
unique_pages={p['path']:p for p in pages}
for p in EXPANSION:unique_pages[p['path']]=p
from discovery_release import apply_release
unique_pages = apply_release(BASE, DIST, unique_pages, SKILLS, GUIDES, fallback)
pages=list(unique_pages.values())
for page in pages:
    if page.get('steps'):
        req=''.join(f'<span class="requirement-chip">{esc(v)}</span>' for v in page.get('requirements',[]))
        steps=''.join(f'<section class="step-card">{icon(v.get("icon","check"))}<span class="step-number">Step {i+1:02d}</span><h2>{esc(v["title"])}</h2><p>{v["action"]}</p><p class="expected-result"><strong>Ready when:</strong> {esc(v["expected"])}</p><label class="step-progress"><input type="checkbox"> Done for this session</label></section>' for i,v in enumerate(page['steps']))
        page['body']=f'<header class="page-intro"><p class="eyebrow">Source-led guide</p><h1>{esc(page["title"])}</h1><p class="lede">{esc(page["description"])}</p><div class="requirement-chips">{req}</div></header><div class="guide-steps">{steps}</div><section class="prose"><h2>Check your result</h2><ul>'+''.join('<li>'+v+'</li>' for v in page.get('verification',[]))+'</ul><details><summary>Fix or undo</summary><ul>'+''.join('<li>'+v+'</li>' for v in page.get('troubleshooting',[]))+'</ul></details><details><summary>Source, date and review limits</summary>'+page.get('sourceDetailsHtml','')+'<p>Reviewed '+esc(page.get('observedOn','2026-11-14'))+'. Source-led guidance; workflow not reproduced.</p></details></section>'
    if page['path'].startswith('guides/'):

        page['body']=guide_steps(page['body'])
    if page['path']=='guides/motion-design.html':
        page['body']=page['body'].replace('<article class="prose">','<article class="prose"><aside class="callout warm"><h2>Want to add it to your agent?</h2><p>Copy the reviewed skill folder into a Codex or Claude Code project. File layout and documentation checked; native activation not exercised.</p><a class="button" href="{{root}}guides/install-motion-design.html">Install Motion Design &rarr;</a></aside>',1)
    from setup_widgets import enhance_setup
    enhance_setup(page, BASE)
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
    for name,data in payload.items():
        asset=DIST/'assets/install-package'/name; asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(data)
    package=json.loads((BASE/'content/installer-package.json').read_text(encoding='utf-8-sig'))
    for entry in package['files']:
        data=payload[entry['relativePath']]
        if len(data)!=entry['size'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:raise ValueError('Installer manifest mismatch')
    (DIST/'assets/installer-package.json').write_text(json.dumps(package,indent=2)+'\n',encoding='utf-8')
    print(f'Packaged {len(payload)} skill files (Markdown and MIT licence only)')
if PUBLIC_ORIGIN:
    excluded={'setup.html','setup-help.html','community.html','for-creators.html','updates.html','developers.html','get-set-up.html'}
    urls=''.join('<url><loc>'+esc(SITE_ORIGIN+'/'+p['path'])+'</loc></url>' for p in pages if p['path'] not in excluded)
    (DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>',encoding='utf-8')
    (DIST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+SITE_ORIGIN+'/sitemap.xml\n',encoding='utf-8')
else:
    (DIST/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
    if (DIST/'sitemap.xml').exists(): (DIST/'sitemap.xml').unlink()
(BASE/'page-manifest.json').write_text(json.dumps([p['path'] for p in pages],indent=2)+'\n',encoding='utf-8')
print(f'Built {len(pages)} English pages and {len(SKILLS)} capabilities')
