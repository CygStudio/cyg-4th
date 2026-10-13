"""Sample actual animation frames for both nav directions and interrupted reversals."""
import json, os, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
base=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:4173').rstrip('/')
out=root/'artifacts/qa/11-theatre-scrapbook';out.mkdir(parents=True,exist_ok=True)
def run(*args):
 p=subprocess.run(['agent-browser','--session',os.environ.get('CYG_QA_SESSION','cyg-nav-motion'),'--json',*args],capture_output=True,text=True)
 assert p.returncode==0,p.stderr+p.stdout
 result=json.loads(p.stdout);assert result.get('success'),result
 return result.get('data',{})
def ev(js):return run('eval',js).get('result')
run('set','media','light','no-preference')
results=[]
for width,height in [(1440,900),(700,900),(390,844),(320,568),(844,390)]:
 run('set','viewport',str(width),str(height));run('open',base+'/')
 ev("sessionStorage.removeItem('cyg-motion-off')")
 run('reload');run('wait','--fn','window.__introDone===true')
 ev("""window.sampleNav = () => {
 const h=document.querySelector('.site-header'), bg=h.querySelector('.nav-backdrop').getBoundingClientRect();
 const links=[...h.querySelectorAll('nav > *')].map(e=>e.getBoundingClientRect());
 return {bottom:bg.bottom,top:bg.top,brandWidth:h.querySelector('.brand b').getBoundingClientRect().width,
  marqueeBottom:document.querySelector('.marquee').getBoundingClientRect().bottom+scrollY,
  compact:h.classList.contains('is-compact'),moving:h.classList.contains('is-transitioning'),
  fits:links.every((r,i)=>r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=bg.bottom+1&&links.every((s,j)=>i===j||r.right<=s.left+1||s.right<=r.left+1||r.bottom<=s.top+1||s.bottom<=r.top+1))};
 };
 window.recordNav = (top,reverse=false) => new Promise(resolve=>{
  const frames=[sampleNav()],start=performance.now();let reversed=false;
  scrollTo({top,behavior:'instant'});
  function frame(now){
   frames.push(sampleNav());
   if(reverse&&!reversed&&now-start>=110){scrollTo({top:0,behavior:'instant'});reversed=true;}
   if(now-start<900)requestAnimationFrame(frame);else resolve(frames);
  }requestAnimationFrame(frame);
 });""")
 for direction,top,reverse in [('shrink',240,False),('expand',0,False),('reverse',240,True)]:
  frames=ev(f'recordNav({top},{str(reverse).lower()})')
  first,last=frames[0],frames[-1]
  assert not last['moving'] and last['compact']==(direction=='shrink'),(direction,last)
  assert all(f['top']==0 and f['fits'] and abs(f['marqueeBottom']-first['marqueeBottom'])<1 for f in frames),(width,direction,frames)
  assert len(set(round(f['bottom'],1) for f in frames))>6,(direction,frames)
  assert len(set(round(f['brandWidth'],2) for f in frames))>6,(direction,frames)
  if direction=='shrink':assert first['bottom']>last['bottom']
  if direction=='expand':assert first['bottom']<last['bottom']
  if direction=='reverse':assert abs(first['bottom']-last['bottom'])<1
  # A single-step jump is exactly what this change is intended to prevent.
  span=max(f['bottom'] for f in frames)-min(f['bottom'] for f in frames)
  largest=max(abs(a['bottom']-b['bottom']) for a,b in zip(frames,frames[1:]))
  assert largest<span*.7,(direction,largest,span)
  results.append({'viewport':[width,height],'direction':direction,'frames':len(frames),'firstHeight':first['bottom'],'lastHeight':last['bottom'],'distinctHeights':len(set(round(f['bottom'],1) for f in frames)),'largestFrameStep':round(largest,2),'noOverlapOrLayoutShift':True})
 run('screenshot',str(out/f'nav-motion-restored-{width}.png'))
 run('click','.motion-toggle')
 assert ev("document.body.classList.contains('motion-off')")
 frames=ev('recordNav(240)')
 assert all(not f['moving'] for f in frames) and frames[-1]['compact']
 run('click','.site-header a[href="#event"]')
 run('wait','--fn','document.querySelector("#event").getBoundingClientRect().top>=document.querySelector(".site-header").getBoundingClientRect().bottom&&document.querySelector("#event").getBoundingClientRect().top<innerHeight/2')
 print(f'PASS {width}x{height}: shrink/expand/reverse frame continuity, links, motion-off',flush=True)
errors=run('errors').get('errors',[]);assert not errors,errors
report={'status':'PASS','base':base,'scenarios':results,'manualMotionOff':True,'pageErrors':errors,'notRun':['實體手機效能']}
(out/('remote-nav-motion.json' if base.startswith('https:') else 'nav-motion.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if not base.startswith('https:'):
 p=root/'versions/11-theatre-scrapbook/QA.json';qa=json.loads(p.read_text());qa['navTransition']=report;p.write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
run('close')
