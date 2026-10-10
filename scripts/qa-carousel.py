import sys,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent.parent
def run(*args):
 p=subprocess.run(['agent-browser','--session','cyg-fourth-505d08606d58','--json',*args],capture_output=True,text=True)
 assert p.returncode==0,p.stdout+p.stderr
 r=json.loads(p.stdout);assert r.get('success'),r
 return r.get('data',{})
def ev(s):return run('eval',s).get('result')
run('set','viewport','390','844');run('set','media','light');run('open','http://127.0.0.1:4173/versions/10-cinema/');run('wait','--fn','window.__introDone===true')
results=[]
for label,expected in [('下一幕','02 / 03'),('下一幕','03 / 03'),('下一幕','01 / 03'),('上一幕','03 / 03')]:
 run('find','role','button','click','--name',label)
 run('wait','--fn',"document.querySelector('.screen-image').complete&&document.querySelector('.screen-image').naturalWidth>0")
 item=ev("({counter:document.querySelector('.frame-count').textContent,src:document.querySelector('.screen-image').getAttribute('src'),alt:document.querySelector('.screen-image').alt,fit:getComputedStyle(document.querySelector('.screen-image')).objectFit})")
 assert item['counter']==expected,item
 if expected.startswith('02'):assert item['fit']=='contain'
 results.append(item)
 if expected.startswith('02'):run('screenshot',str(root/'artifacts/qa/10-cinema/carousel-picnic-mobile.png'))
run('set','media','light','reduced-motion');run('reload');run('wait','--fn','window.__introDone===true')
run('find','role','button','click','--name','下一幕');assert ev("document.querySelector('.frame-count').textContent")=='02 / 03'
assert ev("document.querySelector('.screen-image').style.transform")==''
q=root/'versions/10-cinema/QA.json';data=json.loads(q.read_text());data['carousel']={'status':'PASS','sequence':results,'reducedMotionSwitch':True};q.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('PASS carousel next/previous/wraparound, panorama preservation, reduced-motion')
