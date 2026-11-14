// Original local WebGL lantern. No dependencies or network requests.
'use strict';
(() => {
const canvas=document.getElementById('scene'), fallback=document.getElementById('fallback');
const button=document.getElementById('motion'), status=document.getElementById('status'), stage=document.getElementById('stage');
if(!canvas||!fallback||!button||!status||!stage)return;
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let gl,program,buffer,locations,raf=0,last=0,elapsed=0,running=!reduced.matches,lost=false,inView=true;
let pointerX=0,pointerY=0,turnX=0,turnY=0;
const vertices=[];
const metal=[.24,.29,.28], trim=[.62,.43,.20], light=[1,.67,.25];
function triangle(a,b,c,color,emission=0){
 const u=b.map((v,i)=>v-a[i]),v=c.map((x,i)=>x-a[i]);
 let n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
 const len=Math.hypot(...n)||1;n=n.map(x=>x/len);
 for(const p of [a,b,c])vertices.push(...p,...n,...color,emission);
}
function box(x,y,z,w,h,d,color){
 const p=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]].map(a=>[x+a[0]*w/2,y+a[1]*h/2,z+a[2]*d/2]);
 for(const [a,b,c,d] of [[0,3,2,1],[4,5,6,7],[0,4,7,3],[1,2,6,5],[3,7,6,2],[0,1,5,4]]){triangle(p[a],p[b],p[c],color);triangle(p[a],p[c],p[d],color);}
}
function cylinder(y,radius,height,color,segments=32){
 for(let i=0;i<segments;i++){
 const a=i/segments*Math.PI*2,b=(i+1)/segments*Math.PI*2;
 const p=[radius*Math.cos(a),y-height/2,radius*Math.sin(a)],q=[radius*Math.cos(b),y-height/2,radius*Math.sin(b)];
 const r=[q[0],y+height/2,q[2]],s=[p[0],y+height/2,p[2]];
 triangle(p,s,r,color);triangle(p,r,q,color);triangle([0,y+height/2,0],r,s,color);triangle([0,y-height/2,0],p,q,color);
 }
}
function sphere(cx,cy,cz,rx,ry,rz,color,emission){
 const point=(a,b)=>[cx+rx*Math.sin(a)*Math.cos(b),cy+ry*Math.cos(a),cz+rz*Math.sin(a)*Math.sin(b)];
 for(let j=0;j<20;j++)for(let i=0;i<28;i++){
 const a=j/20*Math.PI,b=(j+1)/20*Math.PI,c=i/28*Math.PI*2,d=(i+1)/28*Math.PI*2;
 triangle(point(a,c),point(b,c),point(b,d),color,emission);triangle(point(a,c),point(b,d),point(a,d),color,emission);
 }
}
// A four-post housing, faceted roof, base and curved tubular handle.
box(0,-.84,0,1.16,.12,1.16,metal);box(0,-.75,0,1.08,.055,1.08,trim);box(0,-.92,0,.94,.045,.94,trim);
box(0,.65,0,1.14,.10,1.14,metal);box(0,.71,0,1.18,.025,1.18,trim);
for(const x of [-.48,.48])for(const z of [-.48,.48]){box(x,-.01,z,.075,1.35,.075,metal);box(x,-.01,z+.041,.025,1.20,.008,trim);}
// Structural interior rails add depth while keeping the light source legible.
box(0,-.58,-.47,.94,.025,.025,trim);box(0,.52,-.47,.94,.025,.025,trim);
const corners=[[-.64,.72,-.64],[.64,.72,-.64],[.64,.72,.64],[-.64,.72,.64]],tip=[0,1.08,0];
for(let i=0;i<4;i++)triangle(corners[(i+1)%4],corners[i],tip,metal);
cylinder(1.10,.13,.09,trim);cylinder(-.59,.24,.16,metal);
sphere(0,-.12,0,.19,.43,.19,light,1);sphere(0,-.22,0,.11,.22,.11,[1,.91,.65],1);
// Torus in the XY plane, open only where it enters the roof.
for(let i=0;i<40;i++)for(let j=0;j<8;j++){
 const point=(a,b)=>[(.30+.033*Math.cos(b))*Math.cos(a),1.31+(.30+.033*Math.cos(b))*Math.sin(a),.033*Math.sin(b)];
 const a=i/40*Math.PI*2,b=(i+1)/40*Math.PI*2,c=j/8*Math.PI*2,d=(j+1)/8*Math.PI*2;
 triangle(point(a,c),point(b,c),point(b,d),metal);triangle(point(a,c),point(b,d),point(a,d),metal);
}
const vertexSource=`attribute vec3 aPosition;attribute vec3 aNormal;attribute vec3 aColor;attribute float aEmission;
uniform mat4 uModel;uniform mat4 uProjection;varying vec3 vPosition;varying vec3 vNormal;varying vec3 vColor;varying float vEmission;
void main(){vec4 world=uModel*vec4(aPosition,1.0);vPosition=world.xyz;vNormal=mat3(uModel)*aNormal;vColor=aColor;vEmission=aEmission;gl_Position=uProjection*vec4(world.xyz+vec3(0.0,-0.16,-5.7),1.0);}`;
const fragmentSource=`precision mediump float;varying vec3 vPosition;varying vec3 vNormal;varying vec3 vColor;varying float vEmission;
uniform vec3 uCore;void main(){vec3 n=normalize(vNormal);vec3 delta=uCore-vPosition;float distanceToLight=length(delta);
float point=max(dot(n,normalize(delta)),0.0)*1.8/(0.7+distanceToLight*distanceToLight);
float fill=max(dot(n,normalize(vec3(-0.7,0.8,1.0))),0.0);
vec3 view=normalize(vec3(0.0,0.16,5.7)-vPosition);vec3 halfVector=normalize(normalize(delta)+view);
float spec=pow(max(dot(n,halfVector),0.0),54.0)*0.65;float rim=pow(1.0-max(dot(n,view),0.0),3.0);
vec3 color=vColor*(vec3(0.38)+vec3(0.65,0.76,0.83)*fill+vec3(1.0,0.58,0.20)*point)+vec3(1.0,0.79,0.48)*spec+vec3(0.36,0.54,0.57)*rim*0.3;
color=mix(color,vColor*1.12,vEmission);color=pow(max(color,vec3(0.0)),vec3(0.82));gl_FragColor=vec4(color,1.0);}`;
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS)){const message=gl.getShaderInfoLog(s);gl.deleteShader(s);throw Error(message);}return s;}
function initialize(){
 gl=canvas.getContext('webgl',{alpha:true,antialias:true,powerPreference:'low-power'});if(!gl)throw Error('WebGL unavailable');
 const vs=shader(gl.VERTEX_SHADER,vertexSource),fs=shader(gl.FRAGMENT_SHADER,fragmentSource);
 program=gl.createProgram();gl.attachShader(program,vs);gl.attachShader(program,fs);gl.linkProgram(program);gl.deleteShader(vs);gl.deleteShader(fs);
 if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));
 gl.useProgram(program);buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(vertices),gl.STATIC_DRAW);
 for(const [name,size,offset] of [['aPosition',3,0],['aNormal',3,12],['aColor',3,24],['aEmission',1,36]]){const at=gl.getAttribLocation(program,name);gl.enableVertexAttribArray(at);gl.vertexAttribPointer(at,size,gl.FLOAT,false,40,offset);}
 locations={model:gl.getUniformLocation(program,'uModel'),projection:gl.getUniformLocation(program,'uProjection'),core:gl.getUniformLocation(program,'uCore')};
 gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.clearColor(0,0,0,0);canvas.hidden=false;fallback.setAttribute('hidden','');button.disabled=false;lost=false;
 resize();updateStatus();schedule();
}
function resize(){if(!gl||lost)return;const r=stage.getBoundingClientRect(),dpr=Math.min(devicePixelRatio||1,1.75);canvas.width=Math.max(1,Math.round(r.width*dpr));canvas.height=Math.max(1,Math.round(r.height*dpr));gl.viewport(0,0,canvas.width,canvas.height);render();}
function render(){
 if(!gl||lost)return;
 const angle=.40+elapsed*.15+turnX,c=Math.cos(angle),s=Math.sin(angle),tilt=-.08+turnY,ct=Math.cos(tilt),st=Math.sin(tilt);
 const bob=Math.sin(elapsed*.75)*.055;
 const model=new Float32Array([c,st*s,-ct*s,0,0,ct,st,0,s,-st*c,ct*c,0,0,bob,0,1]);
 const aspect=canvas.width/canvas.height,f=1/Math.tan(Math.PI/8),near=.1,far=30;
 const projection=new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)/(near-far),-1,0,0,2*far*near/(near-far),0]);
 gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.uniformMatrix4fv(locations.model,false,model);gl.uniformMatrix4fv(locations.projection,false,projection);gl.uniform3f(locations.core,0,-.12+bob,0);gl.drawArrays(gl.TRIANGLES,0,vertices.length/10);
}
function cancel(){if(raf)cancelAnimationFrame(raf);raf=0;last=0;}
function schedule(){if(!raf&&running&&!lost&&!document.hidden&&inView)raf=requestAnimationFrame(frame);}
function frame(now){raf=0;if(!running||lost||document.hidden||!inView)return;const dt=last?Math.min((now-last)/1000,.05):0;last=now;elapsed+=dt;turnX+=(pointerX-turnX)*.045;turnY+=(pointerY-turnY)*.045;render();schedule();}
function updateStatus(){button.textContent=running?'Pause animation':'Resume animation';status.textContent=running?'Animated 3D lantern. Move your pointer gently across the object to change its angle.':'3D lantern paused. Resume is optional'+(reduced.matches?' — reduced motion is enabled.':'.');}
button.addEventListener('click',()=>{running=!running;cancel();updateStatus();if(running)schedule();else render();});
stage.addEventListener('pointermove',e=>{if(!running||e.pointerType==='touch')return;const r=stage.getBoundingClientRect();pointerX=((e.clientX-r.left)/r.width-.5)*.3;pointerY=((e.clientY-r.top)/r.height-.5)*.14;});
stage.addEventListener('pointerleave',()=>{pointerX=0;pointerY=0;});
reduced.addEventListener('change',()=>{if(reduced.matches){running=false;cancel();pointerX=pointerY=0;if(!lost&&gl){updateStatus();render();}}});
document.addEventListener('visibilitychange',()=>{cancel();if(!document.hidden)schedule();});
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();lost=true;cancel();canvas.hidden=true;fallback.removeAttribute('hidden');button.disabled=true;button.textContent='Animation unavailable';status.textContent='3D context interrupted. Showing the still lantern illustration.';});
canvas.addEventListener('webglcontextrestored',()=>{try{initialize();}catch{unavailable();}});
function unavailable(){cancel();if(gl&&!lost){if(buffer)gl.deleteBuffer(buffer);if(program)gl.deleteProgram(program);}lost=true;canvas.hidden=true;fallback.removeAttribute('hidden');button.disabled=true;button.textContent='Animation unavailable';status.textContent='3D is unavailable in this browser. Showing the still lantern illustration.';}
const observer=new ResizeObserver(resize);observer.observe(stage);
const visibilityObserver=typeof IntersectionObserver==='function'?new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;cancel();if(inView)schedule();},{rootMargin:'80px'}):null;
if(visibilityObserver)visibilityObserver.observe(stage);
window.addEventListener('pagehide',()=>{cancel();observer.disconnect();if(visibilityObserver)visibilityObserver.disconnect();if(gl&&!lost){gl.deleteBuffer(buffer);gl.deleteProgram(program);}});
window.addEventListener('pageshow',e=>{if(e.persisted){observer.observe(stage);if(visibilityObserver)visibilityObserver.observe(stage);try{initialize();}catch{unavailable();}}});
try{initialize();}catch{unavailable();}
})();
