// Browser QA uses an isolated profile and a temporary loopback server, both closed afterward.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawn} from 'node:child_process';
const base=path.dirname(fileURLToPath(import.meta.url)),out=path.join(base,'qa-ship');fs.mkdirSync(out,{recursive:true});
const catalogue=JSON.parse(fs.readFileSync(path.join(base,'content/skills.json'),'utf8'));
const expectedNames=category=>catalogue.filter(r=>r.category===category).map(r=>r.name).sort();
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const server=spawn(process.execPath,[path.join(base,'serve.mjs')],{env:{...process.env,SKILLLANTERN_PORT:'0'},windowsHide:true,stdio:['ignore','pipe','pipe']});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'skilllantern-site-'));
let browser,socket,id=0;const pending=new Map(),errors=[],checks=[];
const assert=(pass,name,details=null)=>{checks.push({name,passed:!!pass,details});if(!pass)throw Error(name+' '+JSON.stringify(details))};
try{
  const origin=await new Promise((resolve,reject)=>{let s='';server.stdout.on('data',d=>{s+=d;const m=s.match(/http:\/\/127\.0\.0\.1:\d+/);if(m)resolve(m[0])});server.on('error',reject);setTimeout(()=>reject(Error('Local server did not start')),8000).unref()});
  const response=await fetch(origin+'/');assert(response.status===200&&/SkillLantern/.test(await response.text()),'HTTP homepage');
  const traversal=await fetch(origin+'/%2e%2e%5cAGENTS.md');assert(traversal.status===404,'Server does not expose vault files');
  const zip=await fetch(origin+'/downloads/motion-design-demo.zip');assert(zip.status===200&&(await zip.arrayBuffer()).byteLength>40000,'Demo download serves successfully');
  browser=spawn('C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',['--headless=new','--disable-background-networking','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--user-data-dir='+profile,'--window-size=1440,1000','about:blank'],{windowsHide:true,stdio:'ignore'});
  const pf=path.join(profile,'DevToolsActivePort');for(let n=0;n<150&&!fs.existsSync(pf);n++)await delay(100);
  const port=fs.readFileSync(pf,'utf8').split('\n')[0];
  const targets=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();
  socket=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);
  await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j});
  socket.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.j(Error(JSON.stringify(m.error))):p.r(m.result)}if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails)};
  const call=(method,params={})=>new Promise((r,j)=>{const n=++id;pending.set(n,{r,j});socket.send(JSON.stringify({id:n,method,params}));setTimeout(()=>{if(pending.has(n)){pending.delete(n);j(Error('Timeout '+method))}},8000).unref()});
  const ev=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value};
  const load=async name=>{await call('Page.navigate',{url:name.startsWith('file:')?name:origin+'/'+name});await delay(250);for(let n=0;n<50;n++){if(await ev(`document.readyState==='complete'&&!!document.querySelector('#main')`))break;await delay(40)}await call('Page.bringToFront');await delay(120)};
  const click=async selector=>{const point=await ev(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});e.scrollIntoView({block:'center',behavior:'instant'});const r=e.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);await call('Input.dispatchMouseEvent',{type:'mousePressed',...point,button:'left',clickCount:1});await call('Input.dispatchMouseEvent',{type:'mouseReleased',...point,button:'left',clickCount:1});await delay(50)};
  const screenshot=async name=>{await ev(`Promise.all(Array.from(document.images,img=>{img.loading='eager';return img.decode()}))`);const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(shot.data,'base64'))};
  const visibleCards=()=>ev(`Array.from(document.querySelectorAll('[data-card]')).filter(e=>!e.hidden).map(e=>e.querySelector('h3').textContent)`);
  const pages=JSON.parse(fs.readFileSync(path.join(base,'page-manifest.json'),'utf8'));
  const requests=[];socket.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.method==='Network.requestWillBeSent')requests.push(m.params.request.url)});
  await call('Page.enable');await call('Runtime.enable');await call('Network.enable');
  await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  for(const page of pages){
    await load(page);
    const facts=await ev(`({lang:document.documentElement.lang,title:document.title,description:document.querySelector('meta[name="description"]')?.content,canonical:document.querySelector('link[rel="canonical"]')?.href,text:document.body.innerText,links:[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'))})`);
    assert(facts.lang==='en'&&!facts.links.some(x=>x.includes('/ar/')||x.startsWith('ar/')),'English-only release: '+page);
    assert(!/Local preview|debug banner/i.test(facts.text),'No debug banner: '+page);
    assert(facts.title&&facts.description&&facts.canonical==='https://skilllantern.happymoth22.chatgpt.site/'+page,'Metadata and release canonical: '+page);
    for(const href of facts.links){if(href.startsWith('#')||/^(https?:|mailto:|blob:)/.test(href))continue;const url=new URL(href,origin+'/'+page);assert((await fetch(url)).status===200,'Local destination: '+page+' -> '+href)}
    assert(!facts.links.some(x=>/^https?:/.test(x)&&/example\.com|your-domain|localhost/.test(x)),'No fake external source: '+page);
  }
  await load('index.html');await delay(400);
  const hero=await ev(`({words:document.querySelector('.hero')?.innerText.split(/\\s+/).length,text:document.querySelector('.hero')?.innerText,canvas:getComputedStyle(document.querySelector('#scene')).display,fallback:getComputedStyle(document.querySelector('#fallback')).display})`);
  assert(hero.canvas!=='none'&&hero.fallback==='none','Cinematic renderer is visible',hero);
  assert(hero.words<180,'Concise homepage hero',hero.words);await screenshot('home-desktop');
  await click('#motion');assert((await ev(`document.querySelector('#motion').textContent`)).includes('Resume'),'3D pause control');
  await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});await load('index.html');assert((await ev(`document.querySelector('#motion').textContent`)).includes('Resume'),'Reduced motion starts still');
  await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'no-preference'}]});
  const fallbackScript=await call('Page.addScriptToEvaluateOnNewDocument',{source:"HTMLCanvasElement.prototype.getContext=()=>null"});await load('index.html');assert(await ev(`getComputedStyle(document.querySelector('#fallback')).display!=='none'&&document.querySelector('#motion').disabled`),'Still illustration survives unavailable renderer');await call('Page.removeScriptToEvaluateOnNewDocument',{identifier:fallbackScript.identifier});
  await load('skills.html');assert((await visibleCards()).length===catalogue.length,'Catalogue count');await click('button[data-skill-id="deepseek-harness"]');assert(await ev(`document.querySelector('#skill-dialog').open&&/preview/i.test(document.querySelector('#skill-dialog').innerText)`),'Preview source dialog');
  await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Escape',code:'Escape',windowsVirtualKeyCode:27});assert(await ev(`!document.querySelector('#skill-dialog').open`),'Keyboard Escape closes dialog');
  await load('setup.html');
  await ev(`window.__copied=null;window.__downloads=[];Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async t=>window.__copied=t}});URL.createObjectURL=b=>{window.__downloads.push(b);return 'blob:qa-captured'};HTMLAnchorElement.prototype.click=function(){window.__downloadName=this.download};document.querySelector('[name="outcome"][value="marketing"]').checked=true`);
  await click('#planner-next');assert(await ev(`document.querySelector('#planner-progress').textContent==='Step 2 of 4'`),'Planner step 2');await ev(`document.querySelector('[name="agent"][value="Claude Code"]').checked=true`);await click('#planner-next');
  const unsafe='<img src=x onerror="window.__unsafe=1">';await ev(`document.querySelector('#setup-vision').value=${JSON.stringify(unsafe+' calm ceramics campaign')}`);await click('#planner-next');await ev(`document.querySelector('#setup-constraints').value='No new subscriptions; synthetic assets only'`);await click('#planner-submit');
  assert(await ev(`(()=>{const r=document.querySelector('#setup-result');return !r.hidden&&r.innerText.includes('Marketing content')&&r.innerText.includes('Claude Code')&&r.querySelector('#brief-preview').textContent.includes('calm ceramics campaign')&&r.querySelector('#brief-preview').textContent.includes('No new subscriptions')&&!r.querySelector('img')&&!window.__unsafe})()`),'Planner matches outcome agent vision constraints and escapes HTML');
  await screenshot('planner-final-desktop');
  const plannerButtons=await ev(`[...document.querySelectorAll('#setup-result button')].map(e=>({id:e.id,text:e.textContent}))`);
  const copy=plannerButtons.find(x=>/copy/i.test(x.text)),download=plannerButtons.find(x=>/download/i.test(x.text));assert(copy&&download,'Planner exposes copy and Markdown controls',plannerButtons);
  await click('#'+copy.id);assert(await ev(`window.__copied?.includes('Claude Code')&&window.__copied.includes('calm ceramics campaign')`),'Planner exact brief copied to stub');await click('#'+download.id);assert(await ev(`window.__downloads.length===1&&/\.md$/.test(window.__downloadName)`),'Markdown download produces local Blob');assert(await ev(`(async()=> (await window.__downloads[0].text())===window.__copied)()`),'Markdown Blob contains the exact copied brief');
  assert(await ev(`localStorage.length===0&&sessionStorage.length===0`),'Planner does not persist user answers');
  await call('Emulation.setDeviceMetricsOverride',{width:390,height:1000,deviceScaleFactor:1,mobile:true});assert(await ev(`document.documentElement.scrollWidth<=innerWidth`),'Planner final result fits mobile with unsafe text');await screenshot('planner-final-mobile');await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await load('setup-help.html');assert(await ev(`!/mailto:|calendly|checkout|stripe/.test([...document.querySelectorAll('a')].map(a=>a.href).join(' '))&&!document.querySelector('form')&&/not open|not available|coming soon/i.test(document.body.innerText)`),'Implementation help has no fake booking or payment');
  await load('guides.html');assert(await ev(`document.querySelectorAll('a[href*="guides/"]').length>=2`),'Real guide cards link to guides');
  await load('guides/motion-design.html');await screenshot('guide-desktop');assert(await ev(`/no comparative advantage|tie|no advantage/i.test(document.body.innerText)`),'Tested guide retains bounded outcome');
  await call('Emulation.setDeviceMetricsOverride',{width:390,height:1000,deviceScaleFactor:1,mobile:true});
  for(const page of pages){await load(page);assert(await ev(`document.documentElement.scrollWidth<=innerWidth`),'390px fit: '+page);if(page==='index.html')await screenshot('home-mobile');if(page==='guides/website-design.html')await screenshot('guide-mobile')}
  await load('index.html');await click('#menu-button');assert(await ev(`document.querySelector('#menu-button').getAttribute('aria-expanded')==='true'`),'Mobile menu opens');await click('#menu-button');assert(await ev(`document.querySelector('#menu-button').getAttribute('aria-expanded')==='false'`),'Mobile menu closes');
  assert(errors.length===0,'No runtime JavaScript exceptions',errors);assert(!requests.some(u=>/^https?:/.test(u)&&!u.startsWith(origin)),'No unexpected external page requests');
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({date:'2026-11-14',checks,limitations:['Clipboard stubbed; Markdown Blob captured without downloading to user folders','One headless Edge environment; no human usability study','External source destinations were inspected as URLs, not fetched']},null,2)+'\n');console.log(JSON.stringify({passed:checks.length,failed:0}));await call('Browser.close');socket.close();server.kill();
}catch(e){console.error(e.stack);fs.writeFileSync(path.join(out,'results.json'),JSON.stringify({date:'2026-11-14',checks,error:e.message},null,2)+'\n');if(socket){try{socket.send(JSON.stringify({id:++id,method:'Browser.close'}));socket.close()}catch{}}browser?.kill();server.kill();process.exitCode=1}
