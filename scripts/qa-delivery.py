"""Smoke-test built pages, keyboard use and deliberate resource failures."""
import json, subprocess
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser
root=Path(__file__).resolve().parent.parent
base='http://127.0.0.1:4173/dist/'
class References(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['src','href'] and v and not v.startswith(('https:','#')):self.urls.append(v)
versions=json.loads((root/'versions/catalog.json').read_text());assert len(versions)==11
checked=set()
for url in [base,base+'designs/',*[base+'versions/'+v['slug']+'/' for v in versions]]:
 with urlopen(url) as r:html=r.read().decode();assert r.status==200
 parser=References();parser.feed(html)
 for ref in parser.urls:
  url_ref=urljoin(url,ref)
  if url_ref in checked:continue
  with urlopen(url_ref) as r:assert r.status==200;assert len(r.read())>0
  checked.add(url_ref)
assert not (root/'dist/assets/originals').exists()
def run(*args):
 p=subprocess.run(['agent-browser','--session','cyg-fourth-505d08606d58','--json',*args],capture_output=True,text=True)
 assert p.returncode==0,p.stdout+p.stderr
 r=json.loads(p.stdout);assert r.get('success'),r
 return r.get('data',{})
def ev(js):return run('eval',js).get('result')
art=root/'artifacts/qa/delivery';art.mkdir(parents=True,exist_ok=True)
run('set','media','light');run('set','viewport','1440','1000');run('open',base+'designs/')
run('wait','--fn',"document.querySelectorAll('article').length===11")
ev("(async()=>{for(const e of document.querySelectorAll('article')){e.scrollIntoView();await new Promise(r=>setTimeout(r,100));}window.scrollTo(0,0);return true})()")
run('wait','--fn',"[...document.images].every(i=>i.complete&&i.naturalWidth>0)")
run('screenshot','--full',str(art/'gallery-desktop.png'))
run('set','viewport','390','844');run('reload');run('wait','--fn',"document.querySelectorAll('article').length===11")
assert ev('innerWidth===document.documentElement.scrollWidth')
run('screenshot',str(art/'gallery-mobile.png'))
run('open',base+'versions/10-cinema/');run('wait','--fn','window.__introDone===true')
run('press','Tab');assert ev("document.activeElement.classList.contains('skip')")
run('press','Enter');assert ev("location.hash==='#main'")
run('focus','.next-scene');run('press','Enter');assert ev("document.querySelector('.frame-count').textContent==='02 / 03'")
run('focus','details summary');run('press','Enter');assert ev("document.querySelector('details').open")
blocked=['**/vendor/*.js','**/assets/web/*.webp']
try:
 for pattern in blocked:run('network','route',pattern,'--abort')
 run('open',base+'versions/10-cinema/?resource-failure-check=1');run('wait','--fn','window.__introDone===true')
 assert ev("typeof window.gsap==='undefined'")
 assert ev("[...document.images].every(i=>i.naturalWidth===0)")
 assert ev("getComputedStyle(document.querySelector('h1')).opacity==='1'")
 assert ev("document.querySelector('#event').textContent.includes('13:00')&&document.querySelector('#event').textContent.includes('Little Donkey Cafe 小驢館')")
 run('find','role','button','click','--name','下一幕');assert ev("document.querySelector('.frame-count').textContent==='02 / 03'")
 run('focus','details summary');run('press','Enter');assert ev("document.querySelector('details').open")
 assert not run('errors').get('errors')
 run('screenshot','--full',str(art/'resources-blocked.png'))
finally:
 for pattern in blocked:run('network','unroute',pattern)
run('set','viewport','1440','1000');run('set','media','light');run('open','http://127.0.0.1:4173/designs/')
run('wait','--fn',"document.querySelectorAll('article').length===11")
report={'status':'PASS','builtPages':len(versions)+2,'homepageVersion':11,'collectionPath':'/designs/','localReferencesFetched':len(checked),'rawAssetsExcludedFromBuild':True,'gallery':{'pages':len(versions),'desktopImagesLoaded':len(versions),'mobileWidth':390,'horizontalOverflow':False},'keyboard':{'page':'10-cinema','skipLink':True,'carousel':True,'faq':True},'resourceFailure':{'page':'10-cinema','blocked':['GSAP and ScrollTrigger','WebP images'],'activityTextVisible':True,'faqOperable':True,'carouselStateOperable':True,'pageErrors':[]},'notRun':['實體手機效能','外部頁面內容驗收','素材延遲情境','使用者美術驗收']}
(root/'docs/delivery-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS built pages, local references, gallery, keyboard and resource failure fallback')
