import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.join(path.dirname(fileURLToPath(import.meta.url)),'dist');
const port=Number(process.env.SKILLLANTERN_PORT||4173);
const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.zip':'application/zip','.txt':'text/plain; charset=utf-8'};
const server=http.createServer((req,res)=>{
  try{
    if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);res.end();return}
    let name=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);
    if(name.endsWith('/'))name+='index.html';
    const file=path.resolve(root,'.'+name);
    if(!file.startsWith(root+path.sep)||name.split(/[\\/]/).some(part=>part.startsWith('.'))||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'});res.end('Page not found.');return}
    res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'});
    if(req.method==='HEAD'){res.end();return}fs.createReadStream(file).pipe(res);
  }catch{res.writeHead(400);res.end('Invalid request.')}
});
server.on('error',err=>{console.error(err.message);process.exitCode=1});
server.listen(port,'127.0.0.1',()=>console.log(`SkillLantern local website: http://127.0.0.1:${server.address().port}`));
process.on('SIGINT',()=>server.close(()=>process.exit(0)));
