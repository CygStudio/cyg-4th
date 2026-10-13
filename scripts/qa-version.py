"""Verify a real local browser rendering using the isolated agent-browser session."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
slug=sys.argv[1]
session='cyg-fourth-505d08606d58'
art=root/'artifacts/qa'/slug;art.mkdir(parents=True,exist_ok=True)
def run(*args):
 p=subprocess.run(['agent-browser','--session',session,'--json',*args],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr+p.stdout)
 r=json.loads(p.stdout)
 if not r.get('success'):raise RuntimeError(str(r))
 return r.get('data',{})
def ev(js):return run('eval',js).get('result')
run('set','media','light')
run('set','viewport','1440','1000')
run('open','http://127.0.0.1:4173/versions/'+slug+'/')
ev("sessionStorage.removeItem('cyg-motion-off')")
run('reload');run('wait','--fn','window.__introDone === true')
run('screenshot',str(art/'desktop.png'))
initial=ev("({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,title:document.title,triggers:ScrollTrigger.getAll().length})")
assert initial['width']==initial['scrollWidth'],initial
assert initial['triggers']>0,initial
motion=ev("new Promise(resolve=>{const tween=gsap.globalTimeline.getChildren(true,true,false).find(t=>t.repeat()===-1);const el=tween?.targets()[0];const before=el?getComputedStyle(el).transform:null;requestAnimationFrame(()=>requestAnimationFrame(()=>resolve({before,after:el?getComputedStyle(el).transform:null})))})")
assert motion['before'] != motion['after'], motion
ev("document.querySelector('#gifts').scrollIntoView({behavior:'instant'})")
run('wait','--fn',"[...document.images].filter(i=>i.getBoundingClientRect().top<innerHeight).every(i=>i.complete&&i.naturalWidth>0)")
run('find','role','button','click','--name','複製活動 TAG')
copy=ev("document.querySelector('.status-message').textContent")
assert '四季熙光皆成歌' in copy,copy
run('find','text','現場有哪些應援安排？','click','--exact')
faq=ev("[...document.querySelectorAll('details')].some(e=>e.open && e.textContent.includes('投影機'))")
assert faq
# Scroll through each section, letting real entry animations finish before a full-page capture.
ev("(async()=>{for(const el of document.querySelectorAll('.section,.closing')){el.scrollIntoView({behavior:'instant'});await new Promise(r=>setTimeout(r,180));}await new Promise(r=>setTimeout(r,900));window.scrollTo({top:0,behavior:'instant'});return true})()")
images=ev("[...document.images].map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0}))")
assert all(i['loaded'] for i in images),images
run('screenshot','--full',str(art/'desktop-full.png'))
run('find','role','button','click','--name','動態：開啟')
paused=ev("({off:document.body.classList.contains('motion-off'),triggers:ScrollTrigger.getAll().length})")
assert paused['off'] and paused['triggers']==0,paused
run('find','role','button','click','--name','動態：關閉')
run('wait','--fn','window.__introDone === true')
run('set','viewport','390','844')
ev("window.scrollTo({top:0,behavior:'instant'})")
run('reload');run('wait','--fn','window.__introDone === true')
run('screenshot',str(art/'mobile.png'))
mobile=ev("({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,links:[...document.querySelectorAll('a')].filter(a=>a.href.startsWith('https:')).map(a=>a.href)})")
assert mobile['width']==mobile['scrollWidth'],mobile
run('set','media','light','reduced-motion');run('reload')
run('wait','--fn','window.__introDone === true')
reduced=ev("({off:document.body.classList.contains('motion-off'),triggers:ScrollTrigger.getAll().length,headingVisible:getComputedStyle(document.querySelector('h1')).opacity==='1'})")
assert reduced['off'] and reduced['triggers']==0 and reduced['headingVisible'],reduced
ev("(async()=>{for(const el of document.querySelectorAll('.section,.closing')){el.scrollIntoView({behavior:'instant'});await new Promise(r=>setTimeout(r,100));}window.scrollTo({top:0,behavior:'instant'});return true})()")
run('wait','--fn',"[...document.images].every(i=>i.complete&&i.naturalWidth>0)")
run('screenshot','--full',str(art/'mobile-full.png'))
errors=run('errors')
assert not errors.get('errors'),errors
report={'status':'PASS','desktop':initial,'mobile':mobile,'images':images,'motionSample':motion,'pauseControl':paused,'reducedMotion':reduced,'copyTag':copy,'faqExpanded':faq,'pageErrors':errors.get('errors',[]),'notRun':['實體手機效能','外部網站內容驗收','使用者美術驗收']}
report_path=root/'versions'/slug/'QA.json'
previous=json.loads(report_path.read_text()) if report_path.exists() else {}
for key in ['narrowScreen','carousel','responsiveLayout','viewportHeader']:
 if key in previous:report[key]=previous[key]
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
run('set','media','light')
from PIL import Image
im=Image.open(art/'desktop.png');im.thumbnail((1000,700));im.save(root/'versions'/slug/'preview.webp',quality=85)
print('PASS '+slug+' desktop/mobile/images/motion/FAQ/copy/reduced-motion')
