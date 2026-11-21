"""Visible, source-backed setup controls shared by guides and capability profiles."""
from html import escape as e
import json

COMMANDS = {
 'ui-ux-pro-max': [('Terminal · Codex CLI', 'npx ui-ux-pro-max-cli init --ai codex')],
 'threejs-web': [('Terminal · Codex CLI', 'npx skills add cesartevisual/threejs-skills --agent codex --skill threejs-web')],
 'impeccable': [('Terminal · Codex CLI', 'npx impeccable install --providers=codex --scope=project')],
 'agent-browser': [('Terminal · install CLI', 'npm install agent-browser'), ('Terminal · download browser', 'npx agent-browser install'), ('Terminal · companion skill; select your host', 'npx skills add vercel-labs/agent-browser')],
 'motion-design': [('Terminal · upstream, unpinned; select host and project scope', 'npx skills add LottieFiles/motion-design-skill')],
 'doc-coauthoring': [('Inside Claude Code · add marketplace', '/plugin marketplace add anthropics/skills'), ('Inside Claude Code · installs example collection', '/plugin install example-skills@anthropic-agent-skills')],
 'webapp-testing': [('Inside Claude Code · add marketplace', '/plugin marketplace add anthropics/skills'), ('Inside Claude Code · installs example collection', '/plugin install example-skills@anthropic-agent-skills')],
 'xlsx': [('Inside Claude Code · add marketplace', '/plugin marketplace add anthropics/skills'), ('Inside Claude Code · installs document collection', '/plugin install document-skills@anthropic-agent-skills')],
}
GLYPHS={'Codex CLI':'>_', 'Claude Code':'CC','Claude':'C','Claude Cowork':'CW','Cursor':'↗','Node/npm':'JS','Python 3.x':'Py','Browser':'◎','ui-ux-pro-max':'UI','threejs-web':'3D','impeccable':'✦','agent-browser':'◎','motion-design':'↝','xlsx':'▦','notebook-research':'N','claude-finance':'?','claude-data':'?','claude-operations':'?','claude-legal':'?','ponytail':'?','doc-coauthoring':'Aa','webapp-testing':'?','react-best-practices':'?','deepseek-harness':'D','claude-appearance':'?'}
# Original outline symbols indicate a role; they are not third-party logos.
SYMBOLS={
'ui-ux-pro-max':'<rect x="3" y="3" width="8" height="8" rx="2"/><rect x="13" y="3" width="8" height="8" rx="2"/><rect x="3" y="13" width="8" height="8" rx="2"/><path d="m14 20 6-6m-7 7 2-5 3 3"/>',
 'threejs-web':'<path d="m12 2 9 5v10l-9 5-9-5V7zM3 7l9 5 9-5M12 12v10M12 2v10"/>',
 'motion-design':'<path d="M2 12h4l3-8 6 16 3-8h4"/>',
 'claude-finance':'<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M8 6h8M8 10h2m4 0h2m-8 4h2m4 0h2m-8 4h2m4 0h2"/>',
 'claude-data':'<path d="M3 3v18h18M7 17v-5m5 5V7m5 10V4"/>',
 'claude-operations':'<rect x="2" y="3" width="7" height="6" rx="1"/><rect x="15" y="15" width="7" height="6" rx="1"/><path d="M9 6h9v6m-3-3 3 3 3-3M15 18H6v-6m-3 3 3-3 3 3"/>',
 'claude-legal':'<path d="M12 3v18M5 21h14M3 7h18M6 7l-4 8h8zm12 0-4 8h8z"/>',
 'agent-browser':'<rect x="2" y="3" width="20" height="15" rx="2"/><path d="M2 7h20M8 22h8m-4-4v4"/>',
 'impeccable':'<path d="m12 2 2 7 8 3-8 2-2 8-2-8-8-2 8-3z"/>',
 'terminal':'<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m6 9 4 3-4 3m7 0h5"/>',
 'document':'<path d="M5 2h10l4 4v16H5zM15 2v5h4M8 11h8M8 15h8M8 19h5"/>'}
def glyph(ident):
 body=SYMBOLS.get(ident,SYMBOLS['terminal'] if ident in ('Codex CLI','Claude Code','Cursor','deepseek-harness') else SYMBOLS['document'])
 return '<svg viewBox="0 0 24 24" width="25" height="25" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+body+'</svg>'
