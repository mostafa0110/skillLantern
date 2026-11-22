/* Direct GA4: no external requests until an explicit, saved opt-in. */
(() => {
  'use strict';
  const script = document.currentScript;
  const origin = 'https://skilllantern.app';
  const id = 'G-ZYTQ6DMP0T';
  const key = 'skilllantern.analytics.v1';
  const page = script?.dataset.page;
  const pageTitle = script?.dataset.pageTitle || 'SkillLantern';
  const normalize = path => path.replace(/\.html$/, '').replace(/\/index$/, '/') .replace(/\/$/, '') || '/';
  if (location.origin !== origin || !page || normalize(location.pathname) !== normalize(page)) return;
  const safeURL = value => {
    if (!value) return true;
    try { const url = new URL(value); return /^https?:$/.test(url.protocol) && !url.search && !url.hash && !url.username && !url.password; }
    catch { return false; }
  };
  // Google can inspect the actual URL independently of event overrides. Never
  // load it on query/unsafe-fragment pages or with query/hash-bearing referrers.
  const safeHash = () => !location.hash || (/^#[a-z][a-z0-9-]{0,63}$/.test(location.hash) && !!document.getElementById(location.hash.slice(1)));
  const safeContext = () => !location.search && safeHash() && safeURL(document.referrer);
  // Discovery and editing pages can change URLs after load or contain free text.
  // Keep the Google library entirely off those pages, including saved opt-ins.
  const interactive = document.querySelector('textarea:not([readonly]), form, [contenteditable]:not([contenteditable=false]), input:not([readonly]):not([type=checkbox]):not([type=radio]):not([type=button]):not([type=submit])');
  const excludedRoute = /^\/(?:index|skills|setup|setup-help|get-set-up|popular|best-skills)?$/.test(page);
  const eligible = !interactive && !excludedRoute;
  let storageAvailable = true;
  const validChoice = value => ['allow', 'decline'].includes(value) ? value : null;
  function readChoice() {
    try { return validChoice(localStorage.getItem(key)); }
    catch { storageAvailable = false; return null; }
  }
  let choice = readChoice();
  let openedFromFooter = false;
  function restoreFocus() {
    if (openedFromFooter) document.getElementById('analytics-settings')?.focus({preventScroll: true});
    openedFromFooter = false;
  }
  let loaded = false;
  let sentPage = false;
  window['ga-disable-' + id] = choice !== 'allow';
  const panel = document.createElement('section');
  panel.className = 'analytics-choice';
  panel.id = 'analytics-choice';
  panel.setAttribute('aria-label', 'Optional analytics');
  panel.innerHTML = '<h2>Optional analytics</h2><p>Allow Google Analytics cookies to count visits and guide actions? Search text, URL parameters and copied content are excluded.</p><p class="analytics-status" role="status"></p><div class="analytics-actions"><button type="button" data-choice="allow">Allow analytics</button><button type="button" data-choice="decline">Decline analytics</button><button type="button" data-close>Close settings</button></div>';
  document.body.append(panel);
  const status = panel.querySelector('.analytics-status');
  const close = panel.querySelector('[data-close]');
  function render(open = !choice) {
    panel.hidden = !open;
    document.getElementById('analytics-settings')?.setAttribute('aria-expanded', String(open));
    close.hidden = !choice;
    const saved = storageAvailable ? 'Saved choice' : 'Choice for this page only';
    status.textContent = choice === 'allow' ? saved + ': allowed. Search, editing pages and unsafe URLs are not measured.' : choice === 'decline' ? saved + ': declined. Analytics is off.' : 'Analytics is off until you allow it. ' + (storageAvailable ? 'Your choice is saved on this browser.' : 'Browser storage is unavailable; your choice applies to this page only.');
  }
  function clearCookies() {
    const names = document.cookie.split(';').map(part => part.trim().split('=')[0]).filter(name => /^_ga(?:_|$)|^_gid$|^_gat(?:_|$)/.test(name));
    const paths = new Set(['/']);
    const parts = location.pathname.split('/');
    while (parts.length > 1) { paths.add(parts.join('/') || '/'); parts.pop(); }
    for (const name of names) for (const path of paths) for (const domain of ['', '; Domain=skilllantern.app', '; Domain=.skilllantern.app']) {
      document.cookie = name + '=; Max-Age=0; Path=' + path + domain + '; SameSite=Lax; Secure';
    }
  }
  function start() {
    if (choice !== 'allow' || !eligible || !safeContext() || loaded) return;
    loaded = true;
    window['ga-disable-' + id] = false;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    gtag('consent', 'default', {analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied'});
    gtag('consent', 'update', {analytics_storage: 'granted'});
    gtag('js', new Date());
    // Stream Enhanced Measurement must also be disabled in the GA console.
    gtag('config', id, {send_page_view: false, allow_google_signals: false, allow_ad_personalization_signals: false, page_location: origin + page, page_referrer: '', page_title: pageTitle});
    const tag = document.createElement('script');
    tag.async = true;
    tag.referrerPolicy = 'no-referrer';
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.append(tag);
    if (!sentPage) {
      sentPage = true;
      let referrer = '';
      if (document.referrer) { const url = new URL(document.referrer); if (url.origin !== origin) referrer = url.origin + '/'; }
      gtag('event', 'page_view', {page_location: origin + page, page_referrer: referrer, page_title: pageTitle});
    }
  }
  panel.addEventListener('click', event => {
    const button = event.target.closest('button');
    if (!button) return;
    if (button.hasAttribute('data-close')) { render(false); restoreFocus(); return; }
    const next = button.dataset.choice;
    if (!['allow', 'decline'].includes(next)) return;
    choice = next;
    try { localStorage.setItem(key, choice); storageAvailable = true; } catch { storageAvailable = false; /* choice remains in memory */ }
    if (choice === 'decline') {
      window['ga-disable-' + id] = true;
      clearCookies();
      // Reload unloads tag timers/listeners too; disable takes effect immediately.
      if (loaded) { location.reload(); return; }
    } else start();
    render(false);
    restoreFocus();
  });
  document.getElementById('analytics-settings')?.addEventListener('click', () => {
    openedFromFooter = true;
    render(true);
    panel.querySelector('button').focus({preventScroll: true});
  });
  function synchronize(next) {
    choice = next;
    if (choice !== 'allow') {
      window['ga-disable-' + id] = true;
      clearCookies();
      if (loaded) { location.reload(); return; }
    } else {
      window['ga-disable-' + id] = false;
      start();
    }
    render();
  }
  window.addEventListener('storage', event => {
    if (event.key === key || event.key === null) {
      storageAvailable = true;
      synchronize(event.key === null ? null : validChoice(event.newValue));
    }
  });
  // A cached document may have missed a cross-tab revocation while suspended.
  window.addEventListener('pagehide', event => { if (event.persisted) window['ga-disable-' + id] = true; });
  window.addEventListener('pageshow', event => {
    if (!event.persisted) return;
    if (storageAvailable) {
      const saved = readChoice();
      if (storageAvailable) { synchronize(saved); return; }
    }
    // Blocked storage must preserve the visitor's in-memory choice.
    window['ga-disable-' + id] = choice !== 'allow';
  });
  document.addEventListener('skilllantern:guide-action', event => {
    const action = event.detail?.action;
    const guide = /^\/guides\/([a-z0-9]+(?:-[a-z0-9]+)*)$/.exec(page)?.[1];
    if (!guide || !['copy_command', 'copy_brief', 'download_source'].includes(action) || choice !== 'allow' || !loaded || !safeContext() || window['ga-disable-' + id]) return;
    gtag('event', 'guide_action', {action, guide_slug: guide, page_location: origin + page, page_referrer: '', page_title: pageTitle});
  });
  render();
  start();
})();
