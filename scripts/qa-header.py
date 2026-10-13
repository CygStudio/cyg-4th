"""Verify viewport-sized stage, minimum height and compact navigation in Chromium."""
import json, subprocess
from pathlib import Path
root=Path(__file__).resolve().parent.parent
out=root/'artifacts/qa/11-theatre-scrapbook';out.mkdir(parents=True,exist_ok=True)
def run(*args):
 p=subprocess.run(['agent-browser','--session','cyg-header-viewport','--json',*args],capture_output=True,text=True)
 assert p.returncode==0,p.stderr+p.stdout
 r=json.loads(p.stdout);assert r.get('success'),r
 return r.get('data',{})
def ev(js):return run('eval',js).get('result')
run('set','media','light','reduced-motion')
results=[]
for width,height in [(1440,900),(1440,1200),(1366,768),(1024,600),(844,390),(768,1024),(700,900),(390,844),(320,568)]:
 run('set','viewport',str(width),str(height));run('open','http://127.0.0.1:4173/')
 run('wait','--fn','window.__introDone===true&&document.querySelector(".stage-character img").complete')
 ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
 expanded=ev("""(() => {
 const header=document.querySelector('.site-header').getBoundingClientRect(), hero=document.querySelector('.hero').getBoundingClientRect();
 const image=document.querySelector('.stage-character img'), rect=image.getBoundingClientRect();
 const paintedHeight=Math.min(rect.height,rect.width*image.naturalHeight/image.naturalWidth);
 const faceBottom=rect.top+(rect.height-paintedHeight)/2+paintedHeight*.3;
 return {width:innerWidth,height:innerHeight,headerHeight:header.height,heroHeight:hero.height,heroBottom:hero.bottom,
  minHeight:parseFloat(getComputedStyle(document.querySelector('.hero')).minHeight),scrollWidth:document.documentElement.scrollWidth,
  faceClear:document.querySelector('.hero h1').getBoundingClientRect().top>faceBottom,
  contentContained:[...document.querySelectorAll('.hero-copy h1,.hero-copy .button')].every(e=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.top>=hero.top&&r.bottom<=hero.bottom;})};
 })()""")
 assert abs(expanded['heroBottom']-max(height,expanded['headerHeight']+expanded['minHeight']))<1,expanded
 assert expanded['scrollWidth']==width and expanded['faceClear'] and expanded['contentContained'],expanded
 run('screenshot',str(out/f'header-{width}x{height}.png'))
 ev('window.scrollTo({top:240,behavior:"instant"})')
 run('wait','--fn','document.querySelector(".site-header").classList.contains("is-compact")')
 compact=ev("""(() => {const h=document.querySelector('.site-header'),r=h.getBoundingClientRect();return {top:r.top,height:r.height,position:getComputedStyle(h).position,heroDocumentBottom:document.querySelector('.hero').getBoundingClientRect().bottom+scrollY,links:[...h.querySelectorAll('a')].filter(a=>a.getClientRects().length).length};})()""")
 assert compact['top']==0 and compact['position']=='fixed' and compact['height']<expanded['headerHeight'],compact
 assert abs(compact['heroDocumentBottom']-expanded['heroBottom'])<1,compact
 assert compact['links']==5,compact
 run('click','.site-header a[href="#event"]')
 run('wait','--fn','document.querySelector("#event").getBoundingClientRect().top>=document.querySelector(".site-header").getBoundingClientRect().bottom&&document.querySelector("#event").getBoundingClientRect().top<innerHeight/2')
 run('screenshot',str(out/f'nav-{width}x{height}.png'))
 ev('window.scrollTo({top:0,behavior:"instant"})')
 run('wait','--fn','!document.querySelector(".site-header").classList.contains("is-compact")')
 assert abs(ev('document.querySelector(".site-header").getBoundingClientRect().height')-expanded['headerHeight'])<1
 results.append({'expanded':expanded,'compact':compact,'anchorClear':True,'restoredAtTop':True})
 print(f'PASS {width}x{height}: viewport/min-height, compact nav, stable layout, anchor',flush=True)
# Resize while fixed to exercise a two-row mobile header becoming one-row desktop.
ev('window.scrollTo({top:240,behavior:"instant"})')
run('wait','--fn','document.querySelector(".site-header").classList.contains("is-compact")')
run('set','viewport','1440','900')
run('wait','--fn','Math.abs(document.querySelector(".hero").getBoundingClientRect().height+document.querySelector(".header-slot").getBoundingClientRect().height-innerHeight)<1')
assert ev('document.querySelector(".site-header").getBoundingClientRect().top')==0
errors=run('errors').get('errors',[]);assert not errors,errors
p=root/'versions/11-theatre-scrapbook/QA.json';report=json.loads(p.read_text());report['viewportHeader']={'status':'PASS','scenarios':results,'resizeWhileFixed':True,'pageErrors':errors};p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
run('close')