CSS='''<style>.setup-tools{margin:2rem 0;padding:clamp(1rem,3vw,2rem);border:1px solid var(--line,#d7d9cd);border-radius:20px;background:var(--surface,#fffdf6);color:var(--ink,#202824)}.setup-tool-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:1rem}.setup-tool{min-width:0;padding:1rem;border:1px solid #d7d9cd;border-radius:14px}.setup-tool h3{display:flex;gap:.7rem;align-items:center;margin-top:0;font-size:1.1rem}.tool-glyph{display:inline-grid;place-items:center;flex:0 0 38px;width:38px;height:38px;border-radius:11px;background:#e6eddb;color:#314739;font:bold 17px monospace}.tool-hosts{display:flex;gap:.5rem;flex-wrap:wrap;margin:.8rem 0}.tool-hosts span{font-size:.82rem;border:1px solid #d7d9cd;border-radius:20px;padding:.3rem .6rem}.tool-hosts b{margin-right:.3rem}.setup-command{margin:1rem 0}.setup-command label{font-size:.8rem;display:block;margin-bottom:.4rem;font-weight:650}.setup-command input{display:block;width:100%;min-width:0;padding:.7rem;border:1px solid #b7c3b1;border-radius:8px;font:13px monospace;background:#f2f5ed;color:#202824}.setup-command button{margin-top:.4rem;min-height:40px;border:1px solid #89977e;border-radius:8px;background:transparent;color:inherit;padding:.4rem .8rem;cursor:pointer}.setup-command input:focus,.setup-command button:focus-visible{outline:3px solid #829c60;outline-offset:3px}.setup-tool p{font-size:.9rem}.setup-tool-status{min-height:1.3em;font-size:.85rem}.setup-tools .small{font-size:.85rem}.setup-card .setup-tools{grid-column:1/-1;width:100%;margin:.7rem 0}.setup-card:has(.setup-tools){min-width:0}</style>'''

def badge(name):
    return '<span><b aria-hidden="true">'+glyph(name)+'</b>'+e(name)+'</span>'

def card(p, role='Selected capability'):
    ident=p['id']; blocks=[]
    for i,(label,command) in enumerate(COMMANDS.get(ident,[])):
        cid='cmd-'+ident+'-'+str(i)
        blocks.append(f'<div class="setup-command"><label for="{cid}">{e(label)}</label><input id="{cid}" readonly value="{e(command,quote=True)}" spellcheck="false" aria-label="{e(label+": "+p["name"])}"><button type="button" data-setup-copy="{cid}">Copy command</button></div>')
    if ident.startswith('claude-') and ident in ('claude-finance','claude-data','claude-operations','claude-legal'):
        blocks.append('<ol>'+''.join('<li>'+e(step)+'</li>' for step in p['setupSteps'])+'</ol><p>These are Claude menu steps. Choose the workflow in the / or + chat menu; it is not a terminal command. Availability depends on your plan and organisation.</p>')
    elif not blocks:
        blocks.append('<p>'+e(p.get('setupSteps',['Read the original setup instructions for this host.'])[0])+'</p><p>No universal terminal command is provided for this route.</p>')
    if ident=='motion-design':
        blocks.insert(0,'<p><strong>Pinned route:</strong> <a href="{{root}}install.html">Browser installer</a> or <a href="{{root}}guides/install-motion-design.html">verified ZIP and manual copy</a>. The upstream command below fetches current files and is a separate, unpinned route.</p>')
    hosts=p.get('apps',[])
    return f'<article class="setup-tool" data-setup-tool="{e(ident)}"><h3><span class="tool-glyph" aria-hidden="true">{glyph(ident)}</span>{e(p["name"])}</h3><p><strong>{e(role)}</strong></p><div class="tool-hosts">'+''.join(badge(h) for h in hosts)+'</div><p><strong>Needs:</strong> '+e(' · '.join(p.get('requirements',[])))+'</p>'+((' <details><summary>Show optional setup</summary>'+''.join(blocks)+'</details>') if role.startswith('Optional') else ''.join(blocks))+f'<p class="small"><a href="{e(p.get("setupSourceUrl",p["sourceUrl"]))}" target="_blank" rel="noopener noreferrer">Original setup instructions</a> · Reviewed {e(p["reviewedOn"])}</p></article>'

