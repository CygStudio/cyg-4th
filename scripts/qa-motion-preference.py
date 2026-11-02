import subprocess,json
from pathlib import Path

def run(*args):
 p=subprocess.run(['agent-browser','--session','cyg-motion-preference','--json',*args],capture_output=True,text=True)
 assert p.returncode==0,p.stdout+p.stderr
 r=json.loads(p.stdout);assert r['success'],r
 if args[0] in ['open','reload']:run('tab','t1')
 return r.get('data',{})
def ev(s):return run('eval',s).get('result')
def state():return ev("({off:document.body.classList.contains('motion-off'),pressed:document.querySelector('.motion-toggle').getAttribute('aria-pressed'),label:document.querySelector('.motion-toggle').textContent})")
run('set','viewport','390','900');run('set','media','light','reduced-motion');run('open','http://127.0.0.1:4173/?preference-regression=1')
ev("sessionStorage.removeItem('cyg-motion-off')");run('reload')
initial=state()
ev("document.querySelector('.motion-toggle').click()")
first=state()
ev("document.querySelector('.motion-toggle').click()")
second=state()
print(json.dumps({'initial':initial,'firstClick':first,'secondClick':second},ensure_ascii=False),flush=True)
assert not initial['off'] and initial['pressed']=='true','Fresh visit must default ON even with system reduced motion'
assert first['off'] and first['pressed']=='false','Explicit OFF must work'
assert not second['off'] and second['pressed']=='true','Explicit ON must work'
run('wait','--fn','window.__introDone===true')
depth=ev("""(async()=>{window.scrollTo({top:400,behavior:'instant'});await new Promise(r=>setTimeout(r,1000));return +gsap.getProperty('.stage-character','y')})()""")
assert depth < -5,'Parallax must actually animate under system reduced motion'
drawer=ev("""(async()=>{document.querySelector('.menu-toggle').click();const start=+gsap.getProperty('.drawer-panel','xPercent');await new Promise(r=>setTimeout(r,150));return {start,middle:+gsap.getProperty('.drawer-panel','xPercent')}})()""")
assert drawer['start']>drawer['middle']>0,drawer
run('wait','--fn',"Math.abs(gsap.getProperty('.drawer-panel','xPercent'))<.1")
travel=ev("""(async()=>{document.querySelector('.drawer-content a[href="#credits"]').click();await new Promise(r=>setTimeout(r,500));return {y:scrollY,open:document.querySelector('dialog').open,target:document.querySelector('#credits').getBoundingClientRect().top}})()""")
assert not travel['open'] and travel['y']>400 and travel['target']>150,travel
run('wait','--fn',"document.querySelector('#credits').getBoundingClientRect().top<100")
ev("document.querySelector('.motion-toggle').click()")
run('reload');assert state()['off'],'Explicit OFF must survive reload'
ev("document.querySelector('.motion-toggle').click()")
run('reload');assert not state()['off'],'Explicit ON must survive reload'
run('set','media','light','no-preference');run('set','media','light','reduced-motion')
assert not state()['off'],'OS setting must not override explicit ON'
Path('docs/motion-preference-qa.json').write_text(json.dumps({'status':'PASS','defaultOnUnderReducedMotion':True,'toggleBothDirections':True,'explicitPreferencePersists':True,'parallaxY':depth,'drawer':drawer,'smoothScroll':travel},indent=2)+'\n')
print('PASS motion preference, real parallax, drawer and smooth scroll',flush=True)
