import subprocess,json
from pathlib import Path
out=Path('artifacts/qa/drawer');out.mkdir(parents=True,exist_ok=True)
def run(*args):
 p=subprocess.run(['agent-browser','--session','cyg-drawer-qa','--json',*args],capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
 r=json.loads(p.stdout);assert r['success'],r
 if args[0] in ['open','reload']:run('tab','t1')
 return r.get('data',{})
def ev(s):return run('eval',s).get('result')
reports=[]
for width in [320,390,760]:
 run('set','viewport',str(width),'844');run('set','media','light','reduced-motion');run('open',f'http://127.0.0.1:4173/?drawer=v3-{width}');run('wait','--fn','window.__introDone === true')
 assert ev("document.documentElement.scrollWidth===innerWidth && document.querySelector('.menu-toggle').checkVisibility()")
 run('screenshot',str(out/f'{width}-closed.png'))
 ev("window.scrollTo({top:1000,behavior:'instant'})");run('click','.menu-toggle')
 assert ev("document.querySelector('#mobile-menu').open && document.activeElement.classList.contains('menu-close') && document.body.classList.contains('drawer-open')")
 run('screenshot',str(out/f'{width}-open.png'))
 run('press','Shift+Tab')
 assert ev("document.activeElement.classList.contains('motion-toggle')"),'focus must stay in drawer'
 run('press','Tab');assert ev("document.activeElement.classList.contains('menu-close')")
 run('press','Escape');run('wait','--fn',"!document.querySelector('#mobile-menu').open")
 assert ev("window.scrollY===1000 && !document.body.classList.contains('drawer-open') && document.activeElement.classList.contains('menu-toggle')")
 run('click','.menu-toggle');run('click','.drawer-content a[href="#credits"]')
 assert ev("!document.querySelector('#mobile-menu').open && location.hash==='#credits' && document.activeElement.id==='credits'")
 assert ev("document.querySelector('#credits').getBoundingClientRect().top>=document.querySelector('.site-header').getBoundingClientRect().bottom"),'anchor hidden by header'
 run('click','.menu-toggle');run('click','.menu-close');assert ev("!document.querySelector('#mobile-menu').open")
 run('click','.menu-toggle');run('set','viewport','1100','844');ev("window.dispatchEvent(new Event('resize'))");run('wait','--fn',"!document.querySelector('#mobile-menu').open")
 assert ev("!document.querySelector('#mobile-menu').open && !document.body.classList.contains('drawer-open') && document.querySelector('.site-header nav')!==null")
 reports.append({'width':width,'status':'PASS','focusTrap':True,'escape':True,'scrollRestored':True,'anchor':True,'resize':True})
 print('PASS',width,flush=True)
run('set','viewport','390','844');run('set','media','light','no-preference');run('open','http://127.0.0.1:4173/?drawer=animated')
ev("sessionStorage.removeItem('cyg-motion-off')");run('reload');run('wait','--fn','window.__introDone === true')
run('click','.menu-toggle');run('click','.menu-close');run('wait','--fn',"!document.querySelector('#mobile-menu').open")
run('click','.menu-toggle');run('wait','--fn',"Math.abs(document.querySelector('.drawer-panel').getBoundingClientRect().right-innerWidth)<1")
# Native dialog's empty left area acts as the backdrop dismissal target.
run('mouse','move','5','400');run('mouse','down');run('mouse','up');run('wait','--fn',"!document.querySelector('#mobile-menu').open")
print('PASS animated close and backdrop dismissal',flush=True)
Path('docs/drawer-qa.json').write_text(json.dumps({'layouts':reports,'animatedDismissal':'PASS','humanAcceptance':'NOT RUN'},indent=2)+'\n')
