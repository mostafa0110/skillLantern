// Browser QA uses an isolated profile and a temporary loopback server, both closed afterward.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {spawn} from 'node:child_process';
const base=path.dirname(path.dirname(fileURLToPath(import.meta.url))),out=path.join(base,'qa-product');fs.mkdirSync(out,{recursive:true});
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
  await call('Page.enable');await call('Runtime.enable');await call('Emulation.setDeviceMetricsOverride',{width:390,height:1000,deviceScaleFactor:1,mobile:true});await load('popular.html');const spacing=await ev(`(()=>{const a=document.querySelector('#popular-rows td>a'),s=document.querySelector('#popular-rows td>small');return {title:getComputedStyle(a).display,slug:getComputedStyle(s).display,margin:getComputedStyle(s).marginTop,titleBottom:a.getBoundingClientRect().bottom,slugTop:s.getBoundingClientRect().top}})()`);assert(spacing.title==='block'&&spacing.slug==='block'&&parseFloat(spacing.margin)>=6&&spacing.slugTop>=spacing.titleBottom,'Popular title and slug separated',spacing);await screenshot('popular-mobile');
  await load('install.html');assert(await ev(`document.body.textContent.includes('.skilllantern-owned.json')&&/18/.test(document.body.textContent)`),'Static file plan discloses payload plus ownership record');
  await load('skills.html');assert(await ev(`document.querySelector('a[href="popular.html"]')&&[...document.querySelectorAll('a')].every(a=>!a.textContent.trim().endsWith('?'))`),'Secondary labels render no question-mark arrows');
  fs.writeFileSync(path.join(out,'cosmetic-results.json'),JSON.stringify({date:'2026-11-14',checks},null,2));console.log(JSON.stringify({passed:checks.length,failed:0}));await call('Browser.close');socket.close();server.kill();
}catch(e){console.error(e.stack);if(socket){try{socket.send(JSON.stringify({id:++id,method:'Browser.close'}));socket.close()}catch{}}browser?.kill();server.kill();process.exitCode=1}
