"""Build Pages output in isolation; never rewrite the ordinary private dist."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit


def clean_url(url):
    return url.replace('/index.html', '/').removesuffix('.html')


def prepare_pages(dist, routes, origin):
    """Align SEO URLs and shortlist return navigation with Pages clean routes."""
    for route in routes:
        path = dist / route
        html = path.read_text(encoding='utf-8')
        html = re.sub(r'(?<="' + re.escape(origin) + r')/[^"<>]*',
                      lambda match: clean_url(origin + match.group())[len(origin):], html)
        path.write_text(html, encoding='utf-8')
    sitemap = dist / 'sitemap.xml'
    if sitemap.exists():
        sitemap.write_text(re.sub(r'<loc>(.*?)</loc>',
                                 lambda match: '<loc>' + clean_url(match[1]) + '</loc>',
                                 sitemap.read_text(encoding='utf-8')), encoding='utf-8')
    js = dist / 'assets/discovery.js'
    old = r'/^(index|skills)\.html(\?|$)/'
    new = r'/^(?:(?:index|skills)(?:\.html)?|)(\?|$)/'
    text = js.read_text(encoding='utf-8')
    if old not in text:
        raise ValueError('Discovery return-route expression changed; review Pages adaptation')
    js.write_text(text.replace(old, new), encoding='utf-8')


def require_production_origin():
    """Prevent the public Workers main build from silently becoming private."""
    if (os.environ.get('WORKERS_CI') == '1' and
            os.environ.get('WORKERS_CI_BRANCH') == 'main' and
            not os.environ.get('SKILLLANTERN_PUBLIC_ORIGIN', '').strip()):
        raise ValueError(
            'Production Workers main build requires SKILLLANTERN_PUBLIC_ORIGIN. '
            'Set this build variable to the existing public HTTPS origin in '
            'Cloudflare Workers build settings, then rebuild.')


def main():
    require_production_origin()
    base = Path(__file__).resolve().parent
    output = base / 'pages-dist'
    with tempfile.TemporaryDirectory(prefix='skilllantern-pages-') as temporary:
        source = Path(temporary) / 'source'
        shutil.copytree(base, source, ignore=shutil.ignore_patterns(
            '.git', 'pages-dist', '__pycache__', '*.pyc'))
        subprocess.run([sys.executable, 'build.py'], cwd=source, check=True)
        routes = json.loads((source / 'page-manifest.json').read_text(encoding='utf-8'))
        origin = os.environ.get('SKILLLANTERN_PUBLIC_ORIGIN', '').rstrip('/')
        if not origin and os.environ.get('CF_PAGES') and not os.environ.get('CF_PAGES_URL'):
            raise ValueError('Cloudflare preview requires CF_PAGES_URL or an explicit public origin')
        preview_origin = os.environ.get('CF_PAGES_URL', '').rstrip('/')
        private_origin = 'https://skilllantern.happymoth22.chatgpt.site'
        if not origin and preview_origin:
            parsed = urlsplit(preview_origin)
            if (parsed.scheme != 'https' or not parsed.netloc or parsed.path or
                    parsed.query or parsed.fragment or parsed.username or parsed.password):
                raise ValueError('CF_PAGES_URL must be an HTTPS origin')
            for route in routes:
                page = source / 'dist' / route
                page.write_text(page.read_text(encoding='utf-8').replace(
                    private_origin, preview_origin), encoding='utf-8')
        origin = origin or preview_origin or private_origin
        prepare_pages(source / 'dist', routes, origin)
        if output.exists():
            shutil.rmtree(output)
        shutil.copytree(source / 'dist', output)
        print(f'Pages output: {output}; authored routes: {len(routes)}')


if __name__ == '__main__':
    main()
