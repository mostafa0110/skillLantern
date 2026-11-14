'use strict';
(() => {
  const root=document.body.dataset.root||'';
  const skills=window.SKILLLANTERN_SKILLS||[];
  const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const menu=document.getElementById('menu-button'),nav=document.getElementById('site-nav');
  if(menu&&nav){
    menu.hidden=false;nav.dataset.collapsible='true';
    menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open)});
    nav.addEventListener('keydown',e=>{if(e.key==='Escape'){nav.classList.remove('is-open');menu.setAttribute('aria-expanded','false');menu.focus()}});
  }
  const search=document.getElementById('skill-search'),evidence=document.getElementById('evidence-filter');
  const params=new URLSearchParams(location.search);
  if(search&&evidence){
    const cards=[...document.querySelectorAll('[data-card]')],chips=[...document.querySelectorAll('[data-filter-category]')];
    let type='all';
    const typeButtons=[...document.querySelectorAll('[data-filter-type]')];
    let category=chips.some(b=>b.dataset.filterCategory===params.get('category'))?params.get('category'):'all';
    search.value=params.get('q')||'';
    const apply=()=>{
      const words=search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let count=0;
      for(const card of cards){const match=(type==='all'||card.dataset.type===type)&&(category==='all'||card.dataset.category===category)&&(evidence.value==='all'||card.dataset.evidence===evidence.value)&&words.every(w=>card.dataset.search.toLocaleLowerCase().includes(w));card.hidden=!match;if(match)count++}
      for(const b of typeButtons)b.setAttribute('aria-pressed',String(b.dataset.filterType===type));
      for(const button of chips)button.setAttribute('aria-pressed',String(button.dataset.filterCategory===category));
      document.getElementById('result-count').textContent=count+' '+(count===1?'capability':'capabilities');
      const empty=document.getElementById('empty-state');empty.hidden=count!==0;
      if(!count){empty.querySelector('h2').textContent=type==='plugin'?'Plugin reviews are coming next.':type==='workflow'?'More workflow reviews are on the way.':'No matching capabilities yet.';empty.querySelector('p').textContent=(type==='plugin'||type==='workflow')?'We only list sourced entries. Explore the existing guides while this collection grows.':'Try a broader task or clear the filters.'}
    };
    const clear=()=>{category='all';type='all';search.value='';evidence.value='all';apply();search.focus()};
    typeButtons.forEach(b=>b.addEventListener('click',()=>{type=b.dataset.filterType;apply()}));
    chips.forEach(b=>b.addEventListener('click',()=>{category=b.dataset.filterCategory;apply()}));
    document.getElementById('clear-filters').addEventListener('click',clear);
    document.querySelectorAll('[data-clear-filters]').forEach(b=>b.addEventListener('click',clear));
    search.addEventListener('input',apply);evidence.addEventListener('change',apply);apply();
  }
  const dialog=document.getElementById('skill-dialog'),content=document.getElementById('skill-dialog-content');
  const openSkill=id=>{
    const skill=skills.find(s=>s.id===id);if(!skill||!dialog||!content)return;
    const tested=skill.evidenceStatus==='task-tested';
    content.innerHTML=`<p class="eyebrow">${escape(skill.publisher)} · ${escape(skill.category)}</p><h2 id="skill-dialog-title">${escape(skill.name)}</h2><p>${escape(skill.summary)}</p><span class="badge ${tested?'tested':'candidate'}">${tested?'Task tested · one pair':'Research candidate'}</span><h3>What the evidence says</h3><p>${escape(skill.evidenceSummary)}</p><h3>Requirements to check</h3><ul>${skill.requirements.map(t=>`<li>${escape(t)}</li>`).join('')}</ul><h3>Limits</h3><ul>${skill.limitations.map(t=>`<li>${escape(t)}</li>`).join('')}</ul><p class="small">${escape(skill.licenseNote)}</p><p class="small">Source review: ${escape(skill.reviewedOn)}</p><p>${skill.guidePath?`<a class="button" href="${root}${escape(skill.guidePath)}">Open the tested guide ↗</a> `:''}<a class="button secondary" href="${escape(skill.sourceUrl)}" target="_blank" rel="noopener noreferrer">Read the original source ↗</a></p>`;
    if(typeof dialog.showModal==='function')dialog.showModal();else dialog.setAttribute('open','');
  };
  document.querySelectorAll('[data-skill-id]').forEach(b=>b.addEventListener('click',()=>openSkill(b.dataset.skillId)));
  if(dialog){
    dialog.querySelector('.dialog-close').addEventListener('click',()=>dialog.close());
    dialog.addEventListener('click',e=>{if(e.target!==dialog)return;const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()});
  }
  if(params.has('skill'))openSkill(params.get('skill'));
  document.querySelectorAll('[data-copy-target]').forEach(button=>button.addEventListener('click',async()=>{
    const target=document.getElementById(button.dataset.copyTarget);if(!target)return;
    const text=target.textContent,original=button.textContent;let copied=false;
    try{await navigator.clipboard.writeText(text);copied=true}catch{
      const area=document.createElement('textarea');area.value=text;area.className='sr-only';document.body.append(area);area.select();
      try{copied=document.execCommand('copy')}catch{}area.remove();button.focus();
    }
    button.textContent=copied?(document.documentElement.lang==='ar'?'تم النسخ':'Copied'):'Select the prompt and copy';
    if(!copied){const range=document.createRange();range.selectNodeContents(target);const selection=getSelection();selection.removeAllRanges();selection.addRange(range)}
    setTimeout(()=>button.textContent=original,2500);
  }));
})();

