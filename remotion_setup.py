"""A bounded Remotion composition and source-led agent-skill setup."""
from html import escape
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROUTE = 'guides/remotion-hero-loop.html'
DATE = '2026-11-22'
FIXTURE = Path(__file__).resolve().parent / 'content/fixtures/remotion-hero'

PROMPT = '''Use the installed official Remotion skills for this project.
Make one original 3-second hero loop: 1280 x 720, 30 fps, 90 frames.
Use only React, CSS and simple shapes; no external images, fonts or audio.
Keep the headline still and readable: "Make room for a clearer idea."
Animate 3 small cards labelled Plan, Draft and Refine with subtle periodic motion.
Derive all motion from useCurrentFrame(); no CSS animation or wall-clock time.
Make the period exactly 90 frames, so the loop wraps without a visible jump.
Register a composition named HeroLoop and produce an H.264 MP4 plus frame-0 poster.
Keep text inside safe margins. Supply a static poster and user-controlled playback
for the website. Do not autoplay, publish, install unrelated tools or use paid APIs.
List the render command and verify width, height, frame rate, count and duration.
If rendering is unavailable, say so; do not claim that a valid source file is a rendered video.'''

CSS = '''<style>
.rm-guide{max-width:1000px;margin:0 auto;padding:30px 0 55px}.rm-hero{max-width:820px;margin:22px 0 30px}.rm-hero h1{font-size:clamp(38px,5.6vw,66px);line-height:1.08;margin:14px 0 22px}.rm-guide h2{font-size:29px;line-height:1.2}.rm-guide h3{font-size:21px}.rm-guide p,.rm-guide li{line-height:1.7}.rm-guide section{margin:32px 0;scroll-margin-top:25px}.rm-tools{display:grid;grid-template-columns:1fr 1fr;gap:16px}.rm-tool{padding:22px;border:1px solid var(--line,#d9ded2);border-radius:14px;background:#fffdf6;min-width:0}.rm-tool h3{display:flex;align-items:center;gap:12px;margin-top:0}.rm-tool p{font-size:14px}.rm-icon{display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;background:#e8edde;border-radius:12px;color:#36533e;flex-shrink:0}.rm-guide pre{padding:16px;background:#edf1e7;border-radius:10px;white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.7;font-size:13px}.rm-guide button{margin:0 0 12px}.rm-guide video,.rm-guide .rm-poster{display:block;width:100%;height:auto;border-radius:14px;background:#17291f}.rm-note{padding:18px 22px;background:#edf2e8;border-left:4px solid #687d49;border-radius:0 12px 12px 0}.rm-facts{display:flex;flex-wrap:wrap;gap:10px 20px;font-size:14px;color:var(--muted,#566156)}.rm-guide summary{cursor:pointer;font-weight:650}.rm-guide a:focus-visible,.rm-guide button:focus-visible{outline:3px solid #819858;outline-offset:4px}@media(max-width:700px){.rm-tools{grid-template-columns:1fr}.rm-guide{padding-top:18px}.rm-guide h2{font-size:26px}}
</style>'''


def link(url, title):
    return '<a href="'+escape(url, quote=True)+'" target="_blank" rel="noopener noreferrer">'+escape(title)+'</a>'


def command(ident, text, label='Copy command'):
    return '<pre><code id="'+ident+'">'+escape(text)+'</code></pre><button class="button secondary" type="button" data-copy-target="'+ident+'">'+label+'</button>'