def panel(cards):
    terminal='Terminal ' in cards
    commands='data-setup-copy=' in cards
    finance=any('data-setup-tool="'+ident+'"' in cards for ident in ('claude-finance','claude-data','claude-operations','claude-legal'))
    if terminal:
        intro='Open a terminal in your project folder and copy the command for your tool. Use Node/npm in PowerShell, macOS Terminal or Linux; review the host, scope and permission prompts.'
    elif finance:
        intro='In Claude, open Customize &rarr; Plugins &rarr; Discover. Choose a plugin, then Add.'
    elif commands:
        intro='Paste these commands inside Claude Code, one at a time. Review the collection and permissions before installing.'
    else:
        intro='Follow the steps for your app, then try one small task in a practice project.'
    fallback='<p class="small">Copy unavailable? Select the command field, then use Ctrl+C or Command+C.</p>' if commands else ''
    return '<section class="setup-tools" aria-label="Tools and easy setup"><h2>Your tools, ready to set up.</h2><p>'+intro+'</p><p class="small">Source reviewed; installation and activation not reproduced.</p><div class="setup-tool-grid">'+cards+'</div><p class="setup-tool-status" role="status" aria-live="polite"></p>'+fallback+'</section>'


def enhance_setup(page, base):
    data=json.loads((base/'content/launch-library.json').read_text(encoding='utf-8-sig'))
    profiles={p['id']:p for p in data['profiles']}
    path=page['path']; chosen=[]
    if path=='guides/website-upgrades.html':chosen=[('ui-ux-pro-max','Start here · design direction'),('threejs-web','3D hero - required for the 3D route'),('impeccable','Optional · critique and polish'),('agent-browser','Optional - browser verification'),('motion-design','Optional - motion and feedback')]
    elif path in ('guides/finance-upgrades.html','guides/finance-operations.html'):chosen=[('claude-finance','Required for Finance plugin route'),('claude-data','Optional · data exploration'),('claude-operations','Optional · vendor comparisons'),('claude-legal','Optional · contract review')]
    elif path in ('guides/install-motion-design.html','guides/motion-design.html','install.html'):chosen=[('motion-design','Selected capability')]
    elif path.startswith('capabilities/') and path.split('/')[-1][:-5] in profiles:chosen=[(path.split('/')[-1][:-5],'Selected capability · match your host')]
    elif path=='guides/website-design.html':
        profiles['claude-desktop-guide']={'id':'claude-desktop-guide','name':'Claude Desktop and browser','apps':['Claude Code','Browser'],'requirements':['Eligible Claude Code access','Windows or macOS','Separate practice folder'],'setupSteps':['Install Claude Desktop from its official setup page, sign in, open the Code tab and choose your practice folder. Open the resulting index.html in your browser.'],'sourceUrl':'https://code.claude.com/docs/en/desktop','reviewedOn':'2026-11-14'}
        chosen=[('claude-desktop-guide','Required for this desktop walkthrough')]

    else:
        for ident in ('notebook-research','doc-coauthoring','xlsx','webapp-testing','deepseek-harness'):
            if profiles.get(ident,{}).get('guidePath')==path:chosen.append((ident,'Required for this workflow'))
    saved=path=='get-set-up.html'
    if not chosen and not saved:return
    templates={ident:panel(card(p)).replace('{{root}}','') for ident,p in profiles.items()}
    if chosen:
        widget=panel(''.join(card(profiles[i],role) for i,role in chosen if i in profiles))
        # Keep the commands near the start, before the long guide or setup steps.
        body=page['body']; pos=body.find('</header>')
        page['body']=body[:pos+9]+widget+body[pos+9:] if pos>=0 else widget+body
    js=r'''<script>document.addEventListener('DOMContentLoaded',()=>{document.addEventListener('click',async ev=>{const b=ev.target.closest('[data-setup-copy]');if(!b)return;const input=document.getElementById(b.dataset.setupCopy),status=b.closest('.setup-tools').querySelector('[role="status"]');try{await navigator.clipboard.writeText(input.value);status.textContent='Command copied. Review it, then paste into the app named above.';}catch{input.focus();input.select();status.textContent='Command selected. Press Ctrl+C or ⌘C to copy manually.';}});SAVED});</script>'''
    savedjs=''
    if saved:
        savedjs='const templates='+json.dumps(templates,ensure_ascii=False)+';const panel=document.getElementById("saved-setup");const decorate=()=>{panel.querySelectorAll("[data-copy-item]").forEach(b=>{const card=b.closest("article");if(card&&!card.querySelector(".setup-tools")&&templates[b.dataset.copyItem])card.insertAdjacentHTML("beforeend",templates[b.dataset.copyItem]);});};if(panel){new MutationObserver(decorate).observe(panel,{childList:true,subtree:true});decorate();}'
    page['body']+=CSS+js.replace('SAVED',savedjs)