// This planner only composes a local brief from the reviewed catalogue.
(() => {
  const form=document.getElementById('setup-form');if(!form)return;
  const product=window.SKILLLANTERN_PRODUCT||{matches:{},guides:[]}, skills=window.SKILLLANTERN_SKILLS||[];
  const safe=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const labels={website:'A distinctive website',marketing:'Marketing content',data:'A reliable spreadsheet',motion:'Better interface motion'};
  const params=new URLSearchParams(location.search), initial=params.get('outcome');
  if(Object.hasOwn(labels,initial))form.querySelector(`[name="outcome"][value="${initial}"]`).checked=true;
  let step=0, brief='';
  const next=document.getElementById('planner-next'),back=document.getElementById('planner-back'),submit=document.getElementById('planner-submit');
  const show=()=>{form.querySelectorAll('[data-step]').forEach((el,i)=>el.hidden=i!==step);back.hidden=step===0;next.hidden=step===3;submit.hidden=step!==3;document.getElementById('planner-progress').textContent=`Step ${step+1} of 4`;};
  next.addEventListener('click',()=>{step=Math.min(3,step+1);show();form.querySelector(`[data-step="${step}"] input, [data-step="${step}"] textarea`)?.focus()});
  back.addEventListener('click',()=>{step=Math.max(0,step-1);show()});
  form.addEventListener('submit',e=>{
    e.preventDefault();const data=new FormData(form),outcome=data.get('outcome'),agent=data.get('agent');
    const selected=(product.matches[outcome]||[]).map(id=>skills.find(s=>s.id===id)).filter(Boolean);
    const guides=product.guides.filter(g=>g.outcome===outcome);
    const requirements=[...new Set(selected.flatMap(s=>s.requirements))];
    const checklist=['Confirm your agent can read the selected source and project files.','Review the current source, licence, dependencies and permissions before running anything.','Use a copy or a new practice folder; keep the original files.','Agree on a small acceptance checklist before making changes.','Check the actual output and record failures, costs and remaining limits.'];
    const taskChecks={website:'Check mobile layout, keyboard navigation, contrast, links and every form action.',marketing:'Check every factual claim against its source; review brand voice and usage rights.',data:'Check totals, formulas, types and row counts against the untouched input.',motion:'Check loading, success, failure and retry states with reduced motion enabled.'};
    checklist.push(taskChecks[outcome]);
    brief=`# Agent setup brief\n\nOutcome: ${labels[outcome]}\nExisting agent: ${agent}\nPriority: ${data.get('priority')}\nVision: ${data.get('vision')||'Define the desired result before starting.'}\nConstraints: ${data.get('constraints')||'Confirm time, budget, tools and permissions before starting.'}\n\n## Suggested capabilities\n${selected.map(s=>`- ${s.name} (${s.publisher}): ${s.summary}\n  Source: ${s.sourceUrl}\n  Evidence: ${s.evidenceStatus==='task-tested'?'One paired task test; no superiority established':'Source reviewed; installation and performance untested'}`).join('\n')}\n\n## Requirements to confirm\n${requirements.map(s=>'- '+s).join('\n')}\n\n## Working approach\n1. Inspect the linked source and ask how to provide it as explicit context in your agent. Native installation is not assumed.\n2. Describe the desired output and boundaries. Do not install tools, spend or publish without explicit permission.\n3. Make a small version in a separate working copy.\n4. Run the checklist and report what actually passed.\n\n## Readiness and acceptance\n${checklist.map(s=>'- [ ] '+s).join('\n')}\n\n## Relevant guides\n${guides.length?guides.map(g=>'- '+g.title+' — '+g.path).join('\n'):'No dedicated guide for this outcome yet. Use the source notes and requirements above.'}\n\nBased on reviewed workflows. This is deterministic guidance, not a live agent assessment. Nothing was installed or tested by generating this brief.\nPrepared ${new Date().toISOString().slice(0,10)}; source review dates are in the catalogue.\n`;
    const result=document.getElementById('setup-result');
    result.innerHTML=`<p class="eyebrow">Based on reviewed workflows</p><h2 id="result-title">Your starting setup.</h2><p>${safe(labels[outcome])} · ${safe(agent)} · ${safe(data.get('priority'))}</p><p class="trust-note">A local planning brief. No tools were installed and no private inputs were sent.</p><h3>Capabilities to consider</h3><div class="grid three">${selected.map(s=>`<article class="step-card"><span class="badge">${s.evidenceStatus==='task-tested'?'One paired task test':'Source reviewed'}</span><h3>${safe(s.name)}</h3><p>${safe(s.summary)}</p><a href="skills.html?skill=${encodeURIComponent(s.id)}">Requirements &amp; source →</a></article>`).join('')}</div><h3>Before you start</h3><ul>${requirements.map(s=>`<li>${safe(s)}</li>`).join('')}</ul><h3>Readiness &amp; acceptance checklist</h3><ul>${checklist.map(s=>`<li>${safe(s)}</li>`).join('')}</ul><h3>Your next guide</h3>${guides.length?'<ul>'+guides.map(g=>`<li><a href="${safe(g.path)}">${safe(g.title)} →</a></li>`).join('')+'</ul>':'<p>No dedicated guide for this task yet. Start with the linked source notes and confirm compatibility.</p>'}<div class="planner-actions"><button type="button" class="button" id="download-brief">Download setup brief</button><button type="button" class="button secondary" id="copy-brief">Copy brief</button></div><p id="brief-status" role="status"></p><details><summary>Read the complete brief</summary><pre class="code-block" id="brief-preview"></pre></details>`;
    result.querySelector('#brief-preview').textContent=brief;
    result.querySelector('#download-brief').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([brief],{type:'text/markdown;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='skilllantern-setup-brief.md';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);result.querySelector('#brief-status').textContent='Setup brief prepared for download.'});
    result.querySelector('#copy-brief').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(brief);result.querySelector('#brief-status').textContent='Brief copied.'}catch{result.querySelector('details').open=true;const range=document.createRange();range.selectNodeContents(result.querySelector('#brief-preview'));const selection=getSelection();selection.removeAllRanges();selection.addRange(range);result.querySelector('#brief-status').textContent='Select and copy the complete brief below.'}});
    result.hidden=false;result.focus();result.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  });
})();

