import sys,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent.parent
session='cyg-fourth-505d08606d58'
def run(*args):
 p=subprocess.run(['agent-browser','--session',session,'--json',*args],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 r=json.loads(p.stdout)
 if not r.get('success'):raise RuntimeError(str(r))
 return r.get('data',{})
def ev(s):return run('eval',s).get('result')
for slug in sys.argv[1:]:
 run('set','media','light','reduced-motion');run('set','viewport','320','800');run('open','http://127.0.0.1:4173/versions/'+slug+'/');run('wait','--fn','window.__introDone === true')
 narrow=ev("({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,h1:[...document.querySelector('h1').childNodes].filter(n=>n.nodeType===3||n.nodeType===1).map(n=>{let r=document.createRange();r.selectNodeContents(n);let b=r.getBoundingClientRect();return {left:b.left,right:b.right}}),body:document.body.innerText})")
 assert narrow['width']==narrow['scrollWidth'],(slug,narrow)
 assert all(x['left']>=-1 and x['right']<=321 for x in narrow['h1']),(slug,narrow['h1'])
 ev("(async()=>{for(const e of document.querySelectorAll('.section,.closing')){e.scrollIntoView({behavior:'instant'});await new Promise(r=>setTimeout(r,100));}window.scrollTo({top:0,behavior:'instant'});return true})()")
 assert ev("[...document.images].every(i=>i.complete&&i.naturalWidth>0)"),slug
 # The panorama must retain its full aspect ratio instead of cropping the face.
 panorama=ev("[...document.querySelectorAll('.story-photo img[src*=picnic]')].map(i=>({ratio:i.clientWidth/i.clientHeight,fit:getComputedStyle(i).objectFit}))")
 assert all(abs(p['ratio']-2.82)<.04 and p['fit']=='contain' for p in panorama),(slug,panorama)
 run('screenshot','--full',str(root/'artifacts/qa'/slug/'narrow-full.png'))
 data={'status':'PASS','width':320,'horizontalOverflow':False,'headingInViewport':True,'panorama':panorama}
 q=root/'versions'/slug/'QA.json';report=json.loads(q.read_text());report['narrowScreen']=data;q.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print('PASS narrow layout '+slug,flush=True)
