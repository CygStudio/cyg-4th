// CDP input runs only against this task's owned agent-browser session.
import { execFileSync } from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';
const url = process.argv[2] || 'http://127.0.0.1:4173/cafe/';
const wsUrl = execFileSync('agent-browser', ['--session', 'donkey-cafe-505d08606d58', 'get', 'cdp-url'], {encoding:'utf8'}).trim();
const ws=new WebSocket(wsUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j});
let serial=0;const pending=new Map();
ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result)}};
function call(method,params={},sessionId){return new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params,sessionId}));})}
const {targetInfos}=await call('Target.getTargets');const target=targetInfos.find(t=>t.type==='page'&&t.url===url);if(!target)throw Error('Owned cafe tab not found');
const {sessionId}=await call('Target.attachToTarget',{targetId:target.targetId,flatten:true});
const page=(method,params)=>call(method,params,sessionId);
const ev=async(expression)=>(await page('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true})).result.value;
try {
 await page('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:3,mobile:true});
 await page('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:5});
 await ev('window.scrollTo(0,0);document.querySelector("#reset").click()');
 await ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');
 const start=await ev('window.__cafe.snapshot()');if(start.renderer.dpr!==1.6)throw Error('DPR cap incorrect');
 const r=await ev('(()=>{const b=document.querySelector("canvas").getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2}})()');
 const touch=(type,points)=>page('Input.dispatchTouchEvent',{type,touchPoints:points.map((p,i)=>({x:p[0],y:p[1],id:i,radiusX:4,radiusY:4,force:1}))});
 await touch('touchStart',[[r.x,r.y]]);await touch('touchMove',[[r.x+50,r.y+20]]);await touch('touchEnd',[]);
 const drag=await ev('window.__cafe.snapshot()');if(JSON.stringify(start.camera)===JSON.stringify(drag.camera))throw Error('Touch orbit unchanged');
 const distance=s=>Math.hypot(...s.camera.map((x,i)=>x-s.target[i]));
 await touch('touchStart',[[r.x-30,r.y],[r.x+30,r.y]]);await touch('touchMove',[[r.x-65,r.y],[r.x+65,r.y]]);await touch('touchEnd',[]);
 const pinch=await ev('window.__cafe.snapshot()');if(Math.abs(distance(drag)-distance(pinch))<.01)throw Error('Pinch zoom unchanged');
 await ev('document.querySelector("#quality").value="light";document.querySelector("#quality").dispatchEvent(new Event("change"))');
 if((await ev('window.__cafe.snapshot()')).renderer.dpr!==1)throw Error('Light DPR incorrect');
 const qa=JSON.parse(await readFile('cafe/QA.json','utf8'));
 qa.checks.emulatedTouch={orbit:true,pinchZoom:true,deviceDpr:3,balancedRendererDpr:1.6,lightRendererDpr:1,physicalDevice:false};
 await writeFile('cafe/QA.json',JSON.stringify(qa,null,2)+'\n');console.log('PASS emulated touch orbit, pinch zoom, DPR 3 capped to 1.6 / 1');
} finally {
 await page('Emulation.setTouchEmulationEnabled',{enabled:false});await page('Emulation.clearDeviceMetricsOverride');ws.close();
}