(() => {
const table=document.getElementById('popular-rows');if(!table)return;
const original=window.SKILLLANTERN_POPULAR,search=document.getElementById('popular-search'),sort=document.getElementById('popular-sort'),button=document.getElementById('popular-refresh'),status=document.getElementById('popular-status');let rows=original.items.map(v=>({...v}));
const text=(tag,value)=>{const el=document.createElement(tag);el.textContent=value;return el};
const render=()=>{const q=search.value.trim().toLowerCase(),filtered=rows.filter(v=>[v.name,v.repository,v.kind,v.description].join(' ').toLowerCase().includes(q)).sort((a,b)=>sort.value==='name'?a.name.localeCompare(b.name):(b.stars??-1)-(a.stars??-1));table.replaceChildren();for(const v of filtered){const tr=document.createElement('tr'),td=document.createElement('td'),a=text('a',v.name);a.href='https://github.com/'+v.repository;a.target='_blank';a.rel='noopener noreferrer';td.append(a,text('small',v.repository),text('p',v.description||''));tr.append(td,text('td',v.stars==null?'Unavailable':Number(v.stars).toLocaleString()),text('td',v.kind),text('td',(v.starsCheckedAt||'Unknown')+' · '+v.fetchStatus));table.append(tr)}document.getElementById('popular-empty').hidden=filtered.length!==0};
search.addEventListener('input',render);sort.addEventListener('change',render);
button.addEventListener('click',async()=>{button.disabled=true;status.textContent='Requesting public counts from GitHub…';let index=0,limited=false,failed=0;const updates=new Map();const worker=async()=>{while(index<rows.length&&!limited){const v=rows[index++];try{const response=await fetch('https://api.github.com/repos/'+v.repository,{headers:{Accept:'application/vnd.github+json'},credentials:'omit'});if(response.status===429||response.status===403){limited=true;break}if(!response.ok)throw Error('Unavailable');const data=await response.json();if(!Number.isInteger(data.stargazers_count))throw Error('Invalid count');updates.set(v.id,{stars:data.stargazers_count,starsCheckedAt:new Date().toISOString(),fetchStatus:'reader-refreshed'})}catch{failed++}}};try{await Promise.all([worker(),worker(),worker()]);if(limited){rows=original.items.map(v=>({...v}));status.textContent='GitHub rate limit reached. Showing the dated published snapshot; no further requests will be started.'}else{rows=rows.map(v=>({...v,...(updates.get(v.id)||{}),fetchStatus:updates.has(v.id)?'reader-refreshed':v.fetchStatus}));status.textContent=`Refreshed ${updates.size} repositories in memory. ${failed?failed+' unavailable; their dated snapshot counts remain.':'Published JSON feeds are unchanged.'}`}render()}finally{button.disabled=false}});
render();
})();
