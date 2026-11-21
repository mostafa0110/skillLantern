"""Discover, select and set up reviewed capabilities; static, dependency-free UI."""
from html import escape as e
import json
import shutil
from urllib.parse import urlparse
from pathlib import Path


def apply_release(base, dist, pages, skills, guides, fallback):
    library_path=base/'content/launch-library.json'
    data=json.loads(library_path.read_text(encoding='utf-8-sig')) if library_path.exists() else {'profiles':[], 'guides':[]}
    items={}
    for s in skills:
        tasks=['Motion','Design'] if s['category']=='Design & motion' else ['Documents'] if 'doc' in s['id'] else ['Spreadsheets','Finance'] if s['id']=='xlsx' else ['Coding','Design']
        items[s['id']]={**s,'kind':s['sourceKind'],'apps':['Check source'],'tasks':tasks,'setupSteps':['Open the original source and review its current instructions and license.','Check the requirements below against your app and project.','Add only the selected capability using the source instructions; review requested permissions.','Try one small task in a copy of your project and inspect the result.'],'detailPath':'capabilities/'+s['id']+'.html'}
    for p in data.get('profiles',[]):
        existing=items.get(p['id'],{})
        if existing.get('evidenceStatus')=='task-tested':existing['lastTestedOn']=existing['reviewedOn']
        items[p['id']]={**existing,**p,'detailPath':'capabilities/'+p['id']+'.html'}
    profiles=list(items.values())
    for p in profiles:
        for key in ('requirements','limitations','setupSteps','apps','tasks'):p.setdefault(key,[])
        original_tasks=list(p['tasks'])
        groups={'Design':['design','interface','website','accessibility','3d'],'Motion':['motion','animation'],'Finance':['financ','invoice','reconcil','budget','operations'],'Documents':['document','writing','report'],'Coding':['code','coding','test','agent','developer'],'Marketing':['market','content','research'],'Spreadsheets':['spreadsheet','workbook','excel']}
        for group,terms in groups.items():
            if any(t in (' '.join(original_tasks)+' '+p['summary']).lower() for t in terms) and group not in p['tasks']:p['tasks'].append(group)
        p.setdefault('reviewedOn','Review date unavailable');p.setdefault('publisher',urlparse(p['sourceUrl']).hostname or 'Source');p.setdefault('evidenceStatus','research-candidate')
    def card(p):
        tags=''.join('<span>'+e(v)+'</span>' for v in p['apps'])
        return f'''<article class="discovery-card" data-discovery-card data-id="{e(p['id'])}" data-apps="{e('|'.join(p['apps']))}" data-tasks="{e('|'.join(p['tasks']))}" data-kind="{e(p['kind'])}" data-text="{e(' '.join([p['name'],p['summary'],*p['apps'],*p['tasks'],p['kind'],p.get('outcome',''),p.get('example',''),p.get('useWhen','')]).lower())}"><div class="card-top"><span class="cap-kind">{e(p['kind'])}</span><button class="save-cap" data-save="{e(p['id'])}" aria-pressed="false" aria-label="Save {e(p['name'])}">+ Save</button></div><h3><a data-profile href="{e(p['detailPath'])}">{e(p['name'])}</a></h3><p>{e(p['summary'])}</p><div class="app-tags">{tags}</div><div class="card-evidence"><span>{'One task tested' if p['evidenceStatus']=='task-tested' else 'Source reviewed'} · {e(p['reviewedOn'])}</span><a href="{e(p['sourceUrl'])}" target="_blank" rel="noopener noreferrer">Source</a></div><a class="card-action" data-profile href="{e(p['detailPath'])}">View details &amp; setup</a></article>'''
    def collection():
        def select(key,title,values):return f'<label>{title}<select name="{key}" aria-label="{title}"><option value="">All {title.lower()+'s' if title!='Kind' else 'kinds'}</option>'+''.join(f'<option>{e(v)}</option>' for v in sorted(set(values)))+'</select></label>'
        return '''<section class="discovery-section" id="explore" aria-labelledby="collection-title"><div class="section-head"><div><p class="eyebrow">The collection</p><h2 id="collection-title">Find your next useful upgrade.</h2></div><a href="get-set-up.html">My saved setup <span data-saved-count>0</span></a></div><form class="discover-form" id="discover-form" role="search"><label class="wide-search">What do you want your AI to do?<input type="search" name="q" placeholder="Try motion, research, marketing, spreadsheets…" autocomplete="off"></label><div class="discovery-filters">'''+select('app','App',[a for p in profiles for a in p['apps']])+select('task','Task',[t for p in profiles for t in p['tasks']])+select('kind','Kind',[p['kind'] for p in profiles])+'''<button class="button secondary" type="reset">Reset filters</button></div></form><div class="results-line"><p id="discovery-count" role="status" aria-live="polite">'''+str(len(profiles))+''' capabilities</p><label class="saved-only"><input type="checkbox" id="saved-only"> Saved only</label></div><div class="discovery-grid">'''+''.join(card(p) for p in profiles)+'''</div><div id="discovery-empty" class="empty-state" hidden><h3>No matches yet.</h3><p>Try another app, a broader task, or clear your filters.</p><button class="button" data-reset>Show the full collection</button></div><noscript><p>All capabilities are listed above. Search and saving need JavaScript; details, sources and setup guides work without it.</p></noscript></section>'''
    def page(path,title,description,body,active='skills',**kwargs):pages[path]=dict(path=path,title=title,description=description,body=body,activeNav=active,**kwargs)
    task_browse='<section class="task-browse"><p class="eyebrow">Start with your task</p><div>'+''.join('<a href="skills.html?task='+task+'"><strong>'+label+'</strong><span>'+description+'</span></a>' for task,label,description in [('Design','Website & design','Make an interface clearer'),('Motion','Motion','Give feedback a purpose'),('Documents','Writing & documents','Build a draft with structure'),('Marketing','Marketing & research','Work from your sources'),('Finance','Finance & spreadsheets','Check the numbers'),('Coding','Coding & testing','Build, inspect and improve')])+'</div></section>'
    home=f'''<section class="discovery-hero"><div><h1>Find the right upgrades<br>for your AI.</h1><p class="lede">Discover skills, plugins and tools for the apps you already use. Choose what fits your task, then make it work.</p><form action="skills.html" class="hero-search" role="search"><label for="home-query">What do you want your AI to do?</label><div><input id="home-query" name="q" type="search" placeholder="Design a website, analyse data, write better?"><button class="button">Explore</button></div></form><div class="hero-quick"><a href="skills.html">Browse the full collection</a><a href="skills.html?app=Codex+CLI">Codex</a><a href="skills.html?app=Claude+Code">Claude Code</a><a href="skills.html?app=Claude+Cowork">Claude Cowork</a></div></div><div class="hero-art"><div class="lantern-stage" id="stage"><div class="floor" aria-hidden="true"></div><canvas id="scene" aria-hidden="true" hidden></canvas>{fallback}</div><p id="status" class="sr-only" role="status">A still lantern while 3D support loads.</p></div></section>'''+task_browse+'''<section class="example-shelf"><div><p class="eyebrow">Practical starting points</p><h2>See a setup in context.</h2></div><a href="guides/website-upgrades.html"><span class="cap-kind">Website & design</span><h3>A stronger website workflow</h3><p>Choose design guidance, visual tools and browser checks.</p></a><a href="guides/finance-upgrades.html"><span class="cap-kind">Finance & spreadsheets</span><h3>A careful finance workflow</h3><p>Use synthetic fixtures, exact checks and clear app boundaries.</p></a><a href="guides/marketing-launch-campaign.html"><span class="cap-kind">Marketing</span><h3>Build a campaign from a clear brief</h3><p>Plan the message, draft content and review the claims.</p></a><a href="guides/notes-to-word-report.html"><span class="cap-kind">Writing & documents</span><h3>Turn notes into a Word report</h3><p>Shape a clear draft, then check the finished document.</p></a></section>'''+collection()
    page('index.html','Discover useful upgrades for your AI','Explore curated AI skills, plugins, tools and harnesses for your app and task. Read sources, save a setup and follow practical guides.',home,lantern=True)
    page('skills.html','Explore AI skills, plugins and tools','Search capabilities by app, task and kind. Review source evidence and setup instructions.', '<header class="page-intro compact-intro"><p class="eyebrow">Explore</p><h1>Find the right capability<br>for the work in front of you.</h1><p class="lede">Start with your task and the app you use. Every profile includes a source, requirements and review limits.</p></header>'+collection())
    for p in profiles:
        bullet=lambda values:'<ul>'+''.join('<li>'+e(str(v))+'</li>' for v in values)+'</ul>'
        steps='<ol class="setup-steps">'+''.join('<li>'+e(str(v))+'</li>' for v in p['setupSteps'])+'</ol>'
        guide=f'<a class="button" href="{{{{root}}}}{e(p["guidePath"])}">Follow the practical guide</a>' if p.get('guidePath') else '<p>Use the original source instructions for this capability; a dedicated SkillLantern walkthrough is not available yet.</p>'
        context=''.join('<section><h2>'+e(label)+'</h2><p>'+e(p[field])+'</p></section>' for field,label in [('outcome','What you can make'),('example','A concrete first task'),('useWhen','Choose this when'),('skipWhen','Choose another route when'),('hostBoundary','App and setup boundaries')] if p.get(field))
        if p.get('setupHost'):context+='<section><h2>Setup route in this profile</h2><p>'+e(p['setupHost'])+'</p></section>'
        source_setup='<p><a href="'+e(p.get('setupSourceUrl',p['sourceUrl']))+'" target="_blank" rel="noopener noreferrer">Original installation instructions</a></p>'
        body=f'''<a class="back-link" data-back-explore href="{{{{root}}}}skills.html">Back to collection</a><header class="profile-header"><div><p class="eyebrow">{e(p['kind'])} · {e(p['publisher'])}</p><h1>{e(p['name'])}</h1><p class="lede">{e(p['summary'])}</p><div class="app-tags">{''.join('<span>'+e(x)+'</span>' for x in p['apps'])}</div></div><aside class="profile-verdict"><p class="eyebrow">Before you choose</p><p>{'One bounded task tested; native installation not exercised.' if p['evidenceStatus']=='task-tested' else 'Source reviewed. Installation and task results are not verified here.'}</p><p class="small">Reviewed {e(p['reviewedOn'])}</p><button class="button" data-save="{e(p['id'])}" aria-pressed="false">+ Save to my setup</button><a href="{{{{root}}}}get-set-up.html">Review my setup</a></aside></header><div class="profile-layout"><div>{context}<section><h2>What you need</h2>{bullet(p['requirements'])}</section><section id="setup"><h2>Setup instructions</h2>{guide}{source_setup}{steps}<div class="callout"><strong>Check before keeping it</strong><p>Ask for one small result, inspect the output and permissions, and confirm it suits your app. If it fails, undo your changes and return to your original project.</p></div></section><section><h2>Limits to keep in view</h2>{bullet(p['limitations'])}</section></div><aside class="profile-source"><h3>Original source</h3><p>{e(p['publisher'])}</p><a href="{e(p['sourceUrl'])}" target="_blank" rel="noopener noreferrer">Read the source instructions</a><p class="small">Reviewed {e(p['reviewedOn'])}. Upstream instructions and app support can change.</p><h3>Useful for</h3>{bullet(p['tasks'])}<p class="small">{e(p.get('licenseNote','Check the original source license and app terms before use.'))}</p></aside></div>'''
        page(p['detailPath'],p['name']+' — requirements and setup',p['summary'],body)
    # Publish source-led launch guides from the content specialist, retaining old guide URLs.
    if data.get('guides'):
        from release_content import render_guide
        for g in data['guides']:
            page(g['path'],g['title'],g.get('description',g.get('summary','Practical setup guidance.')),render_guide(g),'guides')
            for download in g.get('downloads',[]):
                source=(base/download['source']).resolve();target=(dist/download['path']).resolve()
                if not source.is_relative_to((base/'content/fixtures').resolve()) or not target.is_relative_to((dist/'downloads').resolve()):raise ValueError('Invalid fixture path')
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    allguides={g['path']:g for g in guides}
    allguides.update({g['path']:g for g in data.get('guides',[])})
    guide_cards=''.join(f'<a class="guide-list-card" href="{e(g["path"])}"><span class="cap-kind">Practical guide</span><h2>{e(g["title"])}</h2><p>{e(g.get("cardSummary",g.get("description","Requirements, steps and checks for a bounded first attempt.")))}</p><span>Read guide</span></a>' for g in allguides.values())
    page('guides.html','Practical setup guides','Source-led practical guides with requirements, setup instructions and checks.','<header class="page-intro compact-intro"><p class="eyebrow">Guides</p><h1>From interesting<br>to actually useful.</h1><p class="lede">Follow a bounded workflow. Check requirements before starting, then inspect what changed.</p></header><div class="guide-list">'+guide_cards+'</div>','guides')
    setup='''<header class="page-intro compact-intro"><p class="eyebrow">My setup</p><h1>Your choices.<br>A clearer next step.</h1><p class="lede">Save capabilities as you explore, then choose one to try. Your selection stays in this browser; no account is needed.</p></header><section id="saved-setup"><div class="empty-state"><h2>Start with one useful upgrade.</h2><p>Browse the collection and save what fits your app and task.</p><a class="button" href="skills.html">Explore the full collection</a></div></section><section class="section"><h2>A manageable first attempt.</h2><div class="journey-strip"><div><h3>Check the fit</h3><p>Read app requirements, access needs and source permissions.</p></div><div><h3>Choose one</h3><p>Follow its practical guide or the original setup instructions.</p></div><div><h3>Verify your result</h3><p>Try a small task in a copy. Keep only changes you understand.</p></div></div></section>'''
    page('get-set-up.html','My saved AI setup','Review saved capabilities and follow a practical setup path.',setup,'setup')
    for old in ('setup.html','setup-help.html','collections.html','community.html','for-creators.html','updates.html'):
        page(old,'Explore useful AI capabilities','Find capabilities for your app and task.','<header class="page-intro"><p class="eyebrow">Find your next step</p><h1>Good tools, matched<br>to your work.</h1><p class="lede">Browse the full collection or continue with your saved capabilities.</p><a class="button" href="skills.html">Explore capabilities</a> <a class="button secondary" href="get-set-up.html">My saved setup</a></header>')
    # Existing snapshots and the dated Popular functionality remain available without speculative sales copy.
    pages['popular.html']['body']=pages['popular.html']['body'].split('<section class="section"><h2>Build with this data')[0]
    page('developers.html','Published capability snapshots','Static JSON feeds with source links and review dates.','<header class="page-intro"><p class="eyebrow">Published snapshots</p><h1>Useful data.<br>Clear provenance.</h1><p class="lede">Read-only JSON snapshots for this curated collection. These are published files with dates, rather than a live API.</p></header><section class="prose"><h2>Available feeds</h2><p><a href="api/capabilities.json">Reviewed capabilities JSON</a></p><p><a href="api/top-skills.json">Dated repository shortlist JSON</a></p><p>Source review, app compatibility and task testing are separate evidence. Check each record before relying on it.</p></section>')
    page('about.html','About SkillLantern','A curated route from AI discovery to useful setups.','<header class="page-intro"><p class="eyebrow">About</p><h1>Make AI possibilities<br>easier to use.</h1><p class="lede">SkillLantern brings together useful skills, plugins, tools and harnesses with original sources, requirements and practical next steps.</p></header><section class="prose"><h2>Evidence you can inspect</h2><p>Source-reviewed guidance is labelled separately from the one bounded task comparison. We do not treat popularity as proof of quality or promise universal app compatibility.</p><p><a href="how-we-test.html">Read our evidence policy</a></p><h2>Your browser, your choices</h2><p>Saved capabilities use local browser storage. They are not uploaded or shared with an account. Clear them from My setup or remove this site’s browser data. Search and filters remain in the page URL.</p><h2>Original creators stay visible</h2><p>Every capability links to its original source. Check its license, permissions, current instructions and app requirements before installing.</p></section>')
    for profile in profiles:
        profile.setdefault('sourceKind',profile['kind'])
        profile.setdefault('category',profile['tasks'][0] if profile['tasks'] else 'General')
        profile.setdefault('taskKeywords',profile['tasks'])
    (dist/'api/capabilities.json').write_text(json.dumps({'schemaVersion':1,'generatedOn':'2026-11-22','scope':'Curated source-reviewed capabilities. App support reflects source instructions; native setup not verified.','items':profiles},ensure_ascii=False,indent=2),encoding='utf-8')
    (dist/'assets/discovery-data.json').write_text(json.dumps(profiles,ensure_ascii=False),encoding='utf-8')
    css=(base/'discovery.css').read_text(encoding='utf-8');js=(base/'discovery.js').read_text(encoding='utf-8')
    (dist/'assets/discovery.css').write_text(css,encoding='utf-8')
    (dist/'assets/discovery.js').write_text('window.SKILLLANTERN_LIBRARY='+json.dumps(profiles,ensure_ascii=False)+';\n'+js,encoding='utf-8')
    from best_skills import add_best_skills
    add_best_skills(pages)
    from chase_compare import apply_comparison
    apply_comparison(base, dist, pages)
    from practical_playbooks import add_practical_playbooks
    add_practical_playbooks(pages)
    from marketing_setup import add_marketing_setup
    add_marketing_setup(pages)
    from remotion_setup import add_remotion_setup, write_remotion_assets
    add_remotion_setup(pages)
    write_remotion_assets(base, dist)
    marker = '<div class="guide-list">'
    if marker not in pages['guides.html']['body']: raise ValueError('Guide list missing')
    for route in ('guides/marketing-launch-campaign.html', 'guides/remotion-hero-loop.html'):
        guide = pages[route]
        card = '<a class="guide-list-card" href="' + guide['path'] + '"><span class="cap-kind">Practical setup</span><h2>' + e(guide['title']) + '</h2><p>' + e(guide['description']) + '</p><span>Read guide</span></a>'
        pages['guides.html']['body'] = pages['guides.html']['body'].replace(marker, marker + card, 1)
    return pages
