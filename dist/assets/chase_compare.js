/* Local, in-memory comparison. No requests, storage or external dependencies. */
(() => {
  'use strict';
  const byId = id => document.getElementById(id);
  const form = byId('comparison-form');
  if (!form) return;
  const presets = JSON.parse(byId('comparison-presets').textContent);
  const preset = byId('comparison-preset');
  let edited = false;
  const number = value => new Intl.NumberFormat('en', {maximumFractionDigits: 3}).format(value);
  const keys = ['cost', 'time', 'quality'];
  const measurements = {};
  let exportText = '';
  const numeric = id => {
    const input = byId(id);
    if (input.validity.badInput) return {invalid: true};
    if (input.value === '') { input.removeAttribute('aria-invalid'); return {value: null}; }
    const value = input.valueAsNumber;
    const invalid = !Number.isFinite(value) || value < 0 || (id.endsWith('quality') && value > 100);
    input.setAttribute('aria-invalid', String(invalid));
    return {value, invalid};
  };
  function describe(key, a, b) {
    if (a.invalid || b.invalid) return 'Enter valid non-negative numbers'+(key === 'quality' ? ' from 0 to 100.' : '.');
    if (a.value === null || b.value === null) return 'Not compared · enter both measurements.';
    const delta = b.value - a.value;
    if (delta === 0) return 'Equal · no measured difference.';
    if (key === 'quality') return number(Math.abs(delta))+' percentage points '+(delta > 0 ? 'higher' : 'lower')+' with the extension.';
    const unit = key === 'cost' ? '$'+number(Math.abs(delta)) : number(Math.abs(delta))+' min';
    const direction = key === 'cost' ? (delta > 0 ? 'more' : 'less') : (delta > 0 ? 'slower' : 'faster');
    const percentage = a.value === 0 ? 'Percentage change undefined from a zero baseline.' : number(Math.abs(delta / a.value * 100))+'% '+direction+'.';
    return unit+' '+direction+' · '+percentage;
  }
  function update() {
    const summary = [];
    let validPairs = 0;
    let improves = 0;
    let worsens = 0;
    for (const key of keys) {
      const a = numeric('baseline-'+key), b = numeric('plugin-'+key);
      measurements[key] = {a, b};
      const result = byId(key+'-result');
      const title = document.createElement('h3');
      title.textContent = {cost: 'Cost', time: 'Elapsed time', quality: 'Result criterion'}[key];
      const text = document.createElement('p');
      text.textContent = describe(key, a, b);
      result.replaceChildren(title, text);
      if (!a.invalid && !b.invalid && a.value !== null && b.value !== null) {
        validPairs++;
        const delta = b.value - a.value;
        const better = key === 'quality' ? delta > 0 : delta < 0;
        const worse = key === 'quality' ? delta < 0 : delta > 0;
        improves += Number(better); worsens += Number(worse);
        result.dataset.direction = better ? 'better' : worse ? 'worse' : 'equal';
      } else result.dataset.direction = 'missing';
      summary.push(title.textContent+': '+text.textContent);
    }
    const reading = !validPairs ? 'Add paired measurements to see the tradeoff.' : improves && worsens ? 'Mixed results. Decide which improvements matter enough to justify the tradeoff for this task.' : validPairs < 3 ? 'Partial comparison. Missing measurements may change the decision; equal measured results do not establish equal quality in every respect.' : improves ? 'The entered measurements favour the extension on at least one dimension. Check unmeasured quality and repeatability before deciding.' : worsens ? 'The entered measurements favour the baseline on at least one dimension. This one task does not settle every use case.' : 'Equal on the entered measurements. Consider unmeasured quality, setup effort and repeatability.';
    byId('comparison-reading').textContent = reading;
    const get = id => byId(id).value.trim();
    const p = presets[preset.value];
    const raw = key => {
      const {a,b} = measurements[key];
      return [a,b].map(v => v.invalid ? 'Invalid entry' : v.value === null ? 'Unmeasured' : number(v.value)).join(' | ');
    };
    exportText = '# Plugin comparison\n\nTask: '+(get('comparison-task') || 'Not entered')+'\nExtension: '+(get('comparison-plugin') || 'Not entered')+'\nCriterion: '+(get('comparison-criterion') || 'Not entered')+'\n\nProvenance: '+p.note+(edited ? '\nEdited in this browser; current entries are not the original reported measurements.' : '')+'\n'+(p.source ? 'Source: '+new URL(p.source.replace('{{root}}', document.body.dataset.root || '../'), location.href).href+'\n' : '')+'\n| Measure | Plain baseline | With extension |\n| --- | --- | --- |\n| Cost (USD) | '+raw('cost')+' |\n| Elapsed time (min) | '+raw('time')+' |\n| Criterion met (%) | '+raw('quality')+' |\n\n'+summary.join('\n')+'\n\n'+reading+'\n\nContext and corrections: '+(get('comparison-notes') || 'Not entered')+'\n\nOne task is not a universal ranking. Compare identical acceptance checks; repeat when affordable.\n';
    byId('comparison-export').value = exportText;
    byId('comparison-export-status').textContent = '';
    byId('comparison-provenance').textContent = p.note+(edited ? ' Edited here: current entries are your changes, not the original reported measurements.' : '');
  }
  function load() {
    const p = presets[preset.value];
    edited = false;
    for (const [id,key] of [['comparison-task','task'],['comparison-plugin','plugin'],['comparison-criterion','criterion']]) byId(id).value = p[key];
    for (const key of keys) for (const side of ['baseline', 'plugin']) {
      const input = byId(side+'-'+key);
      input.value = p[side+key[0].toUpperCase()+key.slice(1)] ?? '';
      input.removeAttribute('aria-invalid');
    }
    byId('comparison-notes').value = '';
    const source = byId('comparison-source');
    source.hidden = !p.source;
    if (p.source) source.href = p.source.replace('{{root}}', document.body.dataset.root || '../');
    update();
  }
  preset.addEventListener('change', load);
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', event => { if (event.target !== preset) { edited = true; update(); } });
  byId('load-motion').addEventListener('click', () => { preset.value = 'motion'; load(); byId('try-comparison').scrollIntoView({behavior: 'instant'}); preset.focus({preventScroll:true}); });
  byId('copy-comparison').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(exportText); byId('comparison-export-status').textContent = 'Comparison copied.'; }
    catch { byId('comparison-export').closest('details').open = true; byId('comparison-export').focus(); byId('comparison-export').select(); byId('comparison-export-status').textContent = 'Copy unavailable here. Select and copy the text below, or download it.'; }
  });
  byId('download-comparison').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([exportText], {type:'text/markdown;charset=utf-8'}));
    const a = document.createElement('a'); a.href = url; a.download = 'plugin-comparison.md'; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    byId('comparison-export-status').textContent = 'Comparison download prepared.';
  });
  load();
})();