def add_remotion_setup(pages):
    evidence_path = FIXTURE / 'render-evidence.json'
    evidence = json.loads(evidence_path.read_text(encoding='utf-8')) if evidence_path.exists() else {}
    if evidence.get('renderPassed') is True and not all((FIXTURE / name).is_file() for name in ('hero-loop.mp4', 'hero-loop-poster.png')):
        raise ValueError('Remotion evidence claims a render but public media is missing')
    rendered = evidence.get('renderPassed') is True and all((FIXTURE / name).is_file() for name in ('hero-loop.mp4', 'hero-loop-poster.png'))
    media = ('<video controls loop muted playsinline preload="none" poster="{{root}}assets/remotion/hero-loop-poster.png" width="1280" height="720" aria-label="Original three-second hero graphic with gently moving Plan, Draft and Refine cards"><source src="{{root}}assets/remotion/hero-loop.mp4" type="video/mp4">Download the sample using the link below.</video><p><a href="{{root}}assets/remotion/hero-loop.mp4" download>Download the sample MP4</a> · <a href="{{root}}assets/remotion/hero-loop-poster.png" download>Download static poster</a></p>' if rendered else '<p class="rm-note">Download the source below and render the practice composition locally. No rendered sample is available in this build.</p>')
    measured = ('<p><strong>Rendered example:</strong> the supplied composition was rendered with Remotion '+escape(str(evidence.get('remotionVersion', '')))+' on '+DATE+'. Metadata check: 1280 × 720, 30 fps, 90 frames, 3.000 seconds, H.264, no audio. The MP4 is '+escape(str(evidence.get('bytes', '')))+' bytes. This verifies the example render, not native agent installation or a measured skill improvement.</p>' if rendered else '<p>The source specifies 90 frames at 30 fps. A completed local render and metadata check are required before reporting a successful video export.</p>')
    film = '<svg viewBox="0 0 24 24" width="25" height="25" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m10 8 6 4-6 4zM6 4v16m12-16v16"/></svg>'
    terminal = '<svg viewBox="0 0 24 24" width="25" height="25" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m6 9 4 3-4 3m7 0h5"/></svg>'
    body = CSS + '''<article class="rm-guide"><a href="{{root}}guides.html">← All guides</a><header class="rm-hero"><p class="eyebrow">Motion · A small, repeatable project</p><h1>Make a three-second hero loop with Remotion.</h1><p class="lede">Use official Agent Skills in Codex or Claude Code to create a short website graphic. Start from a real composition you can inspect, render and adapt.</p><p><a href="{{root}}capabilities/remotion-agent-skills.html">Explore Remotion Agent Skills →</a></p></header>
<div class="rm-facts"><span>1280 × 720</span><span>30 fps · 90 frames</span><span>No external media or audio</span><span>Play the example below</span></div>'''+media+'''
<section id="setup"><h2>1. Choose your starting point</h2><div class="rm-tools"><article class="rm-tool"><h3><span class="rm-icon">'''+film+'''</span>Remotion</h3><p>The React-based project and renderer produce the actual video. You need Node.js/npm and a browser runtime; the first render can download one.</p>'''+link('https://www.remotion.dev/docs', 'Official getting started guide')+'''</article><article class="rm-tool"><h3><span class="rm-icon">'''+terminal+'''</span>Codex or Claude Code</h3><p>Your existing coding agent reads the Remotion skills and edits the composition. Skills supply instructions; they do not install an agent or replace the renderer.</p>'''+link('https://www.remotion.dev/docs/ai/skills', 'Official skills and supported agents')+'''</article></div>
<p><strong>New to Remotion?</strong> In a parent folder outside an existing Git repository, create a blank project. Follow its installation prompts, then open the new folder in your coding agent.</p>'''+command('rm-create', 'npx create-video@latest --yes --blank hero-loop')+command('rm-open', 'cd hero-loop')+'''
<p><strong>Already have a Remotion project?</strong> Skip scaffolding. In its project folder, add the official skills:</p>'''+command('rm-skills', 'npx remotion skills add')+'''
<p>Follow the installer’s prompts to select <strong>Codex</strong> or <strong>Claude Code</strong> and the project scope. Review the selected destination before confirming. If Remotion is not yet installed, the documented alternative is:</p>'''+command('rm-skills-alternative', 'npx skills add remotion-dev/skills')+'''
<p>Choose one installation route. These commands fetch current upstream files. In PowerShell, use <code>npx.cmd</code> if script execution policy blocks <code>npx</code>. Select a relevant skill from your host’s menu, or explicitly ask it to use the installed Remotion skills. Exact invocation depends on the host.</p></section>
<section id="brief"><h2>2. Give the agent a bounded brief</h2><p>Paste this in your project’s agent session. It asks for a decorative website asset with a readable still state.</p>'''+command('rm-brief', PROMPT, 'Copy project brief')+'''
<p>Begin with the umbrella skill <code>remotion-best-practices</code> when unsure which specific skill to use. Review the generated composition before running it.</p></section>
<section id="example"><h2>3. Run the supplied example</h2><p>Want a known starting point? The source download contains our original composition and a small package manifest. Extract it to a new folder, open a terminal there, then install dependencies and render. It is separate from the agent-skill installation above.</p><p><a class="button" href="{{root}}downloads/remotion-hero-source.zip" download>Download example source</a></p>'''+command('rm-example-install', 'npm install')+command('rm-example-render', 'npm run render')+command('rm-example-poster', 'npm run poster')+'''
<details><summary>Use the composition in an existing project</summary><p>Copy the downloaded <code>index.tsx</code> to <code>src/hero-loop.tsx</code> without replacing your existing entry file. It registers its own root. Render it directly:</p>'''+command('rm-render-existing', 'npx remotion render src/hero-loop.tsx HeroLoop out/hero-loop.mp4 --codec=h264')+'''</details>
<p>The example keeps its headline static while three cards move with a sine/cosine phase derived from the frame number. Its phase repeats every 90 frames; the hypothetical frame 90 matches frame 0. Frame 89 should flow into frame 0, not duplicate it.</p></section>
<section id="verify"><h2>4. Verify the export and the loop</h2>'''+measured+'''
<ol><li><strong>Probe the output:</strong> if FFprobe is installed, run the command below. Expect 1280 × 720, <code>30/1</code> frame rate, <code>90</code> frames and <code>3.000000</code> seconds.</li><li><strong>Watch several cycles:</strong> inspect the wrap from the last frame to the first. Check that the static headline stays readable and no shape jumps or clips.</li><li><strong>Check the website:</strong> use a poster and visible playback controls. Retain a static alternative for people who prefer reduced motion; this sample never starts automatically.</li><li><strong>Check delivery size:</strong> choose an encoding and resolution appropriate to your page. A short clip can still hurt load time; do not preload a decorative video unnecessarily.</li></ol>'''+command('rm-probe', 'ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_read_frames:format=duration -of json hero-loop.mp4')+'''
<p><strong>If rendering fails:</strong> read the actual error first. Common blockers include missing project dependencies and the initial browser download. A successful source edit is not a successful render. Keep Remotion package versions aligned.</p>
<p><strong>Before commercial use:</strong> check Remotion’s current license eligibility and terms for your organisation and version. Agent access, rendering infrastructure and any external media can have separate costs. This source uses only original text and simple shapes.</p></section>
<section id="sources"><details><summary>Sources and scope · reviewed '''+DATE+'''</summary><p>Official source review and one bounded example. Native Codex/Claude Code skill installation and any improvement over an unassisted agent were not tested.</p><ul><li>'''+link('https://www.remotion.dev/docs/ai/skills', 'Remotion: official Agent Skills setup')+'''</li><li>'''+link('https://www.remotion.dev/docs/cli/create-video', 'Remotion: create-video scaffold')+'''</li><li>'''+link('https://www.remotion.dev/docs/cli/render', 'Remotion: render command')+' · '+link('https://www.remotion.dev/docs/idea', 'Frames, dimensions and frame rate')+'''</li><li>'''+link('https://www.remotion.dev/docs/license/pricing', 'License eligibility and pricing')+' · '+link('https://www.remotion.dev/docs/terms-4-0', 'Terms for Remotion 4.0')+'''</li></ul><p><a href="{{root}}downloads/remotion-render-evidence.json">Inspect the example’s recorded render evidence</a></p></details></section></article>'''
    pages[ROUTE] = dict(path=ROUTE, title='Remotion Agent Skills setup: a three-second hero loop', description='Install official Remotion skills for Codex or Claude Code, render a small original hero loop, and verify the 90-frame export.', body=body, activeNav='guides')


