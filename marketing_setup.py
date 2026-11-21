"""Source-reviewed marketing workflow; no installed-plugin or campaign-result claim."""
from html import escape

DATE = '2026-11-22'
ROUTE = 'guides/marketing-launch-campaign.html'
REPO = 'https://github.com/anthropics/knowledge-work-plugins/tree/main/marketing'
HELP = 'https://support.claude.com/en/articles/13837440-use-plugins-in-claude'

BRIEF = '''PRACTICE EXAMPLE — fictional product, no real customer data.
Product: Desk Reset, a printable weekly planning pack for independent designers.
Approved facts: 6 PDF pages; A4 and US Letter; English; printable at home.
Offer: proposed price USD 9. Sale date, checkout, refund policy and seller
identity are NOT confirmed. Use [CHECKOUT LINK] and [LAUNCH DATE] placeholders.
Audience hypothesis: independent designers who want to plan client work on paper.
Proof: no customers, testimonials, savings studies or conversion history.
Voice: clear, calm, specific. Avoid "best", "guaranteed", "transform your life".
Goal: propose a 14-day launch draft. Planning target: 20 qualified waitlist
signups; this is a target, not a forecast or an observed result.
Resources: one person, 4 hours total, USD 0 incremental campaign spend.
Channels: existing Instagram account and a proposed landing page only.
CTA: Join the waitlist at [WAITLIST LINK]. Form and consent flow need testing.
Produce: one-page plan, 3 Instagram captions, landing-page hero and FAQ,
and a claims/unknowns checklist. Give each task an owner and minute estimate.
Ask about missing blockers. Mark assumptions. Do not invent facts or research.
Draft only: do not publish, connect accounts, send messages or buy anything.'''

DRAFT_PROMPT = '''Use the approved practice brief and campaign plan above.
Draft 3 Instagram captions, each no more than 90 words, plus a landing-page
headline, subheadline, primary CTA and 3 FAQ answers.
Keep the price explicitly proposed. Preserve all unresolved placeholders.
For every factual claim, identify the supporting line in the brief.
Omit testimonials, performance statistics and false scarcity.
If a required fact is missing, ask or leave a clearly labelled placeholder.
Finish with a list of decisions needed before publication.'''

REVIEW_PROMPT = '''Review the drafts against the practice brief and its voice rules.
Flag unsupported claims, invented dates, price presented as final, hidden
assumptions and any action that exceeds the 4-hour / USD 0 campaign limit.
For every issue, quote the draft, explain the problem and propose a correction.
Do not treat the planning target as a result or predict conversions.
Return a corrected draft and an unresolved-decision checklist.'''

CSS = '''<style>
.mk-guide{max-width:1000px;margin:0 auto;padding:30px 0 55px}.mk-hero{max-width:800px;margin:24px 0 32px}.mk-hero h1{font-size:clamp(38px,5.6vw,66px);line-height:1.08;margin:14px 0 22px}.mk-guide h2{font-size:29px;line-height:1.2;margin:0 0 16px}.mk-guide h3{font-size:21px;line-height:1.3}.mk-guide p,.mk-guide li{line-height:1.7}.mk-meta{font-size:13px;color:var(--muted,#566156)}.mk-guide section{margin:32px 0;padding-top:12px;scroll-margin-top:30px}.mk-note{background:#edf2e8;border-left:4px solid #687d49;padding:17px 22px;border-radius:0 12px 12px 0}.mk-toc{display:flex;flex-wrap:wrap;gap:10px 22px;padding:18px 0;border-top:1px solid var(--line,#d9ded2);border-bottom:1px solid var(--line,#d9ded2)}.mk-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.mk-card{min-width:0;padding:22px;border:1px solid var(--line,#d9ded2);border-radius:14px;background:#fffdf6}.mk-icon{display:inline-grid;place-items:center;width:44px;height:44px;border-radius:12px;background:#e8edde;color:#36533e}.mk-card p{font-size:14px}.mk-card h3{margin:16px 0 10px}.mk-guide textarea{display:block;box-sizing:border-box;width:100%;padding:16px;border:1px solid #a8b49c;border-radius:12px;background:#f5f7f0;color:#202824;font:13px/1.65 ui-monospace,monospace;resize:vertical}.mk-guide label{display:block;font-weight:650;margin:18px 0 8px}.mk-guide button{margin:8px 0 16px}.mk-guide summary{cursor:pointer;font-weight:650}.mk-guide pre{max-width:100%;overflow-x:auto;padding:16px;border-radius:10px;background:#edf1e7;line-height:1.8}.mk-table-wrap{overflow-x:auto}.mk-guide table{width:100%;border-collapse:collapse;text-align:left}.mk-guide th,.mk-guide td{padding:14px;border-bottom:1px solid var(--line,#d9ded2);vertical-align:top;line-height:1.6}.mk-guide th{background:#edf1e7}.mk-guide caption{text-align:left;font-weight:650;margin-bottom:12px}.mk-sources{font-size:14px}.mk-guide a:focus-visible,.mk-guide textarea:focus-visible{outline:3px solid #819858;outline-offset:4px}@media(max-width:700px){.mk-grid{grid-template-columns:1fr}.mk-guide{padding-top:18px}.mk-guide h2{font-size:26px}.mk-card{padding:19px}}
</style>'''


