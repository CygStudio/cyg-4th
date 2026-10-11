"""Real Chromium checks. Requires existing agent-browser; installs nothing."""
import json, subprocess, sys, time
from pathlib import Path
root=Path(__file__).resolve().parent.parent
base=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:4173'
session='donkey-cafe-505d08606d58'
shots=root/'artifacts/qa/cafe';shots.mkdir(parents=True,exist_ok=True)
def run(*args):
 p=subprocess.run(['agent-browser','--session',session,'--json',*args],capture_output=True,text=True)
 if p.returncode: raise RuntimeError(p.stdout+p.stderr)
 r=json.loads(p.stdout)
 if not r.get('success'):raise RuntimeError(str(r))
 return r.get('data',{})
def ev(js):return run('eval',js).get('result')
def snap():return ev('window.__cafe.snapshot()')
def ready():run('wait','--fn','window.__cafe?.ready === true')
def click(selector):
 run('click',selector)
 # Viewer redraw is demand-driven; sample after the requested frame has rendered.
 ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
report={'environment':'Chromium desktop and mobile emulation; not physical mobile','checks':{}}
c=report['checks']
run('set','viewport','1440','1050');run('set','media','light','reduced-motion');run('open',base+'/cafe/');ready()
run('errors','--clear')
first=snap();assert first['meshes']==54 and first['renderer']['calls']<=120
report['desktopInitial']=first
run('screenshot','--full',str(shots/'desktop.png'))
c['views']={}
for name in ['overview','interior','window','counter','plan']:
 click('[data-view="'+name+'"]');s=snap();assert s['view']==name
 assert ev('document.querySelectorAll("[data-view][aria-pressed=true]").length')==1
 run('screenshot',str(shots/(name+'.png')));c['views'][name]={'calls':s['renderer']['calls'],'camera':s['camera']}
click('#reset');before=snap();time.sleep(.6);after=snap();assert after['frameCount']==before['frameCount'];c['idleRenderStopped']=True
click('#outline');off=snap();assert not off['outline'] and off['renderer']['calls']<before['renderer']['calls'];c['outlineDrawCalls']={'on':before['renderer']['calls'],'off':off['renderer']['calls']};click('#outline')
click('#evidence');assert snap()['evidence'];c['inferredMeshes']=snap()['inferredMeshes'];click('#evidence')
click('#cutaway');assert not snap()['cutaway'];click('#cutaway')
run('focus','#scene');before=snap()['camera'];run('press','ArrowRight');assert snap()['camera']!=before;run('press','r');c['keyboardOrbitReset']=True
before=snap()['camera'];click('#zoom-in');assert snap()['camera']!=before;click('#zoom-out');click('#reset');c['zoomButtons']=True
rect=ev('(()=>{let r=document.querySelector("#scene").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()')
before=snap()['camera'];x,y=int(rect['x']),int(rect['y']);run('mouse','move',str(x),str(y));run('mouse','down');run('mouse','move',str(x+80),str(y+30));run('mouse','up');assert snap()['camera']!=before;c['pointerDrag']=True
run('focus','#daylight');run('press','ArrowLeft');assert snap()['daylight']==.9;c['lightControl']=True
click('#open-research');assert ev('document.querySelector("dialog").open');run('press','Escape');assert not ev('document.querySelector("dialog").open');c['researchDialogEscape']=True
c['responsive']={}
run('set','device','iPhone 12');run('open',base+'/cafe/');ready()
for width in [390,320]:
 run('set','viewport',str(width),'844');click('#reset')
 layout=ev('({width:innerWidth,scroll:document.documentElement.scrollWidth,dpr:devicePixelRatio})');assert layout['width']==width and layout['scroll']==width
 assert snap()['renderer']['dpr']<=1.6
 click('[data-view="interior"]');assert snap()['view']=='interior';click('#reset')
 ev('window.scrollTo({top:0,behavior:"instant"})')
 run('screenshot','--full',str(shots/('mobile-'+str(width)+'.png')));c['responsive'][str(width)]=layout
run('select','#quality','light');assert snap()['renderer']['dpr']==1;c['lightQualityDpr']=1
report['consoleBeforeFailureTests']=run('errors');assert not report['consoleBeforeFailureTests'].get('errors')
run('network','route','**/little-donkey.glb','--abort');run('open',base+'/cafe/');run('wait','--fn','!document.querySelector("#error-panel").hidden')
assert ev('document.querySelector("#fallback").naturalWidth>0 && !document.querySelector("#fallback").classList.contains("hidden") && document.querySelector("#zoom-in").disabled')
click('#open-research');assert ev('document.querySelector("dialog").open');run('press','Escape');c['glbNetworkFailureFallback']=True
run('network','unroute','**/little-donkey.glb');click('#retry');ready();c['retryRecovered']=True
# Real WebGL context loss, not a synthetic DOM event.
ev('document.querySelector("canvas").getContext("webgl2").getExtension("WEBGL_lose_context").loseContext()');run('wait','--fn','!document.querySelector("#error-panel").hidden');c['webglContextLossFallback']=True
run('open',base+'/cafe/');ready();run('set','viewport','1440','1050');run('errors','--clear')
report['status']='PASS';report['notRun']=['physical Android/iPhone FPS and touch usability','site measurements and visual fidelity acceptance','photogrammetry or video reconstruction']
(root/'cafe/QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':c},ensure_ascii=False,indent=2))