def write_remotion_assets(base, dist):
    """Copy only the explicitly public example artifacts; never dependencies."""
    fixture = Path(base) / 'content/fixtures/remotion-hero'
    evidence = fixture / 'render-evidence.json'
    if not evidence.is_file():
        raise ValueError('Remotion render evidence is missing')
    record = json.loads(evidence.read_text(encoding='utf-8'))
    if record.get('renderPassed') is True:
        for name in ('hero-loop.mp4', 'hero-loop-poster.png', 'index.tsx'):
            if not (fixture / name).is_file():
                raise ValueError('Remotion render evidence artifact is missing: '+name)
        media_bytes = (fixture / 'hero-loop.mp4').read_bytes()
        if len(media_bytes) != record.get('bytes') or hashlib.sha256(media_bytes).hexdigest() != record.get('sha256'):
            raise ValueError('Remotion MP4 does not match recorded bytes and SHA-256')
        if hashlib.sha256((fixture / 'index.tsx').read_bytes()).hexdigest() != record.get('sourceSha256'):
            raise ValueError('Remotion source does not match recorded SHA-256')
    dist = Path(dist)
    download = dist / 'downloads'
    download.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(download / 'remotion-hero-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in ('index.tsx', 'package.json', 'README.md'):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 22, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (fixture / name).read_bytes())
    for name in ('hero-loop.mp4', 'hero-loop-poster.png'):
        source = fixture / name
        if source.is_file():
            target = dist / 'assets/remotion' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    shutil.copyfile(evidence, download / 'remotion-render-evidence.json')