def link(url, text):
    return '<a href="'+escape(url, quote=True)+'" target="_blank" rel="noopener noreferrer">'+escape(text)+'</a>'


def text_box(ident, label, value, rows):
    return ('<label for="'+ident+'">'+escape(label)+'</label><textarea id="'+ident+
            '" readonly rows="'+str(rows)+'" spellcheck="false">'+escape(value)+'</textarea><button class="button secondary" type="button" data-copy-target="'+ident+'">Copy '+escape(label.lower())+'</button>')


def skill_card(slug, title, body, icon):
    svg = '<svg viewBox="0 0 24 24" width="25" height="25" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+icon+'</svg>'
    return ('<article class="mk-card"><span class="mk-icon" aria-hidden="true">'+svg+
            '</span><h3>'+title+'</h3><p>'+body+'</p>'+link(REPO.replace('/tree/', '/blob/')+'/skills/'+slug+'/SKILL.md', 'Read the original skill')+'</article>')


def add_marketing_setup(pages):
    cards = ''.join([
        skill_card('campaign-plan', '1. Campaign Plan', 'Turn one brief into an audience, message, channel plan and calendar. Useful when a launch needs a manageable sequence of decisions.', '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 10h18m-13 5 3 3 5-5"/>'),
        skill_card('draft-content', '2. Draft Content', 'Adapt the approved message into specific formats. Supply the channel, audience, tone and length so the draft has clear boundaries.', '<path d="M4 3h12l4 4v14H4zM16 3v5h4M8 12h8m-8 4h5"/>'),
        skill_card('brand-review', '3. Brand Review', 'Check the draft against your voice and approved claims. Ask for concrete corrections; a clean AI review still needs your own fact check.', '<path d="M12 2 21 6v6c0 5-9 10-9 10S3 17 3 12V6zM8 12l3 3 5-6"/>'),
    ])
    body = CSS + '''<article class="mk-guide">
<a href="{{root}}guides.html">← All guides</a>
<header class="mk-hero"><p class="eyebrow">Marketing · No coding required</p><h1>Turn a product brief into a launch campaign.</h1><p class="lede">Plan the work, draft the assets, then check the claims with Anthropic’s Marketing plugin. Start with a small practice brief before giving it your real launch.</p><p class="mk-meta">Source reviewed '''+DATE+''' · Claude web / Cowork · Optional Claude Code route</p></header>
<p><a href="{{root}}capabilities/claude-marketing.html">Explore the Marketing plugin &rarr;</a></p>
<nav class="mk-toc" aria-label="Guide sections"><a href="#setup">Set it up</a><a href="#skills">Choose the skills</a><a href="#practice">Try the brief</a><a href="#check">Check the result</a><a href="#sources">Sources</a></nav>
<section id="setup"><h2>Set it up in Claude</h2><p>You need a paid Claude plan with plugins available. Organisation settings can restrict installation. The basic practice run uses pasted text; it needs no CRM, mailing list or design account.</p>
<ol><li>Open Claude on the web or in the desktop app. For Cowork, open the Cowork tab first.</li><li>Open <strong>Customize → Plugins → Discover</strong>.</li><li>Find <strong>Marketing by Anthropic</strong> and select <strong>Add</strong>. Check the publisher and included connections before continuing.</li><li>In a new conversation, type <strong>/</strong> or open <strong>+</strong> to find its skills. In Cowork, you can also use <code>/marketing:campaign-plan</code>, <code>/marketing:draft-content</code> and <code>/marketing:brand-review</code>.</li></ol>
<p>''' + link('https://claude.com/marketplace/plugins/marketing', 'Official Marketing listing')+' · '+link(HELP, 'Official plugin installation help')+'''</p>
<p><strong>If it is missing:</strong> confirm that plugins are enabled for your account and organisation. Use the menu’s actual command names. Do not paste a terminal install command into ordinary Claude chat.</p>
<details><summary>Already use Claude Code? Optional terminal setup</summary><p>With Claude Code already installed and authenticated, run these upstream commands in your terminal, one at a time. They fetch the current marketplace version.</p><pre><code id="marketing-install-market">claude plugin marketplace add anthropics/knowledge-work-plugins</code></pre><button class="button secondary" type="button" data-copy-target="marketing-install-market">Copy marketplace command</button><pre><code id="marketing-install-plugin">claude plugin install marketing@knowledge-work-plugins</code></pre><button class="button secondary" type="button" data-copy-target="marketing-install-plugin">Copy install command</button><p>''' + link(REPO+'#installation', 'Upstream installation instructions')+'''</p></details>
<p>Start with pasted text and leave external services disconnected. Add a connector only when a real task needs it; service accounts, permissions and fees are separate.</p></section>
<section id="skills"><h2>Three skills, one working sequence</h2><p>A plugin is the installable bundle. These skills are the task instructions inside it; you do not need three separate installations.</p><div class="mk-grid">'''+cards+'''</div><p class="mk-meta">The current source files use the names above. Some upstream overview text still uses broader labels such as “campaign planning” and “brand voice.” Follow the installed menu and linked files.</p></section>
<section id="practice"><h2>Try a fictional launch before your own</h2><p>This example is a proposed exercise, not a real product or a reported result. Replace it with approved product facts later. Keep customer data and confidential commercial details out of the practice run.</p><p>Use the Copy buttons, or select text and copy with Ctrl+C or Command+C. In Claude, choose the named skill, then paste the corresponding input.</p>
<details open><summary>Practice brief and prompts</summary><h3>1. Plan a launch that fits the resources</h3><p>Choose <strong>Campaign Plan</strong>. Paste this brief and ask for the requested deliverables. If it asks a useful clarification, answer it before approving the plan.</p>'''+text_box('marketing-brief', 'Practice brief', BRIEF, 10)+'''
<h3>2. Draft only the approved assets</h3><p>Choose <strong>Draft Content</strong> in the same conversation. Keep the brief and approved plan in context; paste them again if you start a fresh conversation.</p>'''+text_box('marketing-draft', 'Drafting prompt', DRAFT_PROMPT, 7)+'''
<h3>3. Review the claims and voice</h3><p>Choose <strong>Brand Review</strong> and provide the original brief plus the generated drafts. Pasting the voice rules makes this exercise work without editing plugin configuration files.</p>'''+text_box('marketing-review', 'Review prompt', REVIEW_PROMPT, 6)+'''
</details><aside class="mk-note"><strong>Example copy:</strong> “Make space for next week’s client work. Desk Reset is a six-page printable planning pack in A4 and US Letter. Join the waitlist at [WAITLIST LINK].” This illustrates the intended result.</aside></section>
<section id="check"><h2>Check the result before you use it</h2><p>Run this acceptance check yourself. Passing means the draft fits this brief; it does not establish demand, conversion lift or launch readiness.</p><div class="mk-table-wrap"><table><caption>Practice acceptance checks — expected behaviour, not recorded test results</caption><thead><tr><th scope="col">Check</th><th scope="col">What passes</th></tr></thead><tbody>
<tr><th scope="row">Facts stay intact</th><td>Six PDF pages, both paper sizes and English remain accurate. Every factual statement maps to the brief.</td></tr>
<tr><th scope="row">Unknowns stay visible</th><td>Date, checkout and waitlist URL remain labelled placeholders; USD 9 stays proposed.</td></tr>
<tr><th scope="row">Work fits capacity</th><td>Task estimates total no more than 240 minutes. No paid channels or new subscriptions appear.</td></tr>
<tr><th scope="row">No invented proof</th><td>No testimonials, user counts, “proven” results or urgency claims. The signup target is labelled a target.</td></tr>
<tr><th scope="row">Assets are usable</th><td>Three captions meet the requested word limit. Hero and FAQs share one consistent waitlist action.</td></tr>
<tr><th scope="row">Review catches an error</th><td>In a separate practice copy, add “Guaranteed to save five hours every week.” Brand Review should flag the missing evidence and remove or qualify it. If it misses this, correct it yourself and strengthen the review prompt.</td></tr>
</tbody></table></div>
<p><strong>Before publication:</strong> confirm the actual seller, final offer, date and policies; replace and test links; inspect the landing page and form on a phone; verify consent wording and signup recording. A generated plan is a draft handoff. Approve publishing and any account actions separately.</p>
<p><strong>Where this setup stops:</strong> it does not supply customer research, establish that Instagram is the right channel or verify demand. Treat audience and channel choices as hypotheses. Use actual audience feedback and signups to decide what to change next.</p></section>
<section id="sources" class="mk-sources"><details><summary>Sources and scope</summary><p>Primary sources checked '''+DATE+'''. Official source review only; native installation, campaign outcomes and comparative effectiveness were not tested. The practice example and checks are editorial material.</p><ul>
<li>'''+link(HELP, 'Anthropic help: plugin availability, installation and invocation')+'''</li>
<li>'''+link('https://claude.com/marketplace/plugins/marketing', 'Anthropic Marketplace: Marketing plugin')+'''</li>
<li>'''+link(REPO, 'Anthropic repository: plugin setup and integrations')+'''</li>
<li>'''+link(REPO.replace('/tree/', '/blob/')+'/skills/campaign-plan/SKILL.md', 'Campaign Plan instructions')+' · '+link(REPO.replace('/tree/', '/blob/')+'/skills/draft-content/SKILL.md', 'Draft Content instructions')+' · '+link(REPO.replace('/tree/', '/blob/')+'/skills/brand-review/SKILL.md', 'Brand Review instructions')+'''</li></ul>
<p>Need just a short caption? Start with an ordinary prompt and the same factual brief. The plugin is most useful here when you want the repeatable plan → draft → review sequence.</p></details></section></article>'''
    pages[ROUTE] = dict(path=ROUTE, title='AI marketing setup: brief to launch campaign',
                        description='Set up Anthropic’s Marketing plugin in Claude, try a realistic practice brief, and check your campaign draft before publishing.',
                        body=body, activeNav='guides')
