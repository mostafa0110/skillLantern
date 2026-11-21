"""Render source-led launch guides from the shared content library."""
from html import escape
import json
from pathlib import Path


def load_release_content(base):
    return json.loads((Path(base) / 'content' / 'launch-library.json').read_text(encoding='utf-8'))


def render_guide(guide):
    e = escape
    parts = [f'<header class="page-intro"><p class="eyebrow">{e(guide["category"])} · Practical guide</p>'
             f'<h1>{e(guide["title"])}</h1><p class="lede">{e(guide["description"])}</p></header>',
             '<article class="prose">', f'<p>{e(guide["intro"])}</p>',
             '<p><strong>Before you start:</strong> ' + e('; '.join(guide['requirements'])) + '.</p>']
    for i, section in enumerate(guide['sections']):
        parts.append(f'<section><h2>{e(section["title"])}</h2>')
        if 'html' in section:
            parts.append(section['html'])
        if 'prompt' in section:
            target = Path(guide['path']).stem + '-prompt-' + str(i)
            parts.append(f'<button type="button" class="copy-button" data-copy-target="{target}">Copy prompt</button>'
                         f'<pre class="code-block"><code id="{target}">{e(section["prompt"])}</code></pre>')
        parts.append('</section>')
    parts.append(f'<details><summary>Sources and review coverage · {e(guide["checkedOn"])}</summary><ul>')
    for source in guide['sources']:
        parts.append(f'<li><a href="{e(source["url"], quote=True)}">{e(source["label"])}</a></li>')
    parts.append(f'</ul><p>{e(guide["evidence"])}</p></details></article>')
    return ''.join(parts)
